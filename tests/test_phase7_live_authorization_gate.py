"""Phase 7 authorization gate — template must remain BLOCKED."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_template_budget_not_authorized():
    r = subprocess.run(
        [sys.executable, "scripts/validate_phase7_live_authorization.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode != 0
    data = json.loads(r.stdout)
    assert data["live_execution_gate"] == "PHASE7_LIVE_BLOCKED"
    assert data["api_spend_permitted"] is False


def test_pending_placeholders_block_live():
    data = json.loads((ROOT / "docs/research/PHASE7_LIVE_AUTHORIZATION.json").read_text())
    assert "pending" in " ".join(data.get("errors", [])).lower() or data["live_execution_gate"] == "PHASE7_LIVE_BLOCKED"
