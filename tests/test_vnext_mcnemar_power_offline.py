"""Offline McNemar power / sensitivity for Track A (no LLM)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.statistics import (  # noqa: E402
    mcnemar_exact_p_value,
    track_a_mcnemar_power_sensitivity,
)

SCRIPT = ROOT / "scripts/recompute_vnext_mcnemar_power.py"
ARTIFACT = ROOT / "docs/paper/q1_findings/artifacts/vnext_track_a_power_sensitivity.json"
DELTA_CI = ROOT / "docs/paper/q1_findings/artifacts/vnext_delta_ci_offline.json"


def test_observed_p_matches_audit():
    assert abs(mcnemar_exact_p_value(5, 0) - 0.0625) < 1e-9


def test_thresholds_n61_b01_zero():
    out = track_a_mcnemar_power_sensitivity(61, b01_assumed=0, observed_b10=5)
    th = out["thresholds_b01_fixed"]
    assert th["min_b10_significant"] == 6
    assert th["min_b10_msid_point"] == 13
    obs = out["observed_track_a"]
    assert obs["significant_at_alpha"] is False
    assert obs["msid_met"] is False


def test_power_at_msid_high_under_simplified_model():
    out = track_a_mcnemar_power_sensitivity(61, b01_assumed=0, alternative_delta=0.20)
    power = out["power_mcnemar_significance"]["theta_0.2"]
    assert power > 0.95


def test_script_writes_artifact_with_delta_ci_reference(tmp_path):
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "src")}
    out = tmp_path / "power.json"
    subprocess.run(
        [sys.executable, str(SCRIPT), "--out", str(out)],
        cwd=ROOT,
        check=True,
        env=env,
    )
    record = json.loads(out.read_text(encoding="utf-8"))
    assert "delta_hat_ci_reference" in record
    assert record["delta_hat_ci_reference"]["ci_95"]["upper"] == pytest.approx(
        0.163934, rel=1e-4
    )


@pytest.mark.skipif(not ARTIFACT.is_file(), reason="artifact not committed")
def test_committed_power_artifact(tmp_path):
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "src")}
    out = tmp_path / "fresh.json"
    subprocess.run(
        [sys.executable, str(SCRIPT), "--out", str(out)],
        cwd=ROOT,
        check=True,
        env=env,
    )
    assert json.loads(out.read_text())["thresholds_b01_fixed"] == json.loads(
        ARTIFACT.read_text()
    )["thresholds_b01_fixed"]
