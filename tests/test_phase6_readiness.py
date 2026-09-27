"""Phase 6 pre-experiment validation (no live runs)."""
import json
from pathlib import Path

import yaml

from adapti_guard.evaluation.condition_resolver import resolve_condition

MATRIX = Path("docs/research/EXPERIMENT_MATRIX.yaml")
READINESS = Path("docs/research/PHASE6_CONDITION_READINESS.yaml")


def test_matrix_and_readiness_same_condition_ids():
    rows = yaml.safe_load(MATRIX.read_text())["rows"]
    ready = yaml.safe_load(READINESS.read_text())["rows"]
    assert {r["condition_id"] for r in rows} == {r["condition_id"] for r in ready}


def test_confirmatory_rows_target_ne_judge():
    rows = yaml.safe_load(MATRIX.read_text())["rows"]
    for row in rows:
        if not row.get("target_ne_judge"):
            continue
        judge = row.get("judge_id")
        if judge in (None, "n/a", "mock_judge"):
            continue
        assert row["target_model_id"] != judge


def test_offline_conditions_resolve():
    for cid in (
        "COND-E1-STATEFUL-OFFLINE",
        "COND-E2-ADAPTIVE-OFFLINE",
        "COND-E3-AGENT-OFFLINE",
    ):
        _row, ctx = resolve_condition(cid, matrix_path=MATRIX)
        assert ctx.evidence_status == "OFFLINE"


def test_phase6_completion_json_exists_after_validator():
    p = Path("docs/research/PHASE6_COMPLETION.json")
    if p.is_file():
        data = json.loads(p.read_text())
        assert data.get("phase7_live_gate") == "PHASE7_LIVE_BLOCKED"
