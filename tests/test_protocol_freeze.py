"""Freeze record for the confirmatory protocol (author sign-off 2026-10-11). Offline."""
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/protocols/CONFIRMATORY_PROTOCOL_DRAFT_v0.1.md"
FREEZE = ROOT / "docs/protocols/CONFIRMATORY_PROTOCOL_FROZEN.sha256"


def test_the_frozen_sha256_matches_the_protocol_file():
    line = FREEZE.read_text().strip()
    recorded, name = line.split("  ", 1)
    assert name == "docs/protocols/CONFIRMATORY_PROTOCOL_DRAFT_v0.1.md"
    assert hashlib.sha256(PROTOCOL.read_bytes()).hexdigest() == recorded


def test_the_protocol_status_is_frozen_not_registered_and_not_proposed():
    text = PROTOCOL.read_text()
    assert "**Status: FROZEN. NOT REGISTERED.**" in text
    assert "Author sign-off recorded 2026-10-11" in text
    assert "PROPOSED" not in text
    assert not re.search(r"awaiting (author )?sign-off", text)
