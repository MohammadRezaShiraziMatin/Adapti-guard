"""Offline tests for scripts/injecagent_executed_launcher_v02.py. No network, no live model call, no loopback socket.

The client is an in-process fake that returns scripted payloads and scripted /auth/key values. Every test uses a
temporary git repository that copies the repository's real .gitignore, so the git checks run for real."""
import datetime as dt
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("launcher", ROOT / "scripts" / "injecagent_executed_launcher_v02.py")
L = importlib.util.module_from_spec(_spec)
sys.modules["launcher"] = L
_spec.loader.exec_module(L)

FIXED = dt.datetime(2026, 10, 11, 12, 0, 0, tzinfo=dt.timezone.utc)
TOOLS = [
    {"type": "function", "function": {"name": "read_doc"}},
    {"type": "function", "function": {"name": "send_email"}},
]
MODEL = L.ModelSpec("provider/model-x", "route-a", {"enabled": False})


def payload(calls=(), cost=0.01, finish="tool_calls"):
    return {
        "choices": [{"finish_reason": finish,
                     "message": {"tool_calls": [{"function": {"name": n, "arguments": "{}"}} for n in calls]}}],
        "usage": {"cost": cost},
    }


class FakeClient(L.Client):
    """usage=None: /auth/key reports the cost the fake has returned so far, as the real key endpoint would.
    usage=(before, after): scripted /auth/key readings, used to exercise the reconciliation check."""

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
    base = dict(models=(MODEL,), soft_cap_usd=1.0, http_cap=10, estimate_usd=0.05, seed=7)
    base.update(kw)
    return L.RunSettings(**base)


def run(tmp_path, client, cases, s=None, repo=None, out_root=None):
    repo = repo or make_repo(tmp_path)
    out_root = out_root or tmp_path / "runs"
    return L.run_study(client, cases, s or settings(), out_root, repo, repo / "doc.md", now=lambda: FIXED)


def episodes(result):
    return [json.loads(l) for l in (result.run_dir / "episodes.jsonl").read_text().splitlines()]


# ---------- executed vs proposed ----------

def test_executed_and_proposed_are_both_recorded(tmp_path):
    client = FakeClient([(200, payload(["send_email"]))], usage=(0.0, 0.01))
    rec = episodes(run(tmp_path, client, [make_case("c1")], settings(estimate_usd=0.01)))[0]
    assert rec["first_attacker_tool"] is True
    assert rec["any_attacker_tool"] is True
    assert rec["executed_attacker_call"] is True
    assert rec["executor_log"] == [{"tool": "send_email", "arguments": "{}", "status": "executed"}]


def test_proposed_but_blocked_is_proposed_and_not_executed(tmp_path):
    client = FakeClient([(200, payload(["send_email"]))], usage=(0.0, 0.01))
    cases = [make_case("c1", denied=["send_email"])]
    rec = episodes(run(tmp_path, client, cases, settings(estimate_usd=0.01)))[0]
    assert rec["any_attacker_tool"] is True, "the model did propose the attacker call"
    assert rec["executed_attacker_call"] is False, "the executor denied it, so it must not count as executed"
    assert rec["executor_log"][0]["status"] == "blocked"


def test_no_tool_call_is_neither_proposed_nor_executed(tmp_path):
    client = FakeClient([(200, payload([]))], usage=(0.0, 0.01))
    rec = episodes(run(tmp_path, client, [make_case("c1")], settings(estimate_usd=0.01)))[0]
    assert (rec["first_attacker_tool"], rec["any_attacker_tool"], rec["executed_attacker_call"]) == (False, False, False)


def test_unknown_tool_is_rejected_not_executed(tmp_path):
    client = FakeClient([(200, payload(["not_a_tool"]))], usage=(0.0, 0.01))
    rec = episodes(run(tmp_path, client, [make_case("c1", attacker=("not_a_tool",))], settings(estimate_usd=0.01)))[0]
    assert rec["executor_log"][0]["status"] == "rejected"
    assert rec["executed_attacker_call"] is False


def test_request_is_temperature_zero_with_reasoning_recorded(tmp_path):
    client = FakeClient([(200, payload(["read_doc"]))], usage=(0.0, 0.01))
    rec = episodes(run(tmp_path, client, [make_case("c1")], settings(estimate_usd=0.01)))[0]
    assert client.bodies[0]["temperature"] == 0.0
    assert client.bodies[0]["reasoning"] == {"enabled": False}
    assert (rec["model"], rec["route"], rec["temperature"], rec["reasoning"]) == (
        "provider/model-x", "route-a", 0.0, {"enabled": False})
    assert rec["http_status"] == 200 and rec["cost"] == 0.01


# ---------- settings and flags ----------

@pytest.mark.parametrize("field,value", [("soft_cap_usd", None), ("http_cap", None), ("estimate_usd", None)])
def test_missing_cap_or_estimate_is_refused(tmp_path, field, value):
    with pytest.raises(L.LaunchError):
        run(tmp_path, FakeClient(), [make_case("c1")], settings(**{field: value}))


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
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"models": [{"model_id": "m", "route": "r"}], "cases": []}))
    code = L.main(["--plan", str(plan), "--out-root", str(tmp_path), "--soft-cap-usd", "1", "--http-cap", "2",
                   "--estimate-usd", "0.1", "--live", "--dry-run"])
    assert code == 2
    assert "conflicting flags" in capsys.readouterr().err


def test_cli_missing_soft_cap_is_refused(tmp_path, capsys):
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"models": [{"model_id": "m", "route": "r"}], "cases": []}))
    code = L.main(["--plan", str(plan), "--out-root", str(tmp_path), "--http-cap", "2", "--estimate-usd", "0.1",
                   "--dry-run"])
    assert code == 2
    assert "soft cap" in capsys.readouterr().err


def test_cli_live_without_api_key_is_refused(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"models": [{"model_id": "m", "route": "r"}], "cases": []}))
    code = L.main(["--plan", str(plan), "--out-root", str(tmp_path), "--soft-cap-usd", "1", "--http-cap", "2",
                   "--estimate-usd", "0.1", "--live"])
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


def test_manifest_has_required_fields(tmp_path):
    res = run(tmp_path, FakeClient([(200, payload(["send_email"]))], usage=(0.0, 0.01)), [make_case("c1")],
              settings(estimate_usd=0.01))
    m = json.loads((res.run_dir / "run_manifest.json").read_text())
    for key in ("code_sha", "docs_sha_at_launch", "models", "temperature", "retries", "n_cases", "seed",
                "sample_hash", "soft_cap_usd", "http_cap", "estimate_usd", "status", "http_calls", "errors"):
        assert key in m, key
    assert m["status"] == "COMPLETE"
    assert m["models"][0]["route"] == "route-a"


# ---------- caps ----------

def test_http_cap_stops_before_the_next_request(tmp_path):
    cases = [make_case(f"c{i}") for i in range(5)]
    client = FakeClient()
    res = run(tmp_path, client, cases, settings(http_cap=2, estimate_usd=0.02))
    assert len(client.bodies) == 2
    assert res.status == "STOPPED_HTTP_CAP"


def test_soft_cap_stops_when_spend_reaches_it(tmp_path):
    cases = [make_case(f"c{i}") for i in range(5)]
    client = FakeClient([(200, payload([], cost=0.01))] * 5, usage=(0.0, 0.02))
    res = run(tmp_path, client, cases, settings(soft_cap_usd=0.015, estimate_usd=0.02))
    assert len(client.bodies) == 2, "second episode brings spend to 0.02, above the 0.015 cap; the third never starts"
    assert res.status == "STOPPED_SOFT_CAP"


# ---------- /auth/key ----------

def test_unreadable_auth_key_refuses_before_any_model_call(tmp_path):
    client = UnreadableClient()
    with pytest.raises(L.LaunchError, match="before launch"):
        run(tmp_path, client, [make_case("c1")])
    assert client.bodies == []


def test_auth_key_mismatch_beyond_five_percent_is_refused(tmp_path):
    client = FakeClient([(200, payload([]))], usage=(1.0, 1.5))
    with pytest.raises(L.LaunchError, match="5%"):
        run(tmp_path, client, [make_case("c1")], settings(estimate_usd=0.1))
    m = json.loads(next(Path(tmp_path / "runs").glob("*/run_manifest.json")).read_text())
    assert m["status"] == "AUTH_MISMATCH"


def test_auth_key_within_five_percent_passes(tmp_path):
    client = FakeClient([(200, payload([], cost=0.1))], usage=(1.0, 1.1))
    res = run(tmp_path, client, [make_case("c1")], settings(estimate_usd=0.1))
    assert res.status == "COMPLETE"
    assert (res.run_dir / "auth_key_pre.json").exists() and (res.run_dir / "auth_key_post.json").exists()


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
