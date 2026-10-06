"""Tests for the E1 interval and E3 cluster-power analyses (offline; they read committed counts, traces and artifacts only)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import e1_interval_estimates as e1  # noqa: E402
import e3_cluster_power as cp  # noqa: E402

ART = ROOT / "docs/research/artifacts"


def test_e1_kappa_reproduces_the_stored_values_and_intervals_contain_them():
    src = json.loads((ART / "tracks_ab_deterministic_rescoring_20260930.json").read_text())
    out = json.loads((ART / "e1_interval_estimates_20261006.json").read_text())
    for track, key in (("A", "A_VNEXT"), ("B", "B_PHASE1")):
        for arm, v in src[key]["arms"].items():
            got = out["arms"][f"{track}:{arm}"]
            if v["kappa_attack"] is None or got["kappa"] is None:
                continue
            assert got["kappa"] == pytest.approx(v["kappa_attack"], abs=1e-4)
            lo, hi = got["kappa_ci95"]
            assert lo <= got["kappa"] <= hi
    assert e1.kappa(40, 18, 0, 3) == pytest.approx(0.1794, abs=1e-4)
    for kind in ("paired_judge", "paired_deterministic"):
        eff = out["paired_effects"][f"B:{kind}"]
        assert eff["ci95"][0] <= eff["delta_hat"] <= eff["ci95"][1]


def test_e3_baselines_match_the_reported_undefended_rates():
    b = cp.baselines()
    assert len(b) == 7 and b.mean() == pytest.approx(57 / 168, abs=1e-3)
    assert sorted(round(float(x) * 24) for x in b) == [0, 4, 5, 8, 8, 9, 23]  # 0/24 ... 23/24 as in section 6.3


def test_ceiling_model_respects_the_ceiling_and_is_calibrated_and_monotone():
    b = cp.baselines()
    rng = np.random.default_rng(1)
    red = cp.simulate_ceiling(rng, np.array([0.0, 0.0]), 24, 1.0, 0.0, cp.Q, 200)
    assert (red == 0).all()  # a family with no undefended attacks cannot show a reduction (nor a change)
    full = cp.simulate_ceiling(rng, b, 24, 1.0, 0.0, 0.0, 400)
    assert np.allclose(full.mean(0), b, atol=0.03)  # complete removal removes about the whole undefended rate and not more
    assert 0.01 <= cp.power_ceiling(b, 0.0, 0.0, cp.Q, 5, 4000) <= 0.09  # type-I error near 0.05
    p = [cp.power_ceiling(b, r, 0.0, cp.Q, 5, 4000) for r in (0.25, 0.5, 1.0)]
    assert p[0] < p[1] <= p[2] + 0.02
    assert cp.power_ceiling(b, 0.5, 0.0, cp.Q, 9, 2000) == cp.power_ceiling(b, 0.5, 0.0, cp.Q, 9, 2000)  # deterministic given the seed


def test_committed_power_artifact_states_that_spread_assumptions_are_not_estimates():
    d = json.loads((ART / "e3_cluster_power_20261006.json").read_text())
    assert d["design"]["sigma_and_tau_are_assumptions"] is True and d["ceiling"]["sigma0.25"]["type_I_error"] is None
    assert d["ceiling"]["sigma0.00"]["power_rho_1.00"] < 0.85  # even complete removal is not detected reliably with seven families
