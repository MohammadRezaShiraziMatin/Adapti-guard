#!/usr/bin/env python3
"""Regenerate Phase 7 simulation artifacts required by sensitivity validation.

Real ExperimentRunner / HarmonizedRunner execution — not fabricated metrics.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.experiments.experiment_runner import ExperimentRunner
from src.adapti_guard.experiments.harmonized_runner import (
    HarmonizedRunner,
    PolicyMode,
    summarize_method,
)
from src.adapti_guard.evaluation.metrics import compute_metrics


OUT = ROOT / "results" / "phase7"
STREAM = ROOT / "results" / "common_attack_stream.json"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    stream = json.loads(STREAM.read_text(encoding="utf-8"))
    assert len(stream) >= 100

    # Adaptive 100 — attack-only frozen stream (Phase 7 contract)
    runner = ExperimentRunner(attack_stream=stream[:100], episode_schedule=None)
    results = runner.run(episodes=100)
    adaptive = [asdict(r) for r in results]
    (OUT / "adaptive_100.json").write_text(
        json.dumps(adaptive, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # Fixed baselines — attack-only schedule (all False = all attacks)
    attack_only = [False] * 100
    hr = HarmonizedRunner(
        attack_stream=stream[:100],
        episode_schedule=attack_only,
    )
    baselines = []
    for mode in (
        PolicyMode.FIXED_L0,
        PolicyMode.FIXED_L1,
        PolicyMode.FIXED_L2,
        PolicyMode.FIXED_L3,
    ):
        method = hr.run_method(mode)
        summary = summarize_method(method)
        baselines.append(
            {
                "method": mode.value,
                "episodes": 100,
                "attack_episodes": int(summary["attack_episodes"]),
                "legitimate_episodes": int(summary["legitimate_episodes"]),
                "asr": summary["asr"],
                "defense_rate": summary["defense_rate"],
                "utility": summary.get("utility"),
                "defense_cost": summary["defense_cost"],
                "security_score": summary.get("security_score"),
                "reward": summary.get("reward"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "evaluation_mode": "LEGACY_SIMULATION_ONLY",
            }
        )
    (OUT / "fixed_baselines_100.json").write_text(
        json.dumps(baselines, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    metrics = compute_metrics(adaptive)
    metrics["evaluation_mode"] = "LEGACY_SIMULATION_ONLY"
    metrics["artifact"] = "adaptive_100.json"
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    (OUT / "config.json").write_text(
        json.dumps(
            {
                "episodes": 100,
                "stream": str(STREAM),
                "schedule": "attack_only",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        )
        + "\n"
    )
    (OUT / "logs.txt").write_text(
        f"{datetime.now(timezone.utc).isoformat()} regenerated phase7 adaptive+baselines\n"
    )
    print("PHASE7_OK", OUT)
    print("adaptive_n", len(adaptive), "baselines", len(baselines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
