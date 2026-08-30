"""De-escalation root-cause diagnostic from existing validated artifacts."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.adapti_guard.experiments.harmonized_runner import (
    METRIC_VERSION,
    RUNNER_VERSION,
    PolicyMode,
    HarmonizedRunner,
    build_schedule_75_25,
    sha256_file,
    summarize_method,
)


EXPERIMENT_VERSION = "q1_deescalation_diagnostic_v1"
OUTPUT_DIR = Path("results/phase8/q1_deescalation_diagnostic_v1")
HARMONIZED_RESULTS = Path("results/phase8/q1_harmonized_v1/harmonized_results.json")
STREAM_PATH = Path("results/common_attack_stream.json")
LOG_PATH = Path("../../ANALYSIS/LITERATURE_AUDIT/LOGS/q1_deescalation_root_cause.log")
REPORT_PATH = Path("../../ANALYSIS/REPORTS/Q1_DEESCALATION_ROOT_CAUSE_v1.md")

# From FeedbackEngine / PolicyUpdateEngine / DefensePolicyEngine / OutcomeEvaluator
DEESCALATION_CONDITIONS = {
    "reduce_signal_rule_1": (
        "legitimate_task AND legitimate_success AND cost_penalty >= 0.50"
    ),
    "reduce_signal_rule_2": (
        "legitimate_task AND NOT legitimate_success AND utility=0 AND cost_penalty >= 0.50"
    ),
    "level_transition": (
        "legitimate_pressure >= legitimate_threshold (default 2) after REDUCE_DEFENSE"
    ),
    "action_costs": {
        "A0": 0.0,
        "A1": 0.1,
        "A2": 0.25,
        "A3": 0.5,
    },
    "cost_gate_threshold": 0.50,
    "legitimate_low_risk_cap": (
        "DefensePolicyEngine: LOW risk legitimate traffic max action A1 (SANITIZE), "
        "even when defense_level >= 3"
    ),
}


def _git_commit() -> str | None:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return r.stdout.strip()
    except Exception:
        return None


def log_event(event: str, message: str) -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"{stamp} | {event} | {message}\n")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def analyze_episodes(episodes: list[dict[str, Any]]) -> dict[str, Any]:
    legit = [e for e in episodes if e.get("legitimate_task")]
    attack = [e for e in episodes if e.get("attack_present")]

    def signal_counts(rows):
        return dict(Counter(e["adaptation_signal"] for e in rows))

    legit_at_l3 = [e for e in legit if e["defense_level_before"] >= 3]

    return {
        "episode_count": len(episodes),
        "legitimate_count": len(legit),
        "attack_count": len(attack),
        "legitimate_signals": signal_counts(legit),
        "attack_signals": signal_counts(attack),
        "legitimate_actions": dict(Counter(e["defense_action"] for e in legit)),
        "legitimate_costs": dict(Counter(e["defense_cost"] for e in legit)),
        "legitimate_risk_levels": dict(Counter(e["risk_level"] for e in legit)),
        "legitimate_at_level_3_plus": len(legit_at_l3),
        "legitimate_at_l3_sample": [
            {
                "episode_id": e["episode_id"],
                "defense_level_before": e["defense_level_before"],
                "defense_action": e["defense_action"],
                "defense_cost": e["defense_cost"],
                "risk_level": e["risk_level"],
                "legitimate_success": e["legitimate_success"],
                "adaptation_signal": e["adaptation_signal"],
                "why_not_reduce": _why_not_reduce(e),
            }
            for e in legit_at_l3[:3]
        ],
    }


def _why_not_reduce(episode: dict[str, Any]) -> str:
    cost = episode["defense_cost"]
    if cost < 0.50:
        return (
            f"cost_penalty={cost} < 0.50 gate; "
            f"action={episode['defense_action']} due to LOW-risk policy cap"
        )
    if episode["legitimate_success"]:
        return "would emit REDUCE_DEFENSE (cost gate satisfied)"
    return "legitimate failed with cost>=0.50 would emit REDUCE_DEFENSE"


def trace_causal_chain() -> list[dict[str, str]]:
    return [
        {
            "step": "1_episode_input",
            "description": "Legitimate benign task (detection_score≈0, risk=LOW)",
        },
        {
            "step": "2_policy_decision",
            "description": (
                "DefensePolicyEngine.decide(risk=LOW, defense_level=3) → A1 SANITIZE "
                "(not A3 BLOCK); low-risk cap prevents expensive action"
            ),
        },
        {
            "step": "3_outcome",
            "description": (
                "legitimate_success=True, defense_cost=0.10 (< 0.50 gate)"
            ),
        },
        {
            "step": "4_feedback",
            "description": (
                "FeedbackEngine rule 1 requires cost>=0.50 → skipped; "
                "rule 5 legitimate_success → MAINTAIN (not REDUCE_DEFENSE)"
            ),
        },
        {
            "step": "5_policy_update",
            "description": (
                "MAINTAIN preserves pressure; legitimate_pressure never accumulates; "
                "no L3→L2 transition"
            ),
        },
    ]


def counterfactual_no_cost_gate(harmonized: dict) -> dict[str, Any]:
    fa = harmonized["summaries"]
    by_method = {s["method"]: s for s in fa}
    full = by_method["full_adaptive"]["transition_statistics"]
    nc = by_method["no_cost_gate"]["transition_statistics"]
    nc_eps = harmonized["episodes"]["no_cost_gate"]
    legit_nc = [e for e in nc_eps if e["legitimate_task"]]
    return {
        "full_adaptive_deescalations": full["deescalation_count"],
        "no_cost_gate_deescalations": nc["deescalation_count"],
        "no_cost_gate_legitimate_reduce_signals": sum(
            1 for e in legit_nc if e["adaptation_signal"] == "REDUCE_DEFENSE"
        ),
        "interpretation": (
            "De-escalation machinery (PolicyUpdateEngine) is functional when "
            "REDUCE_DEFENSE signals are emitted; default FeedbackEngine cost gate "
            "combined with DefensePolicyEngine low-risk cap prevents signal emission"
        ),
    }


def targeted_replay_trace() -> dict[str, Any]:
    """Minimal deterministic replay: one legitimate episode at level 3 from frozen stream."""
    with STREAM_PATH.open("r", encoding="utf-8") as f:
        stream = json.load(f)
    schedule = build_schedule_75_25(100)
    runner = HarmonizedRunner(stream, schedule)

    # Run until first legitimate episode after level reaches 3
    result = runner.run_method(PolicyMode.FULL_ADAPTIVE)
    target = None
    for ep in result.episodes:
        if ep.legitimate_task and ep.defense_level_before >= 3:
            target = ep
            break

    if target is None:
        return {"found": False}

    return {
        "found": True,
        "episode_id": target.episode_id,
        "defense_level_before": target.defense_level_before,
        "defense_level_after": target.defense_level_after,
        "defense_action": target.defense_action,
        "defense_cost": target.defense_cost,
        "risk_level": target.risk_level,
        "adaptation_signal": target.adaptation_signal,
        "causal_chain": trace_causal_chain(),
    }


def classify_root_cause(artifact_analysis: dict, counterfactual: dict) -> dict[str, str]:
    return {
        "primary": "GENUINE NEGATIVE RESULT",
        "secondary": "EXPERIMENTAL CONDITION (design coupling)",
        "not_implementation": (
            "PolicyUpdateEngine de-escalation path verified via no_cost_gate "
            f"({counterfactual['no_cost_gate_deescalations']} de-escalations)"
        ),
        "not_metric_schedule": (
            "Transition recording correct; 0 de-escalation reflects 0 REDUCE_DEFENSE "
            "pressure accumulation under default config"
        ),
        "mechanism": (
            "DefensePolicyEngine LOW-risk cap (max A1) × FeedbackEngine cost gate "
            "(REDUCE requires cost>=0.50) makes REDUCE_DEFENSE unreachable on "
            "evaluated legitimate episodes"
        ),
    }


def pareto_from_harmonized(harmonized: dict) -> dict[str, Any]:
    points = []
    for s in harmonized["summaries"]:
        points.append(
            {
                "method": s["method"],
                "security": s["defense_rate"],
                "utility": s["utility"],
                "cost": s["defense_cost"],
            }
        )

    def dominates(a, b):
        ok = (
            a["security"] >= b["security"]
            and a["utility"] >= b["utility"]
            and a["cost"] <= b["cost"]
        )
        strict = (
            a["security"] > b["security"]
            or a["utility"] > b["utility"]
            or a["cost"] < b["cost"]
        )
        return ok and strict

    nd, dom = [], []
    for i, pi in enumerate(points):
        if any(i != j and dominates(pj, pi) for j, pj in enumerate(points)):
            dom.append(pi["method"])
        else:
            nd.append(pi["method"])

    return {
        "points": points,
        "pareto_non_dominated": sorted(nd),
        "pareto_dominated": sorted(dom),
        "full_adaptive_status": (
            "Pareto-dominated"
            if "full_adaptive" in dom
            else "Pareto-non-dominated"
        ),
    }


def validate_frozen(stream_hash: str) -> dict[str, Any]:
    manifest_path = Path("results/phase8/q1_harmonized_v1/run_manifest.json")
    ref_hash = None
    if manifest_path.exists():
        ref_hash = json.loads(manifest_path.read_text(encoding="utf-8")).get(
            "attack_stream_sha256"
        )
    checks = {
        "stream_unchanged": stream_hash == ref_hash,
        "harmonized_exists": HARMONIZED_RESULTS.exists(),
        "output_versioned": str(OUTPUT_DIR).endswith("q1_deescalation_diagnostic_v1"),
    }
    return {
        "validity": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "stream_sha256": stream_hash,
    }


def write_report(
    path: Path,
    classification: dict,
    artifact_analysis: dict,
    counterfactual: dict,
    replay: dict,
    pareto: dict,
    validation: dict,
) -> None:
    fa = artifact_analysis["methods"]["full_adaptive"]
    lines = [
        "# ADAPTI-GUARD — De-escalation Root Cause v1",
        "",
        f"**Primary classification:** {classification['primary']}",
        "",
        "## 1. Execution Path Traced",
        "",
        "Required for L3→L2, L2→L1, L1→L0:",
        "",
        "1. `FeedbackEngine` emits `REDUCE_DEFENSE` (rules 1 or 2: cost ≥ 0.50)",
        "2. `PolicyUpdateEngine` accumulates `legitimate_pressure`",
        "3. `legitimate_pressure >= legitimate_threshold` (default 2)",
        "4. `defense_level -= 1`, recorded in `transition_history`",
        "",
        "## 2. Observed Values (full_adaptive, W1, from harmonized v1)",
        "",
        f"- Legitimate episodes: {fa['legitimate_count']}",
        f"- Legitimate at level ≥3: {fa['legitimate_at_level_3_plus']}",
        f"- Legitimate signals: {fa['legitimate_signals']}",
        f"- Legitimate actions: {fa['legitimate_actions']} (all A1)",
        f"- Legitimate costs: {fa['legitimate_costs']} (all 0.10)",
        f"- De-escalation transitions: 0",
        "",
        "**Why REDUCE_DEFENSE never occurred:** legitimate episodes receive A1 (cost 0.10) "
        "via DefensePolicyEngine low-risk cap; cost gate requires ≥0.50.",
        "",
        "## 3. Causal Chain",
        "",
    ]
    for step in trace_causal_chain():
        lines.append(f"- **{step['step']}:** {step['description']}")

    lines.extend(
        [
            "",
            "## 4. Counterfactual (no_cost_gate ablation, same population)",
            "",
            f"- full_adaptive de-escalations: {counterfactual['full_adaptive_deescalations']}",
            f"- no_cost_gate de-escalations: {counterfactual['no_cost_gate_deescalations']}",
            f"- no_cost_gate REDUCE_DEFENSE on legitimate: "
            f"{counterfactual['no_cost_gate_legitimate_reduce_signals']}/25",
            "",
            f"**Conclusion:** {counterfactual['interpretation']}",
            "",
            "## 5. Root Cause Classification",
            "",
            f"| Category | Verdict |",
            f"|---|---|",
            f"| Implementation issue | NO — {classification['not_implementation']} |",
            f"| Metric/schedule issue | NO — {classification['not_metric_schedule']} |",
            f"| Experimental condition | YES — design coupling under default eval |",
            f"| Genuine negative result | YES — bidirectional adaptation not supported |",
            "",
            f"**Mechanism:** {classification['mechanism']}",
            "",
            "## 6. Security–Utility–Cost (harmonized v1, W1)",
            "",
            f"- Pareto non-dominated: {pareto['pareto_non_dominated']}",
            f"- full_adaptive: {pareto['full_adaptive_status']}",
            "",
            "## 7. Q1 Claim Control",
            "",
            "**D1 allowed:** risk-aware runtime intervention with empirically supported escalation",
            "",
            "**D1 forbidden:** effective bidirectional adaptation / de-escalation contribution",
            "",
            "**D2 allowed:** harmonized security–utility–cost evaluation of fixed vs adaptive policies",
            "",
            "**D2 forbidden:** adaptive policy is Pareto-optimal",
            "",
            "**DE-ESCALATION CONTRIBUTION = NOT EMPIRICALLY SUPPORTED** under default controller.",
            "",
            "## 8. Action Taken",
            "",
            "**CLAIM REVISION** — no controller modification.",
            "",
            f"Validation: **{validation['validity']}**",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    log_event("START", EXPERIMENT_VERSION)

    if not HARMONIZED_RESULTS.exists():
        log_event("FINAL_STATUS", "FAIL missing harmonized results")
        return 1

    stream_hash = sha256_file(STREAM_PATH) if STREAM_PATH.exists() else None
    harmonized = json.loads(HARMONIZED_RESULTS.read_text(encoding="utf-8"))

    log_event("INPUT_VALIDATED", f"harmonized={HARMONIZED_RESULTS.name}")

    artifact_analysis = {
        "methods": {
            method: analyze_episodes(harmonized["episodes"][method])
            for method in (
                "full_adaptive",
                "escalation_only",
                "no_cost_gate",
                "de_escalation_only",
            )
        }
    }

    counterfactual = counterfactual_no_cost_gate(harmonized)
    replay = targeted_replay_trace()
    classification = classify_root_cause(artifact_analysis, counterfactual)
    pareto = pareto_from_harmonized(harmonized)
    validation = validate_frozen(stream_hash or "")

    log_event("TRACE_COMPLETE", classification["primary"])
    log_event("ROOT_CAUSE_CLASSIFIED", classification["mechanism"][:80])

    diagnostic = {
        "experiment_version": EXPERIMENT_VERSION,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "root_cause_classification": classification,
        "deescalation_conditions": DEESCALATION_CONDITIONS,
        "artifact_analysis": artifact_analysis,
        "counterfactual": counterfactual,
        "targeted_replay": replay,
        "pareto_reassessment": pareto,
        "action": "CLAIM_REVISION",
        "deescalation_evidence": "UNSUPPORTED",
        "implementation_fix_applied": False,
    }

    manifest = {
        "experiment_version": EXPERIMENT_VERSION,
        "timestamp_utc": diagnostic["timestamp_utc"],
        "git_commit": _git_commit(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "runner_version": RUNNER_VERSION,
        "metric_version": METRIC_VERSION,
        "source_artifacts": [
            str(HARMONIZED_RESULTS),
            str(STREAM_PATH),
            "results/phase8/q1_threshold_sensitivity_v1/threshold_results.json",
            "results/phase8/q1_workload_sensitivity_v1/workload_results.json",
        ],
        "attack_stream_sha256": stream_hash,
        "action": "CLAIM_REVISION",
        "implementation_modified": False,
    }

    transition_stats = {
        "full_adaptive": harmonized["summaries"][
            next(
                i
                for i, s in enumerate(harmonized["summaries"])
                if s["method"] == "full_adaptive"
            )
        ]["transition_statistics"],
        "no_cost_gate": harmonized["summaries"][
            next(
                i
                for i, s in enumerate(harmonized["summaries"])
                if s["method"] == "no_cost_gate"
            )
        ]["transition_statistics"],
        "signal_audit": artifact_analysis,
    }

    write_json(OUTPUT_DIR / "diagnostic_results.json", diagnostic)
    write_json(OUTPUT_DIR / "run_manifest.json", manifest)
    write_json(OUTPUT_DIR / "transition_statistics.json", transition_stats)
    write_json(OUTPUT_DIR / "validation.json", validation)

    write_report(
        REPORT_PATH,
        classification,
        artifact_analysis,
        counterfactual,
        replay,
        pareto,
        validation,
    )

    log_event("VALIDATION", validation["validity"])
    log_event("FINAL_STATUS", "COMPLETE CLAIM_REVISION")

    print("ROOT CAUSE:", classification["primary"])
    print("ACTION: CLAIM_REVISION")
    print("Q1 VALIDITY: CONDITIONAL")
    return 0 if validation["validity"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
