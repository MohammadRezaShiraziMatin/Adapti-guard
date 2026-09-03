#!/usr/bin/env python3
"""EXP-002: Real LLM evaluation with independent judge."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.experiments.env_loader import load_project_env, validate_openrouter_key

load_project_env()

from src.adapti_guard.experiments.real_llm_runner import run_real_llm_evaluation


def main() -> int:
    parser = argparse.ArgumentParser(description="EXP-002 Real LLM Evaluation")
    parser.add_argument("--target", default="target_3", help="Model config key")
    parser.add_argument("--split", default="test")
    parser.add_argument("--n-samples", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="experiments/EXP002_REAL_LLM")
    args = parser.parse_args()

    output_dir = ROOT / args.output / args.target
    result = run_real_llm_evaluation(
        experiment_id="EXP-002",
        output_dir=output_dir,
        target_config_key=args.target,
        split=args.split,
        n_samples=args.n_samples,
        seed=args.seed,
    )
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
