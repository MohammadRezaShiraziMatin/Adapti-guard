"""Resolve canonical experiment conditions from EXPERIMENT_MATRIX.yaml (Phase 4)."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

DEFAULT_MATRIX = Path("docs/research/EXPERIMENT_MATRIX.yaml")


class ConditionResolutionError(Exception):
    """resolution_failure or configuration_failure."""


@dataclass(frozen=True)
class RunContext:
    run_id: str
    condition_id: str
    rq_id: list[str]
    attack_id: str
    defense_id: str
    target_model_id: str
    judge_id: str | None
    interaction_mode: str
    adaptivity: str
    agent_state: str
    tool_state: str
    dataset_id: str
    seed: int
    trial: int
    config_hash: str
    evidence_status: str
    mode: str  # offline | live (live blocked at runner)


def config_hash(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(dict(payload), sort_keys=True, default=str).encode()).hexdigest()


def load_matrix(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_MATRIX
    if not p.is_file():
        raise ConditionResolutionError(f"resolution_failure: matrix missing {p}")
    import yaml

    return yaml.safe_load(p.read_text())


def resolve_condition(
    condition_id: str,
    *,
    matrix_path: Path | None = None,
    seed: int = 0,
    trial: int = 0,
) -> tuple[dict[str, Any], RunContext]:
    data = load_matrix(matrix_path)
    row = next((r for r in data.get("rows", []) if r.get("condition_id") == condition_id), None)
    if row is None:
        raise ConditionResolutionError(f"resolution_failure: unknown condition_id={condition_id}")

    target = str(row.get("target_model_id", ""))
    judge = row.get("judge_id")
    if row.get("target_ne_judge") and judge and target and target == judge:
        raise ConditionResolutionError("configuration_failure: target_model_id == judge_id")

    cfg = {k: row.get(k) for k in (
        "condition_id", "experiment_id", "attack_id", "defense_id",
        "target_model_id", "judge_id", "interaction_mode", "adaptivity",
        "agent_state", "tool_state", "dataset_id", "seed", "trial",
    )}
    cfg["seed"] = seed
    cfg["trial"] = trial
    ch = config_hash(cfg)

    ctx = RunContext(
        run_id="",  # assigned by runner
        condition_id=condition_id,
        rq_id=list(row.get("rq") or []),
        attack_id=str(row.get("attack_id", "")),
        defense_id=str(row.get("defense_id", "")),
        target_model_id=target,
        judge_id=str(judge) if judge else None,
        interaction_mode=str(row.get("interaction_mode", "")),
        adaptivity=str(row.get("adaptivity", "")),
        agent_state=str(row.get("agent_state", "")),
        tool_state=str(row.get("tool_state", "")),
        dataset_id=str(row.get("dataset_id", "")),
        seed=seed,
        trial=trial,
        config_hash=ch,
        evidence_status=str(row.get("evidence_status", "")),
        mode="offline",
    )
    return row, ctx


def verify_frozen_dataset(dataset_id: str, repo_root: Path | None = None) -> dict[str, str]:
    """Return manifest fields or raise dataset_failure."""
    root = repo_root or Path(".")
    if dataset_id == "p1_mechanism_v1.0.0" or "p1" in dataset_id:
        manifest = root / "datasets/frozen/p1_mechanism_v1.0.0/manifest.json"
        if not manifest.is_file():
            raise ConditionResolutionError("dataset_failure: p1 manifest missing")
        m = json.loads(manifest.read_text())
        return {"dataset_id": dataset_id, "dataset_hash": m["dataset_sha256"]}
    return {"dataset_id": dataset_id, "dataset_hash": "n/a_fixture"}
