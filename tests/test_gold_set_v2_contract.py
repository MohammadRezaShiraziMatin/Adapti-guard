"""GOLD_SET_v2 offline contract tests."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "experiments/judge_gold/GOLD_SET_v1.jsonl"
V2 = ROOT / "experiments/judge_gold/GOLD_SET_v2.jsonl"


def _items(path: Path) -> list[dict]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("_manifest"):
            continue
        out.append(row)
    return out


def test_v2_size_and_categories():
    items = _items(V2)
    assert len(items) == 40
    cats = {}
    for it in items:
        cats[it["gold_category"]] = cats.get(it["gold_category"], 0) + 1
    assert cats == {"clear_success": 12, "clear_failure": 12, "borderline": 16}


def test_v2_human_labels_null_and_no_v1_attack_overlap():
    v1_ids = {json.loads(l)["attack_id"] for l in V1.read_text().splitlines()[1:]}
    items = _items(V2)
    assert all(it.get("human_label") is None for it in items)
    v2_ids = {it["attack_id"] for it in items}
    assert len(v2_ids) == 40
    assert v2_ids.isdisjoint(v1_ids)


def test_v2_borderline_balanced():
    b = [it for it in _items(V2) if it["gold_category"] == "borderline"]
    t = sum(1 for it in b if it["label_attack_success"])
    assert t == 8
    assert len(b) - t == 8
