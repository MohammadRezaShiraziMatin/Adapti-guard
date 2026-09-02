#!/usr/bin/env python3
"""Post-process EXP-004 artifacts: statistics, category breakdown, reports."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.evaluation.multi_model_statistics import (
    analyze_multi_model_results,
    load_predictions,
    paired_baseline_comparison,
    save_statistical_report,
)
from src.adapti_guard.evaluation.statistics import bootstrap_ci, holm_correction, mcnemar_test

EXP_DIR = ROOT / "experiments" / "EXP-004"
REPORTS = EXP_DIR / "reports"
PROCESSED = EXP_DIR / "processed"


def category_analysis(model_key: str) -> dict:
    b0 = load_predictions(EXP_DIR / model_key / "B0" / "B0_predictions.jsonl")
    b6 = load_predictions(EXP_DIR / model_key / "B6" / "B6_predictions.jsonl")
    b0_map = {r["id"]: r for r in b0}
    b6_map = {r["id"]: r for r in b6}
    cats = sorted(set(r.get("category", "unknown") for r in b0))
    out = {}
    for cat in cats:
        ids = [i for i in b0_map if b0_map[i].get("category") == cat and i in b6_map]
        if not ids:
            continue
        a = [bool(b0_map[i].get("attack_succeeded")) for i in ids]
        b = [bool(b6_map[i].get("attack_succeeded")) for i in ids]
        asr0 = sum(a) / len(a)
        asr6 = sum(b) / len(b)
        mcn = mcnemar_test(a, b)
        out[cat] = {
            "n": len(ids),
            "B0_asr": round(asr0, 4),
            "B6_asr": round(asr6, 4),
            "absolute_diff": round(asr0 - asr6, 4),
            "mcnemar": mcn,
        }
    return out


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)

    models = ["model_a", "model_b", "model_c"]
    report = analyze_multi_model_results(
        EXP_DIR,
        models=models,
        baselines=["B0", "B6"],
        experiment_id="EXP-004",
        reference_baseline="B0",
        treatment_baseline="B6",
    )
    save_statistical_report(report, EXP_DIR)

    cat_reports = {m: category_analysis(m) for m in models}
    stats = {
        "multi_model": report.to_dict(),
        "category_analysis": cat_reports,
    }
    (PROCESSED / "statistical_tests.json").write_text(
        json.dumps(stats, indent=2), encoding="utf-8"
    )

    # CLAIM audit stub
    claim_audit = """# EXP-004 Claim Audit

| Claim | Status | Evidence |
|-------|--------|----------|
| B6 reduces ASR vs B0 | See McNemar p-values | statistical_tests.json |
| SOTA defense | NOT SUPPORTED | No comparable SOTA baseline run |
| Production readiness | NOT SUPPORTED | Research prototype only |
| Benign utility preserved | NOT SUPPORTED | Attack-only eval set |
"""
    (REPORTS / "CLAIM_AUDIT.md").write_text(claim_audit, encoding="utf-8")

    summary_lines = [
        "# EXP-004 Report",
        "",
        f"Status: {report.status}",
        "",
        "## Per-model B0 vs B6",
    ]
    for comp in report.paired_comparisons:
        summary_lines.append(
            f"- {comp.get('model_key')}: B0 ASR={comp.get('asr_reference')} "
            f"B6 ASR={comp.get('asr_treatment')} p={comp.get('mcnemar', {}).get('p_value')}"
        )
    (REPORTS / "EXP-004_REPORT.md").write_text("\n".join(summary_lines), encoding="utf-8")
    print(json.dumps({"status": report.status, "output": str(PROCESSED)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
