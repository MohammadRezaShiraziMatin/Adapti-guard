"""Research trace records for live eval (JSONL); extends experiment_logging patterns."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from adapti_guard.evaluation.experiment_logging import git_commit, utc_now_iso, write_json
from adapti_guard.evaluation.secret_safe import redact_mapping


def append_trace_line(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    safe = redact_mapping(record)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(safe, sort_keys=True, default=str) + "\n")


def base_trace_fields(
    *,
    run_id: str,
    experiment_id: str,
    condition_id: str | None = None,
    phase: str = "live_infra",
    stage: str = "dry_run",
    provider: str | None = None,
    model_id: str | None = None,
    judge_model_id: str | None = None,
    seed: int | None = None,
    trial: int | None = None,
    repetition: int | None = None,
    turn: int | None = None,
    episode_id: str | None = None,
) -> dict[str, Any]:
    return {
        "timestamp": utc_now_iso(),
        "run_id": run_id,
        "experiment_id": experiment_id,
        "condition_id": condition_id,
        "phase": phase,
        "stage": stage,
        "provider": provider,
        "model_id": model_id,
        "judge_model_id": judge_model_id,
        "seed": seed,
        "trial": trial,
        "repetition": repetition,
        "turn": turn,
        "episode_id": episode_id,
        "code_commit": git_commit(),
        "source": "live_eval_trace",
    }


def write_raw_evidence(run_dir: Path, name: str, payload: dict[str, Any]) -> Path:
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / name
    write_json(path, redact_mapping(payload))
    return path
