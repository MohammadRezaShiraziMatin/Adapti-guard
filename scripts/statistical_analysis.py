#!/usr/bin/env python3
"""Unified statistical analysis for Q1 manuscript evidence.

Reads prediction artifacts from EXP-003/004 and produces:
- Bootstrap 95% CI per baseline
- McNemar paired tests
- Wilcoxon signed-rank tests
- Cohen's d effect sizes
- Holm-corrected p-values

Usage:
    python scripts/statistical_analysis.py --input experiments/EXP004_MULTI_MODEL
    python scripts/statistical_analysis.py --input experiments/EXP003_BASELINES

Never fabricates metrics — reports NO_DATA when artifacts missing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.evaluation.multi_model_statistics import (
    analyze_multi_model_results,
    save_statistical_report,
)


def analyze_baseline_comparison(input_dir: Path) -> dict:
    """Analyze EXP-003 style single-model baseline comparison."""
    from src.adapti_guard.evaluation.multi_model_statistics import (
        compute_baseline_statistics,
        load_predictions,
        outcomes_from_predictions,
        paired_baseline_comparison,
    )
    from src.adapti_guard.evaluation.statistics import holm_correction

    baselines = []
    for d in sorted(input_dir.iterdir()):
        if d.is_dir() and (d / f"{d.name}_predictions.jsonl").exists():
            baselines.append(d.name)

    if not baselines:
        return {"status": "NO_DATA", "reason": "no prediction artifacts"}

    outcomes = {}
    stats = {}
    for b in baselines:
        rows = load_predictions(input_dir / b / f"{b}_predictions.jsonl")
        outcomes[b] = outcomes_from_predictions(rows, baseline=b, model_key="single")
        stats[b] = compute_baseline_statistics(outcomes[b])

    comparisons = {}
    if "B0" in outcomes and "B3" in outcomes:
        comparisons["B0_vs_B3"] = paired_baseline_comparison(
            outcomes["B0"], outcomes["B3"], reference="B0", treatment="B3",
        )

    raw_ps = [c["mcnemar"]["p_value"] for c in comparisons.values()]
    holm = holm_correction(raw_ps) if raw_ps else []

    return {
        "status": "COMPLETED",
        "baselines": stats,
        "paired_comparisons": comparisons,
        "holm_corrected": holm,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Q1 statistical analysis")
    parser.add_argument("--input", required=True, help="Experiment output directory")
    parser.add_argument("--models", nargs="*", default=None)
    parser.add_argument("--baselines", nargs="*", default=None)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    input_dir = Path(args.input)
    if not input_dir.is_absolute():
        input_dir = ROOT / input_dir

    # Multi-model layout: input/target_x/B0/...
    has_multi = any(
        (input_dir / d).is_dir() and d.startswith("model_")
        for d in input_dir.iterdir()
    ) if input_dir.exists() else False

    if has_multi:
        models = args.models or [
            d.name for d in sorted(input_dir.iterdir())
            if d.is_dir() and d.name.startswith("model_")
        ]
        baselines = args.baselines or ["B0", "B1", "B2_L1", "B2_L2", "B2_L3", "B3"]
        report = analyze_multi_model_results(
            input_dir, models=models, baselines=baselines, seed=args.seed,
        )
        path = save_statistical_report(report, input_dir)
        print(json.dumps(report.to_dict(), indent=2))
        print(f"\nSaved: {path}")
        return 0 if report.status != "NO_DATA" else 1

    result = analyze_baseline_comparison(input_dir)
    out = input_dir / "statistical_analysis.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
