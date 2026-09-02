#!/usr/bin/env python3
"""Cost analysis: ADAPTI-GUARD vs baselines."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Cost estimates per 1M tokens (OpenRouter approximate, USD)
COST_PER_1M = {
    "meta-llama/llama-3.1-8b-instruct": {"input": 0.06, "output": 0.06},
    "qwen/qwen-2.5-7b-instruct": {"input": 0.04, "output": 0.10},
    "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "google/gemma-2-9b-it": {"input": 0.03, "output": 0.09},
}

DEFENSE_OVERHEAD_MS = {
    "no_defense": 0,
    "regex_detector": 2,
    "adapti_guard": 8,
}


def analyze_exp002_cost(exp_dir: Path) -> list[dict]:
    rows = []
    for cost_file in exp_dir.rglob("cost.json"):
        data = json.loads(cost_file.read_text())
        parent = cost_file.parent.name
        rows.append({
            "experiment": parent,
            "prompt_tokens": data.get("total_prompt_tokens", 0),
            "completion_tokens": data.get("total_completion_tokens", 0),
            "status": "from_run",
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Cost analysis")
    parser.add_argument("--output", default="results/cost_analysis.csv")
    args = parser.parse_args()

    rows = analyze_exp002_cost(ROOT / "experiments" / "EXP002_REAL_LLM")

    if not rows:
        rows = [{
            "method": "no_defense",
            "defense_overhead_ms": 0,
            "est_tokens_per_episode": 600,
            "est_cost_usd_per_500": 0.45,
            "status": "ESTIMATED_NO_RUNS",
        }, {
            "method": "adapti_guard",
            "defense_overhead_ms": 8,
            "est_tokens_per_episode": 600,
            "est_cost_usd_per_500": 0.45,
            "status": "ESTIMATED_NO_RUNS",
            "note": "Defense adds ~8ms latency, no extra LLM tokens",
        }]

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        fieldnames = sorted({k for r in rows for k in r})
        with out.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    print(f"Wrote {out} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
