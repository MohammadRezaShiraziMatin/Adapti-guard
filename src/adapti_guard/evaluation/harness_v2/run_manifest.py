"""Run pack manifest helpers (Amendment 8 + Amendment 9 SHAs)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def _git(
    repo_root: Path,
    *args: str,
    env: dict[str, str] | None = None,
) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    return proc.stdout.strip()


_PILOT_LOCK_PORCELAIN_SUFFIX = "experiments/harness_v2/.pilot_live.lock"


def _porcelain_line_is_pilot_lock(line: str) -> bool:
    path = line[3:].strip() if len(line) >= 4 else line.strip()
    normalized = path.replace("\\", "/")
    return normalized == _PILOT_LOCK_PORCELAIN_SUFFIX or normalized.endswith(
        "/experiments/harness_v2/.pilot_live.lock"
    )


def is_worktree_dirty(repo_root: Path | None = None) -> bool:
    root = repo_root or Path(__file__).resolve().parents[4]
    proc = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    filtered = [ln for ln in lines if not _porcelain_line_is_pilot_lock(ln)]
    return bool(filtered)


def resolve_runner_code_sha(
    repo_root: Path | None = None,
    *,
    override: str | None = None,
) -> str:
    """Last commit touching runner code (src/ or scripts/), pilot 3 semantics."""
    if override is not None:
        return override
    root = repo_root or Path(__file__).resolve().parents[4]
    return _git(root, "log", "-1", "--format=%H", "--", "src", "scripts")


def resolve_repo_head_sha(
    repo_root: Path | None = None,
    *,
    override: str | None = None,
) -> str:
    if override is not None:
        return override
    root = repo_root or Path(__file__).resolve().parents[4]
    return _git(root, "rev-parse", "HEAD")


def resolve_docs_sha_at_launch(
    repo_root: Path | None = None,
    *,
    override: str | None = None,
    docs_path: str = "experiments/harness_v2",
) -> str:
    """Last commit touching harness v2 docs tree (pilot 3 semantics)."""
    if override is not None:
        return override
    root = repo_root or Path(__file__).resolve().parents[4]
    return _git(root, "log", "-1", "--format=%H", "--", docs_path)


def resolve_docs_tree_sha(
    repo_root: Path | None = None,
    *,
    override: str | None = None,
    docs_path: str = "experiments/harness_v2",
) -> str:
    if override is not None:
        return override
    root = repo_root or Path(__file__).resolve().parents[4]
    return _git(root, "rev-parse", f"HEAD:{docs_path}")


def write_run_manifest(
    out_dir: Path,
    *,
    repo_root: Path | None = None,
    runner_code_sha: str | None = None,
    docs_sha_at_launch: str | None = None,
    docs_tree_sha: str | None = None,
    repo_head_sha: str | None = None,
    include_git_provenance: bool = True,
    **fields: Any,
) -> Path:
    root = repo_root or Path(__file__).resolve().parents[4]
    manifest: dict[str, Any] = {
        "python_version": sys.version,
        "python_version_info": list(sys.version_info[:3]),
    }
    if include_git_provenance:
        manifest["repo_head_sha"] = (
            repo_head_sha if repo_head_sha is not None else resolve_repo_head_sha(root)
        )
        manifest["runner_code_sha"] = (
            runner_code_sha if runner_code_sha is not None else resolve_runner_code_sha(root)
        )
        manifest["runner_worktree_dirty"] = is_worktree_dirty(root)
        manifest["docs_sha_at_launch"] = (
            docs_sha_at_launch
            if docs_sha_at_launch is not None
            else resolve_docs_sha_at_launch(root)
        )
        manifest["docs_tree_sha"] = (
            docs_tree_sha if docs_tree_sha is not None else resolve_docs_tree_sha(root)
        )
    manifest.update(fields)
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
