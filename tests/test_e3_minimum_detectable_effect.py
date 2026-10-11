"""The E3 family-level minimum detectable effect (manuscript §8.2). Offline; reads committed files only."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("mde", ROOT / "scripts" / "e3_minimum_detectable_effect.py")
M = importlib.util.module_from_spec(_spec)
sys.modules["mde"] = M
_spec.loader.exec_module(M)
OUT = ROOT / "docs/research/artifacts/e3_minimum_detectable_effect.json"


def test_committed_output_is_exactly_what_the_script_produces():
    assert OUT.read_text() == json.dumps(M.build(), indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def test_seven_families_and_the_committed_pair_counts():
    d = M.build()
    assert d["arms"]["B3"]["families"] == d["arms"]["CORE"]["families"] == 7
    assert (d["arms"]["B3"]["pairs"], d["arms"]["CORE"]["pairs"]) == (167, 168)
    assert sorted(d["arms"]["B3"]["pairs_per_family"]) == [23] + [24] * 6


def test_the_mde_values_quoted_in_the_manuscript():
    d = M.build()
    assert round(d["arms"]["B3"]["mde"] * 100, 1) == 5.6
    assert round(d["arms"]["CORE"]["mde"] * 100, 1) == 4.3


def test_zero_family_variance_gives_a_zero_mde_by_hand():
    # seven families with the same difference: sd = 0, so the MDE is 0 whatever the critical values are
    cells = {f"fam{i}|m": [0, 0, 24] for i in range(7)}
    assert M.mde_for_arm(cells)["mde"] == pytest.approx(0.0, abs=1e-15)


def test_a_hand_case_with_one_discordant_family():
    # six families with difference 0 and one with 1 event difference over 24 pairs: rates 0,...,0,1/24
    cells = {f"fam{i}|m": [0, 1 if i == 6 else 0, 24] for i in range(7)}
    rates = [0.0] * 6 + [1 / 24]
    sd = (sum((r - sum(rates) / 7) ** 2 for r in rates) / 6) ** 0.5
    got = M.mde_for_arm(cells)
    assert got["family_sd"] == pytest.approx(sd, rel=1e-12)
    assert got["mde"] == pytest.approx((got["t_two_sided_0_975"] + got["t_power_0_80"]) * sd / 7 ** 0.5, rel=1e-12)
