"""Offline Q1 findings claim/number verifier."""

from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "docs/paper/q1_findings/verify_q1_findings_facts.py"


def test_verify_q1_findings_facts_pass():
    ns = runpy.run_path(str(SCRIPT), run_name="q1_verify")
    ns["main"]()
