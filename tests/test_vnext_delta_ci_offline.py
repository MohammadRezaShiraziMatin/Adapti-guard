"""Offline Track A delta_hat CI from McNemar contingency (no LLM)."""

from __future__ import annotations

import json
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adapti_guard.evaluation.statistics import (  # noqa: E402
    delta_hat_ci_bootstrap_from_mcnemar_contingency,
    delta_hat_from_mcnemar_contingency,
)

VERDICT = (
    ROOT
    / "experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/verdict.json"
)
ARTIFACT = ROOT / "docs/paper/q1_findings/artifacts/vnext_delta_ci_offline.json"
SCRIPT = ROOT / "scripts/recompute_vnext_delta_ci.py"


def test_delta_hat_point_matches_verdict():
    data = json.loads(VERDICT.read_text(encoding="utf-8"))
    b10, b01 = int(data["b10"]), int(data["b01"])
    n = 61
    point = delta_hat_from_mcnemar_contingency(b10, b01, n)
    assert b10 == 5 and b01 == 0
    assert abs(point - float(data["delta_hat"])) < 1e-9
    assert abs(point - 5 / 61) < 1e-9


def test_bootstrap_ci_contains_point_and_below_msid_upper():
    ci = delta_hat_ci_bootstrap_from_mcnemar_contingency(5, 0, 61, seed=42)
    point = ci["delta_hat"]
    assert ci["ci_lower"] <= point <= ci["ci_upper"]
    # MSID 0.20 — upper CI should remain below useful-intervention bar (sanity on locked counts)
    assert ci["ci_upper"] < 0.20


def test_recompute_script_writes_artifact(tmp_path):
    out = tmp_path / "ci.json"
    subprocess.run(
        [sys.executable, str(SCRIPT), "--out", str(out)],
        cwd=ROOT,
        check=True,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "src")},
    )
    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["label"] == "recomputed_offline_not_in_original_AUDIT"
    assert record["inputs"] == {"b10": 5, "b01": 0, "n_attack": 61}
    lo = record["delta_hat_ci_95"]["lower"]
    hi = record["delta_hat_ci_95"]["upper"]
    assert lo < record["delta_hat_point"] < hi


@pytest.mark.skipif(not VERDICT.is_file(), reason="VNEXT verdict missing")
def test_committed_artifact_matches_script(tmp_path):
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "src")}
    out = tmp_path / "fresh.json"
    subprocess.run(
        [sys.executable, str(SCRIPT), "--out", str(out)],
        cwd=ROOT,
        check=True,
        env=env,
    )
    expected = json.loads(out.read_text(encoding="utf-8"))
    if not ARTIFACT.is_file():
        pytest.skip("committed artifact not checked in yet")
    on_disk = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert on_disk["delta_hat_ci_95"] == expected["delta_hat_ci_95"]
    assert on_disk["inputs_sha256"] == expected["inputs_sha256"]
