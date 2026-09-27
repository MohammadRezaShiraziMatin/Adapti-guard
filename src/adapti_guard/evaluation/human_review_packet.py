"""Human-reviewable decision packet (Phase 5) — design/measurement layer only.

Does not record empirical human outcomes or trust calibration scores.
"""
from __future__ import annotations

from typing import Any, Mapping

from adapti_guard.core.episode import EpisodeTrace


def packet_from_episode_trace(
    trace: EpisodeTrace,
    *,
    condition_id: str | None = None,
    attack_id: str | None = None,
    run_id: str | None = None,
    config_hash: str | None = None,
) -> dict[str, Any]:
    """Machine decision + evidence suitable for operator review (not human verdict)."""
    machine = {
        "detection": {
            "probability": trace.detector_probability,
            "hit": trace.detector_hit,
            "indicators": list(trace.detector_indicators),
        },
        "risk": {
            "score": trace.risk_score,
            "level": trace.risk_level,
            "reasons": list(trace.risk_reasons),
        },
        "defense": {
            "policy_action": trace.policy_action,
            "policy_reason": trace.policy_reason,
            "blocked": trace.blocked,
            "defense_level": trace.defense_level,
        },
        "tool": {
            "requested": trace.tool_requested,
            "executed": trace.tool_executed,
            "permission_allowed": trace.tool_permission_allowed,
            "privileged_tool": trace.privileged_tool,
            "observation": trace.tool_observation,
        },
    }
    provenance = {
        k: v
        for k, v in {
            "condition_id": condition_id,
            "attack_id": attack_id,
            "run_id": run_id,
            "config_hash": config_hash,
        }.items()
        if v is not None
    }
    return {
        "layer": "human_review_packet",
        "status": "machine_decision_only",
        "machine_decision": machine,
        "human_reviewable_evidence": trace.to_dict(),
        "human_decision": None,
        "empirical_human_outcome": None,
        "provenance": provenance,
        "disclaimer": (
            "machine explanation ≠ human understanding; "
            "risk score ≠ human trust; not an empirical human study"
        ),
    }


def packet_from_evidence_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Summarize an offline/live evidence_record for human review (no new metrics)."""
    return {
        "layer": "human_review_packet",
        "status": "evidence_summary_only",
        "machine_decision": None,
        "human_reviewable_evidence": {
            "condition_id": record.get("condition_id"),
            "attack_id": record.get("attack_id"),
            "defense_id": record.get("defense_id"),
            "target_model_id": record.get("target_model_id"),
            "judge_id": record.get("judge_id"),
            "judge_status": record.get("judge_status"),
            "outcome": record.get("outcome"),
            "evidence_type": record.get("evidence_type"),
            "evidence_status": record.get("evidence_status"),
            "config_hash": record.get("config_hash"),
            "dataset_id": record.get("dataset_id"),
            "dataset_hash": record.get("dataset_hash"),
            "repository_revision": record.get("repository_revision"),
            "raw_evidence_path": record.get("raw_evidence_path"),
        },
        "human_decision": None,
        "empirical_human_outcome": None,
        "provenance": {
            "run_id": record.get("run_id"),
            "timestamp": record.get("timestamp"),
        },
    }
