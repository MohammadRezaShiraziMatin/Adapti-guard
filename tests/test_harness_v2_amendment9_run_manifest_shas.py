"""Amendment 9 — run_manifest runner_code_sha and docs_sha_at_launch."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from adapti_guard.evaluation.harness_v2.run_manifest import (
    resolve_docs_sha_at_launch,
    resolve_runner_code_sha,
    write_run_manifest,
)


def test_run_manifest_writes_injected_shas(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    (repo / "experiments").mkdir(parents=True)
    (repo / "experiments" / "harness_v2").mkdir()
    (repo / "experiments" / "harness_v2" / "README.md").write_text("docs\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)
    head = resolve_runner_code_sha(repo)
    docs_tree = resolve_docs_sha_at_launch(repo)
    path = write_run_manifest(
        tmp_path / "out",
        repo_root=repo,
        pilot="harness_v2_pilot_0",
        runner_code_sha=head,
        docs_sha_at_launch=docs_tree,
    )
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert manifest["runner_code_sha"] == head
    assert manifest["docs_sha_at_launch"] == docs_tree
    assert len(manifest["runner_code_sha"]) == 40
    assert len(manifest["docs_sha_at_launch"]) == 40
