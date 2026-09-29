"""Amendment 9 — run_manifest runner_code_sha and docs_sha_at_launch."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from adapti_guard.evaluation.harness_v2.run_manifest import (
    resolve_docs_sha_at_launch,
    resolve_docs_tree_sha,
    resolve_repo_head_sha,
    resolve_runner_code_sha,
    write_run_manifest,
)


def _git_env() -> dict[str, str]:
    import os

    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "test"
    env["GIT_AUTHOR_EMAIL"] = "test@example.com"
    env["GIT_COMMITTER_NAME"] = "test"
    env["GIT_COMMITTER_EMAIL"] = "test@example.com"
    return env


def _run_git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
        env=_git_env(),
    )
    return proc.stdout.strip()


def test_run_manifest_docs_sha_matches_last_commit_touching_harness_v2(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, "init")
    (repo / "experiments").mkdir(parents=True)
    (repo / "experiments" / "harness_v2").mkdir()
    (repo / "experiments" / "harness_v2" / "README.md").write_text("v1\n", encoding="utf-8")
    _run_git(repo, "add", ".")
    _run_git(repo, "commit", "-m", "docs v1")
    first_docs = _run_git(repo, "log", "-1", "--format=%H", "--", "experiments/harness_v2")
    (repo / "other.txt").write_text("noise\n", encoding="utf-8")
    _run_git(repo, "add", "other.txt")
    _run_git(repo, "commit", "-m", "non-docs")
    (repo / "experiments" / "harness_v2" / "README.md").write_text("v2\n", encoding="utf-8")
    _run_git(repo, "add", "experiments/harness_v2/README.md")
    _run_git(repo, "commit", "-m", "docs v2")
    second_docs = _run_git(repo, "log", "-1", "--format=%H", "--", "experiments/harness_v2")
    assert first_docs != second_docs
    expected_docs = resolve_docs_sha_at_launch(repo)
    expected_tree = resolve_docs_tree_sha(repo)
    assert expected_docs == second_docs
    path = write_run_manifest(tmp_path / "out", repo_root=repo, pilot="harness_v2_pilot_0")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["docs_sha_at_launch"] == expected_docs
    assert manifest["docs_tree_sha"] == expected_tree
    assert manifest["runner_code_sha"] == resolve_runner_code_sha(repo)
    assert manifest["repo_head_sha"] == resolve_repo_head_sha(repo)
    assert manifest["runner_worktree_dirty"] is False
