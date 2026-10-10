"""Stage 2 coverage design for attack-pack v4. Generates the matrix; creates no examples.

Usage:
    python3 scripts/dataset_upgrade/coverage_matrix.py [--out-dir DIR]

Writes coverage_matrix_v4.csv and power_multiturn_v4.json into DIR (default:
docs/dataset_upgrade/generated). Every number here is a design target, not a count of
existing data.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

from adapti_guard.data.attack_schema_v4 import CATEGORY_RULES

STYLES = ("formal", "conversational", "structured_or_fabricated_instruction")

# family -> (category, primary cells as (channel, turn_type), target attacks per cell)
FAMILIES: dict[str, tuple[str, list[tuple[str, str]], int]] = {
    "DIRECT_OVERRIDE": ("direct_instruction_override", [("user_turn", "single")], 12),
    "EMAIL_INJECTION": ("email_injection", [("email", "single")], 12),
    "RAG_DOC_INJECTION": ("rag_document_injection", [("retrieved_doc", "single")], 12),
    "TOOL_OUTPUT_INJECTION": ("tool_output_injection", [("tool_output", "single")], 12),
    "WEB_CONTENT_INJECTION": ("web_content_injection", [("web_content", "single")], 12),
    "INDIRECT_CONTEXT": (
        "indirect_context_injection",
        [(c, "single") for c in ("email", "retrieved_doc", "tool_output", "web_content")],
        12,
    ),
    "OBFUSCATION": (
        "obfuscation_encoding",
        [(c, "single") for c in ("user_turn", "email", "retrieved_doc", "tool_output", "web_content")],
        12,
    ),
    "UNAUTHORIZED_TOOL": (
        "privilege_exfil_unauthorized_tool",
        [(c, "single") for c in ("user_turn", "email", "retrieved_doc", "tool_output", "web_content")],
        12,
    ),
    "SYSTEM_PROMPT_LEAKAGE": (
        "system_prompt_leakage",
        [(c, "single") for c in ("user_turn", "retrieved_doc", "web_content")],
        12,
    ),
    "JAILBREAK_ROLEPLAY": ("jailbreak_roleplay", [("user_turn", "single")], 12),
    "MULTI_TURN_PERSISTENCE": ("multi_turn_persistence", [("user_turn", "multi")], 60),
    # 15 per cell x 4 cells = 60 per family.
    "MULTI_TURN_INJECTION": (
        "multi_turn_injection",
        [(c, "multi") for c in ("email", "retrieved_doc", "tool_output", "web_content")],
        15,
    ),
}

# Cells that look plausible but are excluded by the schema or by design.
INFEASIBLE = [
    ("DIRECT_OVERRIDE", "email", "single", "direct override is by definition a user-turn instruction"),
    ("DIRECT_OVERRIDE", "tool_output", "single", "same as above; tool output is covered by TOOL_OUTPUT_INJECTION"),
    ("JAILBREAK_ROLEPLAY", "retrieved_doc", "single", "excluded by schema: roleplay framing is user-turn in v4"),
    ("JAILBREAK_ROLEPLAY", "web_content", "single", "excluded by schema: same reason"),
    ("SYSTEM_PROMPT_LEAKAGE", "email", "single", "excluded by schema in v4 (email is not a leakage vector here)"),
    ("MULTI_TURN_PERSISTENCE", "email", "multi", "excluded by schema: persistence is user-turn in v4"),
    ("MULTI_TURN_INJECTION", "user_turn", "multi", "excluded by schema: user-turn content is single-channel persistence"),
    ("*", "none", "*", "channel 'none' is never an attack channel"),
    ("*", "*", "single", "multi-turn categories cannot be single-turn; other categories cannot be multi-turn in v4"),
]

def _normal_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _norm_ppf(p: float) -> float:
    lo, hi = -10.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if _normal_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def n_per_arm(p1: float, p2: float, alpha: float = 0.05, power: float = 0.80) -> int:
    """Two-sided two-proportion sample size per arm (normal approximation)."""
    z_a = _norm_ppf(1 - alpha / 2)
    z_b = _norm_ppf(power)
    pbar = (p1 + p2) / 2
    num = z_a * math.sqrt(2 * pbar * (1 - pbar)) + z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    return math.ceil(num**2 / (p1 - p2) ** 2)


def power_table() -> dict:
    effects = [(0.50, 0.25), (0.50, 0.30), (0.40, 0.20), (0.30, 0.15)]
    rows = []
    for p1, p2 in effects:
        rows.append({"p_baseline": p1, "p_treated": p2, "n_per_arm_80pct_power": n_per_arm(p1, p2)})
    return {
        "method": "two-sided two-proportion z test, normal approximation, alpha=0.05, power=0.80",
        "note": (
            "Per arm. n=50 gives power 0.74 for 0.50 vs 0.25 (0.59 for 0.40 vs 0.20); "
            "n=60 gives 0.82 and 0.67. A floor of 50 is below the 58 needed for 80% power "
            "at the 0.50 vs 0.25 effect, so 50 is only justified if the owner accepts ~74% power."
        ),
        "rows": rows,
        "floor_per_multi_family": 50,
        "design_target_per_multi_family": 60,
    }


def build_rows() -> list[dict]:
    rows = []
    for family, (category, cells, per_cell) in FAMILIES.items():
        channels_allowed, turns_allowed = CATEGORY_RULES[category]
        for channel, turn in cells:
            assert channel in channels_allowed and turn in turns_allowed, (family, channel, turn)
            for style in STYLES:
                per_style = per_cell // len(STYLES)
                rows.append({
                    "family": family,
                    "category": category,
                    "injection_channel": channel,
                    "turn_type": turn,
                    "style": style,
                    "attacks_target": per_style,
                    "counterparts_target": per_style,
                })
    return rows


def totals(rows: list[dict]) -> dict:
    by_family: dict[str, dict[str, int]] = {}
    for r in rows:
        f = by_family.setdefault(r["family"], {"attacks": 0, "counterparts": 0, "cells": set()})
        f["attacks"] += r["attacks_target"]
        f["counterparts"] += r["counterparts_target"]
        f["cells"].add((r["injection_channel"], r["turn_type"]))
    out = {}
    for family, f in by_family.items():
        out[family] = {
            "attacks": f["attacks"],
            "counterparts": f["counterparts"],
            "primary_cells": len(f["cells"]),
        }
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="docs/dataset_upgrade/generated")
    args = parser.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    rows = build_rows()
    with (out / "coverage_matrix_v4.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    summary = totals(rows)
    power = power_table()
    (out / "power_multiturn_v4.json").write_text(json.dumps(power, indent=2) + "\n", encoding="utf-8")
    (out / "coverage_summary_v4.json").write_text(
        json.dumps({"families": summary, "infeasible": INFEASIBLE}, indent=2) + "\n", encoding="utf-8"
    )

    total_attacks = sum(r["attacks_target"] for r in rows)
    print(f"attacks target: {total_attacks}")
    print(f"benign-side counterparts target: {sum(r['counterparts_target'] for r in rows)}")
    for family, s in summary.items():
        print(f"  {family:24s} cells={s['primary_cells']} attacks={s['attacks']} counterparts={s['counterparts']}")


if __name__ == "__main__":
    main()
