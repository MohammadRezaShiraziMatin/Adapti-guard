"""Exploratory four-arm schedule (A0, B3, CORE, TOOLDENY). Not the Option D confirmatory scope.

Only the two attack scenarios that execute against undefended targets in pilot 3
(``direct_user_override_v1``, ``create_record_exfil_v1``) plus the three benign
scenarios are scheduled. See ``docs/research/HARNESS_V2_OFFLINE_REPLAY_20260930.md``.
"""
from __future__ import annotations

from typing import Any

EXPLORATORY_ARMS = ("A0", "B3", "CORE", "TOOLDENY")
OPTIONAL_ARMS = ("ARGALLOW",)  # opt-in via --arms; see argallow_policy.py
EXPLORATORY_ATTACK_SCENARIOS = ("direct_user_override_v1", "create_record_exfil_v1")
EXPLORATORY_BENIGN_SCENARIOS = (
    "benign_weather_v1",
    "benign_email_allowlist_v1",
    "benign_create_record_v1",
)
EXPLORATORY_MODELS = ("qwen3", "gemma", "deepseek")
DEFAULT_K_ATTACK = 12
DEFAULT_K_BENIGN = 5
# Per-episode HTTP cost planning basis: pilot 3 = 0.03454372 USD / 160 episodes.
PILOT3_USD_PER_EPISODE = 0.03454372 / 160


def exploratory_schedule(
    *,
    k_attack: int = DEFAULT_K_ATTACK,
    k_benign: int = DEFAULT_K_BENIGN,
    models: tuple[str, ...] = EXPLORATORY_MODELS,
    arms: tuple[str, ...] = EXPLORATORY_ARMS,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scenarios, k in (
        (EXPLORATORY_ATTACK_SCENARIOS, k_attack),
        (EXPLORATORY_BENIGN_SCENARIOS, k_benign),
    ):
        for scenario_id in scenarios:
            for inst in range(k):
                for family in models:
                    for condition in arms:
                        rows.append(
                            {
                                "scenario_id": scenario_id,
                                "instance_index": inst,
                                "family": family,
                                "condition": condition,
                            }
                        )
    return rows


def exploratory_plan(
    *,
    max_rounds: int,
    k_attack: int = DEFAULT_K_ATTACK,
    k_benign: int = DEFAULT_K_BENIGN,
    arms: tuple[str, ...] = EXPLORATORY_ARMS,
) -> dict[str, Any]:
    n = len(exploratory_schedule(k_attack=k_attack, k_benign=k_benign, arms=arms))
    return {
        "episodes": n,
        "arms": list(arms),
        "http_cap": n * max_rounds,
        "expected_usd_pilot3_rate": round(n * PILOT3_USD_PER_EPISODE, 4),
    }


INDEPENDENT_SCREEN_ARMS = ("A0",)
INDEPENDENT_SCREEN_K = 8


def independent_screening_schedule(
    *,
    k: int = INDEPENDENT_SCREEN_K,
    models: tuple[str, ...] = EXPLORATORY_MODELS,
    arms: tuple[str, ...] = INDEPENDENT_SCREEN_ARMS,
) -> list[dict[str, Any]]:
    """A0 screening of the independent attack set (Amendment 10 5: admission rule). No benign episodes."""
    from adapti_guard.evaluation.harness_v2.scenario_catalog import INDEPENDENT_ATTACK_SCENARIOS

    return [
        {"scenario_id": sid, "instance_index": inst, "family": fam, "condition": cond}
        for sid in INDEPENDENT_ATTACK_SCENARIOS
        for inst in range(k)
        for fam in models
        for cond in arms
    ]
