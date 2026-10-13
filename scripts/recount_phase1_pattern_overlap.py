#!/usr/bin/env python3
"""Recount how many of the 42 Phase-1 detector patterns match the earlier VNEXT pack and neither Phase-1 pack.

The 42 patterns are the regular expressions in the three ``_PHASE1_*`` lists of
``src/adapti_guard/detector/prompt_injection_detector_phase1.py`` (9 + 8 + 25). A pattern counts as "VNEXT only" when it
matches (case-insensitive) at least one VNEXT episode and no episode of phase1_holdout_v1 or phase1_confirm_v1.
The three lists share one duplicate regex, so there are 42 list entries and fewer unique patterns (reported separately).
Variants: searched text = prompt + context, or the whole JSON record; all episodes, or attack episodes only.
Offline, no API. Output: docs/research/artifacts/phase1_pattern_overlap_recount_20261008.json
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DET = ROOT / "src/adapti_guard/detector/prompt_injection_detector_phase1.py"
PACKS = ("vnext_confirm_v1", "phase1_holdout_v1", "phase1_confirm_v1")


def patterns() -> list[str]:
    out: list[str] = []
    for n in ast.parse(DET.read_text()).body:
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id.startswith("_PHASE1"):
            out += [ast.literal_eval(e) for e in n.value.elts]
    return out


def texts(pack: str, mode: str, attack_only: bool) -> list[str]:
    rows = [json.loads(x) for x in (ROOT / f"datasets/frozen/{pack}/dataset.jsonl").read_text().splitlines() if x.strip()]
    rows = [r for r in rows if not attack_only or r.get("label") == "attack"]
    if mode == "prompt_context":
        return [(r.get("prompt") or "") + "\n" + (r.get("context") or "") for r in rows]
    return [json.dumps(r, ensure_ascii=False) for r in rows]


def main() -> None:
    pats = patterns()
    assert len(pats) == 42, len(pats)
    res = {"n_patterns": len(pats), "variants": {}}
    for mode in ("prompt_context", "whole_json_record"):
        for attack_only in (False, True):
            corpus = {k: texts(k, mode, attack_only) for k in PACKS}
            hits = [tuple(any(re.search(p, t, re.I) for t in corpus[k]) for k in PACKS) for p in pats]
            uniq = {}
            for p, hv in zip(pats, hits):
                uniq[p] = hv
            key = f"{mode}/{'attack_only' if attack_only else 'all_episodes'}"
            res["variants"][key] = {
                "vnext_only": sum(1 for v, h, c in hits if v and not h and not c),
                "match_vnext": sum(1 for v, _, _ in hits if v),
                "match_any_phase1_pack": sum(1 for _, h, c in hits if h or c),
                "vnext_only_unique_patterns": sum(1 for v, h, c in uniq.values() if v and not h and not c),
            }
    res["n_unique_patterns"] = len(set(pats))
    out = ROOT / "docs/research/artifacts/phase1_pattern_overlap_recount_20261008.json"
    out.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res["variants"], indent=1))


if __name__ == "__main__":
    main()
