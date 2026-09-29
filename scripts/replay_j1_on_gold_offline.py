#!/usr/bin/env python3
"""Replay frozen J1 per-item labels against a gold set (report-only). API=0."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from run_judge_gold_eval import evaluate_predictions, load_gold_items, official_label  # noqa: E402


def load_pack_preds(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--gold", type=Path, required=True)
    p.add_argument("--pack-per-item", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    items = load_gold_items(args.gold)
    pack = load_pack_preds(args.pack_per_item)
    by_id = {r["gold_id"]: r for r in pack}
    preds = []
    for it in items:
        gid = it["gold_id"]
        if gid not in by_id:
            raise SystemExit(f"missing pack row for {gid}")
        row = by_id[gid]
        preds.append(
            {
                "attack_success": row["j1_attack_success"],
                "parse_error": None if row.get("j1_parse_ok") else row.get("j1_parse_error"),
                "reason": row.get("j1_reason"),
                "raw_text": row.get("j1_raw_text"),
            }
        )

    report = evaluate_predictions(items, preds)
    report["gold_set"] = str(args.gold)
    report["replay_pack"] = str(args.pack_per_item)
    report["note"] = "Report-only replay; no API calls."

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"accuracy": report["accuracy"], "n_scored": report["n_scored"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
