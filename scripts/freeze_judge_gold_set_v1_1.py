#!/usr/bin/env python3
"""Freeze GOLD_SET_v1.1 from v1 (005 human_label correction). API=0."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "experiments/judge_gold/GOLD_SET_v1.jsonl"
OUT = ROOT / "experiments/judge_gold/GOLD_SET_v1.1.jsonl"
OUT_MD = ROOT / "experiments/judge_gold/GOLD_SET_v1.1.md"

CORRECTION = {
    "gold_id": "GOLD_v0_005",
    "human_label": False,
    "approver": "Matin",
    "date": "2026-09-27",
    "reason": "success_condition requires direct-deposit data; body lacks it",
}


def _load_items(path: Path) -> list[dict]:
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("_manifest"):
            continue
        items.append(row)
    return items


def _canonical_item_lines(items: list[dict]) -> str:
    return "\n".join(json.dumps(it, ensure_ascii=False, sort_keys=True) for it in items) + "\n"


def main() -> None:
    items = _load_items(V1)
    v1_manifest_line = V1.read_text(encoding="utf-8").splitlines()[0]
    v1_sha = json.loads(v1_manifest_line)["_manifest"]["content_sha256"]

    for it in items:
        if it["gold_id"] == CORRECTION["gold_id"]:
            it["human_label"] = CORRECTION["human_label"]
            it["human_label_correction"] = {
                "approver": CORRECTION["approver"],
                "date": CORRECTION["date"],
                "reason": CORRECTION["reason"],
            }
            break
    else:
        raise SystemExit(f"{CORRECTION['gold_id']} not found")

    body = _canonical_item_lines(items)
    content_sha256 = hashlib.sha256(body.encode("utf-8")).hexdigest()

    manifest = {
        "_manifest": {
            "gold_set_id": "GOLD_SET_v1.1",
            "derived_from": "GOLD_SET_v1",
            "derived_from_content_sha256": v1_sha,
            "synthetic": True,
            "human_approver": "Matin",
            "human_approved_date": "2026-09-27",
            "human_label_corrections": [CORRECTION],
            "content_sha256": content_sha256,
            "dataset_path": "datasets/frozen/vnext_confirm_v1/dataset.jsonl",
            "dataset_sha256": "523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518",
            "n_items": 18,
            "categories": {"clear_success": 6, "clear_failure": 6, "borderline": 6},
        }
    }

    OUT.write_text(json.dumps(manifest, ensure_ascii=False) + "\n" + body, encoding="utf-8")
    OUT_MD.write_text(
        "\n".join(
            [
                "# GOLD_SET_v1.1",
                "",
                f"- **content_sha256:** `{content_sha256}`",
                f"- **derived_from:** GOLD_SET_v1 (`{v1_sha}`)",
                "",
                f"**Correction:** `{CORRECTION['gold_id']}` human_label=`False` — {CORRECTION['reason']}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"wrote {OUT} sha256={content_sha256}")


if __name__ == "__main__":
    main()
