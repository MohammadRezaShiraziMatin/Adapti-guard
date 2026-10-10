#!/usr/bin/env python3
"""Offline (no network, no cost) validity + defense-coverage check on the full InjecAgent base cases."""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.external import injecagent as ia  # noqa: E402
from adapti_guard.evaluation.harness_v2.harness_v2_b3_pretarget_wrapper import HarnessV2B3EpisodeContext  # noqa: E402

OUT = ROOT / "docs/research/artifacts/injecagent_offline_check_20260930.json"


def main() -> int:
    specs = ia.load_tool_specs()
    cases = ia.load_cases()
    invalid = {c["case_id"]: b for c in cases if (b := ia.validate_case(c, specs))}
    res = {"provenance": ia.provenance(), "n_cases": len(cases), "n_invalid": len(invalid), "invalid_examples": dict(list(invalid.items())[:5])}
    for cond in ("B3", "CORE"):
        blocked = collections.Counter()
        sanitized = collections.Counter()
        benign_blocked = 0
        for c in cases:
            ctx = HarnessV2B3EpisodeContext.for_condition(cond)  # fresh state per case
            _, b, t = ctx.defense_fn(ia.tool_content(c), None)
            blocked[c["kind"]] += bool(b)
            sanitized[c["kind"]] += (not b and t != ia.tool_content(c))
            ctx2 = HarnessV2B3EpisodeContext.for_condition(cond)
            _, b2, _ = ctx2.defense_fn(ia.tool_content(c, injected=False), None)
            benign_blocked += bool(b2)
        n = collections.Counter(c["kind"] for c in cases)
        bare = sum(bool(HarnessV2B3EpisodeContext.for_condition(cond).defense_fn(c["Attacker Instruction"], None)[1]) for c in cases)
        res[cond] = {
            "attack_blocked": {k: f"{blocked[k]}/{n[k]}" for k in n},
            "attack_modified_not_blocked": {k: f"{sanitized[k]}/{n[k]}" for k in n},
            "bare_attacker_instruction_blocked": f"{bare}/{len(cases)}",
            "neutralised_control_blocked": f"{benign_blocked}/{len(cases)}",
        }
    OUT.write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
