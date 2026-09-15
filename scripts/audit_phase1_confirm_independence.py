#!/usr/bin/env python3
"""Deterministic pack-independence audit for phase1_confirm_v1 (0 LLM/API calls).

Compares prompt/context text against VNEXT confirm + detector-adjacent frozen packs.
Read-only on datasets/frozen/**.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

P1 = ROOT / "datasets/frozen/phase1_confirm_v1/dataset.jsonl"
VN = ROOT / "datasets/frozen/vnext_confirm_v1/dataset.jsonl"
COMPARE = [
    ("vnext_confirm_v1", VN),
    ("layer_a_v2", ROOT / "datasets/frozen/layer_a_v2/dataset.jsonl"),
    ("layer_a_v3", ROOT / "datasets/frozen/layer_a_v3/dataset.jsonl"),
    ("layer_a_v3_train", ROOT / "datasets/frozen/layer_a_v3/train.jsonl"),
    ("layer_a_v3_dev", ROOT / "datasets/frozen/layer_a_v3/dev.jsonl"),
    ("layer_a_v3_test_split", ROOT / "datasets/frozen/layer_a_v3/test_split.jsonl"),
    ("phase1_holdout_v1", ROOT / "datasets/frozen/phase1_holdout_v1/dataset.jsonl"),
    ("eval_v1", ROOT / "datasets/frozen/eval_v1/dataset.jsonl"),
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def prompt_of(row: dict) -> str:
    for key in ("prompt", "user_prompt", "input", "text", "query"):
        val = row.get(key)
        if isinstance(val, str) and val.strip():
            return val
    return ""


def context_of(row: dict) -> str:
    val = row.get("context")
    return val if isinstance(val, str) else ""


def eid(row: dict, idx: int) -> str:
    return str(row.get("id") or row.get("episode_id") or f"row_{idx}")


def ngrams(text: str, n: int = 5) -> set[str]:
    s = norm(text)
    if len(s) < n:
        return {s} if s else set()
    return {s[i : i + n] for i in range(len(s) - n + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def text_blob(row: dict) -> str:
    return norm(prompt_of(row) + "\n" + context_of(row))


def compare_packs(left: list[dict], right: list[dict], j_thresh: float) -> dict:
    left_prompt_h: dict[str, list[str]] = defaultdict(list)
    right_prompt_h: dict[str, list[str]] = defaultdict(list)
    left_blob_h: dict[str, list[str]] = defaultdict(list)
    right_blob_h: dict[str, list[str]] = defaultdict(list)

    for i, row in enumerate(left):
        pid = eid(row, i)
        ph = hashlib.sha256(norm(prompt_of(row)).encode()).hexdigest()
        bh = hashlib.sha256(text_blob(row).encode()).hexdigest()
        if norm(prompt_of(row)):
            left_prompt_h[ph].append(pid)
        if text_blob(row).strip():
            left_blob_h[bh].append(pid)
    for j, row in enumerate(right):
        pid = eid(row, j)
        ph = hashlib.sha256(norm(prompt_of(row)).encode()).hexdigest()
        bh = hashlib.sha256(text_blob(row).encode()).hexdigest()
        if norm(prompt_of(row)):
            right_prompt_h[ph].append(pid)
        if text_blob(row).strip():
            right_blob_h[bh].append(pid)

    exact_prompt = []
    for h in sorted(set(left_prompt_h) & set(right_prompt_h)):
        exact_prompt.append({"left": left_prompt_h[h], "right": right_prompt_h[h]})
    exact_blob = []
    for h in sorted(set(left_blob_h) & set(right_blob_h)):
        exact_blob.append({"left": left_blob_h[h], "right": right_blob_h[h]})

    near = []
    for i, r1 in enumerate(left):
        g1 = ngrams(prompt_of(r1))
        if not g1:
            continue
        for j, r2 in enumerate(right):
            score = jaccard(g1, ngrams(prompt_of(r2)))
            if score >= j_thresh:
                near.append(
                    {
                        "jaccard_char5": round(score, 6),
                        "seqratio": round(
                            SequenceMatcher(
                                None, norm(prompt_of(r1)), norm(prompt_of(r2))
                            ).ratio(),
                            6,
                        ),
                        "left_id": eid(r1, i),
                        "right_id": eid(r2, j),
                    }
                )
    near.sort(key=lambda x: (-x["jaccard_char5"], x["left_id"], x["right_id"]))
    return {
        "exact_prompt_overlap": len(exact_prompt),
        "exact_prompt_pairs": exact_prompt,
        "exact_prompt_context_overlap": len(exact_blob),
        "exact_prompt_context_pairs": exact_blob,
        "near_prompt_pairs_jaccard_ge": j_thresh,
        "near_prompt_count": len(near),
        "near_prompt_top": near[:25],
    }


def main() -> int:
    if not P1.exists() or not VN.exists():
        print("missing frozen packs", file=sys.stderr)
        return 2

    p1 = load_jsonl(P1)
    report: dict = {
        "api_calls": 0,
        "method": "exact SHA256 of normalized prompt / prompt+context; char-5gram Jaccard; SequenceMatcher ratio",
        "phase1_confirm_v1": {
            "path": str(P1.relative_to(ROOT)),
            "n": len(p1),
            "sha256": sha256_file(P1),
            "provenance": dict(Counter((r.get("metadata") or {}).get("provenance") for r in p1)),
            "generation_method": dict(
                Counter((r.get("metadata") or {}).get("generation_method") for r in p1)
            ),
            "seed": dict(Counter((r.get("metadata") or {}).get("seed") for r in p1)),
            "attack_family": dict(
                Counter(
                    (r.get("metadata") or {}).get("attack_family")
                    for r in p1
                    if r.get("label") == "attack" or r.get("category") == "attack"
                )
            ),
            "creation_date_field_present": False,
            "creation_date_status": "UNKNOWN for all episodes (no created_at/date field in metadata)",
            "derived_from_vnext_pack_field": "absent; provenance claims authored_phase1_confirm_v1_independent",
        },
        "comparisons": {},
    }

    for name, path in COMPARE:
        if not path.exists():
            report["comparisons"][name] = {"exists": False, "path": str(path)}
            continue
        rows = load_jsonl(path)
        # VNEXT primary screen uses j>=0.25; holdout kinship uses j>=0.40 for reporting
        thresh = 0.25 if name.startswith("vnext") else 0.40
        cmp_ = compare_packs(p1, rows, thresh)
        meta = {
            "exists": True,
            "path": str(path.relative_to(ROOT)),
            "n": len(rows),
            "sha256": sha256_file(path),
            "provenance": dict(Counter((r.get("metadata") or {}).get("provenance") for r in rows)),
            "generation_method": dict(
                Counter((r.get("metadata") or {}).get("generation_method") for r in rows)
            ),
            "seed": dict(Counter((r.get("metadata") or {}).get("seed") for r in rows)),
            "attack_family": dict(
                Counter(
                    (r.get("metadata") or {}).get("attack_family")
                    for r in rows
                    if (r.get("label") == "attack" or r.get("category") == "attack")
                )
            ),
            **cmp_,
        }
        report["comparisons"][name] = meta

    out = ROOT / "docs/paper/dual_track/artifacts/phase1_independence_audit_metrics.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"wrote": str(out.relative_to(ROOT)), "api_calls": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
