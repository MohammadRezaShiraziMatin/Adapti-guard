"""Offline fair-comparison contract: fixed sequence vs adaptive defense-feedback."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence

from adapti_guard.attacker.adaptive_attacker import AdaptiveAttacker
from adapti_guard.attacker.fixed_sequence_attacker import (
    FixedSequenceAttacker,
    default_fixed_family_sequence,
)
from adapti_guard.evaluation.b2_adaptive_contract import (
    B2_ATTACK_PROTOCOL,
    MULTI_TURN_SUCCESS_SEMANTICS,
)
from adapti_guard.evaluation.adaptive_episode import AdaptiveEpisodeResult, AdaptiveTurnRecord

B2_ATTACK_MODE_ADAPTIVE = "adaptive_defense_feedback"
B2_ATTACK_MODE_FIXED = "fixed_sequence"

# Pilot / live condition identifiers (canonical run_live_condition path).
B2_LIVE_CONDITION_FIXED = "B2-FIXED"
B2_LIVE_CONDITION_ADAPTIVE = "B2-ADAPTIVE"

AttackModeId = Literal["adaptive_defense_feedback", "fixed_sequence"]


@dataclass(frozen=True)
class B2AttackModeComparisonContract:
    """
    Independent factor: attacker_mode only.
    All other arms held equal in offline synthetic / future live comparison.
    """

    attacker_mode: AttackModeId
    attack_protocol: str = B2_ATTACK_PROTOCOL
    success_semantics: str = MULTI_TURN_SUCCESS_SEMANTICS
    max_turns: int = 3
    defense: str = "make_b1_rule_based"
    target_config_key: str = "model_b"
    judge_config_key: str = "judge_fallback"
    note: str = (
        "AdaptiveAttacker adapts on defense-feedback failure (block / non-privileged "
        "target outcome); not target-response-content adaptive."
    )


def attack_mode_for_condition_id(condition_id: str) -> AttackModeId | None:
    if condition_id.startswith("B2-FIXED") or condition_id == B2_LIVE_CONDITION_FIXED:
        return B2_ATTACK_MODE_FIXED
    if (
        condition_id.startswith("B2-ADAPTIVE")
        or condition_id == B2_LIVE_CONDITION_ADAPTIVE
        or condition_id
        in (
            "LIVE-PRO-PI-B2-ADAPTIVE",
            "COND-E2-ADAPTIVE-OFFLINE",
        )
    ):
        return B2_ATTACK_MODE_ADAPTIVE
    return None


def resolve_attack_mode(
    condition_id: str,
    explicit: AttackModeId | None = None,
) -> AttackModeId:
    if explicit is not None:
        return explicit
    mode = attack_mode_for_condition_id(condition_id)
    if mode is None:
        raise ValueError(f"cannot resolve attack_mode for condition_id={condition_id}")
    return mode


def _family_for_payload(payload: str) -> str:
    for family, payloads in AdaptiveAttacker.PAYLOADS.items():
        if payload in payloads:
            return family
    return "unknown"


def _payload_sophistication_index(family: str, payload: str) -> int:
    payloads = AdaptiveAttacker.PAYLOADS.get(family, ())
    for idx, text in enumerate(payloads):
        if text == payload:
            return idx
    return -1


def build_attacker_turn_trace(
    episode_result: AdaptiveEpisodeResult,
) -> tuple[dict[str, object], ...]:
    trace: list[dict[str, object]] = []
    for turn in episode_result.turns:
        family = _family_for_payload(turn.user_message)
        soph = _payload_sophistication_index(family, turn.user_message)
        trace.append(
            {
                "turn_index": turn.turn_index,
                "defense_outcome": "BLOCK" if turn.blocked else "ALLOW",
                "family": family,
                "sophistication_index": soph,
                "payload": turn.user_message,
            }
        )
    return tuple(trace)


def build_attacker_for_mode(
    mode: AttackModeId,
    *,
    max_turns: int = 3,
    fixed_family_sequence: tuple[str, ...] | None = None,
) -> AdaptiveAttacker | FixedSequenceAttacker:
    if mode == B2_ATTACK_MODE_ADAPTIVE:
        return AdaptiveAttacker()
    if mode == B2_ATTACK_MODE_FIXED:
        seq = fixed_family_sequence or default_fixed_family_sequence(max_turns)
        return FixedSequenceAttacker(seq)
    raise ValueError(f"unknown attack mode: {mode}")


def extract_turn_supplementary_metrics(
    turns: Sequence[AdaptiveTurnRecord],
) -> dict[str, int | float | None]:
    """Derived from episode turn records only; does not alter metric core."""
    n = len(turns)
    if n == 0:
        return {
            "evaluated_turns": 0,
            "blocked_turns": 0,
            "turn_block_rate": None,
            "first_allow_turn": None,
            "target_calls": 0,
            "episodes_with_target_call": 0,
        }
    blocked_turns = sum(1 for t in turns if t.blocked)
    target_calls = sum(1 for t in turns if t.target_called)
    first_allow = next((t.turn_index for t in turns if not t.blocked), None)
    return {
        "evaluated_turns": n,
        "blocked_turns": blocked_turns,
        "turn_block_rate": blocked_turns / n,
        "first_allow_turn": first_allow,
        "target_calls": target_calls,
        "episodes_with_target_call": 1 if target_calls > 0 else 0,
    }
