"""Tests for the reconciled prior-run check in scripts/injecagent_executed_launcher_v02.py.

A prior run whose manifest says AUTH_MISMATCH counts only through a committed RECONCILIATION.json. The manifest is never
edited. Every test uses a temporary git repository, so the tracking checks run for real, and nothing touches the
network. The dry-run test checks that --dry-run performs the same prior-run checks as a live run."""
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
sys.modules["launcher"] = L  # dataclasses look the module up by name while it is being executed
_spec.loader.exec_module(L)

RUN = "experiments/external/injecagent_R1_fixture"
CORRECTIONS = "experiments/external/CORRECTIONS.md"
RECON = "RECONCILIATION.json"
SETTLED = 0.007482165
RUNNER = 0.00748218


def git_commit(repo: Path, message: str, *paths: str) -> None:
    git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false"]
    subprocess.run(git + ["add", *paths], check=True)
    subprocess.run(git + ["commit", "-q", "-m", message], check=True)


def reconciliation(manifest_sha: str, **changes) -> dict:
    rec = {
        "schema": "injecagent-reconciliation-v1",
        "run_folder": RUN,
        "run_label": "R1",
        "run_manifest_sha256": manifest_sha,
        "manifest_status": "AUTH_MISMATCH",
        "pre_usage_usd": 0.0,
        "reads": [{"utc": "2026-10-11T23:04:32.642693Z", "usage_usd": SETTLED, "limit_usd": 0.6},
                  {"utc": "2026-10-11T23:14:56.468760Z", "usage_usd": SETTLED, "limit_usd": 0.6}],
        "settled_usage_usd": SETTLED,
        "runner_spend_usd": RUNNER,
        "stable_tolerance_usd": 1e-6,
        "corrections_ref": CORRECTIONS,
    }
    rec.update(changes)
    return rec


def make_repo(tmp_path: Path, with_reconciliation: bool = True, rec_changes: dict | None = None,
              status: str = "AUTH_MISMATCH", commit_reconciliation: bool = True,
              commit_corrections: bool = True) -> tuple[Path, Path]:
    """Committed run folder with an AUTH_MISMATCH manifest, a corrections file, and optionally a reconciliation.
    A file that is not committed stays on disk, untracked, which is what the tracking checks must catch."""
    repo = tmp_path / "repo"
    run = repo / RUN
    run.mkdir(parents=True)
    shutil.copy(ROOT / ".gitignore", repo / ".gitignore")
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    manifest = {"status": status, "run_label": "R1", "pre_usage_usd": 0.0, "spend_recorded_usd": RUNNER,
                "spend_auth_key_usd": 0.006742489}  # the early read, kept as recorded
    (run / "run_manifest.json").write_text(json.dumps(manifest, indent=2))
    (run / "episodes.jsonl").write_text("")
    git_commit(repo, "run folder", ".gitignore", RUN)
    (repo / CORRECTIONS).parent.mkdir(parents=True, exist_ok=True)
    (repo / CORRECTIONS).write_text("# corrections\n")
    if commit_corrections:
        git_commit(repo, "corrections", CORRECTIONS)
    if with_reconciliation:
        sha = L.file_sha256(run / "run_manifest.json")
        (run / RECON).write_text(json.dumps(reconciliation(sha, **(rec_changes or {})), indent=2))
        if commit_reconciliation:
            git_commit(repo, "reconciliation", RUN)
    return repo, run


def test_auth_mismatch_without_reconciliation_refuses(tmp_path):
    repo, run = make_repo(tmp_path, with_reconciliation=False)
    with pytest.raises(L.LaunchError, match="RECONCILIATION.json"):
        L.campaign_budget_check(0.2978, 0.5, [run], repo)


def test_valid_reconciliation_is_accepted_and_counts_the_settled_spend(tmp_path):
    repo, run = make_repo(tmp_path)
    prior = L.campaign_budget_check(0.2978, 0.5, [run], repo)
    assert prior == pytest.approx(SETTLED)  # not the early 0.006742489 in the manifest


def test_reconciliation_with_a_mismatched_value_refuses(tmp_path):
    # Internally consistent reads and settled value, but the settled spend disagrees with the runner's own record.
    repo, run = make_repo(tmp_path, rec_changes={"settled_usage_usd": 0.006742489,
                                                 "reads": [{"utc": "2026-10-11T23:04:32Z", "usage_usd": 0.006742489},
                                                           {"utc": "2026-10-11T23:14:56Z", "usage_usd": 0.006742489}]})
    with pytest.raises(L.LaunchError, match="differs from the runner"):
        L.campaign_budget_check(0.2978, 0.5, [run], repo)


def test_reconciliation_bound_to_another_manifest_refuses(tmp_path):
    repo, run = make_repo(tmp_path, rec_changes={"run_manifest_sha256": "0" * 64})
    with pytest.raises(L.LaunchError, match="does not match this run_manifest.json"):
        L.campaign_budget_check(0.2978, 0.5, [run], repo)


def test_unstable_reads_refuse(tmp_path):
    repo, run = make_repo(tmp_path, rec_changes={"reads": [{"usage_usd": 0.006742489},
                                                           {"usage_usd": SETTLED}]})
    with pytest.raises(L.LaunchError, match="not stable"):
        L.campaign_budget_check(0.2978, 0.5, [run], repo)


def test_uncommitted_reconciliation_refuses(tmp_path):
    repo, run = make_repo(tmp_path, commit_reconciliation=False)
    with pytest.raises(L.LaunchError, match="not committed"):
        L.campaign_budget_check(0.2978, 0.5, [run], repo)


def test_cited_corrections_file_must_be_committed(tmp_path):
    repo, run = make_repo(tmp_path, commit_corrections=False)
    with pytest.raises(L.LaunchError, match="corrections file"):
        L.campaign_budget_check(0.2978, 0.5, [run], repo)


def test_other_non_reconciled_status_still_refuses_even_with_a_reconciliation(tmp_path):
    repo, run = make_repo(tmp_path, status="POST_RUN_AUTH_UNREADABLE")
    with pytest.raises(L.LaunchError, match="not a reconciled run"):
        L.campaign_budget_check(0.2978, 0.5, [run], repo)


def _dry_run_argv(run: Path, plan: Path, out: Path) -> list[str]:
    return ["--plan", str(plan), "--out-root", str(out), "--run-label", "R2", "--soft-cap-usd", "0.2978",
            "--http-cap", "980", "--estimate-usd", "0.147932", "--expected-usage-usd", str(SETTLED),
            "--usage-tolerance-usd", "0.01", "--max-turns", "1", "--retries", "0", "--seed", "20261001",
            "--campaign-cap-usd", "0.5", "--prior-run-dir", str(run), "--dry-run"]


def _plan(tmp_path: Path) -> Path:
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"models": [{"model_id": "m", "route": "r"}], "cases": []}))
    return plan


def test_dry_run_catches_a_missing_reconciliation(tmp_path, monkeypatch, capsys):
    repo, run = make_repo(tmp_path, with_reconciliation=False)
    monkeypatch.chdir(repo)
    rc = L.main(_dry_run_argv(run, _plan(tmp_path), tmp_path / "out"))
    assert rc == 2
    assert "RECONCILIATION.json" in capsys.readouterr().err


def test_dry_run_accepts_a_valid_reconciliation(tmp_path, monkeypatch, capsys):
    repo, run = make_repo(tmp_path)
    monkeypatch.chdir(repo)
    rc = L.main(_dry_run_argv(run, _plan(tmp_path), tmp_path / "out"))
    assert rc == 0
    assert "no network call made" in capsys.readouterr().out
