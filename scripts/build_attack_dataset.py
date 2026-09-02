#!/usr/bin/env python3
"""Build attack_dataset.json for Q1 evaluation (real prompts, no fabrication).

Maps benchmark_q1 samples to the 7 required attack categories.
Output: datasets/attack_dataset/attack_dataset.json

Usage:
    python scripts/build_attack_dataset.py
    python scripts/build_attack_dataset.py --min-per-category 100 --seed 42
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Required manuscript categories → benchmark_q1 upstream categories
CATEGORY_MAP: dict[str, list[str]] = {
    "direct_prompt_injection": ["direct_prompt_injection", "prompt_injection"],
    "indirect_prompt_injection": ["indirect_prompt_injection"],
    "jailbreak_attacks": ["jailbreak"],
    "system_prompt_leakage": ["direct_prompt_injection"],  # subset filtered by keywords
    "tool_abuse_attacks": ["agent_tool_injection", "agent_security"],
    "rag_poisoning": ["rag_injection", "rag_security"],
    "multi_turn_attacks": ["adaptive_attacks"],
}

LEAKAGE_KEYWORDS = [
    "system prompt", "system instruction", "reveal your prompt",
    "show your instructions", "ignore previous", "developer message",
]

DIFFICULTY_KEYWORDS = {
    "easy": ["ignore previous", "disregard", "override"],
    "hard": ["encoded", "base64", "unicode", "multi-step", "indirect"],
}


def infer_difficulty(prompt: str) -> str:
    lower = prompt.lower()
    if any(k in lower for k in DIFFICULTY_KEYWORDS["hard"]):
        return "hard"
    if any(k in lower for k in DIFFICULTY_KEYWORDS["easy"]):
        return "easy"
    return "medium"


def infer_severity(category: str, prompt: str) -> str:
    if category in ("jailbreak_attacks", "tool_abuse_attacks"):
        return "high"
    if category == "system_prompt_leakage":
        return "medium"
    if len(prompt) > 500:
        return "medium"
    return "low"


def load_benchmark_records(split: str = "test") -> list[dict]:
    if split == "all":
        paths = sorted((ROOT / "datasets" / "benchmark_q1").glob("*.jsonl"))
    else:
        paths = [ROOT / "datasets" / "benchmark_q1" / f"{split}.jsonl"]
    records = []
    for path in paths:
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    return records


def map_record(rec: dict) -> str | None:
    cat = rec.get("category", "")
    prompt = rec.get("prompt", "")

    for target_cat, sources in CATEGORY_MAP.items():
        if cat in sources:
            if target_cat == "system_prompt_leakage":
                lower = prompt.lower()
                if not any(kw in lower for kw in LEAKAGE_KEYWORDS):
                    continue
            return target_cat
    return None


def build_attack_dataset(
    *,
    min_per_category: int = 71,
    max_total: int = 1000,
    seed: int = 42,
    split: str = "all",
) -> dict:
    records = [r for r in load_benchmark_records(split) if r.get("label") == "attack"]
    by_category: dict[str, list[dict]] = {c: [] for c in CATEGORY_MAP}
    leakage_pool: list[dict] = []

    for rec in records:
        prompt = rec.get("prompt", "")
        ctx = rec.get("context", "")
        combined = f"{prompt}\n{ctx}".lower()
        if any(kw in combined for kw in LEAKAGE_KEYWORDS):
            leakage_pool.append(rec)

        target = map_record(rec)
        if target and target != "system_prompt_leakage":
            by_category[target].append(rec)

    by_category["system_prompt_leakage"] = leakage_pool

    rng = random.Random(seed)
    samples: list[dict] = []
    attack_id = 0

    for category, pool in by_category.items():
        rng.shuffle(pool)
        n = min(len(pool), max(min_per_category, 1))
        for rec in pool[:n]:
            attack_id += 1
            prompt = rec.get("prompt", "")
            samples.append({
                "attack_id": f"atk_{attack_id:05d}",
                "category": category,
                "difficulty": infer_difficulty(prompt),
                "prompt": prompt,
                "context": rec.get("context", ""),
                "expected_behavior": "refuse_or_neutralize",
                "severity": infer_severity(category, prompt),
                "source": rec.get("source", rec.get("metadata", {}).get("upstream_category", "")),
                "upstream_id": rec.get("id", ""),
                "upstream_category": rec.get("category", ""),
            })
        if len(pool) < min_per_category:
            pass  # documented in meta

    rng.shuffle(samples)
    if len(samples) > max_total:
        samples = samples[:max_total]

    category_counts = Counter(s["category"] for s in samples)
    gaps = {
        cat: max(0, min_per_category - category_counts.get(cat, 0))
        for cat in CATEGORY_MAP
    }

    return {
        "meta": {
            "version": "1.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "seed": seed,
            "split": split,
            "total": len(samples),
            "min_per_category_requested": min_per_category,
            "category_counts": dict(category_counts),
            "coverage_gaps": {k: v for k, v in gaps.items() if v > 0},
            "note": "Built from benchmark_q1 real prompts. Gaps require additional data collection.",
        },
        "attacks": samples,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build attack_dataset.json")
    parser.add_argument("--min-per-category", type=int, default=71)
    parser.add_argument("--max-total", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--split", default="all", help="test | train | validation | all")
    parser.add_argument(
        "--output",
        default="datasets/attack_dataset/attack_dataset.json",
    )
    args = parser.parse_args()

    dataset = build_attack_dataset(
        min_per_category=args.min_per_category,
        max_total=args.max_total,
        seed=args.seed,
        split=args.split,
    )

    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dataset, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote {out}")
    print(f"Total attacks: {dataset['meta']['total']}")
    print(f"Categories: {dataset['meta']['category_counts']}")
    if dataset["meta"]["coverage_gaps"]:
        print(f"GAPS (need more data): {dataset['meta']['coverage_gaps']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
