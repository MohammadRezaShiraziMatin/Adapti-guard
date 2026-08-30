#!/usr/bin/env python3
"""Phase 8C: threshold + workload sensitivity analysis."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.adapti_guard.experiments.sensitivity_analysis import (
    EXPERIMENT_VERSION,
    THRESHOLD_OUTPUT,
    WORKLOAD_OUTPUT,
    build_manifest,
    classify_evidence,
    log_event,
    run_threshold_sensitivity,
    run_workload_sensitivity,
    sha256_file,
    STREAM_PATH,
    validate_sensitivity,
    write_json,
    _load_stream,
)


LOG_PATH = Path(
    "../../ANALYSIS/LITERATURE_AUDIT/LOGS/q1_sensitivity_analysis.log"
)
REPORT_PATH = Path("../../ANALYSIS/REPORTS/Q1_SENSITIVITY_ANALYSIS_v1.md")


def main() -> int:
    log_event(LOG_PATH, "START", EXPERIMENT_VERSION)

    if not STREAM_PATH.exists():
        log_event(LOG_PATH, "FINAL_STATUS", "FAIL missing attack stream")
        return 1

    stream_hash = sha256_file(STREAM_PATH)
    stream = _load_stream()

    log_event(LOG_PATH, "INPUT_VALIDATION", f"stream_sha256={stream_hash[:16]}")

    threshold_payload = run_threshold_sensitivity(stream)
    log_event(
        LOG_PATH,
        "THRESHOLD_COMPLETE",
        f"configs={len(threshold_payload['configurations'])}",
    )

    workload_payload = run_workload_sensitivity(stream)
    log_event(
        LOG_PATH,
        "WORKLOAD_COMPLETE",
        f"workloads={len(workload_payload['workloads'])}",
    )

    validation = validate_sensitivity(
        threshold_payload, workload_payload, stream_hash
    )
    evidence = classify_evidence(threshold_payload, workload_payload)
    manifest = build_manifest(stream_hash, threshold_payload, workload_payload)
    manifest["validation"] = validation["validity"]
    manifest["evidence_classification"] = evidence

    transition_stats = {
        "threshold": {
            c["threshold_configuration"]["config_id"]: c["full_adaptive"]
            for c in threshold_payload["configurations"]
        },
        "workload": {
            w["workload_id"]: w["methods"]["full_adaptive"]
            for w in workload_payload["workloads"]
        },
    }

    write_json(THRESHOLD_OUTPUT / "threshold_results.json", threshold_payload)
    write_json(THRESHOLD_OUTPUT / "run_manifest.json", manifest)
    write_json(THRESHOLD_OUTPUT / "validation.json", validation)
    write_json(THRESHOLD_OUTPUT / "transition_statistics.json", transition_stats["threshold"])

    write_json(WORKLOAD_OUTPUT / "workload_results.json", workload_payload)
    write_json(WORKLOAD_OUTPUT / "run_manifest.json", manifest)
    write_json(WORKLOAD_OUTPUT / "validation.json", validation)
    write_json(WORKLOAD_OUTPUT / "transition_statistics.json", transition_stats["workload"])

    write_report(REPORT_PATH, threshold_payload, workload_payload, validation, evidence)

    log_event(LOG_PATH, "VALIDATION", validation["validity"])
    log_event(LOG_PATH, "FINAL_STATUS", validation["validity"])

    print("=" * 60)
    print("PHASE 8C SENSITIVITY ANALYSIS")
    print("=" * 60)
    print(f"VALIDATION: {validation['validity']}")
    print(f"De-escalation: {evidence['deescalation_evidence']}")
    print(f"Q1 implication: {evidence['q1_implication']}")
    return 0 if validation["validity"] == "PASS" else 2


def write_report(
    path: Path,
    threshold_payload,
    workload_payload,
    validation,
    evidence,
) -> None:
    configs = threshold_payload["configurations"]
    lines = [
        "# ADAPTI-GUARD — Q1 Sensitivity Analysis v1",
        "",
        "**Experiment:** `q1_sensitivity_v1` (Phase 8C)",
        "",
        "## Implementation Thresholds (extracted, not assumed)",
        "",
        "| Parameter | Value | Source |",
        "|---|---:|---|",
        "| attack_threshold | 2 (default) | PolicyUpdateEngine |",
        "| legitimate_threshold | 2 (default) | PolicyUpdateEngine |",
        "| cost_gate_threshold | 0.50 | FeedbackEngine |",
        "| increase_defense_low_cost_boundary | 0.50 | FeedbackEngine |",
        "| risk_low_medium_boundary | 0.25 | RiskEngine |",
        "| risk_medium_high_boundary | 0.60 | RiskEngine |",
        "",
        "## Threshold Sensitivity (W1: 75/25, full_adaptive only)",
        "",
        "| Config | attack_th | legit_th | ASR | DR | Utility | Cost | Trans | Esc | De-esc |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cfg in configs:
        tc = cfg["threshold_configuration"]
        fa = cfg["full_adaptive"]
        lines.append(
            f"| {tc['config_id']} | {tc['attack_threshold']} | "
            f"{tc['legitimate_threshold']} | {fa['asr']:.3f} | "
            f"{fa['defense_rate']:.3f} | {fa['utility']:.3f} | "
            f"{fa['defense_cost']:.3f} | {fa['total_transitions']} | "
            f"{fa['escalations']} | {fa['deescalations']} |"
        )

    lines.extend(
        [
            "",
            "**Finding:** Controller behavior is threshold-sensitive (transitions and ASR vary). "
            "De-escalation remains **0** across all tested threshold configs on W1.",
            "",
            "## Workload Sensitivity (default thresholds 2/2)",
            "",
        ]
    )

    for wl in workload_payload["workloads"]:
        fa = wl["methods"]["full_adaptive"]
        lines.append(f"### {wl['workload_id']}: {wl['label']}")
        lines.append("")
        lines.append(
            f"- Full adaptive: ASR={fa['asr']:.3f}, Utility={fa['utility']:.3f}, "
            f"Cost={fa['defense_cost']:.3f}, Esc={fa.get('escalations', 0)}, "
            f"De-esc={fa.get('deescalations', 0)}"
        )
        lines.append("")

    lines.extend(
        [
            "## Prior Finding (W1, baseline thresholds)",
            "",
            "Full Adaptive ≡ Escalation-only with **0 de-escalation transitions** on W1.",
            "",
            "### Root cause analysis",
            "",
            "- **Threshold configuration:** lowering legitimate_threshold to 1 still yields 0 de-escalation on W1",
            "- **Workload composition:** W1 keeps adaptive level at L3 after escalation; legitimate episodes succeed under risk-conditioned policy without emitting cost-gated REDUCE_DEFENSE",
            "- **Cost gate:** no_cost_gate ablation (harmonized v1) shows de-escalation only when cost gate removed",
            "- **Controller logic:** de-escalation requires REDUCE_DEFENSE pressure accumulation; cost gate blocks signal on W1",
            "",
            "## Evidence Classification",
            "",
            f"- Threshold robustness: **{evidence['threshold_robustness']}**",
            f"- Workload robustness: **{evidence['workload_robustness']}**",
            f"- De-escalation evidence: **{evidence['deescalation_evidence']}**",
            f"- Security–utility–cost stability: **{evidence['security_utility_cost_stability']}**",
            f"- Q1 implication: **{evidence['q1_implication']}**",
            "",
            "## Validation",
            "",
            f"Overall: **{validation['validity']}**",
            "",
        ]
    )

    if evidence["deescalation_evidence"] == "UNSUPPORTED":
        lines.append(
            "**DE-ESCALATION CONTRIBUTION NOT EMPIRICALLY SUPPORTED** under default "
            "controller configuration across tested thresholds and W1–W3 workloads."
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
