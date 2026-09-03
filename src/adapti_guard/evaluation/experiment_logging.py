"""Permanent experiment run logging for Q1 scientific upgrade.

Every executed experiment writes under:

    results/experiment_runs/<experiment_id>/<run_id>/

Required artifacts: config.json, environment.json, command.txt, git_commit.txt,
dataset_manifest.json, model_config.json, metrics.json, stdout.log, stderr.log,
summary.md

Never stores API keys or secrets.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, TextIO

RUNS_ROOT = Path("results/experiment_runs")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _short_hash(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:6]


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


def redact_env() -> dict[str, Any]:
    """Environment snapshot safe for JSON artifacts."""
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "openrouter_api_key": "***REDACTED***" if os.getenv("OPENROUTER_API_KEY") else None,
        "gemini_api_key": "***REDACTED***" if os.getenv("GEMINI_API_KEY") else None,
        "groq_api_key": "***REDACTED***" if os.getenv("GROQ_API_KEY") else None,
        "key_present": bool(os.getenv("OPENROUTER_API_KEY")),
        "gemini_key_present": bool(os.getenv("GEMINI_API_KEY")),
        "groq_key_present": bool(os.getenv("GROQ_API_KEY")),
    }


@dataclass
class ExperimentRunContext:
    experiment_id: str
    run_id: str
    run_dir: Path
    config: dict[str, Any] = field(default_factory=dict)
    _stdout: TextIO | None = field(default=None, repr=False)
    _stderr: TextIO | None = field(default=None, repr=False)

    @classmethod
    def create(
        cls,
        experiment_id: str,
        *,
        config: dict[str, Any] | None = None,
        runs_root: Path | None = None,
    ) -> ExperimentRunContext:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        config = dict(config or {})
        run_id = f"RUN-{stamp}-{_short_hash(experiment_id + stamp)}"
        root = runs_root or RUNS_ROOT
        run_dir = root / experiment_id / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        ctx = cls(
            experiment_id=experiment_id,
            run_id=run_id,
            run_dir=run_dir,
            config=config,
        )
        ctx._open_logs()
        ctx.write_initial_artifacts()
        return ctx

    def _open_logs(self) -> None:
        self._stdout = (self.run_dir / "stdout.log").open("a", encoding="utf-8")
        self._stderr = (self.run_dir / "stderr.log").open("a", encoding="utf-8")

    def log_stdout(self, message: str) -> None:
        if self._stdout:
            self._stdout.write(message.rstrip() + "\n")
            self._stdout.flush()

    def log_stderr(self, message: str) -> None:
        if self._stderr:
            self._stderr.write(message.rstrip() + "\n")
            self._stderr.flush()

    def write_initial_artifacts(self) -> None:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        write_json(self.run_dir / "config.json", self.config)
        write_json(self.run_dir / "environment.json", redact_env())
        (self.run_dir / "git_commit.txt").write_text(
            git_commit() or "UNKNOWN", encoding="utf-8"
        )
        cmd = " ".join(sys.argv)
        (self.run_dir / "command.txt").write_text(cmd + "\n", encoding="utf-8")

    def write_dataset_manifest(self, manifest: dict[str, Any]) -> None:
        write_json(self.run_dir / "dataset_manifest.json", manifest)

    def write_model_config(self, model_config: dict[str, Any]) -> None:
        safe = json.loads(json.dumps(model_config))
        if "api_key" in safe:
            safe["api_key"] = "***REDACTED***"
        write_json(self.run_dir / "model_config.json", safe)

    def write_metrics(self, metrics: dict[str, Any]) -> None:
        write_json(self.run_dir / "metrics.json", metrics)

    def write_summary(self, text: str) -> None:
        (self.run_dir / "summary.md").write_text(text, encoding="utf-8")

    def append_response(self, record: dict[str, Any]) -> None:
        path = self.run_dir / "responses.jsonl"
        safe = json.loads(json.dumps(record))
        for key in list(safe.keys()):
            if "api_key" in key.lower() or key.endswith("_key"):
                safe[key] = "***REDACTED***"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(safe, ensure_ascii=False) + "\n")

    def close(self) -> None:
        if self._stdout:
            self._stdout.close()
            self._stdout = None
        if self._stderr:
            self._stderr.close()
            self._stderr = None

    def __enter__(self) -> ExperimentRunContext:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def update_registry_row(
    registry_path: Path,
    row: dict[str, Any],
) -> None:
    """Append or update a row in experiments/registry.csv (simple CSV)."""
    import csv

    registry_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "experiment_id",
        "run_id",
        "timestamp",
        "status",
        "git_commit",
        "dataset",
        "dataset_hash",
        "target_model",
        "judge_model",
        "n_samples",
        "seed",
        "metrics_path",
        "run_dir",
        "notes",
    ]
    rows: list[dict[str, str]] = []
    if registry_path.exists():
        with registry_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames:
                fieldnames = list(reader.fieldnames)
            rows = list(reader)

    normalized = {k: str(row.get(k, "")) for k in fieldnames}
    for i, existing in enumerate(rows):
        if (
            existing.get("experiment_id") == normalized.get("experiment_id")
            and existing.get("run_id") == normalized.get("run_id")
        ):
            rows[i] = normalized
            break
    else:
        rows.append(normalized)

    with registry_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
