"""Stage 2 coverage design for attack-pack v4. Generates the design tables; creates no examples.

Usage:
    PYTHONPATH=src python3 scripts/dataset_upgrade/coverage_matrix.py [--out-dir DIR]

Writes coverage_matrix_v4.csv, coverage_summary_v4.json and power_multiturn_v4.json into DIR
(default: docs/dataset_upgrade/generated, relative to the current directory). Every number is a
design target, not a count of existing data.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import NormalDist

from adapti_guard.data.attack_schema_v4 import CATEGORY_RULES, FAMILY_CATEGORY

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
    # 60 per family in total. Per-cell figures are attacks per primary cell.
    "MULTI_TURN_PERSISTENCE": ("multi_turn_persistence", [("user_turn", "multi")], 60),
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
    ("MULTI_TURN_INJECTION", "user_turn", "multi", "excluded by schema: user-turn content is covered by persistence"),
    ("*", "none", "*", "channel 'none' is never an attack channel"),
    ("*", "*", "single", "multi-turn categories cannot be single-turn; other categories cannot be multi-turn in v4"),
]

# Statistical design. The test is a two-sided pooled two-proportion z-test with equal n per arm.
ALPHA = 0.05
POWER_TARGET = 0.80
EFFECTS = ((0.50, 0.25), (0.50, 0.30), (0.40, 0.20), (0.30, 0.15))
FLOOR_PER_MULTI_FAMILY = 50
DESIGN_TARGET_PER_MULTI_FAMILY = 60
POWER_ASSUMPTIONS = [
    "Two independent arms with equal n per arm; each attack is assumed to be scored once per arm.",
    "Independent Bernoulli outcomes within each arm: no clustering by family, style or template.",
    "Power is computed for one primary comparison. No multiplicity adjustment is applied; "
    "across 12 families and 28 primary cells the family-wise error rate is not controlled.",
    "Statistical power describes sensitivity of the design. It does not establish that any defense works.",
]


def exact_power(n: int, p1: float, p2: float, alpha: float = ALPHA) -> float:
    """Exact power of the pooled two-proportion z-test by enumerating all (x1, x2) outcomes.

    When the pooled variance is zero (no successes or no failures in both arms), the statistic is
    undefined and the test is counted as not rejecting.
    """
    z_crit = NormalDist().inv_cdf(1 - alpha / 2)
    pmf1 = [math.comb(n, k) * p1**k * (1 - p1) ** (n - k) for k in range(n + 1)]
    pmf2 = [math.comb(n, k) * p2**k * (1 - p2) ** (n - k) for k in range(n + 1)]
    total = 0.0
    for x1 in range(n + 1):
        for x2 in range(n + 1):
            pooled = (x1 + x2) / (2 * n)
            variance = pooled * (1 - pooled) * 2 / n
            if variance == 0:
                continue
            z = (x1 / n - x2 / n) / math.sqrt(variance)
            if abs(z) > z_crit:
                total += pmf1[x1] * pmf2[x2]
    return total


def exact_min_n(p1: float, p2: float, target: float = POWER_TARGET, max_n: int = 400) -> int:
    """Smallest per-arm n with exact power >= target (first n reaching it)."""
    for n in range(2, max_n + 1):
        if exact_power(n, p1, p2) >= target:
            return n
    raise ValueError(f"no n <= {max_n} reaches power {target} for {p1} vs {p2}")


def normal_approx_n(p1: float, p2: float, alpha: float = ALPHA, power: float = POWER_TARGET) -> float:
    """Textbook normal-approximation sample size per arm, unrounded. Reference only."""
    z_a = NormalDist().inv_cdf(1 - alpha / 2)
    z_b = NormalDist().inv_cdf(power)
    pbar = (p1 + p2) / 2
    num = z_a * math.sqrt(2 * pbar * (1 - pbar)) + z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))
    return num**2 / (p1 - p2) ** 2


def power_table() -> dict:
    rows = []
    for p1, p2 in EFFECTS:
        n_min = exact_min_n(p1, p2)
        rows.append({
            "p_baseline": p1,
            "p_treated": p2,
            "normal_approx_n_unrounded": round(normal_approx_n(p1, p2), 3),
            "exact_min_n_power_0.80": n_min,
            "exact_power_at_min_n": round(exact_power(n_min, p1, p2), 4),
            "exact_power_at_n_minus_1": round(exact_power(n_min - 1, p1, p2), 4),
            "exact_power_at_floor_50": round(exact_power(FLOOR_PER_MULTI_FAMILY, p1, p2), 4),
            "exact_power_at_design_60": round(exact_power(DESIGN_TARGET_PER_MULTI_FAMILY, p1, p2), 4),
        })
    return {
        "test": "two-sided pooled two-proportion z-test; power by exact enumeration of all outcomes",
        "alpha": ALPHA,
        "power_target": POWER_TARGET,
        "allocation": "equal n per arm",
        "assumptions": POWER_ASSUMPTIONS,
        "reference_only": "normal_approx_n_unrounded uses unpooled variance under H1; it is not the design basis",
        "rows": rows,
        "floor_per_multi_family": FLOOR_PER_MULTI_FAMILY,
        "design_target_per_multi_family": DESIGN_TARGET_PER_MULTI_FAMILY,
        "note": (
            "For the primary effect (0.50 vs 0.25) the exact minimum n for power 0.80 is 59. The design "
            "target of 60 keeps a margin above that minimum (power 0.818). The floor of 50 gives power "
            "below 0.80 for that effect and is only acceptable if the owner accepts the stated power (decision D4)."
        ),
    }


def build_rows() -> list[dict]:
    rows = []
    for family, (category, cells, per_cell) in FAMILIES.items():
        if FAMILY_CATEGORY.get(family) != category:
            raise ValueError(f"{family} category {category!r} disagrees with the schema registry")
        if per_cell % len(STYLES):
            raise ValueError(f"{family}: per-cell target {per_cell} does not divide across {len(STYLES)} styles")
        channels_allowed, turns_allowed = CATEGORY_RULES[category]
        for channel, turn in cells:
            if channel not in channels_allowed or turn not in turns_allowed:
                raise ValueError(f"{family}: cell ({channel}, {turn}) is not allowed for {category}")
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
    by_family: dict[str, dict] = {}
    for r in rows:
        f = by_family.setdefault(r["family"], {"attacks": 0, "counterparts": 0, "cells": set()})
        f["attacks"] += r["attacks_target"]
        f["counterparts"] += r["counterparts_target"]
        f["cells"].add((r["injection_channel"], r["turn_type"]))
    return {
        family: {"attacks": f["attacks"], "counterparts": f["counterparts"], "primary_cells": len(f["cells"])}
        for family, f in by_family.items()
    }


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
        json.dumps({
            "families": summary,
            "infeasible": INFEASIBLE,
            "hard_negative_allocation": "not encoded: proportion of counterparts labelled hard_negative is pending owner decision D5",
        }, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"attacks target: {sum(r['attacks_target'] for r in rows)}")
    print(f"benign-side counterparts target: {sum(r['counterparts_target'] for r in rows)}")
    for family, s in summary.items():
        print(f"  {family:24s} cells={s['primary_cells']} attacks={s['attacks']} counterparts={s['counterparts']}")


if __name__ == "__main__":
    main()
