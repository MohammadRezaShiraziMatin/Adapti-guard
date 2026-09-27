#!/usr/bin/env python3
"""Freeze Matin-approved human labels on GOLD_SET_v2 (offline). API=0."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "experiments/judge_gold/GOLD_SET_v2.jsonl"
EXPECTED_SHA = "b397431c3e131cb79c260d8a6c0c3b024db27a6395a93874413fcbc6322cb82d"
APPROVER = "Matin"
APPROVED_DATE = "2026-09-27"


def main() -> None:
    lines = V2.read_text(encoding="utf-8").splitlines()
    manifest = json.loads(lines[0])["_manifest"]
    if manifest.get("content_sha256") != EXPECTED_SHA:
        raise SystemExit(
            f"expected content_sha256 {EXPECTED_SHA}, got {manifest.get('content_sha256')}"
        )
    items = []
    for line in lines[1:]:
        it = json.loads(line)
        it["human_label"] = bool(it["label_attack_success"])
        items.append(it)
    body = "\n".join(json.dumps(it, ensure_ascii=False, sort_keys=True) for it in items) + "\n"
    new_sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
    manifest.update(
        {
            "human_approver": APPROVER,
            "human_approved_date": APPROVED_DATE,
            "human_label_note": "human_label frozen equal to label_attack_success for all 40 items.",
            "labels_frozen_from_content_sha256": EXPECTED_SHA,
            "content_sha256": new_sha,
        }
    )
    V2.write_text(json.dumps({"_manifest": manifest}, ensure_ascii=False) + "\n" + body, encoding="utf-8")
    print(f"frozen {V2} content_sha256={new_sha}")


if __name__ == "__main__":
    main()
