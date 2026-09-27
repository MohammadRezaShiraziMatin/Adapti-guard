"""Phase 7 authorization contract schema (template stays blocked)."""
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_budget_yaml_schema_v2_fields():
    auth = yaml.safe_load((ROOT / "docs/research/live_budget_authorization.yaml").read_text())
    assert auth["schema_version"] >= 2
    assert auth["api_spend_permitted"] is False
    assert len(auth["target_models"]) == 4
    assert auth["judge_model"]["config_key_hint"] == "judge_primary"
    for m in auth["target_models"]:
        assert m["lifecycle"] == "PLANNED"


def test_validator_blocked_with_complete_schema():
    r = subprocess.run(
        [sys.executable, "scripts/validate_phase7_live_authorization.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    data = json.loads(r.stdout)
    assert data["contract_schema_complete"] is True
    assert data["live_execution_gate"] == "PHASE7_LIVE_BLOCKED"
    assert data["api_spend_permitted"] is False
