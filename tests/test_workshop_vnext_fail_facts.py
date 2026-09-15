"""Offline wrapper for workshop FAIL-fact verification.

No OpenRouter/LLM. Does not retune TEST, change N, or edit frozen packs.
"""

from __future__ import annotations

import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "docs" / "paper" / "workshop_vnext_fail" / "verify_manuscript_facts.py"


def test_verify_manuscript_facts_pass():
    ns = runpy.run_path(str(SCRIPT), run_name="workshop_verify")
    ns["main"]()
