#!/usr/bin/env python3
"""Run EXP-006 ablation study (A–F variants).

Uses harmonized_runner PolicyMode for simulation; real-LLM path via EXP-004
when evaluation_mode=real_llm_judge and API is available.

Usage:
    python scripts/run_ablation_study.py --mode simulation --episodes 100
    python scripts/run_ablation_study.py --mode real_llm --n-samples 50
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.experiments.harmonized_runner import (
    HarmonizedRunner,
    PolicyMode,
    summarize_method,
)


VARIANT_MAP = {
    "A_full": PolicyMode.FULL_ADAPTIVE,
    "B_no_risk_engine": PolicyMode.FULL_ADAPTIVE,  # TODO: wire risk bypass
    "C_no_cost_gate": PolicyMode.NO_COST_GATE,
    "D_no_feedback": PolicyMode.FIXED_L2,  # proxy until feedback disable hook
    "E_no_policy_adaptation": PolicyMode.FIXED_L2,
    "F_no_escalation": PolicyMode.DE_ESCALATION_ONLY,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="EXP-006 ablation study")
    parser.add_argument("--mode", choices=["simulation", "real_llm"], default="simulation")
    parser.add_argument("--episodes", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="experiments/EXP006_ABLATION")
    args = parser.parse_args()

    out = ROOT / args.output
    out.mkdir(parents=True, exist_ok=True)

    if args.mode == "real_llm":
        status = {
            "status": "BLOCKED",
            "reason": "Real-LLM ablation requires EXP-004 pipeline + ablation hooks in defense_baselines.py",
            "next": "python experiments/EXP004_MULTI_MODEL/run.py --ablations A_full C_no_cost_gate",
        }
        (out / "status.json").write_text(json.dumps(status, indent=2))
        print(json.dumps(status, indent=2))
        return 1

    stream_path = ROOT / "results" / "common_attack_stream.json"
    if not stream_path.exists():
        status = {"status": "BLOCKED", "reason": f"missing {stream_path}"}
        (out / "status.json").write_text(json.dumps(status, indent=2))
        print(json.dumps(status, indent=2))
        return 1

    runner = HarmonizedRunner.from_stream_path(stream_path, episodes=args.episodes)
    results = {}
    for variant_id, policy_mode in VARIANT_MAP.items():
        run_result = runner.run_method(policy_mode)
        metrics = summarize_method(run_result)
        results[variant_id] = metrics
        variant_dir = out / variant_id
        variant_dir.mkdir(exist_ok=True)
        (variant_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))

    summary = {
        "experiment_id": "EXP-006",
        "mode": "LEGACY_SIMULATION_ONLY",
        "seed": args.seed,
        "episodes": args.episodes,
        "variants": {
            k: {
                "ASR": v.get("asr"),
                "utility": v.get("utility"),
                "defense_rate": v.get("defense_rate"),
                "reward": v.get("mean_reward"),
            }
            for k, v in results.items()
        },
        "warning": "Simulation only — not valid for publication ASR claims",
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
