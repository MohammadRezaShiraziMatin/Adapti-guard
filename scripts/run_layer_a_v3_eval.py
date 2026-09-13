#!/usr/bin/env python3
"""CLI wrapper: REAL_LLM_EVAL against the frozen Layer A v3 TEST split.

Uses datasets/frozen/layer_a_v3_test_split_view/ (byte-identical to test_split.jsonl)
so attack_n=40 / benign_n=40 loads the frozen TEST split without resampling train/dev.

Defaults: OpenRouter, target_2, judge_fallback, cache off, seed 42.
"""

from __future__ import annotations

import argparse
import os
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK_VIEW = "datasets/frozen/layer_a_v3_test_split_view"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run REAL_LLM_EVAL on the frozen Layer A v3 TEST split."
    )
    parser.add_argument("--backend", default="openrouter")
    parser.add_argument("--target", default="target_2")
    parser.add_argument("--judge", default="judge_fallback")
    parser.add_argument(
        "--baselines",
        nargs="*",
        default=["B0", "B3", "L3", "ORACLE_BLOCK"],
    )
    parser.add_argument("--attack-n", type=int, default=40)
    parser.add_argument("--benign-n", type=int, default=40)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--split", default="test")
    parser.add_argument("--benchmark-dir", default=PACK_VIEW)
    parser.add_argument(
        "--output",
        default="experiments/real_llm_eval/LAYER_A_V3",
    )
    parser.add_argument("--experiment-id", default="LAYER-A-V3")
    parser.add_argument("--require-key", action="store_true")
    args, extra = parser.parse_known_args()

    if args.require_key and not os.environ.get("OPENROUTER_API_KEY"):
        print("OPENROUTER_API_KEY=MISSING — not running live eval.", file=sys.stderr)
        return 2

    argv = [
        "run_real_eval.py",
        "--backend",
        args.backend,
        "--target",
        args.target,
        "--judge",
        args.judge,
        "--split",
        args.split,
        "--benchmark-dir",
        args.benchmark_dir,
        "--attack-n",
        str(args.attack_n),
        "--benign-n",
        str(args.benign_n),
        "--seed",
        str(args.seed),
        "--output",
        args.output,
        "--experiment-id",
        args.experiment_id,
        "--baselines",
        *args.baselines,
        *extra,
    ]
    sys.argv = argv
    sys.path.insert(0, str(ROOT))
    try:
        runpy.run_path(
            str(ROOT / "experiments" / "REAL_LLM_EVAL" / "run.py"),
            run_name="__main__",
        )
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
