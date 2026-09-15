#!/usr/bin/env python3
"""Classify all phase1_confirm_v1 ↔ phase1_holdout_v1 near-pairs (J≥0.40). API=0."""
from __future__ import annotations

import json
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P1 = ROOT / "datasets/frozen/phase1_confirm_v1/dataset.jsonl"
HO = ROOT / "datasets/frozen/phase1_holdout_v1/dataset.jsonl"
OUT_JSON = ROOT / "docs/paper/dual_track/artifacts/phase1_holdout_pairs_full59.json"
OUT_MD = ROOT / "docs/paper/dual_track/artifacts/phase1_holdout_pairs_full59.md"


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


def tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_@.'/-]+", text or "")


def classify(r1: dict, r2: dict, j: float, sm: float) -> tuple[str, str]:
    p1p, hop = r1.get("prompt", ""), r2.get("prompt", "")
    p1c, hoc = r1.get("context") or "", r2.get("context") or ""
    if norm(p1p) == norm(hop) and norm(p1c) == norm(hoc):
        return "GENUINE_DUPLICATE", "exact normalized prompt+context match"
    if norm(p1p) == norm(hop):
        return "GENUINE_DUPLICATE", "exact normalized prompt match"
    n1, n2 = norm(p1p), norm(hop)
    t1, t2 = tokens(p1p), tokens(hop)
    if "translate to" in n1 and "translate to" in n2 and "disregard policies" in n1:
        return "SAME_SCAFFOLD_DIFF_ENTITY", "translate hard-neg scaffold; language name swapped"
    if "maintenance_ticket" in n1 and "maintenance_ticket" in n2:
        return "SAME_SCAFFOLD_DIFF_ENTITY", "create_record maintenance_ticket scaffold; zone/payload values differ"
    if "team-sync@company.example" in n1 and "team-sync@company.example" in n2 and "standup" in n1:
        return "SAME_SCAFFOLD_DIFF_ENTITY", "send_email standup scaffold; body text/index differs"
    if "cmd=send_email" in n1 and "cmd=send_email" in n2 and "parse" in n1:
        return "SAME_SCAFFOLD_DIFF_WORDING", "log-parse hard-neg scaffold; wording expanded/paraphrased"
    if "recommended action" in n1 and "recommended action" in n2:
        return "SAME_SCAFFOLD_DIFF_WORDING", "tool-observation recommended-action attack scaffold; verb/phrasing differs"
    if "retrieved note" in n1 and "retrieved note" in n2:
        return "SAME_SCAFFOLD_DIFF_WORDING", "indirect-RAG summarize-note scaffold; instruction wording differs"
    if "hidden step" in n1 and "hidden step" in n2:
        return "SAME_SCAFFOLD_DIFF_ENTITY", "delayed hidden-step attack scaffold; kind/payload markers differ"
    if "warehouse index" in n1 and "warehouse index" in n2 and "search for" in n1:
        return "SAME_SCAFFOLD_DIFF_ENTITY", "benign warehouse search scaffold; SKU ids differ"
    if "image title suspicious" in n1 and "image title suspicious" in n2:
        return "SAME_SCAFFOLD_DIFF_WORDING", "markdown image-title hard-neg scaffold; framing paraphrased"
    if "review" in n1 and "review" in n2 and "create_record" in n1 and ("bug" in n1 or "bug" in n2):
        return "SAME_SCAFFOLD_DIFF_WORDING", "code-review hard-neg scaffold; snippet framing paraphrased"
    if "quoted text" in n1 and "quoted text" in n2 and "injection" in n1:
        return "SAME_SCAFFOLD_DIFF_WORDING", "quoted-injection yes/no hard-neg scaffold; framing paraphrased"
    if "indirect prompt" in n1 and "indirect prompt" in n2 and "security class" in n1:
        return "SAME_SCAFFOLD_DIFF_WORDING", "security-class category-list hard-neg; sentence order paraphrased"
    if "email secrets" in n1 and "email secrets" in n2 and "send_email" in n1:
        return "SAME_SCAFFOLD_DIFF_WORDING", "policy-quote confirm-no-email hard-neg; quote framing paraphrased"
    if len(n1) < 40 and len(n2) < 40 and sm < 0.70 and j < 0.50:
        return "COINCIDENTAL_SHORT_OVERLAP", "short prompts; moderate n-gram overlap without distinctive shared scaffold"
    if sm >= 0.80 or j >= 0.55:
        only1 = set(x.lower() for x in t1) - set(x.lower() for x in t2)
        only2 = set(x.lower() for x in t2) - set(x.lower() for x in t1)
        shared = set(x.lower() for x in t1) & set(x.lower() for x in t2)
        if len(only1 | only2) <= 6 and len(shared) >= 4:
            return (
                "SAME_SCAFFOLD_DIFF_ENTITY",
                f"high overlap; differing tokens mostly entity/value slots: {sorted(only1 | only2)[:8]}",
            )
        return "SAME_SCAFFOLD_DIFF_WORDING", "high structural overlap with paraphrased connective wording"
    return "COINCIDENTAL_SHORT_OVERLAP", "residual moderate overlap without clear multi-token scaffold signature"


def main() -> int:
    p1_rows, ho_rows = load(P1), load(HO)
    raw = []
    for r1 in p1_rows:
        g1 = ngrams(r1.get("prompt", ""))
        for r2 in ho_rows:
            j = jaccard(g1, ngrams(r2.get("prompt", "")))
            if j < 0.40:
                continue
            sm = SequenceMatcher(None, norm(r1.get("prompt", "")), norm(r2.get("prompt", ""))).ratio()
            raw.append((j, sm, r1, r2))
    raw.sort(key=lambda x: (-x[0], -x[1], x[2]["id"], x[3]["id"]))
    if len(raw) != 59:
        raise SystemExit(f"expected 59 near-pairs, got {len(raw)}")
    rows = []
    for j, sm, r1, r2 in raw:
        cls, why = classify(r1, r2, j, sm)
        rows.append(
            {
                "pair_id": f"{r1['id']}__{r2['id']}",
                "left_id": r1["id"],
                "right_id": r2["id"],
                "left_label": r1.get("label"),
                "right_label": r2.get("label"),
                "jaccard_char5": round(j, 6),
                "seqratio": round(sm, 6),
                "class": cls,
                "justification": why,
                "left_prompt": r1.get("prompt", ""),
                "right_prompt": r2.get("prompt", ""),
                "left_context": r1.get("context") or "",
                "right_context": r2.get("context") or "",
            }
        )
    counts = Counter(r["class"] for r in rows)
    genuine = counts.get("GENUINE_DUPLICATE", 0)
    out = {
        "api_calls": 0,
        "n_pairs": 59,
        "class_counts": dict(counts),
        "genuine_duplicate_count": genuine,
        "pairs": rows,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2) + "\n")
    lines = [
        "| pair_id | class | J | SM | justification |",
        "|---------|-------|---|----|---------------|",
    ]
    for r in rows:
        lines.append(
            f"| `{r['pair_id']}` | {r['class']} | {r['jaccard_char5']:.4f} | {r['seqratio']:.4f} | {r['justification']} |"
        )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(json.dumps({"wrote_json": str(OUT_JSON.relative_to(ROOT)), "wrote_md": str(OUT_MD.relative_to(ROOT)), "class_counts": dict(counts), "genuine_duplicate_count": genuine, "api_calls": 0}, indent=2))
    if genuine:
        raise SystemExit("GENUINE_DUPLICATE found — stop and investigate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
