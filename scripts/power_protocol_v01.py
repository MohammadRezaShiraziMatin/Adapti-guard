"""Design arithmetic for docs/protocols/CONFIRMATORY_PROTOCOL_DRAFT_v0.1.md. Offline; reads committed files only.

Endpoints. The committed InjecAgent records have no executed-call field (per-episode keys: first_attacker_tool,
any_attacker_tool, attacker_tools, finish, http, cost, ...). The H2 power below is therefore computed on the
PROPOSAL-level endpoint (first_attacker_tool), which is the only endpoint the committed records support. Executed-
endpoint power is reported as NOT AVAILABLE, not inferred.

Costs. One rule for every InjecAgent target: per-episode cost = total `cost` / number of priced episodes in ONE file,
chosen as the registered run where it exists (llama-4-maverick, qwen3.8-flash) and otherwise the InjecAgent panel
calibration file (deepseek-v4.1-flash, glm-4.7, gpt-5.6-sol). Hard-set costs in calibration.json are not used.

Formulas are standard and are tested in tests/test_protocol_power_v01.py against independent routes.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "experiments/external/injecagent_registered_20261001"
CAL = ROOT / "experiments/external/injecagent_panel_calib_20261001"

# target -> (file used for cost and discordance, path relative to the registered/panel directory)
COST_FILE = {
    "meta-llama/llama-4-maverick": REG / "meta-llama__llama-4-maverick.json",
    "qwen/qwen3.8-flash": REG / "qwen__qwen3.8-flash.json",
    "deepseek/deepseek-v4.1-flash": CAL / "deepseek__deepseek-v4.1-flash.json",
    "z-ai/glm-4.7": CAL / "z-ai__glm-4.7.json",
    "openai/gpt-5.6-sol": CAL / "openai__gpt-5.6-sol.json",
}
H2_TARGETS = {"meta-llama/llama-4-maverick": REG / "meta-llama__llama-4-maverick.json",
              "qwen/qwen3.8-flash": REG / "qwen__qwen3.8-flash.json"}
EXECUTED_FIELD = None  # no executed-call field in the committed records (checked by tests)

Z = {0.05: 1.959964, 0.025: 2.241403, 0.0125: 2.497705, 0.01: 2.575829}  # two-sided normal quantiles
Z_POWER_80 = 0.841621
EPISODES_PER_N = lambda n: 3 * n + 40  # arms A0, SPOT_TOOL, A0_REP per case, plus NOINJ (40)
N_OPTIONS = (72, 100, 150, 186)


def cp_upper_zero(n: int, alpha: float = 0.05) -> float:
    """Two-sided (1 - alpha) Clopper-Pearson upper bound for 0 events in n trials: 1 - (alpha/2)^(1/n)."""
    return 1.0 - (alpha / 2.0) ** (1.0 / n)


def min_n_zero_events(threshold: float, alpha: float = 0.05) -> int:
    n = 1
    while cp_upper_zero(n, alpha) >= threshold:
        n += 1
    return n


def proposal_discordance(path: Path) -> tuple[int, int, int]:
    """(n_pairs, A0-only, SPOT-only) on first_attacker_tool (proposal level)."""
    eps = json.loads(path.read_text())["episodes"]
    a0 = {e["case_id"]: int(e["first_attacker_tool"]) for e in eps if e["arm"] == "A0"}
    sp = {e["case_id"]: int(e["first_attacker_tool"]) for e in eps if e["arm"] == "SPOT_TOOL"}
    b = sum(1 for c in a0 if a0[c] == 1 and sp[c] == 0)
    c = sum(1 for k in a0 if a0[k] == 0 and sp[k] == 1)
    return len(a0), b, c


def executed_discordance(path: Path):
    """Not available: the committed records carry no executed-call field. Returns None."""
    eps = json.loads(path.read_text())["episodes"]
    if any("executed" in k for e in eps for k in e):
        raise RuntimeError("an executed-call field now exists; update this function and the protocol")
    return None


def mcnemar_pairs(delta: float, p_discord: float, alpha: float, power_z: float = Z_POWER_80) -> int:
    """Pairs for a paired test of a marginal difference delta, discordant fraction p_discord (Connor-type):
    n = ((z_a sqrt(pd) + z_b sqrt(pd - delta^2)) / delta)^2."""
    za = Z[alpha]
    return math.ceil(((za * math.sqrt(p_discord) + power_z * math.sqrt(p_discord - delta * delta)) / delta) ** 2)


def per_episode_cost(path: Path) -> tuple[int, int, float, float]:
    """(episodes, priced episodes, total USD over priced episodes, USD per priced episode)."""
    eps = json.loads(path.read_text())["episodes"]
    priced = [e["cost"] for e in eps if "cost" in e]
    return len(eps), len(priced), sum(priced), sum(priced) / len(priced)


def multiplicity_table() -> dict[str, dict[str, float]]:
    """Per-test alpha under Bonferroni for each panel option; the closed model is in or out per option.
    Holm uses the same first-step threshold; its later steps are alpha/(k-i+1) for k tests."""
    return {
        "P-A two targets (both open)": {"family": 2, "bonferroni_alpha": 0.05 / 2},
        "P-B five targets, closed model in H2 family": {"family": 5, "bonferroni_alpha": 0.05 / 5},
        "P-B five targets, closed model out of H2 family (4 open)": {"family": 4, "bonferroni_alpha": 0.05 / 4},
        "P-C four open targets": {"family": 4, "bonferroni_alpha": 0.05 / 4},
    }


def cost_table() -> dict[str, dict[str, float]]:
    """USD per option (episodes per target = 3n + 40) for each target, using the rule above."""
    out: dict[str, dict[str, float]] = {}
    for n in N_OPTIONS:
        row = {}
        for target, path in COST_FILE.items():
            _, _, _, rate = per_episode_cost(path)
            row[target] = round(EPISODES_PER_N(n) * rate, 4)
        out[f"n={n}"] = row
    return out


def main() -> None:
    print("H1: smallest n with zero events and 95% CP upper bound < 5%:", min_n_zero_events(0.05))
    for n in (72, 100, 150, 186):
        print(f"  n={n}: CP upper bound {100 * cp_upper_zero(n):.2f}%")
    print("H2 endpoint: PROPOSAL level (first_attacker_tool). Executed endpoint: not available in committed records.")
    for target, path in H2_TARGETS.items():
        n_pairs, b, c = proposal_discordance(path)
        pd = (b + c) / n_pairs
        delta = (b - c) / n_pairs
        print(f"  {target}: pairs={n_pairs} A0-only={b} SPOT-only={c} discordant={pd:.4f} delta={delta:.4f}")
        for alpha in (0.05, 0.025, 0.0125, 0.01):
            print(f"    reduction 0.10, alpha {alpha}: pairs needed at 80% power = {mcnemar_pairs(0.10, pd, alpha)}")
    print("Costs (USD per target, episodes = 3n+40, rule: one file per target):")
    for k, row in cost_table().items():
        print(" ", k, row)


if __name__ == "__main__":
    main()
