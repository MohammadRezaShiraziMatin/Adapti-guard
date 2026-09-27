"""Q1 confirmatory protocol helpers (offline; no live API).

Implements Owner Sheet v2 analysis/runner semantics: McNemar complete pairs,
timeout as judge failure, network-only retries, judge blindness to arm.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from adapti_guard.evaluation.attack_success import EvalEpisode, episode_judge_failed
from adapti_guard.evaluation.llm_judge import FORBIDDEN_JUDGE_FIELDS, JudgeInput
from adapti_guard.evaluation.q1_cost_preflight import estimate_q1_phase_preflight
import yaml

DEFAULT_CONTRACT_PATH = Path("configs/q1_evaluation_contract.yaml")

NETWORK_RETRY_FAILURE_KINDS = frozenset({
    "network_error",
    "connection_error",
    "timeout",
    "rate_limit",
})

JUDGE_TIMEOUT_REASONS = frozenset({
    "timeout",
    "judge_timeout",
    "target_timeout",
})


def q1_episode_judge_failed(ep: EvalEpisode, *, timeout_is_failure: bool = True) -> bool:
    """Extend global judge-fail semantics with Q1 timeout rule (D09)."""
    if episode_judge_failed(ep):
        return True
    if not timeout_is_failure:
        return False
    meta = ep.metadata or {}
    if meta.get("timeout") or meta.get("timed_out"):
        return True
    if ep.judge_reason in JUDGE_TIMEOUT_REASONS:
        return True
    if ep.metadata.get("target_error_kind") in JUDGE_TIMEOUT_REASONS:
        return True
    return False


def mcnemar_pair_complete(
    arm_a: EvalEpisode,
    arm_b: EvalEpisode,
    *,
    timeout_is_failure: bool = True,
) -> bool:
    """Both arms must be judgeable for primary McNemar (complete-pair rule)."""
    return not q1_episode_judge_failed(arm_a, timeout_is_failure=timeout_is_failure) and not q1_episode_judge_failed(
        arm_b, timeout_is_failure=timeout_is_failure
    )


def classify_retry_allowed(exc_or_kind: str) -> bool:
    """D15: retry only on network-class failures."""
    low = str(exc_or_kind).lower()
    return any(k in low for k in NETWORK_RETRY_FAILURE_KINDS)


@dataclass
class Q1NetworkRetryBudget:
    max_retries: int
    retries_used: int = 0

    def attempt(self, failure_kind: str) -> bool:
        if not classify_retry_allowed(failure_kind):
            return False
        if self.retries_used >= self.max_retries:
            return False
        return True

    def record_retry(self) -> None:
        self.retries_used += 1


def validate_judge_blind_payload(payload: Mapping[str, Any]) -> None:
    """D14: judge input must not encode defense arm / condition."""
    forbidden = set(FORBIDDEN_JUDGE_FIELDS) | {
        "condition_id",
        "defense_arm",
        "defense_mode",
        "baseline",
        "arm",
        "pre_target_defense",
    }
    for key in payload:
        if key in forbidden:
            raise ValueError(f"judge payload leaks arm/condition: {key}")


def build_blind_judge_input(
    *,
    user_prompt: str,
    model_response: str,
    task_context: str = "",
    success_condition: str = "",
    is_benign: bool = False,
) -> JudgeInput:
    ji = JudgeInput(
        user_prompt=user_prompt,
        model_response=model_response,
        task_context=task_context,
        success_condition=success_condition,
        is_benign=is_benign,
    )
    validate_judge_blind_payload(ji.to_blind_payload())
    return ji


def _load_contract_dict(path: Path | None = None) -> dict[str, Any]:
    p = path or DEFAULT_CONTRACT_PATH
    with Path(p).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def primary_causal_episode_count(contract: dict[str, Any] | None = None) -> int:
    contract = contract or _load_contract_dict()
    sheet = contract.get("q1_decision_sheet_v2") or {}
    fam = sheet.get("primary_holm_family") or {}
    n_targets = len(list(fam.get("open_target_model_ids") or []))
    n_attack = int((contract.get("dataset") or {}).get("n_attack", 61))
    n_arms = 2  # A0 vs B3
    return n_attack * n_targets * n_arms
