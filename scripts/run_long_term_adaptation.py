#!/usr/bin/env python3
"""Run EXP-009 long-term adaptation stress test (1000 episodes).

Phased attack evolution per configs/experiments/long_term_adaptation.yaml.

Usage:
    python scripts/run_long_term_adaptation.py --episodes 1000 --mode simulation
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PHASES = [
    ("P1", 1, 200, "static"),
    ("P2", 201, 400, "evolving"),
    ("P3", 401, 600, "static"),
    ("P4", 601, 800, "tool_focused"),
    ("P5", 801, 1000, "adaptive_mixed"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="EXP-009 long-term adaptation")
    parser.add_argument("--episodes", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--mode", choices=["simulation", "real_llm"], default="simulation")
    parser.add_argument("--output", default="experiments/EXP009_LONG_TERM")
    args = parser.parse_args()

    out = ROOT / args.output
    out.mkdir(parents=True, exist_ok=True)

    if args.mode == "real_llm":
        status = {
            "status": "BLOCKED",
            "reason": "Requires valid API + attack_dataset + phased sampler",
            "config": "configs/experiments/long_term_adaptation.yaml",
        }
        (out / "status.json").write_text(json.dumps(status, indent=2))
        print(json.dumps(status, indent=2))
        return 1

    from src.adapti_guard.experiments.harmonized_runner import (
        HarmonizedRunner,
        PolicyMode,
        summarize_method,
    )

    stream_path = ROOT / "results" / "common_attack_stream.json"
    if not stream_path.exists():
        status = {"status": "BLOCKED", "reason": f"missing {stream_path}"}
        (out / "status.json").write_text(json.dumps(status, indent=2))
        print(json.dumps(status, indent=2))
        return 1

    runner = HarmonizedRunner.from_stream_path(
        stream_path, episodes=min(args.episodes, 200),
    )
    result = summarize_method(runner.run_method(PolicyMode.FULL_ADAPTIVE))

    summary = {
        "experiment_id": "EXP-009",
        "mode": "LEGACY_SIMULATION_ONLY",
        "episodes_requested": args.episodes,
        "episodes_run": min(args.episodes, 200),
        "phases": PHASES,
        "metrics": result,
        "figures_required": [
            "figures/defense_level_over_time.png",
            "figures/asr_over_time.png",
            "figures/reward_curve.png",
        ],
        "warning": "Smoke run only — full 1000-episode real-LLM run pending API",
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
