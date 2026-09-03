#!/usr/bin/env python3
"""EXP-003: Baseline comparison with real LLM evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.experiments.env_loader import load_project_env

load_project_env()

from baselines.baseline_runner import BaselineComparisonRunner
from src.adapti_guard.evaluation.attack_success import load_benchmark_records


def main() -> int:
    parser = argparse.ArgumentParser(description="EXP-003 Baseline Comparison")
    parser.add_argument("--split", default="test")
    parser.add_argument("--n-samples", type=int, default=100)
    parser.add_argument("--target", default="target_3")
    parser.add_argument("--output", default="experiments/EXP003_BASELINES")
    args = parser.parse_args()

    output_dir = ROOT / args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    records = load_benchmark_records(split=args.split, limit=args.n_samples)
    runner = BaselineComparisonRunner(target_config_key=args.target)
    rows = runner.compare_all(records)

    (output_dir / "baseline_comparison.json").write_text(
        json.dumps(rows, indent=2), encoding="utf-8"
    )
    runner.save_csv(rows, output_dir / "baseline_comparison.csv")
    runner.save_figure(rows, ROOT / "figures" / "baseline_comparison.png")

    status = "COMPLETED" if rows and rows[0].get("status") != "BLOCKED" else "BLOCKED"
    (output_dir / "metrics.json").write_text(json.dumps({
        "status": status,
        "n_methods": len(rows),
        "n_samples": len(records),
        "results": rows,
    }, indent=2))

    print(json.dumps({"status": status, "methods": len(rows)}, indent=2))
    return 0 if status == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
