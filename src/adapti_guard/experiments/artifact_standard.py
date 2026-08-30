"""Standard artifact, manifest, validation, and logging helpers for NEW experiments.

Existing Phase 7/8 validated bundles are frozen; use these helpers for future runs only.
Does not modify algorithms, metrics, or frozen result artifacts.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

ARTIFACT_STANDARD_VERSION = "v1"

# TOTAL--/ANALYSIS from .../01_BASE_Q1/adapti_guard/src/adapti_guard/experiments/
_RESEARCH_ROOT = Path(__file__).resolve().parents[5]
ANALYSIS_DIR = _RESEARCH_ROOT / "ANALYSIS"
RESEARCH_AUDIT_LOG = ANALYSIS_DIR / "LOGS" / "research_audit.log"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return result.stdout.strip()
    except Exception:
        return None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def archive_if_exists(path: Path) -> Path | None:
    """Non-destructive: archive existing file before overwrite."""
    if not path.exists():
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archived = path.with_name(f"{path.stem}_{stamp}{path.suffix}")
    path.replace(archived)
    return archived


def log_structured(
    log_path: Path,
    level: str,
    component: str,
    event: str,
    **fields: Any,
) -> None:
    """Format: timestamp_utc | LEVEL | COMPONENT | EVENT | key=value ..."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    parts = [f"{k}={fields[k]}" for k in sorted(fields)]
    suffix = " | ".join(parts) if parts else ""
    line = f"{utc_now_iso()} | {level.upper()} | {component} | {event}"
    if suffix:
        line = f"{line} | {suffix}"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def log_research_event(event: str, detail: str = "") -> None:
    """Append major research lifecycle events to ANALYSIS/LOGS/research_audit.log."""
    RESEARCH_AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    stamp = utc_now_iso()
    line = f"{stamp} | {event} | {detail}\n" if detail else f"{stamp} | {event}\n"
    with RESEARCH_AUDIT_LOG.open("a", encoding="utf-8") as handle:
        handle.write(line)


def write_json(path: Path, payload: dict[str, Any], *, overwrite: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        archive_if_exists(path)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def build_run_manifest(
    *,
    experiment_name: str,
    experiment_version: str,
    configuration: dict[str, Any],
    methods: list[str],
    source_artifacts: list[str],
    output_artifacts: list[str],
    status: str,
    metric_version: str | None = None,
    attack_protocol: str | None = None,
    attack_set_version: str | None = None,
    episode_count: int | None = None,
    attack_count: int | None = None,
    legitimate_count: int | None = None,
    seed: int | None = None,
    deterministic: bool | None = None,
    code_version: str | None = None,
) -> dict[str, Any]:
    """Minimum run_manifest.json schema for new experiments."""
    return {
        "artifact_version": ARTIFACT_STANDARD_VERSION,
        "experiment_name": experiment_name,
        "experiment_version": experiment_version,
        "timestamp_utc": utc_now_iso(),
        "code_version": code_version or git_commit() or "UNKNOWN",
        "configuration": configuration,
        "seed": seed,
        "deterministic": deterministic,
        "episode_count": episode_count,
        "attack_count": attack_count,
        "legitimate_count": legitimate_count,
        "attack_protocol": attack_protocol,
        "attack_set_version": attack_set_version,
        "metric_version": metric_version,
        "methods": methods,
        "source_artifacts": source_artifacts,
        "output_artifacts": output_artifacts,
        "status": status,
        "python_version": sys.version,
        "platform": platform.platform(),
    }


def build_validation_record(
    checks: dict[str, str],
    *,
    overall: str | None = None,
) -> dict[str, Any]:
    """Standard validation.json for new experiments. Values: PASS | FAIL | WARN | NOT_CHECKED."""
    allowed = {"PASS", "FAIL", "WARN", "NOT_CHECKED"}
    normalized = {}
    for key, value in checks.items():
        upper = str(value).upper()
        if upper not in allowed:
            upper = "NOT_CHECKED"
        normalized[key] = upper

    if overall is None:
        if any(v == "FAIL" for v in normalized.values()):
            overall = "FAIL"
        elif any(v == "WARN" for v in normalized.values()):
            overall = "WARN"
        elif all(v in {"PASS", "NOT_CHECKED"} for v in normalized.values()):
            overall = "PASS"
        else:
            overall = "NOT_CHECKED"

    return {
        "artifact_version": ARTIFACT_STANDARD_VERSION,
        "timestamp_utc": utc_now_iso(),
        "validity": overall,
        "checks": normalized,
    }


def attach_checksums(manifest: dict[str, Any], artifact_paths: list[Path]) -> dict[str, Any]:
    """Add sha256 checksums for listed artifacts (audit value only)."""
    checksums: dict[str, str] = {}
    for path in artifact_paths:
        if path.exists() and path.is_file():
            checksums[str(path)] = sha256_file(path)
    manifest["checksums"] = checksums
    return manifest
