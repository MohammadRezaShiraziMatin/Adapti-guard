"""Immutability checks for frozen P1 mechanism pack v1.0.0.

Does not modify packs. No LLM/API.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "datasets" / "frozen" / "p1_mechanism_v1.0.0"
CANDIDATE = ROOT / "datasets" / "candidates" / "p1_mechanism_v1"

EXPECTED_SHA = "1a0b0053c392e7b3e0727b92b4f088790abda001fd852ec1703c5ee0a67dd235"
HISTORICAL = {
    ROOT
    / "datasets/frozen/eval_v1/dataset.jsonl": "27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24",
    ROOT
    / "results/common_attack_stream.json": "d101f94d97e0a29e8b9f9cc4dacb92472e29cd9af403114cb09b8f1d50a06c47",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_frozen_pack_files_exist():
    for name in ("dataset.jsonl", "manifest.json", "hashes.sha256", "DATASET_CARD.md", "README.md"):
        assert (FROZEN / name).is_file(), name


def test_frozen_dataset_sha_matches_expected():
    assert _sha(FROZEN / "dataset.jsonl") == EXPECTED_SHA


def test_candidate_and_frozen_dataset_bytes_identical():
    assert (CANDIDATE / "dataset.jsonl").read_bytes() == (FROZEN / "dataset.jsonl").read_bytes()


def test_frozen_manifest_status():
    man = json.loads((FROZEN / "manifest.json").read_text(encoding="utf-8"))
    assert man["status"] == "FROZEN"
    assert man["live_evaluated"] is False
    assert man["version"] == "p1_mechanism_v1.0.0"
    assert man["dataset_sha256"] == EXPECTED_SHA
    assert man["attack_count"] == 44
    assert man["benign_twin_count"] == 44
    assert man["hard_negative_count"] == 8
    assert man["mechanism_count"] == 22
    assert man["attacks_per_leaf"] == 2
    assert "C4" in man["out_of_scope_families"]
    assert len(man["known_limitations"]) >= 10


def test_hashes_sidecar_lists_dataset_digest():
    listed = (FROZEN / "hashes.sha256").read_text(encoding="utf-8").split()[0]
    assert listed == EXPECTED_SHA


def test_historical_frozen_hashes_unchanged():
    for path, expected in HISTORICAL.items():
        assert _sha(path) == expected, path


def test_candidate_manifest_remains_candidate_provenance():
    man = json.loads((CANDIDATE / "manifest.json").read_text(encoding="utf-8"))
    assert man["status"] == "CANDIDATE"
    assert man["live_evaluated"] is False
