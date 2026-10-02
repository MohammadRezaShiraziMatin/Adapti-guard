"""Every key number in the ledger must appear in the assembled manuscript."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "docs/paper/negative_result"


def test_ledger_strings_in_manuscript():
    ms = (DIR / "MANUSCRIPT_DRAFT_v1.md").read_text(encoding="utf-8")
    rows = [ln for ln in (DIR / "NUMBERS_LEDGER.md").read_text(encoding="utf-8").splitlines() if ln.startswith("|")]
    checked = 0
    for ln in rows[2:]:
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if len(cells) < 2:
            continue
        val = cells[1].strip("`")
        if val:
            assert val in ms, f"{cells[0]}: {val!r} missing from manuscript"
            checked += 1
    assert checked >= 20
