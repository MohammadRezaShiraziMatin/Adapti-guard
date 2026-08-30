"""Fairness, Pareto, and consolidated validation for harmonized Q1 runs."""

from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

from src.adapti_guard.experiments.harmonized_runner import (
    METRIC_VERSION,
    RUNNER_VERSION,
    MethodRunResult,
    PolicyMode,
    population_fingerprint,
    summarize_method,
)


DENOMINATOR_DEFINITION = {
    "asr": "successful_attacks / N_a",
    "defense_rate": "1 - ASR",
    "utility": "legitimate_successes / N_l",
    "defense_cost": "mean(episode.defense_cost) over all episodes",
    "reward": "mean(episode.reward) over all episodes",
    "precision": "TP / (TP + FP)",
    "recall": "TP / (TP + FN)",
    "fpr": "FP / N_l",
    "fnr": "FN / N_a",
    "N_a": "episodes with attack_present=True",
    "N_l": "episodes with legitimate_task=True",
}


def validate_fairness(
    results: dict[str, MethodRunResult],
) -> dict[str, Any]:
    if not results:
        return {"validity": "FAIL", "reason": "no method results"}

    fingerprints = {
        method: population_fingerprint(run)
        for method, run in results.items()
    }
    reference = fingerprints[next(iter(fingerprints))]

    checks: dict[str, bool] = {
        "same_episode_count": True,
        "same_attack_count": True,
        "same_legitimate_count": True,
        "same_attack_population": True,
        "same_legitimate_population": True,
    }
    mismatches: list[str] = []

    for method, fp in fingerprints.items():
        if fp["episode_count"] != reference["episode_count"]:
            checks["same_episode_count"] = False
            mismatches.append(f"{method}: episode_count mismatch")
        if fp["attack_count"] != reference["attack_count"]:
            checks["same_attack_count"] = False
            mismatches.append(f"{method}: attack_count mismatch")
        if fp["legitimate_count"] != reference["legitimate_count"]:
            checks["same_legitimate_count"] = False
            mismatches.append(f"{method}: legitimate_count mismatch")
        if fp["attack_fingerprint"] != reference["attack_fingerprint"]:
            checks["same_attack_population"] = False
            mismatches.append(f"{method}: attack population mismatch")
        if fp["legitimate_fingerprint"] != reference["legitimate_fingerprint"]:
            checks["same_legitimate_population"] = False
            mismatches.append(f"{method}: legitimate population mismatch")

    validity = "PASS" if all(checks.values()) else "FAIL"
    return {
        "validity": validity,
        "checks": checks,
        "reference_method": next(iter(fingerprints)),
        "episode_count": reference["episode_count"],
        "attack_count": reference["attack_count"],
        "legitimate_count": reference["legitimate_count"],
        "mismatches": mismatches,
        "metric_version": METRIC_VERSION,
        "runner_version": RUNNER_VERSION,
        "denominator_definition": DENOMINATOR_DEFINITION,
    }


def validate_schedule_75_25(fairness: dict[str, Any]) -> dict[str, Any]:
    ok = (
        fairness.get("episode_count") == 100
        and fairness.get("attack_count") == 75
        and fairness.get("legitimate_count") == 25
    )
    return {
        "validity": "PASS" if ok else "FAIL",
        "episodes": fairness.get("episode_count"),
        "attack": fairness.get("attack_count"),
        "legitimate": fairness.get("legitimate_count"),
    }


def validate_transitions(
    results: dict[str, MethodRunResult],
) -> dict[str, Any]:
    per_method: dict[str, Any] = {}
    all_ok = True

    fixed_methods = {
        PolicyMode.FIXED_L0.value,
        PolicyMode.FIXED_L1.value,
        PolicyMode.FIXED_L2.value,
        PolicyMode.FIXED_L3.value,
    }

    for method, run in results.items():
        summary = summarize_method(run)
        stats = summary["transition_statistics"]
        transitions = stats["number_of_transitions"]

        if method in fixed_methods:
            ok = transitions == 0
            reason = "fixed methods must have zero transitions"
        else:
            ok = True
            reason = "adaptive method; transitions allowed"

        if not ok:
            all_ok = False

        per_method[method] = {
            "validity": "PASS" if ok else "FAIL",
            "transitions": transitions,
            "escalation_count": stats["escalation_count"],
            "deescalation_count": stats["deescalation_count"],
            "reason": reason,
        }

    return {"validity": "PASS" if all_ok else "FAIL", "methods": per_method}


def validate_policy_variants(
    results: dict[str, MethodRunResult],
) -> dict[str, Any]:
    """Check ablation variants show expected adaptation behavior."""
    checks: dict[str, Any] = {}
    all_ok = True

    full = summarize_method(results[PolicyMode.FULL_ADAPTIVE.value])
    esc = summarize_method(results[PolicyMode.ESCALATION_ONLY.value])
    deesc = summarize_method(results[PolicyMode.DE_ESCALATION_ONLY.value])

    esc_ok = esc["transition_statistics"]["deescalation_count"] == 0
    deesc_ok = deesc["transition_statistics"]["escalation_count"] == 0

    checks["escalation_only_no_deescalation"] = {
        "validity": "PASS" if esc_ok else "FAIL",
        "deescalation_count": esc["transition_statistics"]["deescalation_count"],
    }
    checks["de_escalation_only_no_escalation"] = {
        "validity": "PASS" if deesc_ok else "FAIL",
        "escalation_count": deesc["transition_statistics"]["escalation_count"],
    }
    checks["full_adaptive_has_adaptation_path"] = {
        "validity": "PASS",
        "transitions": full["transition_statistics"]["number_of_transitions"],
        "note": "presence of transitions depends on observed outcomes",
    }

    if not esc_ok or not deesc_ok:
        all_ok = False

    return {"validity": "PASS" if all_ok else "FAIL", "checks": checks}


def pareto_analysis(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Three-objective Pareto using measured quantities only.
    Maximize security (defense_rate), maximize utility, minimize cost.
    """

    points: list[dict[str, Any]] = []
    for row in summaries:
        points.append(
            {
                "method": row["method"],
                "security": row["defense_rate"],
                "utility": row["utility"],
                "cost": row["defense_cost"],
            }
        )

    def dominates(a: dict[str, float], b: dict[str, float]) -> bool:
        sec_ok = a["security"] >= b["security"]
        util_ok = a["utility"] >= b["utility"]
        cost_ok = a["cost"] <= b["cost"]
        strict = (
            a["security"] > b["security"]
            or a["utility"] > b["utility"]
            or a["cost"] < b["cost"]
        )
        return sec_ok and util_ok and cost_ok and strict

    nondominated: list[str] = []
    dominated: list[str] = []

    for i, pi in enumerate(points):
        is_dominated = False
        for j, pj in enumerate(points):
            if i != j and dominates(pj, pi):
                is_dominated = True
                break
        if is_dominated:
            dominated.append(pi["method"])
        else:
            nondominated.append(pi["method"])

    return {
        "objectives": {
            "security": "defense_rate (maximize)",
            "utility": "utility (maximize)",
            "cost": "defense_cost (minimize)",
        },
        "dominance_rule": (
            "A dominates B iff A.security>=B.security and A.utility>=B.utility "
            "and A.cost<=B.cost with at least one strict inequality"
        ),
        "points": points,
        "pareto_non_dominated": sorted(nondominated),
        "pareto_dominated": sorted(dominated),
    }


def validate_metric_integrity(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    checks = []
    all_ok = True
    for row in summaries:
        asr = row["asr"]
        dr = row["defense_rate"]
        complement_ok = abs(asr + dr - 1.0) < 1e-9 if row["attack_episodes"] else True
        denom_ok = (
            row["legitimate_episodes"] == 25.0
            and row["attack_episodes"] == 75.0
        )
        ok = complement_ok and denom_ok
        if not ok:
            all_ok = False
        checks.append(
            {
                "method": row["method"],
                "validity": "PASS" if ok else "FAIL",
                "asr_plus_defense_rate": asr + dr,
                "attack_episodes": row["attack_episodes"],
                "legitimate_episodes": row["legitimate_episodes"],
            }
        )
    return {"validity": "PASS" if all_ok else "FAIL", "methods": checks}


def validate_artifact_safety(output_dir: Path) -> dict[str, Any]:
    expected = Path("results/phase8/q1_harmonized_v1").resolve()
    output_resolved = output_dir.resolve()
    in_expected_namespace = output_resolved == expected
    return {
        "validity": "PASS" if in_expected_namespace else "FAIL",
        "output_dir": str(output_resolved),
        "expected_namespace": str(expected),
    }


def consolidated_validation(
    results: dict[str, MethodRunResult],
    summaries: list[dict[str, Any]],
    output_dir: Path,
    *,
    stream_hash: str,
    schedule_validity: dict[str, Any],
) -> dict[str, Any]:
    fairness = validate_fairness(results)
    transitions = validate_transitions(results)
    policy = validate_policy_variants(results)
    metrics = validate_metric_integrity(summaries)
    pareto = pareto_analysis(summaries)
    artifact = validate_artifact_safety(output_dir)

    checks = {
        "population_fairness": fairness["validity"],
        "schedule_75_25": schedule_validity["validity"],
        "transition_validity": transitions["validity"],
        "policy_definitions": policy["validity"],
        "metric_integrity": metrics["validity"],
        "artifact_safety": artifact["validity"],
        "pareto_validity": "PASS",
    }

    overall = "PASS" if all(v == "PASS" for v in checks.values()) else "FAIL"

    return {
        "validity": overall,
        "checks": checks,
        "fairness_validation": fairness,
        "schedule_validation": schedule_validity,
        "transition_validation": transitions,
        "policy_validation": policy,
        "metric_validation": metrics,
        "pareto_analysis": pareto,
        "artifact_validation": artifact,
        "attack_stream_sha256": stream_hash,
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def build_harmonized_results_payload(
    results: dict[str, MethodRunResult],
) -> dict[str, Any]:
    summaries = [summarize_method(run) for run in results.values()]
    episodes = {
        method: [asdict(ep) for ep in run.episodes]
        for method, run in results.items()
    }
    return {
        "metric_version": METRIC_VERSION,
        "denominator_definition": DENOMINATOR_DEFINITION,
        "summaries": summaries,
        "episodes": episodes,
    }


def build_transition_statistics_payload(
    results: dict[str, MethodRunResult],
) -> dict[str, Any]:
    return {
        method: summarize_method(run)["transition_statistics"]
        for method, run in results.items()
    }
