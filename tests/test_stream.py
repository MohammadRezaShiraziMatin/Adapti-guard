"""Common attack stream invariants."""

import json
from collections import Counter
from pathlib import Path

STREAM_PATH = Path("results/common_attack_stream.json")

REQUIRED_FAMILIES = {
    "direct_injection",
    "indirect_injection",
    "context_manipulation",
    "tool_output_injection",
}


def test_common_stream_structure():
    assert STREAM_PATH.exists()
    stream = json.loads(STREAM_PATH.read_text(encoding="utf-8"))

    assert len(stream) == 100
    ids = [int(e["episode_id"]) for e in stream]
    assert ids == list(range(1, 101))
    assert len(set(ids)) == 100

    families = Counter(e["attack_family"] for e in stream)
    assert set(families) == REQUIRED_FAMILIES
    assert all(v == 25 for v in families.values())

    for episode in stream:
        assert str(episode["payload"]).strip()
        assert episode["attack_family"] in REQUIRED_FAMILIES
