"""Offline tests for the detached launch, checkpoints, remote push, timeouts and pre-detach validation of
scripts/injecagent_executed_launcher_v02.py.

No live model call and no external network: the study uses the in-process FakeClient from the launcher test file,
and the git checks run for real in temporary repositories. The stalled-push test uses a git ext:: remote that sleeps.

This file has 18 tests. The counts recorded in docs/protocols/DEVIATIONS.md (D3) were for the 12-test version: 12 of 12
on the base 6b309d2, 6 of 12 on 5aa352e, and 1 of 12 on b188675 (the stalled-push test only). The thirteenth test
(manifest and launcher_stdout.log in the checkpoint) fails on edd13b2 and passes with the checkpoint fix; the counts
for the other reference launchers were not re-measured for it."""
import importlib.util
import json
import os
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_injecagent_executed_launcher_v02 import (FIXED, FakeClient, L, ROOT, _commit_prior_run,  # noqa: E402
                                                   _reconciled, make_case, make_repo, payload, run, settings)

SCRIPT = ROOT / "scripts" / "injecagent_executed_launcher_v02.py"


def git_log(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


def checkpoint_repo(tmp_path):
    """make_repo plus a repository-local identity, so commits do not depend on the host's git configuration (CI has none)."""
    repo = make_repo(tmp_path)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@example.invalid"], check=True)
    return repo


def test_detached_command_runs_the_launcher_under_setsid_and_nohup_without_the_detach_flag():
    argv = ["--live", "--run", "R2", "--detach", "--out-root", "runs"]
    cmd = L.detached_command(argv, SCRIPT)
    assert cmd[:3] == ["setsid", "-f", "nohup"]
    assert cmd[3] == sys.executable and cmd[4] == str(SCRIPT)
    assert cmd[5:] == ["--live", "--run", "R2", "--out-root", "runs", "--detached-child"]


def test_detach_flag_is_accepted_by_the_parser():
    args = L.build_parser().parse_args(["--out-root", "x", "--detach"])
    assert args.detach is True


def test_checkpoint_commits_progress_and_episodes_each_time(tmp_path):
    repo = checkpoint_repo(tmp_path)
    run_dir = repo / "runs" / "R2_test"
    run_dir.mkdir(parents=True)
    (run_dir / "progress.log").write_text("start\n")
    (run_dir / "episodes.jsonl").write_text('{"case": "c1"}\n')

    assert "committed" in L.checkpoint_progress(repo, run_dir)
    (run_dir / "episodes.jsonl").write_text('{"case": "c1"}\n{"case": "c2"}\n')
    assert "committed" in L.checkpoint_progress(repo, run_dir)

    log = git_log(repo, "log", "--format=%s", "--", "runs")
    assert log.count("checkpoint R2_test") == 2
    assert git_log(repo, "status", "--porcelain", "--", "runs") == ""


def test_checkpoint_commits_the_manifest_and_the_launcher_stdout_log_into_the_run_folder(tmp_path):
    repo = checkpoint_repo(tmp_path)
    out_root = repo / "runs"
    run_dir = out_root / "R2_stdout"
    run_dir.mkdir(parents=True)
    (run_dir / "progress.log").write_text("start\n")
    (run_dir / "episodes.jsonl").write_text("")
    (run_dir / "run_manifest.json").write_text('{"status": "running"}\n')
    (run_dir / "launcher_stdout.log").write_text("Traceback: none yet\n")

    result = L.checkpoint_progress(repo, run_dir)

    tracked = git_log(repo, "ls-tree", "-r", "--name-only", "HEAD", "--", "runs/R2_stdout").split()
    assert "runs/R2_stdout/run_manifest.json" in tracked
    assert "runs/R2_stdout/launcher_stdout.log" in tracked
    assert result.startswith("committed")


def test_checkpoint_commits_the_rest_when_launcher_stdout_log_is_not_a_regular_file(tmp_path):
    repo = checkpoint_repo(tmp_path)
    run_dir = repo / "runs" / "R2_copy_fails"
    run_dir.mkdir(parents=True)
    (run_dir / "progress.log").write_text("start\n")
    (run_dir / "episodes.jsonl").write_text("")
    (run_dir / "run_manifest.json").write_text('{"status": "running"}\n')
    (run_dir / "launcher_stdout.log").mkdir()  # not a file: it cannot be committed

    result = L.checkpoint_progress(repo, run_dir)

    tracked = git_log(repo, "ls-tree", "-r", "--name-only", "HEAD", "--", "runs/R2_copy_fails").split()
    assert "runs/R2_copy_fails/progress.log" in tracked
    assert "runs/R2_copy_fails/episodes.jsonl" in tracked
    assert "runs/R2_copy_fails/run_manifest.json" in tracked
    assert result.startswith("launcher_stdout.log not committed: not a regular file; committed")


def test_detached_child_routes_its_stdout_into_the_run_folder(tmp_path):
    run_dir = tmp_path / "R2_routed"
    run_dir.mkdir()
    saved_out, saved_err = os.dup(1), os.dup(2)
    try:
        L.route_stdio_to_run_folder(run_dir)
        os.write(1, b"traceback line from the run\n")  # fd 1 itself, past pytest's sys.stdout capture
    finally:
        os.dup2(saved_out, 1)
        os.dup2(saved_err, 2)
        os.close(saved_out)
        os.close(saved_err)

    assert (run_dir / "launcher_stdout.log").read_text() == "traceback line from the run\n"


def test_checkpoint_with_nothing_new_makes_no_commit(tmp_path):
    repo = checkpoint_repo(tmp_path)
    run_dir = repo / "runs" / "R2_same"
    run_dir.mkdir(parents=True)
    (run_dir / "progress.log").write_text("start\n")
    (run_dir / "episodes.jsonl").write_text("")
    L.checkpoint_progress(repo, run_dir)
    before = git_log(repo, "rev-list", "--count", "HEAD")
    assert L.checkpoint_progress(repo, run_dir).startswith("nothing new to commit")
    assert git_log(repo, "rev-list", "--count", "HEAD") == before


def test_checkpoint_refuses_a_run_folder_outside_the_repository(tmp_path):
    repo = checkpoint_repo(tmp_path)
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    (outside / "progress.log").write_text("start\n")
    assert L.checkpoint_progress(repo, outside).startswith("not committed")


def test_run_study_commits_checkpoints_while_the_run_is_in_progress(tmp_path):
    cases = [make_case(f"c{i}") for i in range(12)]
    client = FakeClient([(200, payload([], cost=0.01)) for _ in cases], usage=(0.0, 0.12))
    s = settings(expected_usage_usd=0.0, pre_usage_tolerance_usd=0.01, estimate_usd=0.12, http_cap=100)
    repo = checkpoint_repo(tmp_path)
    res = run(tmp_path, client, cases, s, repo=repo, out_root=repo / "runs")
    assert res.status == "COMPLETE"
    assert len(res.run_dir.joinpath("episodes.jsonl").read_text().splitlines()) == 12
    log = git_log(repo, "log", "--format=%s")
    assert log.count("checkpoint ") >= 1 and "progress and episodes so far" in log
    assert "checkpoint: committed" in res.run_dir.joinpath("progress.log").read_text()


def test_a_truncated_response_is_a_transport_error_for_that_episode_and_the_run_continues(tmp_path):
    """IncompleteRead is an http.client.HTTPException, not an OSError: before the fix it escaped run_episode, ended
    the run with ERROR: IncompleteRead at 109/980 (run 20261012T100745Z) and left episodes unsent."""
    import http.client

    class TruncatedOnce(FakeClient):
        def chat(self, body):
            if len(self.bodies) == 1:
                self.bodies.append(body)
                raise http.client.IncompleteRead(b"partial")
            return super().chat(body)

    cases = [make_case(f"c{i}") for i in range(3)]
    client = TruncatedOnce([(200, payload([], cost=0.01)) for _ in cases], usage=(0.0, 0.03))  # the provider bills the truncated episode too
    s = settings(expected_usage_usd=0.0, pre_usage_tolerance_usd=0.01, estimate_usd=0.03, http_cap=100)
    res = run(tmp_path, client, cases, s)
    assert res.status == "COMPLETE"
    recs = [json.loads(line) for line in res.run_dir.joinpath("episodes.jsonl").read_text().splitlines()]
    assert len(recs) == 3
    assert recs[1]["error"] == "transport:IncompleteRead" and recs[1]["http_status"] == "transport:IncompleteRead"
    assert recs[0]["error"] is None and recs[2]["error"] is None


def _bare_remote(tmp_path):
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    return remote


def _remote_file(remote, branch, path):
    return subprocess.run(["git", "--git-dir", str(remote), "show", f"refs/heads/{branch}:{path}"],
                          check=True, capture_output=True, text=True).stdout


def test_checkpoint_pushes_each_checkpoint_to_a_run_branch_on_the_remote(tmp_path):
    repo = checkpoint_repo(tmp_path)
    remote = _bare_remote(tmp_path)
    subprocess.run(["git", "-C", str(repo), "remote", "add", "origin", str(remote)], check=True)
    run_dir = repo / "runs" / "R2_remote"
    run_dir.mkdir(parents=True)
    (run_dir / "progress.log").write_text("start\n")
    (run_dir / "episodes.jsonl").write_text('{"case": "c1"}\n')

    assert "pushed to origin runs/R2_remote" in L.checkpoint_progress(repo, run_dir, "origin")
    (run_dir / "episodes.jsonl").write_text('{"case": "c1"}\n{"case": "c2"}\n')
    assert "pushed to origin runs/R2_remote" in L.checkpoint_progress(repo, run_dir, "origin")

    assert _remote_file(remote, "runs/R2_remote", "runs/R2_remote/episodes.jsonl").count("\n") == 2


def test_a_failed_checkpoint_push_is_reported_and_the_local_commit_is_kept(tmp_path):
    repo = checkpoint_repo(tmp_path)
    run_dir = repo / "runs" / "R2_nopush"
    run_dir.mkdir(parents=True)
    (run_dir / "progress.log").write_text("start\n")
    (run_dir / "episodes.jsonl").write_text("")
    result = L.checkpoint_progress(repo, run_dir, str(tmp_path / "does-not-exist.git"))
    assert "committed" in result and "push to" in result and "FAILED" in result
    assert "checkpoint R2_nopush" in git_log(repo, "log", "--format=%s")


def test_run_study_pushes_checkpoints_to_the_remote_while_the_run_is_in_progress(tmp_path):
    cases = [make_case(f"c{i}") for i in range(12)]
    client = FakeClient([(200, payload([], cost=0.01)) for _ in cases], usage=(0.0, 0.12))
    s = settings(expected_usage_usd=0.0, pre_usage_tolerance_usd=0.01, estimate_usd=0.12, http_cap=100)
    repo = checkpoint_repo(tmp_path)
    remote = _bare_remote(tmp_path)
    subprocess.run(["git", "-C", str(repo), "remote", "add", "origin", str(remote)], check=True)
    res = L.run_study(client, cases, s, repo / "runs", repo, repo / "doc.md", now=lambda: FIXED,
                      checkpoint_remote="origin")
    assert res.status == "COMPLETE"
    branch = f"runs/{res.run_dir.name}"
    assert len(_remote_file(remote, branch, f"runs/{res.run_dir.name}/episodes.jsonl").splitlines()) >= 10


def _detach_must_not_run(monkeypatch):
    calls = []
    monkeypatch.setattr(L, "launch_detached", lambda *a, **k: calls.append(a) or 0)
    return calls


def test_detach_refuses_a_missing_plan_before_anything_is_spawned(tmp_path, monkeypatch, capsys):
    calls = _detach_must_not_run(monkeypatch)
    rc = L.main(["--detach", "--dry-run", "--out-root", str(tmp_path / "out"), "--plan", str(tmp_path / "nope.json")])
    assert rc == 2 and calls == []
    assert "refused: cannot read --plan" in capsys.readouterr().err


def _minimal_plan(tmp_path):
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"models": [{"model_id": "m", "route": "r"}], "cases": []}))
    return plan


def _live_detach_argv(tmp_path, repo, **extra):
    """Argv for --detach --live that skips the real R1/R2/R3 plan gate (injected in tests only)."""
    plan = _minimal_plan(tmp_path)
    base = ["--detach", "--live", "--out-root", str(repo / "out"), "--plan", str(plan), "--run", "R2",
            "--run-label", "lbl", "--soft-cap-usd", "0.25", "--http-cap", "10", "--estimate-usd", "0.1",
            "--expected-usage-usd", "0", "--usage-tolerance-usd", "0.01", "--seed", "7",
            "--protocol-doc", "doc.md", "--campaign-cap-usd", "0.50"]
    for k, v in extra.items():
        flag = f"--{k.replace('_', '-')}"
        if isinstance(v, (list, tuple)):
            for item in v:
                base.extend([flag, str(item)])
        else:
            base.extend([flag, str(v)])
    return base


@pytest.mark.parametrize("extra_kw", [{"prior_run_dir": "prior"}, {"soft_cap_usd": 0.60}], ids=["prior-plus-soft-cap", "soft-cap-alone"])
def test_detach_live_refuses_budget_before_forking(tmp_path, monkeypatch, capsys, extra_kw):
    """With --detach --live, parent refuses when prior+soft cap or soft cap alone exceeds --campaign-cap-usd."""
    calls = _detach_must_not_run(monkeypatch)
    repo = checkpoint_repo(tmp_path)
    if extra_kw.get("prior_run_dir") == "prior":
        prior = _commit_prior_run(repo, "r1", _reconciled(0.30))
        extra_kw = {"prior_run_dir": prior}
    monkeypatch.chdir(repo)
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-FAKE-TEST-not-used-in-this-test")
    monkeypatch.setattr(L, "check_against_campaign_plan", lambda *a, **k: None)
    rc = L.main(_live_detach_argv(tmp_path, repo, **extra_kw))
    err = capsys.readouterr().err
    assert rc == 2 and calls == []
    assert "campaign cap exceeded" in err
    assert not (repo / "out").exists() or not any((repo / "out").iterdir())


def test_detach_refuses_live_without_a_campaign_cap_before_anything_is_spawned(tmp_path, monkeypatch, capsys):
    calls = _detach_must_not_run(monkeypatch)
    plan = tmp_path / "plan.json"
    plan.write_text('{"models": [{"model_id": "m", "route": "r"}], "cases": []}')
    argv = ["--detach", "--live", "--out-root", str(tmp_path / "out"), "--plan", str(plan), "--run", "R2",
            "--run-label", "lbl", "--soft-cap-usd", "1", "--http-cap", "10", "--estimate-usd", "0.1",
            "--expected-usage-usd", "0", "--usage-tolerance-usd", "0.01", "--seed", "7"]
    rc = L.main(argv)
    assert rc == 2 and calls == []
    assert "--campaign-cap-usd" in capsys.readouterr().err


def test_a_stalled_push_times_out_is_reported_and_the_run_is_not_held_up(tmp_path, monkeypatch):
    # The remote's helper sleeps and never speaks git's protocol, so the push stalls until it is stopped.
    import time
    monkeypatch.setenv("GIT_ALLOW_PROTOCOL", "ext")
    monkeypatch.setattr(L, "CHECKPOINT_GIT_TIMEOUT_S", 2.0, raising=False)
    repo = checkpoint_repo(tmp_path)
    subprocess.run(["git", "-C", str(repo), "remote", "add", "origin", "ext::sleep 20"], check=True)
    run_dir = repo / "runs" / "R2_stall"
    run_dir.mkdir(parents=True)
    (run_dir / "progress.log").write_text("start\n")
    (run_dir / "episodes.jsonl").write_text('{"case": "c1"}\n')
    started = time.monotonic()
    result = L.checkpoint_progress(repo, run_dir, "origin")
    elapsed = time.monotonic() - started
    assert "push to origin runs/R2_stall FAILED" in result and "timed out" in result
    assert elapsed < 10, f"checkpoint held the run for {elapsed:.1f} s"
    assert "checkpoint R2_stall" in git_log(repo, "log", "--format=%s")


FAKE_OPENROUTER_KEY = "sk-or-FAKE-TEST-0123456789abcdef0123456789ab"


class _SecretLeakHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _reply_json(self, status, obj):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.server.received.append(f"GET {self.path}")
        usage = self.server.usage_script
        val = usage.pop(0) if len(usage) > 1 else usage[0]
        self._reply_json(200, {"data": {"usage": val}})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)
        self.server.received.append(f"POST {self.path}")
        action = self.server.chat_script.pop(0) if self.server.chat_script else ("json", 200, payload([]))
        if action[0] == "truncated":
            partial = b'{"choices":[{"message":{'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", "9999")
            self.end_headers()
            self.wfile.write(partial)
            return
        if action[0] == "json":
            self._reply_json(action[1], action[2])


def _loopback_secret_server():
    try:
        server = ThreadingHTTPServer(("127.0.0.1", 0), _SecretLeakHandler)
    except OSError as exc:
        pytest.fail(f"loopback is required and is unavailable: {exc}")
    try:
        with socket.create_connection(server.server_address, timeout=2):
            pass
    except OSError as exc:
        server.server_close()
        pytest.fail(f"loopback is required and is unreachable: {exc}")
    return server


def _assert_fake_key_absent(key, run_dir, repo):
    rel_root = f"runs/{run_dir.name}"
    paths = [run_dir / n for n in ("launcher_stdout.log", "progress.log", "episodes.jsonl", "run_manifest.json")]
    tracked = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "--name-only", "HEAD", "--", rel_root],
                             check=True, capture_output=True, text=True).stdout.split()
    paths.extend(repo / p for p in tracked)
    for path in paths:
        if path.is_file():
            assert key not in path.read_text(errors="replace"), f"fake API key leaked into {path.relative_to(repo)}"


def test_transport_errors_do_not_leak_openrouter_key_into_logs_or_checkpoints(tmp_path, monkeypatch):
    """IncompleteRead and tracebacks must not copy OPENROUTER_API_KEY into run artifacts or git checkpoints."""
    monkeypatch.setenv("OPENROUTER_API_KEY", FAKE_OPENROUTER_KEY)
    server = _loopback_secret_server()
    server.daemon_threads = True
    server.chat_script = [("truncated",), ("json", 200, payload([], cost=0.01)), ("json", 200, payload([], cost=0.01))]
    server.usage_script = [0.0, 0.02]
    server.received = []
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}/api/v1"
    try:
        cases = [make_case(f"c{i}") for i in range(3)]
        client = L.OpenRouterClient(FAKE_OPENROUTER_KEY, base_url=base, timeout=2)
        s = settings(expected_usage_usd=0.0, pre_usage_tolerance_usd=0.01, estimate_usd=0.02, http_cap=100,
                     settle_max_reads=1, settle_wait_s=0)
        repo = checkpoint_repo(tmp_path)
        (repo / "doc.md").write_text("protocol draft\n")
        res = L.run_study(client, cases, s, repo / "runs", repo, repo / "doc.md", now=lambda: FIXED,
                          command_line=L.redact_argv(["launcher", "--live", f"--api-key={FAKE_OPENROUTER_KEY}"]),
                          route_stdout=True)
        assert res.status == "COMPLETE"
        L.checkpoint_progress(repo, res.run_dir)
        _assert_fake_key_absent(FAKE_OPENROUTER_KEY, res.run_dir, repo)
        assert server.received, "mock transport must have been used (no external network)"
    finally:
        server.shutdown()
        server.server_close()
