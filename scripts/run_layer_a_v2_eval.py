#!/usr/bin/env python3
"""CLI wrapper: REAL_LLM_EVAL against datasets/frozen/layer_a_v2.

Defaults match the Layer A scientific contract:
  --backend openrouter --target target_2 --judge judge_fallback
  cache.enabled=false (configs/models.yaml)
  multi_model.judge=judge_fallback

Examples:

  # B0 probe (20+20, seed 42) — only when OPENROUTER_API_KEY is set
  python3 scripts/run_layer_a_v2_eval.py \\
    --baselines B0 --attack-n 20 --benign-n 20 --seed 42 \\
    --output experiments/real_llm_eval/LAYER_A_V2_B0_PROBE/<timestamp> \\
    --experiment-id LAYER-A-V2-B0-PROBE

  # Full pack (40+40)
  python3 scripts/run_layer_a_v2_eval.py \\
    --baselines B0 --attack-n 40 --benign-n 40 --seed 42

Do NOT run full B0+B3 Layer A until a B0 probe ASR is ≥ 0.15 (or report blocker).
Do not treat a low ASR on the old benchmark_q1 mix as a defense win.
"""

from __future__ import annotations

import argparse
import os
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "datasets/frozen/layer_a_v2"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run REAL_LLM_EVAL on the Layer A v2 attack pack."
    )
    parser.add_argument("--backend", default="openrouter")
    parser.add_argument("--target", default="target_2")
    parser.add_argument("--judge", default="judge_fallback")
    parser.add_argument("--baselines", nargs="*", default=["B0"])
    parser.add_argument("--attack-n", type=int, default=20)
    parser.add_argument("--benign-n", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--split", default="test")
    parser.add_argument("--benchmark-dir", default=PACK)
    parser.add_argument(
        "--output",
        default="experiments/real_llm_eval/LAYER_A_V2",
    )
    parser.add_argument("--experiment-id", default="LAYER-A-V2")
    parser.add_argument(
        "--require-key",
        action="store_true",
        help="Exit 2 if OPENROUTER_API_KEY is missing (probe mode).",
    )
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
        runpy.run_path(str(ROOT / "experiments" / "REAL_LLM_EVAL" / "run.py"), run_name="__main__")
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
