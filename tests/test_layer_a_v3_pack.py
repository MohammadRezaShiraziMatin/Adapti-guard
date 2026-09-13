"""Offline checks for the Layer A v3 frozen attack pack."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "datasets" / "frozen" / "layer_a_v3"

REQUIRED_ATK_META = (
    "attack_family",
    "attack_subtype",
    "direct_or_indirect",
    "single_or_multi_turn",
    "source_type",
    "expected_behavior",
    "target_behavior",
    "difficulty",
    "provenance",
    "generation_method",
    "seed",
    "canary",
    "mechanism",
    "construction",
)

FAMILIES = {
    "DIRECT_INJECTION",
    "INDIRECT_INJECTION",
    "OBFUSCATED_INJECTION",
    "MULTI_TURN_INJECTION",
}


def _load(name: str) -> list[dict]:
    path = PACK / name
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _rows() -> list[dict]:
    return _load("dataset.jsonl")


def test_pack_files_exist():
    for name in (
        "dataset.jsonl",
        "test.jsonl",
        "train.jsonl",
        "dev.jsonl",
        "test_split.jsonl",
        "DATASET_CARD.md",
        "hashes.sha256",
        "manifest.json",
        "README.md",
    ):
        assert (PACK / name).is_file(), name


def test_dataset_and_test_are_byte_identical():
    assert (PACK / "dataset.jsonl").read_bytes() == (PACK / "test.jsonl").read_bytes()


def test_counts_80_80():
    rows = _rows()
    assert len(rows) == 160
    attacks = [r for r in rows if r["label"] == "attack"]
    benign = [r for r in rows if r["label"] == "benign"]
    assert len(attacks) == 80
    assert len(benign) == 80


def test_train_dev_test_sizes():
    rows = _rows()
    by_split = Counter(r["split"] for r in rows)
    assert by_split["train"] == 40
    assert by_split["dev"] == 40
    assert by_split["test"] == 80

    for split, path, n in (
        ("train", "train.jsonl", 40),
        ("dev", "dev.jsonl", 40),
        ("test", "test_split.jsonl", 80),
    ):
        split_rows = _load(path)
        assert len(split_rows) == n
        assert all(r["split"] == split for r in split_rows)
        assert sum(1 for r in split_rows if r["label"] == "attack") == n // 2
        assert sum(1 for r in split_rows if r["label"] == "benign") == n // 2


def test_unique_ids_and_exact_bodies():
    rows = _rows()
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids))
    assert all(i.startswith("la_v3_atk_") or i.startswith("la_v3_ben_") for i in ids)
    bodies = [
        hashlib.sha256(
            (r.get("prompt", "") + "\n" + (r.get("context") or "")).encode()
        ).hexdigest()
        for r in rows
    ]
    assert len(bodies) == len(set(bodies))


def test_required_metadata_on_attacks():
    for r in _rows():
        if r["label"] != "attack":
            continue
        meta = r.get("metadata") or {}
        for field in REQUIRED_ATK_META:
            assert field in meta, f"{r['id']} missing {field}"
        assert meta["difficulty"] in {"D1", "D2", "D3", "D4"}
        assert meta["attack_family"] in FAMILIES
        assert r.get("success_condition")
        sc_meta = meta.get("success_condition")
        assert sc_meta is None or len(str(sc_meta)) > 10


def test_hard_negative_present_on_some_benign():
    benign = [r for r in _rows() if r["label"] == "benign"]
    assert all("hard_negative" in (r.get("metadata") or {}) for r in benign)
    hn = [r for r in benign if r["metadata"]["hard_negative"] is True]
    ordinary = [r for r in benign if r["metadata"]["hard_negative"] is False]
    assert len(hn) == 40
    assert len(ordinary) == 40
    assert all(r["metadata"].get("canary") is None for r in benign)


def test_family_coverage():
    attacks = [r for r in _rows() if r["label"] == "attack"]
    fam = Counter(r["metadata"]["attack_family"] for r in attacks)
    for family in FAMILIES:
        assert fam[family] >= 1, family
    test_attacks = [r for r in attacks if r["split"] == "test"]
    test_fam = {r["metadata"]["attack_family"] for r in test_attacks}
    assert test_fam == FAMILIES


def test_hash_file_matches():
    raw = (PACK / "hashes.sha256").read_text(encoding="utf-8").strip().splitlines()
    listed = {}
    for line in raw:
        digest, name = line.split()
        listed[name] = digest
    for name in (
        "dataset.jsonl",
        "test.jsonl",
        "train.jsonl",
        "dev.jsonl",
        "test_split.jsonl",
    ):
        got = hashlib.sha256((PACK / name).read_bytes()).hexdigest()
        assert listed[name] == got, name


def test_manifest_pack_id_and_hashes():
    manifest = json.loads((PACK / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["pack_id"] == "layer_a_v3.0"
    assert manifest["seed"] == 42
    dataset_sha = hashlib.sha256((PACK / "dataset.jsonl").read_bytes()).hexdigest()
    test_split_sha = hashlib.sha256((PACK / "test_split.jsonl").read_bytes()).hexdigest()
    assert manifest["dataset_sha256"] == dataset_sha
    assert manifest["test_split_sha256"] == test_split_sha


def test_multi_turn_context_and_schema_fields():
    multi = [
        r
        for r in _rows()
        if r["label"] == "attack"
        and r["metadata"]["attack_family"] == "MULTI_TURN_INJECTION"
    ]
    assert len(multi) >= 12
    for r in multi:
        assert r["metadata"]["single_or_multi_turn"] == "multi"
        assert r.get("context")
        assert "User:" in r["context"] or "Assistant:" in r["context"]
        for key in (
            "id",
            "category",
            "attack_type",
            "prompt",
            "label",
            "split",
            "success_condition",
        ):
            assert key in r
