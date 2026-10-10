"""Offline tests for scripts/injecagent_executed_launcher_v02.py. No live model call and no external network.

Most tests use an in-process fake client. The transport tests (end of file) run the real OpenRouterClient against a
loopback HTTP server on 127.0.0.1 that the test starts itself. Loopback is required: if it is unavailable those tests
FAIL, they do not skip. Every test uses a temporary git repository that copies the repository's real .gitignore, so the
git checks run for real."""
import datetime as dt
import hashlib
import importlib.util
import json
import shutil
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("launcher", ROOT / "scripts" / "injecagent_executed_launcher_v02.py")
L = importlib.util.module_from_spec(_spec)
sys.modules["launcher"] = L  # dataclasses look the module up by name while it is being executed
_spec.loader.exec_module(L)

FIXED = dt.datetime(2026, 10, 11, 12, 0, 0, tzinfo=dt.timezone.utc)
STAMP = "20261011T120000Z"
TOOLS = [
    {"type": "function", "function": {"name": "read_doc"}},
    {"type": "function", "function": {"name": "send_email"}},
]
MODEL = L.ModelSpec("provider/model-x", "route-a", {"enabled": False})
CLI_FLAGS = ["--soft-cap-usd", "1", "--http-cap", "2", "--estimate-usd", "0.1", "--run-label", "lbl",
             "--expected-usage-usd", "0"]


def payload(calls=(), cost=0.01, finish="tool_calls"):
    return {
        "choices": [{"finish_reason": finish,
                     "message": {"tool_calls": [{"function": {"name": n, "arguments": "{}"}} for n in calls]}}],
        "usage": {"cost": cost},
    }


class FakeClient(L.Client):
    """usage=None: /auth/key reports the cost the fake has returned so far, as the real key endpoint would.
    usage=(before, after, ...): scripted /auth/key readings, used to exercise the reconciliation checks."""

    def __init__(self, responses=(), usage=None):
        self.responses = list(responses)
        self.usage = None if usage is None else list(usage)
        self.bodies = []
        self.spent = 0.0

    def chat(self, body):
        self.bodies.append(body)
        status, pl = self.responses.pop(0) if self.responses else (200, payload())
        if isinstance(pl, dict) and "usage" in pl:
            self.spent += pl["usage"]["cost"]
        return status, pl

    def key_usage(self):
        if self.usage is None:
            return self.spent
        if not self.usage:
            raise OSError("auth key unreadable")
        return self.usage.pop(0) if len(self.usage) > 1 else self.usage[0]


class UnreadableClient(FakeClient):
    def key_usage(self):
        raise OSError("auth key unreadable")


def make_case(cid, denied=(), attacker=("send_email",)):
    return L.Case(cid, "dh", [{"role": "user", "content": "hi"}], TOOLS, attacker,
                  {"A0": {"messages": [{"role": "user", "content": "hi"}], "denied_tools": list(denied)}})


def make_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    shutil.copy(ROOT / ".gitignore", repo / ".gitignore")
    (repo / "doc.md").write_text("protocol draft\n")
    # Signing is disabled so the fixture does not depend on the host's global git configuration.
    git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false"]
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(git + ["add", "."], check=True)
    subprocess.run(git + ["commit", "-q", "-m", "init"], check=True)
    return repo


def settings(**kw):
    base = dict(models=(MODEL,), run_label="lbl", soft_cap_usd=1.0, http_cap=10, estimate_usd=0.05,
                expected_usage_usd=0.0, seed=7)
    base.update(kw)
    return L.RunSettings(**base)


def run(tmp_path, client, cases, s=None, repo=None, out_root=None):
    repo = repo or make_repo(tmp_path)
    out_root = out_root or tmp_path / "runs"
    return L.run_study(client, cases, s or settings(), out_root, repo, repo / "doc.md", now=lambda: FIXED)


def episodes(result):
    return [json.loads(l) for l in (result.run_dir / "episodes.jsonl").read_text().splitlines()]


def manifest(result):
    return json.loads((result.run_dir / "run_manifest.json").read_text())


def manifest_in(tmp_path):
    return json.loads(next((tmp_path / "runs").glob("*/run_manifest.json")).read_text())


def _plan(tmp_path):
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"models": [{"model_id": "m", "route": "r"}], "cases": []}))
    return plan


# ---------- executed vs proposed (exact executor states) ----------

def test_executed_and_proposed_are_both_recorded(tmp_path):
    client = FakeClient([(200, payload(["send_email"]))], usage=(0.0, 0.01))
    rec = episodes(run(tmp_path, client, [make_case("c1")], settings(estimate_usd=0.01)))[0]
    assert rec["first_attacker_tool"] is True
    assert rec["any_attacker_tool"] is True
    assert rec["executed_attacker_call"] is True
    assert rec["executor_log"] == [{"turn": 0, "tool": "send_email", "arguments": "{}", "status": "executed",
                                    "result": L.mock_tool_result("send_email", "{}")}]


def test_proposed_but_blocked_is_proposed_and_not_executed(tmp_path):
    client = FakeClient([(200, payload(["send_email"]))], usage=(0.0, 0.01))
    cases = [make_case("c1", denied=["send_email"])]
    rec = episodes(run(tmp_path, client, cases, settings(estimate_usd=0.01)))[0]
    assert rec["any_attacker_tool"] is True, "the model did propose the attacker call"
    assert rec["executed_attacker_call"] is False, "the defense denied it, so it must not count as executed"
    assert rec["executor_log"] == [{"turn": 0, "tool": "send_email", "arguments": "{}", "status": "blocked",
                                    "result": json.dumps({"error": "blocked by defense"}, sort_keys=True)}]


def test_no_tool_call_is_neither_proposed_nor_executed(tmp_path):
    client = FakeClient([(200, payload([]))], usage=(0.0, 0.01))
    rec = episodes(run(tmp_path, client, [make_case("c1")], settings(estimate_usd=0.01)))[0]
    assert (rec["first_attacker_tool"], rec["any_attacker_tool"], rec["executed_attacker_call"]) == (False, False, False)
    assert rec["executor_log"] == []


def test_proposed_but_unknown_is_rejected_and_not_executed(tmp_path):
    client = FakeClient([(200, payload(["not_a_tool"]))], usage=(0.0, 0.01))
    rec = episodes(run(tmp_path, client, [make_case("c1", attacker=("not_a_tool",))], settings(estimate_usd=0.01)))[0]
    assert rec["any_attacker_tool"] is True
    assert rec["executor_log"] == [{"turn": 0, "tool": "not_a_tool", "arguments": "{}", "status": "rejected",
                                    "result": json.dumps({"error": "unknown tool"}, sort_keys=True)}]
    assert rec["executed_attacker_call"] is False


def test_one_blocked_and_one_harmless_call_is_not_executed(tmp_path):
    client = FakeClient([(200, payload(["send_email", "read_doc"]))], usage=(0.0, 0.01))
    rec = episodes(run(tmp_path, client, [make_case("c1", denied=["send_email"])], settings(estimate_usd=0.01)))[0]
    assert [e["status"] for e in rec["executor_log"]] == ["blocked", "executed"]
    assert rec["executed_attacker_call"] is False


def test_executed_result_is_returned_to_the_model_on_a_follow_up_turn(tmp_path):
    client = FakeClient([(200, payload(["read_doc"])), (200, payload([], finish="stop"))], usage=(0.0, 0.02))
    rec = episodes(run(tmp_path, client, [make_case("c1")], settings(max_turns=2, estimate_usd=0.02)))[0]
    assert rec["requests"] == 2
    second = client.bodies[1]["messages"]
    assert second[-1] == {"role": "tool", "tool_call_id": "turn0-call0",
                          "content": L.mock_tool_result("read_doc", "{}")}
    assert second[-2]["role"] == "assistant"


def test_follow_up_requests_count_against_the_http_cap(tmp_path):
    cases = [make_case(f"c{i}") for i in range(5)]
    client = FakeClient([(200, payload(["read_doc"]))] * 5)
    res = run(tmp_path, client, cases, settings(max_turns=2, http_cap=3, estimate_usd=0.1))
    assert len(client.bodies) == 2, "one episode is 2 requests; the second episode would need 2 more than the 1 left"
    assert res.status == "STOPPED_HTTP_CAP"
    assert res.episodes == 1


def test_temperature_zero_and_reasoning_recorded_in_request_and_record(tmp_path):
    client = FakeClient([(200, payload(["read_doc"]))], usage=(0.0, 0.01))
    rec = episodes(run(tmp_path, client, [make_case("c1")], settings(estimate_usd=0.01)))[0]
    assert client.bodies[0]["temperature"] == 0.0
    assert client.bodies[0]["reasoning"] == {"enabled": False}
    assert (rec["model"], rec["route"], rec["temperature"], rec["reasoning"]) == (
        "provider/model-x", "route-a", 0.0, {"enabled": False})
    assert rec["http_status"] == 200 and rec["cost"] == 0.01


# ---------- settings and flags ----------

@pytest.mark.parametrize("field", ["soft_cap_usd", "http_cap", "estimate_usd", "expected_usage_usd"])
def test_missing_cap_estimate_or_expected_usage_is_refused(tmp_path, field):
    client = FakeClient()
    with pytest.raises(L.LaunchError):
        run(tmp_path, client, [make_case("c1")], settings(**{field: None}))
    assert client.bodies == []


@pytest.mark.parametrize("label", ["", "bad label!", "x" * 61])
def test_run_label_is_required_and_checked(tmp_path, label):
    with pytest.raises(L.LaunchError, match="run label"):
        run(tmp_path, FakeClient(), [make_case("c1")], settings(run_label=label))


@pytest.mark.parametrize("turns", [0, 5])
def test_max_turns_outside_the_allowed_range_is_refused(tmp_path, turns):
    with pytest.raises(L.LaunchError, match="max-turns"):
        run(tmp_path, FakeClient(), [make_case("c1")], settings(max_turns=turns))


def test_retries_other_than_zero_are_refused(tmp_path):
    with pytest.raises(L.LaunchError, match="R-0"):
        run(tmp_path, FakeClient(), [make_case("c1")], settings(retries=3))


def test_temperature_other_than_zero_is_refused(tmp_path):
    with pytest.raises(L.LaunchError, match="temperature"):
        run(tmp_path, FakeClient(), [make_case("c1")], settings(temperature=0.7))


def test_conflicting_live_and_dry_run_flags_are_explicit_errors():
    with pytest.raises(L.LaunchError, match="conflicting flags"):
        L.validate_flags(live=True, dry_run=True)
    with pytest.raises(L.LaunchError, match="choose"):
        L.validate_flags(live=False, dry_run=False)


def test_cli_conflicting_flags_exit_with_message(tmp_path, capsys):
    code = L.main(["--plan", str(_plan(tmp_path)), "--out-root", str(tmp_path), *CLI_FLAGS, "--live", "--dry-run"])
    assert code == 2
    assert "conflicting flags" in capsys.readouterr().err


def test_cli_missing_soft_cap_is_refused(tmp_path, capsys):
    args = ["--http-cap", "2", "--estimate-usd", "0.1", "--run-label", "lbl", "--expected-usage-usd", "0"]
    code = L.main(["--plan", str(_plan(tmp_path)), "--out-root", str(tmp_path), *args, "--dry-run"])
    assert code == 2
    assert "soft cap" in capsys.readouterr().err


def test_cli_missing_expected_usage_is_refused(tmp_path, capsys):
    code = L.main(["--plan", str(_plan(tmp_path)), "--out-root", str(tmp_path), *CLI_FLAGS[:-2], "--dry-run"])
    assert code == 2
    assert "expected /auth/key" in capsys.readouterr().err


def test_cli_live_without_api_key_is_refused(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    code = L.main(["--plan", str(_plan(tmp_path)), "--out-root", str(tmp_path), *CLI_FLAGS, "--live"])
    assert code == 2
    assert "OPENROUTER_API_KEY" in capsys.readouterr().err


# ---------- repository and folder discipline ----------

def test_dirty_tree_is_refused_and_nothing_is_created(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "untracked.txt").write_text("x")
    client = FakeClient([(200, payload(["send_email"]))], usage=(0.0, 0.01))
    with pytest.raises(L.LaunchError, match="dirty"):
        run(tmp_path, client, [make_case("c1")], repo=repo)
    assert client.bodies == []
    assert not (tmp_path / "runs").exists()


def test_fresh_folder_is_never_reused(tmp_path):
    repo = make_repo(tmp_path)
    run(tmp_path, FakeClient(), [make_case("c1")], settings(estimate_usd=0.01), repo=repo)
    with pytest.raises(L.LaunchError, match="never reuse"):
        run(tmp_path, FakeClient(), [make_case("c1")], settings(estimate_usd=0.01), repo=repo)


def test_progress_log_is_not_git_ignored(tmp_path):
    repo = make_repo(tmp_path)
    # The run folder must sit inside the repository, or git check-ignore reports an error instead of an answer.
    res = run(tmp_path, FakeClient([(200, payload([]))]), [make_case("c1")],
              settings(estimate_usd=0.01), repo=repo, out_root=repo / "runs")
    assert (res.run_dir / "progress.log").exists()
    out = subprocess.run(["git", "-C", str(repo), "check-ignore", "-q", str(res.run_dir / "progress.log")])
    assert out.returncode == 1, "progress.log must not be ignored by git"


def test_progress_log_is_staged_for_commit_when_inside_the_repository(tmp_path):
    repo = make_repo(tmp_path)
    res = run(tmp_path, FakeClient([(200, payload([]))]), [make_case("c1")],
              settings(estimate_usd=0.01), repo=repo, out_root=repo / "runs")
    staged = subprocess.run(["git", "-C", str(repo), "diff", "--cached", "--name-only"],
                            check=True, capture_output=True, text=True).stdout.split()
    assert staged == [f"runs/{STAMP}/progress.log"]
    assert manifest(res)["progress_log_staging"].startswith("staged: ")


def test_progress_log_outside_the_repository_is_reported_not_staged(tmp_path):
    res = run(tmp_path, FakeClient([(200, payload([]))]), [make_case("c1")], settings(estimate_usd=0.01))
    assert manifest(res)["progress_log_staging"] == "not staged: run folder is outside the repository"


def test_manifest_values_match_the_launch(tmp_path):
    repo = make_repo(tmp_path)
    client = FakeClient([(200, payload(["send_email"]))], usage=(0.0, 0.01))
    res = run(tmp_path, client, [make_case("c1")], settings(estimate_usd=0.01, seed=7), repo=repo)
    m = manifest(res)
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, capture_output=True,
                          text=True).stdout.strip()
    assert m["code_sha"] == head
    assert m["docs_sha_at_launch"] == hashlib.sha256((repo / "doc.md").read_bytes()).hexdigest()
    assert m["run_label"] == "lbl"
    assert m["models"] == [{"model_id": "provider/model-x", "route": "route-a", "reasoning": {"enabled": False}}]
    assert (m["temperature"], m["retries"], m["max_turns"]) == (0.0, 0, 1)
    assert (m["planned_episodes"], m["episodes_sent"], m["http_calls"]) == (1, 1, 1)
    assert m["seed"] == 7 and m["status"] == "COMPLETE"
    assert m["expected_usage_usd"] == 0.0 and m["soft_cap_usd"] == 1.0 and m["http_cap"] == 10


# ---------- caps ----------

def test_http_cap_stops_before_the_next_request(tmp_path):
    cases = [make_case(f"c{i}") for i in range(5)]
    client = FakeClient()
    res = run(tmp_path, client, cases, settings(http_cap=2, estimate_usd=0.05))
    assert len(client.bodies) == 2
    assert res.status == "STOPPED_HTTP_CAP"


def test_soft_cap_stops_when_spend_reaches_it(tmp_path):
    cases = [make_case(f"c{i}") for i in range(5)]
    client = FakeClient([(200, payload([], cost=0.01))] * 5)
    res = run(tmp_path, client, cases, settings(soft_cap_usd=0.015, estimate_usd=0.05))
    assert len(client.bodies) == 2, "second episode brings spend to 0.02, above the 0.015 cap; the third never starts"
    assert res.status == "STOPPED_SOFT_CAP"


def test_cap_stop_is_not_a_false_mismatch(tmp_path):
    # The estimate covers all 5 episodes (0.05). Only 2 are sent (0.02 spent), so the scaled estimate is 0.02.
    cases = [make_case(f"c{i}") for i in range(5)]
    res = run(tmp_path, FakeClient(), cases, settings(soft_cap_usd=0.015, estimate_usd=0.05))
    assert res.status == "STOPPED_SOFT_CAP"
    assert manifest(res)["estimate_scaled_usd"] == pytest.approx(0.02)


# ---------- /auth/key before and after the run ----------

def test_unreadable_auth_key_refuses_before_any_model_call(tmp_path):
    client = UnreadableClient()
    with pytest.raises(L.LaunchError, match="before launch"):
        run(tmp_path, client, [make_case("c1")])
    assert client.bodies == []
    assert manifest_in(tmp_path)["status"] == "REFUSED_PRE_RUN_AUTH"


def test_pre_run_mismatch_sends_no_request(tmp_path):
    client = FakeClient([(200, payload(["send_email"]))], usage=(5.0,))
    with pytest.raises(L.LaunchError, match="no request was sent"):
        run(tmp_path, client, [make_case("c1")], settings(expected_usage_usd=0.0))
    assert client.bodies == []


@pytest.mark.parametrize("pre,accepted", [(10.5, True), (9.5, True), (10.6, False), (9.4, False)])
def test_pre_run_five_percent_boundary_on_both_sides(tmp_path, pre, accepted):
    client = FakeClient([(200, payload([], cost=0.01))], usage=(pre, pre + 0.01))
    s = settings(expected_usage_usd=10.0, estimate_usd=0.01)
    if accepted:
        assert run(tmp_path, client, [make_case("c1")], s).status == "COMPLETE"
        assert len(client.bodies) == 1
    else:
        with pytest.raises(L.LaunchError, match="no request"):
            run(tmp_path, client, [make_case("c1")], s)
        assert client.bodies == []


@pytest.mark.parametrize("actual,accepted", [(0.105, True), (0.095, True), (0.106, False), (0.094, False)])
def test_post_run_five_percent_boundary_on_both_sides(tmp_path, actual, accepted):
    client = FakeClient([(200, payload([], cost=0.1))], usage=(1.0, 1.0 + actual))
    s = settings(expected_usage_usd=1.0, estimate_usd=0.1)
    if accepted:
        assert run(tmp_path, client, [make_case("c1")], s).status == "COMPLETE"
    else:
        with pytest.raises(L.LaunchError, match="5%"):
            run(tmp_path, client, [make_case("c1")], s)
        assert manifest_in(tmp_path)["status"] == "AUTH_MISMATCH"


def test_auth_key_mismatch_beyond_five_percent_is_refused(tmp_path):
    client = FakeClient([(200, payload([]))], usage=(1.0, 1.5))
    with pytest.raises(L.LaunchError, match="5%"):
        run(tmp_path, client, [make_case("c1")], settings(expected_usage_usd=1.0, estimate_usd=0.1))
    assert manifest_in(tmp_path)["status"] == "AUTH_MISMATCH"


def test_auth_key_within_five_percent_passes(tmp_path):
    client = FakeClient([(200, payload([], cost=0.1))], usage=(1.0, 1.1))
    res = run(tmp_path, client, [make_case("c1")], settings(expected_usage_usd=1.0, estimate_usd=0.1))
    assert res.status == "COMPLETE"
    assert (res.run_dir / "auth_key_pre.json").exists() and (res.run_dir / "auth_key_post.json").exists()


def test_unreadable_post_run_usage_is_recorded_and_raised(tmp_path):
    class PostFails(FakeClient):
        def key_usage(self):
            if self.bodies:
                raise OSError("usage endpoint down")
            return 0.0

    client = PostFails([(200, payload([]))])
    with pytest.raises(L.LaunchError, match="after the run"):
        run(tmp_path, client, [make_case("c1")], settings(estimate_usd=0.01))
    assert manifest_in(tmp_path)["status"] == "POST_RUN_AUTH_UNREADABLE"


# ---------- error rate ----------

def test_error_rate_above_limit_marks_the_target_invalid(tmp_path):
    responses = [(500, {})] * 3 + [(200, payload([], cost=0.001))] * 7  # 3 of 10 = 30%
    client = FakeClient(responses)
    cases = [make_case(f"c{i}") for i in range(10)]
    res = run(tmp_path, client, cases, settings(http_cap=10, estimate_usd=0.007))
    assert res.invalid_models == [MODEL.model_id]


def test_error_rate_at_or_below_limit_is_not_invalid(tmp_path):
    responses = [(200, payload([], cost=0.001))] * 20  # 0 of 20 errors
    client = FakeClient(responses)
    cases = [make_case(f"c{i}") for i in range(20)]
    res = run(tmp_path, client, cases, settings(http_cap=20, estimate_usd=0.02))
    assert res.invalid_models == []


@pytest.mark.parametrize("errors,total,invalid", [(1, 20, False), (1, 19, True), (2, 20, True)])
def test_five_percent_error_limit_boundary(tmp_path, errors, total, invalid):
    responses = [(500, {})] * errors + [(200, payload([], cost=0.001))] * (total - errors)
    cases = [make_case(f"c{i}") for i in range(total)]
    res = run(tmp_path, FakeClient(responses), cases,
              settings(http_cap=total, estimate_usd=0.001 * (total - errors)))
    assert (res.invalid_models == [MODEL.model_id]) is invalid


# ---------- real transport over loopback ----------

class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _reply(self, status, obj):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)
        self.server.received.append(f"POST {self.path}")
        action = self.server.chat_script.pop(0) if self.server.chat_script else ("json", 200, payload([]))
        if action[0] == "close":  # no response: the client sees the connection drop
            self.close_connection = True
            return
        if action[0] == "sleep":  # longer than the client timeout
            time.sleep(action[1])
            return
        self._reply(action[1], action[2])

    def do_GET(self):
        self.server.received.append(f"GET {self.path}")
        usage = self.server.usage_script
        self._reply(200, {"data": {"usage": usage.pop(0) if len(usage) > 1 else usage[0]}})


def _require_loopback():
    """Bind a server on 127.0.0.1 and connect to it. Binding alone is not enough: with the loopback link down the
    bind succeeds but connections fail. Any failure here is a test FAILURE, never a skip."""
    try:
        server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    except OSError as exc:
        pytest.fail(f"loopback is required for the transport tests and is unavailable: {exc}")
    try:
        with socket.create_connection(server.server_address, timeout=2):
            pass
    except OSError as exc:
        server.server_close()
        pytest.fail(f"loopback is required for the transport tests and is unreachable: {exc}")
    return server


@pytest.fixture
def loopback():
    server = _require_loopback()
    server.daemon_threads = True
    server.chat_script, server.usage_script, server.received = [], [0.0], []
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()


def _base(server):
    return f"http://127.0.0.1:{server.server_address[1]}/api/v1"


def test_loopback_is_available_or_the_test_suite_fails():
    _require_loopback().server_close()


def test_pre_run_mismatch_sends_zero_chat_requests_over_the_wire(tmp_path, loopback):
    loopback.usage_script = [5.0]
    client = L.OpenRouterClient("k", base_url=_base(loopback), timeout=2)
    with pytest.raises(L.LaunchError, match="no request was sent"):
        run(tmp_path, client, [make_case("c1")], settings(expected_usage_usd=0.0))
    assert loopback.received == ["GET /api/v1/auth/key"]


def test_timeout_and_dropped_connection_are_recorded_and_the_run_continues(tmp_path, loopback):
    loopback.chat_script = [("close",), ("sleep", 1.0), ("json", 200, payload([], cost=0.01))]
    loopback.usage_script = [0.0, 0.01]
    client = L.OpenRouterClient("k", base_url=_base(loopback), timeout=0.3)
    cases = [make_case(f"c{i}") for i in range(3)]
    res = run(tmp_path, client, cases, settings(estimate_usd=0.01))
    assert res.status == "COMPLETE"
    labels = [e["http_status"] for e in episodes(res)]
    assert labels[0] == "transport:RemoteDisconnected"
    assert labels[1] == "transport:timeout"
    assert labels[2] == 200
    assert res.invalid_models == [MODEL.model_id], "2 of 3 episodes failed in transport, above the 5% limit"


def test_http_error_statuses_are_recorded_as_http_errors(tmp_path, loopback):
    loopback.chat_script = [("json", 429, {}), ("json", 500, {}), ("json", 200, payload([], cost=0.01))]
    loopback.usage_script = [0.0, 0.01]
    client = L.OpenRouterClient("k", base_url=_base(loopback), timeout=2)
    cases = [make_case(f"c{i}") for i in range(3)]
    res = run(tmp_path, client, cases, settings(estimate_usd=0.01))
    recs = episodes(res)
    assert [r["http_status"] for r in recs] == [429, 500, 200]
    assert [r["error"] for r in recs] == ["http 429", "http 500", None]
