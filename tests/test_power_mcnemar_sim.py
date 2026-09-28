"""CLI for power_mcnemar_sim — Holm alpha flag."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_power_module():
    spec = importlib.util.spec_from_file_location(
        "power_mcnemar_sim",
        ROOT / "scripts" / "power_mcnemar_sim.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_build_power_tables_default_alpha_is_holm_four():
    mod = _load_power_module()
    out = mod.build_power_tables(n_sim=1000, seed=20260927, alpha=0.05 / 4)
    assert out["alpha_per_model"] == 0.0125
    assert out["holm_family"] == 4
    assert out["tables"]["p1_0.12"][0]["alpha_holm_step1_two_sided"] == 0.0125


def test_build_power_tables_custom_alpha():
    mod = _load_power_module()
    alpha = 0.05 / 3
    out = mod.build_power_tables(n_sim=1000, seed=20260927, alpha=alpha)
    assert out["alpha_per_model"] == alpha
    assert out["holm_family"] == 3
