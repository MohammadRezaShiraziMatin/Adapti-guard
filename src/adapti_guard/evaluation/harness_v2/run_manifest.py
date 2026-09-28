"""Run pack manifest helpers (Amendment 8 + Amendment 9 SHAs)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def _git_rev_parse(spec: str, *, repo_root: Path) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", spec],
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout.strip()


def resolve_runner_code_sha(
    repo_root: Path | None = None,
    *,
    override: str | None = None,
) -> str:
    if override is not None:
        return override
    root = repo_root or Path(__file__).resolve().parents[4]
    return _git_rev_parse("HEAD", repo_root=root)


def resolve_docs_sha_at_launch(
    repo_root: Path | None = None,
    *,
    override: str | None = None,
    docs_path: str = "experiments/harness_v2",
) -> str:
    """Git tree object for harness v2 docs directory at HEAD (launch snapshot)."""
    if override is not None:
        return override
    root = repo_root or Path(__file__).resolve().parents[4]
    return _git_rev_parse(f"HEAD:{docs_path}", repo_root=root)


def write_run_manifest(
    out_dir: Path,
    *,
    repo_root: Path | None = None,
    runner_code_sha: str | None = None,
    docs_sha_at_launch: str | None = None,
    **fields: Any,
) -> Path:
    root = repo_root or Path(__file__).resolve().parents[4]
    manifest = {
        "python_version": sys.version,
        "python_version_info": list(sys.version_info[:3]),
        "runner_code_sha": runner_code_sha
        if runner_code_sha is not None
        else resolve_runner_code_sha(root),
        "docs_sha_at_launch": docs_sha_at_launch
        if docs_sha_at_launch is not None
        else resolve_docs_sha_at_launch(root),
        **fields,
    }
    path = out_dir / "run_manifest.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path


def write_pip_freeze(out_dir: Path) -> Path:
    proc = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        capture_output=True,
        text=True,
        check=True,
    )
    path = out_dir / "pip_freeze.txt"
    path.write_text(proc.stdout, encoding="utf-8")
    return path
