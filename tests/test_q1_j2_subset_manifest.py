"""Offline checks for Q1 D13 J2 preregistered subset manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

MANIFEST = Path("configs/q1/manifests/j2_preregistered_subset.jsonl")
CONTRACT = Path("configs/q1_evaluation_contract.yaml")
SEED = 42

TARGETS = [
    "qwen/qwen3-30b-a3b",
    "google/gemma-4-31b-it",
    "meta-llama/llama-3.3-70b-instruct",
    "deepseek/deepseek-v3.2",
]
PER_TARGET = [13, 12, 12, 12]


def _load_manifest_rows():
    lines = MANIFEST.read_text(encoding="utf-8").splitlines()
    assert lines
    meta = json.loads(lines[0])["_manifest"]
    pairs = [json.loads(line) for line in lines[1:]]
    return meta, pairs


def test_d13_manifest_exists_and_sha_matches_contract():
    contract = yaml.safe_load(CONTRACT.read_text(encoding="utf-8"))
    d13 = contract["q1_decision_sheet_v2"]["j2_subset_d13"]
    fam = contract["q1_decision_sheet_v2"]["primary_holm_family"]
    assert fam["primary_family_paired_comparisons"] == 244
    assert fam["primary_family_causal_episodes"] == 488
    assert d13["subset_pairs"] == 49
    assert d13["j2_episodes"] == 98
    assert MANIFEST.as_posix() == d13["manifest_path"]
    actual_sha = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
    assert actual_sha == d13["manifest_sha256"]
    assert "frozen/vnext_confirm_v1" not in d13["manifest_path"]

    meta, pairs = _load_manifest_rows()
    assert meta["subset_pairs"] == 49
    assert meta["j2_episodes"] == 98
    assert len(pairs) == 49


def test_d13_stratified_selection_rule():
    ds_path = Path("datasets/frozen/vnext_confirm_v1/dataset.jsonl")
    attack_ids = []
    for line in ds_path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("label") == "attack":
            attack_ids.append(row["id"])
    assert len(attack_ids) == 61

    def rank_attack(target: str, attack_id: str) -> str:
        return hashlib.sha256(f"{SEED}|{target}|{attack_id}".encode()).hexdigest()

    expected = []
    for target, n_take in zip(TARGETS, PER_TARGET):
        ranked = sorted(attack_ids, key=lambda a: rank_attack(target, a))
        for aid in ranked[:n_take]:
            expected.append((aid, target))
    expected.sort(key=lambda p: (TARGETS.index(p[1]), rank_attack(p[1], p[0])))

    _, manifest_pairs = _load_manifest_rows()
    actual = [(p["attack_id"], p["target_model_id"]) for p in manifest_pairs]
    assert actual == expected
