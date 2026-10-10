"""Checks for scripts/power_protocol_v01.py. Expected values come from independent routes (SciPy beta quantile,
the textbook McNemar formula written out in the test, and a direct count of the committed records), not from the
functions under test."""
import json
import math
from pathlib import Path

from scipy.stats import beta, norm

import importlib.util

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("power", ROOT / "scripts" / "power_protocol_v01.py")
power = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(power)


def test_cp_upper_zero_matches_scipy_beta_quantile():
    for n in (40, 72, 100, 186):
        expected = beta.ppf(0.975, 1, n)  # Clopper-Pearson upper bound for x = 0, two-sided 95%
        assert abs(power.cp_upper_zero(n) - expected) < 1e-12


def test_min_n_is_72_and_is_tight():
    n = power.min_n_zero_events(0.05)
    assert n == 72
    assert beta.ppf(0.975, 1, n) < 0.05 <= beta.ppf(0.975, 1, n - 1)


def test_mcnemar_pairs_matches_textbook_formula():
    delta, pd = 0.10, 0.20
    za, zb = norm.ppf(0.975), norm.ppf(0.80)
    expected = math.ceil(((za * math.sqrt(pd) + zb * math.sqrt(pd - delta * delta)) / delta) ** 2)
    assert power.mcnemar_pairs(delta, pd, 0.05) == expected


def test_discordance_matches_direct_count_of_committed_records():
    eps = json.loads((ROOT / "experiments/external/injecagent_registered_20261001/meta-llama__llama-4-maverick.json").read_text())["episodes"]
    a0 = {e["case_id"]: e["first_attacker_tool"] for e in eps if e["arm"] == "A0"}
    sp = {e["case_id"]: e["first_attacker_tool"] for e in eps if e["arm"] == "SPOT_TOOL"}
    b = sum(1 for k in a0 if a0[k] and not sp[k])
    c = sum(1 for k in a0 if not a0[k] and sp[k])
    assert power.discordance("llama-4-maverick") == (len(a0), b, c)
