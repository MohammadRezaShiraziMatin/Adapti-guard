#!/usr/bin/env python3
"""Offline validator for datasets/candidates/p1_mechanism_v1 (no LLM)."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "datasets" / "candidates" / "p1_mechanism_v1"

REQUIRED_META = (
    "family",
    "family_name",
    "mechanism",
    "surface_form",
    "security_objective",
    "context_source",
    "turn_count",
    "tool_dependency",
    "external_content_dependency",
    "expected_harm",
    "difficulty",
    "provenance",
    "generation_method",
    "version",
    "pack_id",
    "seed",
    "content_sha256",
    "estimand_tags",
    "sequential_representation",
)

IN_SCOPE = {
    "A1",
    "A2",
    "A3",
    "B1",
    "B2",
    "B3",
    "B4",
    "B5",
    "C1",
    "C2",
    "C3",
    "D1",
    "D2",
    "D3",
    "D4",
    "E1",
    "E2",
    "E3",
    "F1",
    "F2",
    "F3",
    "F4",
}


def load_rows() -> list[dict]:
    return [
        json.loads(line)
        for line in (PACK / "dataset.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def validate(rows: list[dict]) -> list[str]:
    errors: list[str] = []
    if len(rows) != 96:
        errors.append(f"expected 96 rows, got {len(rows)}")

    attacks = [r for r in rows if r.get("label") == "attack"]
    benigns = [r for r in rows if r.get("label") == "benign"]
    if len(attacks) != 44:
        errors.append(f"expected 44 attacks, got {len(attacks)}")
    if len(benigns) != 52:
        errors.append(f"expected 52 benigns, got {len(benigns)}")

    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)):
        errors.append("duplicate ids")

    fam_counts = Counter(r["metadata"]["family"] for r in attacks)
    for fam in sorted(IN_SCOPE):
        if fam_counts.get(fam, 0) != 2:
            errors.append(f"family {fam} attack count {fam_counts.get(fam, 0)} != 2")
    if any(r["metadata"]["family"] == "C4" for r in rows):
        errors.append("C4 must have zero rows")

    by_id = {r["id"]: r for r in rows}
    for atk in attacks:
        twin = atk["metadata"].get("benign_twin")
        if not twin or twin not in by_id:
            errors.append(f"{atk['id']} missing benign_twin")
            continue
        ben = by_id[twin]
        if ben["label"] != "benign":
            errors.append(f"{twin} is not benign")
        if ben["metadata"].get("attack_twin") != atk["id"]:
            errors.append(f"{twin} attack_twin mismatch")

    hard = [r for r in benigns if r["metadata"].get("hard_negative")]
    if len(hard) != 8:
        errors.append(f"expected 8 hard negatives, got {len(hard)}")

    for r in rows:
        meta = r.get("metadata") or {}
        for key in REQUIRED_META:
            if key not in meta:
                errors.append(f"{r.get('id')} missing metadata.{key}")
        if r["label"] == "attack" and not r.get("success_condition"):
            errors.append(f"{r['id']} missing success_condition")
        # Role-play DAN surface banned as primary taxonomy (P0)
        blob = f"{r.get('prompt','')} {r.get('context','')}".lower()
        if "you are now dan" in blob or "do anything now" in blob:
            errors.append(f"{r['id']} contains banned DAN surface")

        seq = meta.get("sequential_representation")
        if meta.get("family") in {"C1", "C2", "C3"} and r["label"] == "attack":
            if seq != "frozen_context":
                errors.append(f"{r['id']} sequential family must be frozen_context")

    # Exact prompt+context uniqueness among attacks
    seen = set()
    for r in attacks:
        key = (r["prompt"], r.get("context") or "")
        if key in seen:
            errors.append(f"duplicate attack prompt/context: {r['id']}")
        seen.add(key)

    listed = (PACK / "hashes.sha256").read_text(encoding="utf-8").strip().split()
    file_digest = hashlib.sha256((PACK / "dataset.jsonl").read_bytes()).hexdigest()
    if listed and listed[0] != file_digest:
        errors.append("hashes.sha256 mismatch vs dataset.jsonl")
    man = json.loads((PACK / "manifest.json").read_text(encoding="utf-8"))
    if man.get("dataset_sha256") != file_digest:
        errors.append("manifest dataset_sha256 mismatch")
    if man.get("live_evaluated") is not False:
        errors.append("manifest.live_evaluated must be false")
    if man.get("status") != "CANDIDATE":
        errors.append("manifest.status must be CANDIDATE")

    return errors


def main() -> int:
    rows = load_rows()
    errors = validate(rows)
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("OK", len(rows), "rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
