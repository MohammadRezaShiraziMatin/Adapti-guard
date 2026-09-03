#!/usr/bin/env python3
"""EXP-005: Adaptation ablation — prove adaptive contribution."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.evaluation.statistics import bootstrap_ci
from src.adapti_guard.experiments.harmonized_runner import (
    HarmonizedRunner,
    PolicyMode,
    summarize_method,
)


MODES = {
    "A_no_adaptation": PolicyMode.FIXED_L1,
    "B_rule_based": PolicyMode.ESCALATION_ONLY,
    "C_bayesian_risk": PolicyMode.DE_ESCALATION_ONLY,
    "D_full_adapti_guard": PolicyMode.FULL_ADAPTIVE,
}


def run_ablation(episodes: int, seed: int) -> dict:
    stream_path = ROOT / "results" / "common_attack_stream.json"
    if not stream_path.exists():
        return {"status": "BLOCKED", "reason": f"missing {stream_path}"}

    runner = HarmonizedRunner.from_stream_path(stream_path, episodes=episodes)
    results = {}
    for label, mode in MODES.items():
        run_result = runner.run_method(mode)
        metrics = summarize_method(run_result)
        results[label] = {
            "mode": mode.value,
            "asr": metrics.get("asr"),
            "defense_rate": metrics.get("defense_rate"),
            "utility": metrics.get("utility"),
            "mean_cost": metrics.get("mean_cost"),
            "f1": metrics.get("f1"),
        }
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="EXP-005 Adaptation Ablation")
    parser.add_argument("--episodes", type=int, default=100)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--output", default="experiments/EXP005_ADAPTATION")
    args = parser.parse_args()

    output_dir = ROOT / args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    all_seeds: dict[str, list] = {k: [] for k in MODES}
    seed_results = []

    for seed in range(1, args.seeds + 1):
        result = run_ablation(args.episodes, seed)
        if result.get("status") == "BLOCKED":
            blocked = {"status": "BLOCKED", "reason": result["reason"]}
            (output_dir / "metrics.json").write_text(json.dumps(blocked, indent=2))
            print(json.dumps(blocked, indent=2))
            return 1
        seed_results.append({"seed": seed, "results": result})
        for label, metrics in result.items():
            all_seeds[label].append(metrics.get("asr", 0))

    summary = {}
    for label, asrs in all_seeds.items():
        if asrs:
            mean, lo, hi = bootstrap_ci(asrs, seed=42)
            summary[label] = {
                "asr_mean": round(mean, 4),
                "asr_std": round(float(np.std(asrs)), 4),
                "asr_ci_95": [round(lo, 4), round(hi, 4)],
                "seeds": asrs,
            }

    output = {
        "status": "COMPLETED",
        "experiment_id": "EXP-005",
        "n_seeds": args.seeds,
        "episodes_per_seed": args.episodes,
        "note": "Uses harmonized_runner simulation path (attack_outcome heuristics). Real LLM ablation requires EXP-002 infrastructure.",
        "evaluation_mode": "LEGACY_SIMULATION_ONLY",
        "per_seed": seed_results,
        "summary": summary,
    }
    (output_dir / "metrics.json").write_text(json.dumps(output, indent=2))
    (output_dir / "ablation_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({"status": "COMPLETED", "summary": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
