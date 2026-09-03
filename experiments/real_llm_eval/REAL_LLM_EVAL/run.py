#!/usr/bin/env python3
"""REAL-LLM-EVAL: Publication-grade evaluation with target LLM + independent judge.

Pipeline:
    Attack/Benign Prompt → Defense (B0–B3) → Target LLM → LLM Judge → Metrics

ASR is derived ONLY from the independent judge — never from regex/simulation.
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

from src.adapti_guard.experiments.real_llm_pipeline import (
    DEFAULT_BASELINES,
    EvaluationBackend,
    PipelineConfig,
    run_real_llm_pipeline,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ADAPTI-GUARD Real LLM Evaluation (target + judge)"
    )
    parser.add_argument("--target", default="target_2", help="Target model config key")
    parser.add_argument("--judge", default="judge", help="Judge model config key")
    parser.add_argument(
        "--backend",
        choices=["auto", "openrouter", "ollama", "groq", "gemini"],
        default="auto",
    )
    parser.add_argument("--split", default="test")
    parser.add_argument("--n-samples", type=int, default=None, help="Cap samples (attack-only smoke; first N lines)")
    parser.add_argument(
        "--attack-n",
        type=int,
        default=None,
        help="Seeded attack sample size (enables mixed benchmark sampling)",
    )
    parser.add_argument(
        "--benign-n",
        type=int,
        default=None,
        help="Seeded benign sample size (required for utility/FPR)",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--benchmark-dir", default="datasets/benchmark_q1")
    parser.add_argument(
        "--unified-dataset",
        default=None,
        help="Path to unified_security_dataset.jsonl (enables unified mode)",
    )
    parser.add_argument(
        "--baselines",
        nargs="*",
        default=None,
        help=f"Baseline keys (default: {DEFAULT_BASELINES})",
    )
    parser.add_argument("--output", default="experiments/REAL_LLM_EVAL")
    parser.add_argument("--experiment-id", default="REAL-LLM-EVAL")
    args = parser.parse_args()

    use_unified = args.unified_dataset is not None
    config = PipelineConfig(
        experiment_id=args.experiment_id,
        output_dir=ROOT / args.output,
        target_config_key=args.target,
        judge_config_key=args.judge,
        backend=EvaluationBackend(args.backend),
        baselines=args.baselines or list(DEFAULT_BASELINES),
        split=args.split,
        n_samples=args.n_samples,
        attack_n=args.attack_n,
        benign_n=args.benign_n,
        seed=args.seed,
        benchmark_dir=args.benchmark_dir,
        unified_dataset=args.unified_dataset,
        use_unified_dataset=use_unified,
    )

    print("ADAPTI-GUARD Real LLM Evaluation")
    print(f"  Backend: {config.backend.value}")
    print(f"  Target:  {config.target_config_key}")
    print(f"  Judge:   {config.judge_config_key}")
    print(f"  Mode:    real_llm_judge (no simulation ASR)")
    if use_unified:
        print(f"  Dataset: unified ({config.attack_n}+{config.benign_n}, seed={config.seed})")
    elif config.attack_n is not None or config.benign_n is not None:
        print(
            f"  Dataset: {config.benchmark_dir}/{config.split} "
            f"mixed attack_n={config.attack_n} benign_n={config.benign_n} seed={config.seed}"
        )
    else:
        print(f"  Dataset: {config.benchmark_dir}/{config.split}")
    if config.n_samples:
        print(f"  Samples: {config.n_samples} (capped / attack-only first-N mode)")
    if config.target_config_key == config.judge_config_key:
        print(
            "  WARNING: target and judge share the same config key — "
            "judge independence is weakened for publication claims."
        )

    result = run_real_llm_pipeline(config)
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
