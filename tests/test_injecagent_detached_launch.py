"""Offline tests for the detached launch and incremental checkpoints of scripts/injecagent_executed_launcher_v02.py.

No live model call and no external network: the study uses the in-process FakeClient from the launcher test file,
and the git checks run for real in a temporary repository. These tests fail on a launcher without detached_command
and checkpoint_progress, and pass once they exist."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_injecagent_executed_launcher_v02 import (FIXED, FakeClient, L, ROOT, make_case, make_repo,  # noqa: E402
                                                   payload, run, settings)

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
    assert cmd[5:] == ["--live", "--run", "R2", "--out-root", "runs"]


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
