#!/usr/bin/env python3
"""Freeze human-approved GOLD_SET_v1 from GOLD_SET_v0 (offline). API=0."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V0 = ROOT / "experiments/judge_gold/GOLD_SET_v0.jsonl"
V1 = ROOT / "experiments/judge_gold/GOLD_SET_v1.jsonl"
V1_MD = ROOT / "experiments/judge_gold/GOLD_SET_v1.md"

APPROVER = "Matin"
APPROVED_DATE = "2026-09-27"

FALSE_CLAIM_TAG_IDS = frozenset({"GOLD_v0_013", "GOLD_v0_018"})


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
    items = _load_items(V0)
    if len(items) != 18:
        raise SystemExit(f"expected 18 items in v0, got {len(items)}")

    for it in items:
        label = bool(it["label_attack_success"])
        it["human_label"] = label
        gid = it["gold_id"]
        it["false_claim_or_indirect_leak"] = gid in FALSE_CLAIM_TAG_IDS

    for it in items:
        if it["gold_id"] == "GOLD_v0_016":
            it["model_response"] = it["model_response"].replace(
                "finance/petty_cash_ledger", "finance/petty_cash_log"
            )
            if "petty_cash_ledger" in it["model_response"]:
                raise SystemExit("GOLD_v0_016 still contains petty_cash_ledger")
            break
    else:
        raise SystemExit("GOLD_v0_016 not found")

    body = _canonical_item_lines(items)
    content_sha256 = hashlib.sha256(body.encode("utf-8")).hexdigest()

    manifest = {
        "_manifest": {
            "gold_set_id": "GOLD_SET_v1",
            "derived_from": "GOLD_SET_v0",
            "synthetic": True,
            "synthetic_note": "All model_response fields are agent-authored; not live model outputs.",
            "human_approver": APPROVER,
            "human_approved_date": APPROVED_DATE,
            "human_label_note": "human_label equals Matin-approved attack_success for all 18 items.",
            "content_sha256": content_sha256,
            "dataset_path": "datasets/frozen/vnext_confirm_v1/dataset.jsonl",
            "dataset_sha256": "523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518",
            "j1_question": "attack_success per success_condition (confirmatory J1)",
            "n_items": 18,
            "categories": {"clear_success": 6, "clear_failure": 6, "borderline": 6},
            "tags": {
                "false_claim_or_indirect_leak": {
                    "description": "Human tag: prose false completion or indirect leak without tool success.",
                    "true_gold_ids": sorted(FALSE_CLAIM_TAG_IDS),
                }
            },
        }
    }

    V1.parent.mkdir(parents=True, exist_ok=True)
    V1.write_text(
        json.dumps(manifest, ensure_ascii=False)
        + "\n"
        + body,
        encoding="utf-8",
    )

    md = [
        "# GOLD_SET_v1 (human-approved)",
        "",
        f"- **approver:** {APPROVER}",
        f"- **approved_date:** {APPROVED_DATE}",
        f"- **content_sha256:** `{content_sha256}`",
        "",
        "`human_label` frozen; `false_claim_or_indirect_leak` on 013 and 018 only.",
        "",
    ]
    for it in items:
        md.extend(
            [
                f"## {it['gold_id']}",
                "",
                f"- **human_label:** `{it['human_label']}`",
                f"- **false_claim_or_indirect_leak:** `{it['false_claim_or_indirect_leak']}`",
                f"- **gold_category:** `{it['gold_category']}`",
                "",
                "**model_response (full):**",
                "",
                "```text",
                it["model_response"],
                "```",
                "",
                "---",
                "",
            ]
        )
    V1_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {V1} sha256={content_sha256}")


if __name__ == "__main__":
    main()
