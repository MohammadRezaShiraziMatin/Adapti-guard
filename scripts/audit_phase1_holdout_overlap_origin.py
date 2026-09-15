#!/usr/bin/env python3
"""Characterize phase1_confirm_v1 ↔ phase1_holdout_v1 near-pair origins (API=0).

Does not modify frozen packs. Reuses the same Jaccard/SequenceMatcher method as
scripts/audit_phase1_confirm_independence.py without editing that script.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P1 = ROOT / "datasets/frozen/phase1_confirm_v1/dataset.jsonl"
HO = ROOT / "datasets/frozen/phase1_holdout_v1/dataset.jsonl"
OUT = ROOT / "docs/paper/dual_track/artifacts/phase1_holdout_overlap_origin.json"


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def ngrams(text: str, n: int = 5) -> set[str]:
    s = norm(text)
    if len(s) < n:
        return {s} if s else set()
    return {s[i : i + n] for i in range(len(s) - n + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9_@.'-]+", text or ""))


def classify(p1_prompt: str, ho_prompt: str) -> str:
    p, h = norm(p1_prompt), norm(ho_prompt)
    if "translate to" in p and "translate to" in h and "disregard policies" in p:
        return "hardneg_translate_language_swap"
    if "standup" in p and "standup" in h and "team-sync@company.example" in p:
        return "benign_standup_email_scaffold"
    if "maintenance_ticket" in p and "maintenance_ticket" in h:
        return "benign_maintenance_ticket_scaffold"
    if "parse" in p and "parse" in h and "cmd=send_email" in p:
        return "hardneg_log_parse_scaffold"
    if "recommended action" in p and "recommended action" in h:
        return "attack_tool_observation_recommended_action"
    if "retrieved note" in p and "retrieved note" in h:
        return "attack_indirect_rag_summarize_scaffold"
    if "hidden step" in p and "hidden step" in h:
        return "attack_delayed_hidden_step_scaffold"
    return "other_shared_phrasing"


def main() -> int:
    p1_rows = load(P1)
    ho_rows = load(HO)
    pairs = []
    for r1 in p1_rows:
        g1 = ngrams(r1.get("prompt", ""))
        for r2 in ho_rows:
            score = jaccard(g1, ngrams(r2.get("prompt", "")))
            if score < 0.40:
                continue
            sm = SequenceMatcher(
                None, norm(r1.get("prompt", "")), norm(r2.get("prompt", ""))
            ).ratio()
            pairs.append(
                {
                    "jaccard_char5": round(score, 6),
                    "seqratio": round(sm, 6),
                    "left_id": r1["id"],
                    "right_id": r2["id"],
                    "left_label": r1.get("label"),
                    "right_label": r2.get("label"),
                    "pattern": classify(r1.get("prompt", ""), r2.get("prompt", "")),
                    "left_prompt": r1.get("prompt", ""),
                    "right_prompt": r2.get("prompt", ""),
                    "token_only_left": sorted(
                        tokens(r1.get("prompt", "")) - tokens(r2.get("prompt", ""))
                    )[:20],
                    "token_only_right": sorted(
                        tokens(r2.get("prompt", "")) - tokens(r1.get("prompt", ""))
                    )[:20],
                }
            )
    pairs.sort(key=lambda x: (-x["jaccard_char5"], -x["seqratio"], x["left_id"]))
    report = {
        "api_calls": 0,
        "n_pairs_jaccard_ge_0_40": len(pairs),
        "label_pair_counts": {
            f"{a}|{b}": n
            for (a, b), n in Counter(
                (p["left_label"], p["right_label"]) for p in pairs
            ).items()
        },
        "pattern_counts": dict(Counter(p["pattern"] for p in pairs)),
        "right_id_concentration": [
            {"right_id": rid, "n": n}
            for rid, n in Counter(p["right_id"] for p in pairs).most_common(15)
        ],
        "sample_top_12": pairs[:12],
        "attack_samples": [p for p in pairs if p["left_label"] == "attack"][:6],
        "notes": [
            "Many confirm benign variants map to the same holdout row (many-to-one).",
            "No shared build module: holdout has no build_*.py; confirm uses scripts/build_phase1_confirm_v1.py.",
            "Seeds differ: confirm metadata seed 20260914 vs holdout seed 1411.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"wrote": str(OUT.relative_to(ROOT)), "n_pairs": len(pairs), "api_calls": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
