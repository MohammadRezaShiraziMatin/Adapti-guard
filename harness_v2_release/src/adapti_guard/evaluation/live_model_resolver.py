"""Resolve target/judge from configs (no live spend unless explicitly allowed)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from adapti_guard.evaluation.llm_judge import LLMJudge, build_judge
from adapti_guard.evaluation.target_model import TargetModel, build_target_model, load_model_config


class TargetJudgeGuardError(Exception):
    """configuration_failure: target == judge or blocked live."""


def assert_target_ne_judge(
    target_model_id: str,
    judge_model_id: str,
    *,
    pending_ok: bool = True,
) -> None:
    if pending_ok and (
        target_model_id.startswith("PENDING")
        or judge_model_id.startswith("PENDING")
        or not target_model_id
        or not judge_model_id
    ):
        return
    if target_model_id == judge_model_id:
        raise TargetJudgeGuardError("configuration_failure: target_model_id == judge_model_id")


def resolve_target_model(
    config_key: str,
    *,
    config_path: str | Path = "configs/models.yaml",
    allow_live: bool = False,
    cache_enabled: bool | None = None,
) -> TargetModel:
    if not allow_live:
        raise TargetJudgeGuardError("configuration_failure: live target resolution blocked (allow_live=False)")
    return build_target_model(config_key, config_path=config_path, cache_enabled=cache_enabled)


def resolve_judge(
    *,
    config_path: str | Path = "configs/models.yaml",
    allow_live: bool = False,
    cache_enabled: bool | None = None,
) -> LLMJudge:
    if not allow_live:
        raise TargetJudgeGuardError("configuration_failure: live judge resolution blocked (allow_live=False)")
    return build_judge(config_path=config_path, cache_enabled=cache_enabled)


def model_id_for_config_key(config_key: str, config_path: str | Path = "configs/models.yaml") -> str:
    spec = load_model_config(config_path)["models"][config_key]
    return str(spec.get("model", config_key))


def validate_target_judge_keys(
    target_config_key: str,
    judge_config_key: str,
    *,
    config_path: str | Path = "configs/models.yaml",
) -> dict[str, Any]:
    t_id = model_id_for_config_key(target_config_key, config_path)
    j_id = model_id_for_config_key(judge_config_key, config_path)
    assert_target_ne_judge(t_id, j_id, pending_ok=False)
    return {"target_model_id": t_id, "judge_model_id": j_id, "target_config_key": target_config_key, "judge_config_key": judge_config_key}
