#!/usr/bin/env python3
"""EXP-008: Adaptive attack evaluation — defense vs evolving attacker."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.adapti_guard.attacker.adaptive_attacker import AdaptiveAttacker
from src.adapti_guard.detector.prompt_injection_detector import PromptInjectionDetector
from src.adapti_guard.defense.action_layer import DefenseActionLayer
from src.adapti_guard.policy.policy_engine import DefensePolicyEngine
from src.adapti_guard.risk.risk_engine import RiskEngine


def run_adaptive_eval(n_rounds: int, n_attacks: int, seed: int) -> dict:
    attacker = AdaptiveAttacker()
    detector = PromptInjectionDetector()
    risk_engine = RiskEngine()
    policy_engine = DefensePolicyEngine()
    action_layer = DefenseActionLayer()

    round_results = []
    defense_level = 1

    for round_num in range(1, n_rounds + 1):
        round_blocked = 0
        round_evolved = 0
        round_success = 0
        prev_family = attacker.state.current_family

        for _ in range(n_attacks):
            attempt = attacker.generate()
            if attempt.family != prev_family:
                round_evolved += 1
            prev_family = attempt.family

            detection = detector.detect(attempt.payload)
            risk = risk_engine.assess(detection)
            decision = policy_engine.decide(
                risk=risk, tool_sensitive=False, defense_level=defense_level
            )
            defense = action_layer.execute(decision.action, attempt.payload)
            blocked = not defense.allowed
            attacker.record(attempt)
            attacker.observe(successful=not blocked)

            if blocked:
                round_blocked += 1
            else:
                round_success += 1

        round_results.append({
            "round": round_num,
            "attacks": n_attacks,
            "blocked": round_blocked,
            "evolved": round_evolved,
            "passed_defense": round_success,
            "block_rate": round(round_blocked / n_attacks, 4) if n_attacks else 0,
            "final_family": attacker.state.current_family,
        })

    return {
        "status": "COMPLETED",
        "experiment_id": "EXP-008",
        "n_rounds": n_rounds,
        "n_attacks_per_round": n_attacks,
        "seed": seed,
        "evaluation_mode": "LEGACY_SIMULATION_ONLY",
        "note": "Measures detector block rate on evolved attacks. Real LLM ASR requires EXP-002 pipeline.",
        "rounds": round_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="EXP-008 Adaptive Attack Evaluation")
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--attacks", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="experiments/EXP008_ADAPTIVE_ATTACK")
    args = parser.parse_args()

    output_dir = ROOT / args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    result = run_adaptive_eval(args.rounds, args.attacks, args.seed)
    (output_dir / "metrics.json").write_text(json.dumps(result, indent=2))
    (output_dir / "logs.json").write_text(json.dumps(result.get("rounds", []), indent=2))
    print(json.dumps({"status": result.get("status")}, indent=2))
    return 0 if result.get("status") == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
