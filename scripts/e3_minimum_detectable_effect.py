"""Family-level minimum detectable effect (MDE) for the E3 paired comparison (manuscript §8.2). Offline.

The E3 set has seven attack families. Each family is one cluster: its paired difference is (arm executed − A0 executed)
over its pairs, pooled across the three models. With seven clusters, the MDE for a two-sided 5% test with 80% power is

    MDE = (t_{0.975, 6} + t_{0.80, 6}) * sd / sqrt(7),

using the observed family-level standard deviation. It is post hoc: it uses the same data it describes, so it bounds what
these data could have shown, not what a new study would need. Reads only the committed paired analysis.

Usage: python scripts/e3_minimum_detectable_effect.py
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

from scipy.stats import chi2, t as student_t

ROOT = Path(__file__).resolve().parents[1]
PAIRED = ROOT / "experiments/harness_v2/HARNESS_V2_INDEPENDENT_DEFENDED_20260930/paired_vs_a0_analysis.json"
OUT = ROOT / "docs/research/artifacts/e3_minimum_detectable_effect.json"
ALPHA = 0.05
POWER = 0.80


def family_differences(cells: dict[str, list[int]]) -> dict[str, tuple[int, int, int]]:
    """cells are keyed 'scenario|model' with [A0 executed, arm executed, pairs]; the family is the scenario."""
    fam: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    for key, (a0, arm, n) in cells.items():
        f = fam[key.split("|")[0]]
        f[0] += a0
        f[1] += arm
        f[2] += n
    return {k: tuple(v) for k, v in sorted(fam.items())}


def mde_for_arm(cells: dict[str, list[int]]) -> dict:
    fam = family_differences(cells)
    k = len(fam)
    rates = [(arm - a0) / n for a0, arm, n in fam.values()]
    sd = statistics.stdev(rates)
    df = k - 1
    t_two = student_t.ppf(1 - ALPHA / 2, df)
    t_pow = student_t.ppf(POWER, df)
    se = sd / math.sqrt(k)
    # one-sided 95% upper confidence bound for the family sd: sd * sqrt(df / chi2_{0.05, df})
    sd_upper = sd * math.sqrt(df / chi2.ppf(0.05, df))
    return {
        "families": k,
        "pairs": sum(n for _, _, n in fam.values()),
        "pairs_per_family": [n for _, _, n in fam.values()],
        "mean_difference": statistics.mean(rates),
        "family_sd": sd,
        "t_two_sided_0_975": t_two,
        "t_power_0_80": t_pow,
        "mde": (t_two + t_pow) * se,
        "sd_upper_95_one_sided": sd_upper,
        "mde_at_sd_upper_95": (t_two + t_pow) * sd_upper / math.sqrt(k),
    }


def build() -> dict:
    paired = json.loads(PAIRED.read_text())
    return {
        "status": "EXPLORATORY, post hoc, family-level MDE on the committed E3 data (manuscript §8.2)",
        "source": str(PAIRED.relative_to(ROOT)),
        "method": "two-sided 5%, 80% power, seven family clusters, t with 6 degrees of freedom, observed family-level sd; "
              "also at the one-sided 95% upper confidence bound of that sd (chi-square, 6 degrees of freedom)",
        "arms": {arm: mde_for_arm(paired["arms"][arm]["cells"]) for arm in ("B3", "CORE")},
    }


def main() -> int:
    text = json.dumps(build(), indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    OUT.write_text(text)
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
