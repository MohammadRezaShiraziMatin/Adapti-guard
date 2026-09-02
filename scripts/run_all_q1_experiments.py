#!/usr/bin/env python3
"""Run all Q1 experiments in order."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], desc: str) -> int:
    print(f"\n{'='*60}\n{desc}\n{'='*60}")
    print(" ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-samples", type=int, default=500)
    parser.add_argument("--baseline-samples", type=int, default=100)
    parser.add_argument("--skip-llm", action="store_true")
    args = parser.parse_args()

    py = sys.executable

    run([py, "scripts/build_benchmark_q1.py"], "Phase 2: Build benchmark_q1")

    if not args.skip_llm:
        for target in ("target_3", "target_1", "target_2"):
            rc = run(
                [py, "experiments/EXP002_REAL_LLM/run.py",
                 "--target", target, "--n-samples", str(args.n_samples)],
                f"Phase 3: EXP-002 Real LLM ({target})",
            )
            if rc != 0:
                print(f"WARN: EXP-002 {target} exited {rc}")

        run(
            [py, "experiments/EXP003_BASELINES/run.py",
             "--n-samples", str(args.baseline_samples)],
            "Phase 4: EXP-003 Baselines",
        )

    run([py, "experiments/EXP005_ADAPTATION/run.py"], "Phase 5: Adaptation ablation")
    run([py, "experiments/EXP008_ADAPTIVE_ATTACK/run.py"], "Phase 6: Adaptive attack")
    run([py, "scripts/run_cost_analysis.py"], "Phase 8: Cost analysis")

    print("\nDone. See docs/Q1_FINAL_READINESS_REPORT.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
