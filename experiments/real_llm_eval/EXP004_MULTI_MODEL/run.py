#!/usr/bin/env python3
"""EXP-004: Multi-model real LLM evaluation with statistical analysis.

Evaluates B0–B3 baselines across target_1, target_2, target_3 with:
- Independent LLM judge (Gemma-2-9B)
- Bootstrap 95% CI per model × baseline
- Paired McNemar test (B0 vs B3)
- Holm-corrected multiple comparisons
- Cross-model ASR comparison (not pooled)

Usage:
    python experiments/EXP004_MULTI_MODEL/run.py --n-samples 50
    python experiments/EXP004_MULTI_MODEL/run.py --stats-only
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.experiments.env_loader import load_project_env

load_project_env()

from src.adapti_guard.evaluation.multi_model_statistics import (
    analyze_multi_model_results,
    save_statistical_report,
)
from src.adapti_guard.experiments.multi_model_eval import (
    DEFAULT_TARGET_KEYS,
    OPTIONAL_TARGET_KEYS,
    MultiModelConfig,
    run_multi_model_evaluation,
)
from src.adapti_guard.experiments.real_llm_pipeline import DEFAULT_BASELINES, EvaluationBackend


def main() -> int:
    parser = argparse.ArgumentParser(description="EXP-004 Multi-Model Real LLM Evaluation")
    parser.add_argument(
        "--targets",
        nargs="*",
        default=None,
        help=f"Target config keys (default: {DEFAULT_TARGET_KEYS})",
    )
    parser.add_argument(
        "--baselines",
        nargs="*",
        default=None,
        help=f"Baseline keys (default: {DEFAULT_BASELINES})",
    )
    parser.add_argument("--backend", choices=["auto", "openrouter", "ollama"], default="auto")
    parser.add_argument("--split", default="test")
    parser.add_argument("--n-samples", type=int, default=500)
    parser.add_argument("--attack-n", type=int, default=1500)
    parser.add_argument("--benign-n", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--benchmark-dir", default="datasets/benchmark_q1")
    parser.add_argument("--unified-dataset", default=None)
    parser.add_argument("--output", default="experiments/EXP004_MULTI_MODEL")
    parser.add_argument(
        "--include-model-d",
        action="store_true",
        help="Include optional Claude Sonnet 4 target (model_d)",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip baselines whose metrics file already exists",
    )
    parser.add_argument(
        "--frozen-eval",
        action="store_true",
        help="Use datasets/frozen/eval_v1/dataset.jsonl",
    )
    parser.add_argument(
        "--frozen-dataset",
        default="datasets/frozen/eval_v1/dataset.jsonl",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Re-run statistical analysis on existing prediction artifacts",
    )
    args = parser.parse_args()

    output_dir = ROOT / args.output
    target_keys = args.targets or list(DEFAULT_TARGET_KEYS)
    if args.include_model_d and "model_d" not in target_keys:
        target_keys = target_keys + list(OPTIONAL_TARGET_KEYS)
    baselines = args.baselines or ["B0", "B6"]

    if args.stats_only:
        report = analyze_multi_model_results(
            output_dir,
            models=target_keys,
            baselines=baselines,
            experiment_id="EXP-004",
            seed=args.seed,
        )
        path = save_statistical_report(report, output_dir)
        print(json.dumps(report.to_dict(), indent=2))
        print(f"\nSaved: {path}")
        return 0 if report.status != "NO_DATA" else 1

    config = MultiModelConfig(
        output_dir=output_dir,
        target_keys=target_keys,
        backend=EvaluationBackend(args.backend),
        baselines=baselines,
        split=args.split,
        n_samples=args.n_samples,
        attack_n=args.attack_n,
        benign_n=args.benign_n,
        seed=args.seed,
        benchmark_dir=args.benchmark_dir,
        unified_dataset=args.unified_dataset,
        use_unified_dataset=args.unified_dataset is not None,
        skip_existing=args.skip_existing,
        frozen_dataset=args.frozen_dataset,
        use_frozen_eval=args.frozen_eval,
    )

    print("EXP-004: Multi-Model Real LLM Evaluation")
    print(f"  Models:    {target_keys}")
    print(f"  Baselines: {baselines}")
    print(f"  Samples:   {config.n_samples}")
    print(f"  Seed:      {config.seed}")
    print(f"  Backend:   {config.backend.value}")
    print(f"  Mode:      real_llm_judge")

    result = run_multi_model_evaluation(config)
    print(json.dumps(result, indent=2))

    status = result.get("status", "UNKNOWN")
    return 0 if status in ("COMPLETED", "PARTIAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
