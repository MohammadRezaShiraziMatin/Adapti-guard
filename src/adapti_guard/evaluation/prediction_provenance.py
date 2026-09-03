"""Shared prediction-row provenance for publication-grade real-LLM evaluation."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from src.adapti_guard.evaluation.attack_success import EvalEpisode

PROVENANCE_SCHEMA_VERSION = "1.2"


def build_prediction_row(
    ep: EvalEpisode,
    *,
    baseline: str,
    model_id: str,
    model_config_key: str,
    experiment_id: str,
    git_commit: str,
    seed: int,
    dataset_hash: str,
    cache_enabled: bool,
    config_version: str = PROVENANCE_SCHEMA_VERSION,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Build a publication-grade prediction row from an evaluated episode."""
    meta = ep.metadata or {}
    judge_model = meta.get("judge_model") or None
    judge_raw = meta.get("judge_raw") or None
    judge_fallback_used = bool(meta.get("judge_fallback_used", False))
    target_cache_hit = meta.get("target_cache_hit")
    judge_cache_hit = meta.get("cache_hit")

    prompt_tokens = ep.prompt_tokens if ep.prompt_tokens else None
    completion_tokens = ep.completion_tokens if ep.completion_tokens else None
    total_tokens = (
        (prompt_tokens or 0) + (completion_tokens or 0)
        if prompt_tokens is not None or completion_tokens is not None
        else None
    )
    judge_parse_error = meta.get("judge_parse_error")
    target_error = meta.get("target_error")
    if target_error or ep.judge_reason == "target_api_error":
        api_status = "target_error"
        judge_failure = False
    elif judge_parse_error or ep.judge_reason in ("judge_api_error", "judge_parse_error"):
        api_status = "judge_error"
        judge_failure = ep.judge_reason in ("judge_api_error", "judge_parse_error")
    else:
        api_status = "ok"
        judge_failure = False

    row: dict[str, Any] = {
        "experiment_id": experiment_id,
        "sample_id": ep.id,
        "episode_id": ep.id,
        "model_id": model_id,
        "model_config_key": model_config_key,
        "baseline": baseline,
        "category": ep.category,
        "label": ep.label,
        "blocked": ep.blocked,
        "attack_succeeded": ep.attack_succeeded,
        "utility_success": ep.utility_success,
        "target_response": ep.model_response if ep.model_response else None,
        "judge_raw": judge_raw,
        "judge_model": judge_model,
        "judge_fallback_used": judge_fallback_used,
        "judge_reason": ep.judge_reason,
        "target_latency_ms": ep.target_latency_ms,
        "judge_latency_ms": ep.judge_latency_ms,
        "episode_latency_ms": ep.latency_ms,
        "cache_hit": bool(judge_cache_hit or target_cache_hit),
        "target_cache_hit": target_cache_hit,
        "judge_cache_hit": judge_cache_hit,
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "evaluation_mode": meta.get("evaluation_mode", "real_llm_judge"),
        "git_commit": git_commit,
        "seed": seed,
        "dataset_hash": dataset_hash,
        "cache_enabled": cache_enabled,
        "config_version": config_version,
        # Pilot-compatible aliases (PHASE2_7_PILOT schema)
        "model": model_id,
        "attack_label": ep.label,
        "attack_success": ep.attack_succeeded,
        "input_tokens": prompt_tokens,
        "output_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "utility_note": (
            "attack-only frozen eval — benign utility N/A"
            if ep.label == "attack"
            else None
        ),
        "judge_mode": "blind",
        "prompt_hash": hashlib.sha256(
            f"{ep.prompt}\n---\n{ep.context}".encode()
        ).hexdigest(),
        "output_hash": (
            hashlib.sha256(ep.model_response.encode()).hexdigest()
            if ep.model_response
            else ""
        ),
        "api_status": api_status,
        "judge_failure": judge_failure,
        "target_error": target_error or None,
        "model_response_preview": ep.model_response[:200] if ep.model_response else "",
        "target_prompt": ep.prompt,
        "action": ep.defense_action,
    }
    # Backward-compatible alias used by statistical loaders.
    row["id"] = ep.id
    return row
