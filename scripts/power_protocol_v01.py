"""Design arithmetic for docs/protocols/CONFIRMATORY_PROTOCOL_DRAFT_v0.1.md. Offline; reads committed records only.

(a) H1: smallest n with zero events whose two-sided 95% Clopper-Pearson upper bound is below a threshold.
(b) H2: paired (McNemar-type) sample size for a reduction of executed attacker calls, using discordance counts
    observed in experiments/external/injecagent_registered_20261001 (A0 vs SPOT_TOOL, same cases).
Formulas are the standard ones and are tested in tests/test_protocol_power_v01.py against hand-computed values.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "experiments/external/injecagent_registered_20261001"
REG_FILES = {"llama-4-maverick": "meta-llama__llama-4-maverick.json", "qwen3.8-flash": "qwen__qwen3.8-flash.json"}
Z = {0.05: 1.959964, 0.0125: 2.4977}  # two-sided normal quantiles for alpha (0.0125 = alpha/4 Bonferroni, 4 targets)
Z_POWER_80 = 0.841621


def cp_upper_zero(n: int, alpha: float = 0.05) -> float:
    """Two-sided (1 - alpha) Clopper-Pearson upper bound for 0 events in n trials: 1 - (alpha/2)^(1/n)."""
    return 1.0 - (alpha / 2.0) ** (1.0 / n)


def min_n_zero_events(threshold: float, alpha: float = 0.05) -> int:
    """Smallest n with cp_upper_zero(n) < threshold."""
    n = 1
    while cp_upper_zero(n, alpha) >= threshold:
        n += 1
    return n


def discordance(name: str) -> tuple[int, int, int]:
    """(n_pairs, b = A0 only, c = SPOT_TOOL only) from the registered per-episode records."""
    eps = json.loads((REG / REG_FILES[name]).read_text())["episodes"]
    a0 = {e["case_id"]: int(e["first_attacker_tool"]) for e in eps if e["arm"] == "A0"}
    sp = {e["case_id"]: int(e["first_attacker_tool"]) for e in eps if e["arm"] == "SPOT_TOOL"}
    b = sum(1 for c in a0 if a0[c] == 1 and sp[c] == 0)
    c = sum(1 for k in a0 if a0[k] == 0 and sp[k] == 1)
    return len(a0), b, c


def mcnemar_pairs(delta: float, p_discord: float, alpha: float, power_z: float = Z_POWER_80) -> int:
    """Pairs needed for a paired test of a difference delta in marginal proportions, given the discordant
    fraction p_discord (Connor-type approximation): n = ((z_a sqrt(pd) + z_b sqrt(pd - delta^2)) / delta)^2."""
    za = Z[alpha] if alpha in Z else Z[0.05]
    return math.ceil(((za * math.sqrt(p_discord) + power_z * math.sqrt(p_discord - delta * delta)) / delta) ** 2)


def main() -> None:
    print("H1: smallest n with zero events and 95% CP upper bound < 5%:", min_n_zero_events(0.05))
    for n in (72, 100, 186):
        print(f"  n={n}: CP upper bound {100 * cp_upper_zero(n):.2f}%")
    for name in REG_FILES:
        n_pairs, b, c = discordance(name)
        pd = (b + c) / n_pairs
        delta = (b - c) / n_pairs
        print(f"H2 {name}: pairs={n_pairs} A0-only={b} SPOT-only={c} discordant={pd:.4f} delta={delta:.4f}")
        for target in (0.10,):
            for alpha in (0.05, 0.0125):
                print(f"  reduction {target:.2f}, alpha {alpha}: pairs needed at 80% power = {mcnemar_pairs(target, pd, alpha)}")


if __name__ == "__main__":
    main()
