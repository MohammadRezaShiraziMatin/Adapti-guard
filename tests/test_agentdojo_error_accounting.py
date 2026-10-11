"""Independent recount of the AgentDojo error-accounting numbers in SECTION_AGENTDOJO_ERROR_ACCOUNTING.md.

Reads the two committed episode CSVs directly. It does not import scripts/agentdojo_error_ledger.py, so a bug there cannot make this pass.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "verify/agentdojo"


def _rows(name):
    with (DIR / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _flag(v):
    return v.strip().lower() in ("true", "1")


def test_llama_published_and_unresolved_counts():
    rows = _rows("episodes_llama3_70b_important_instructions.csv")
    assert len(rows) == 629
    errored = [r for r in rows if _flag(r["errored"])]
    assert len(errored) == 35
    assert sum(_flag(r["security"]) for r in rows) == 161
    kept = [r for r in rows if not _flag(r["errored"])]
    assert len(kept) == 594
    assert sum(_flag(r["security"]) for r in kept) == 126


def test_gpt4o_control_unchanged():
    rows = _rows("episodes_gpt4o_important_instructions.csv")
    assert len(rows) == 629
    assert not any(_flag(r["errored"]) for r in rows)
    assert sum(_flag(r["security"]) for r in rows) == 300


def test_subsection_states_the_counts():
    text = (ROOT / "docs/paper/negative_result/SECTION_AGENTDOJO_ERROR_ACCOUNTING.md").read_text(encoding="utf-8")
    for s in ("161/629", "126/594", "300/629", "### 6.6 External case: AgentDojo error accounting"):
        assert s in text
