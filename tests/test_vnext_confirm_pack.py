"""Offline checks for the VNEXT confirmation pack v1.

Deterministic local tests only. No LLM/API, no live eval, no Layer A TEST retune.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path
from unittest.mock import MagicMock

from src.adapti_guard.defense.tool_loop import extract_tool_request
from src.adapti_guard.evaluation.attack_success import evaluate_episode
from src.adapti_guard.evaluation.llm_judge import JudgeVerdict, LLMJudge
from src.adapti_guard.evaluation.target_model import MockTargetModel
from src.adapti_guard.experiments.defense_baselines import get_defense_fn

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "datasets" / "frozen" / "vnext_confirm_v1"
BUILDER = ROOT / "scripts" / "build_vnext_confirm_v1_pack.py"

LAYER_A_V3_TEST = ROOT / "datasets" / "frozen" / "layer_a_v3" / "test_split.jsonl"
LAYER_A_V3 = ROOT / "datasets" / "frozen" / "layer_a_v3" / "dataset.jsonl"
LAYER_A_V2 = ROOT / "datasets" / "frozen" / "layer_a_v2" / "dataset.jsonl"

LAYER_A_HASHES = {
    LAYER_A_V2: "76c60433d07258d06c5df451bfdd5be4d8ff08988b26c3ecea32ebc32d09ac33",
    LAYER_A_V3_TEST: "47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8",
    LAYER_A_V3: "abbc87134dc6563231aa422cb923226a5158d512c260a0ec17fd6997877632dd",
}

FAMILIES = {
    "DIRECT_OVERRIDE",
    "INDIRECT_RAG_DOC",
    "TOOL_OUTPUT_INJECTION",
    "MULTI_TURN_PERSISTENCE",
    "OBFUSCATION",
    "PRIVILEGE_EXFIL",
}

REQUIRED_ATK_META = (
    "attack_family",
    "attack_subtype",
    "attack_objective",
    "expected_behavior",
    "target_behavior",
    "difficulty",
    "mechanism",
    "tool_use",
    "hard_negative",
    "direct_or_indirect",
    "single_or_multi_turn",
    "source_type",
    "canary",
    "construction",
    "pack_id",
)


def _load_builder():
    spec = importlib.util.spec_from_file_location("build_vnext_confirm_v1_pack", BUILDER)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _load(name: str) -> list[dict]:
    path = PACK / name
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _rows() -> list[dict]:
    return _load("dataset.jsonl")


def _jsonl_ids(path: Path) -> set[str]:
    return {
        json.loads(line)["id"]
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def _listed_hashes() -> dict[str, str]:
    listed = {}
    for line in (PACK / "hashes.sha256").read_text(encoding="utf-8").strip().splitlines():
        digest, name = line.split()
        listed[name] = digest
    return listed


def test_pack_files_exist():
    for name in (
        "dataset.jsonl",
        "confirmation.jsonl",
        "DATASET_CARD.md",
        "hashes.sha256",
        "manifest.json",
        "README.md",
    ):
        assert (PACK / name).is_file(), name


def test_dataset_and_confirmation_are_byte_identical():
    assert (PACK / "dataset.jsonl").read_bytes() == (
        PACK / "confirmation.jsonl"
    ).read_bytes()


def test_counts_61_61():
    rows = _rows()
    assert len(rows) == 122
    attacks = [r for r in rows if r["label"] == "attack"]
    benign = [r for r in rows if r["label"] == "benign"]
    assert len(attacks) == 61
    assert len(benign) == 61
    assert all(r["split"] == "confirmation" for r in rows)


def test_unique_ids_and_bodies():
    rows = _rows()
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids))
    assert all(
        i.startswith("vnext_c1_atk_") or i.startswith("vnext_c1_ben_") for i in ids
    )
    assert not any(i.startswith("la_v2_") or i.startswith("la_v3_") for i in ids)
    bodies = [
        hashlib.sha256(
            (r.get("prompt", "") + "\n" + (r.get("context") or "")).encode()
        ).hexdigest()
        for r in rows
    ]
    assert len(bodies) == len(set(bodies))


def test_disjoint_from_layer_a_v3_test_split_ids():
    pack_ids = {r["id"] for r in _rows()}
    test_ids = _jsonl_ids(LAYER_A_V3_TEST)
    v3_ids = _jsonl_ids(LAYER_A_V3)
    v2_ids = _jsonl_ids(LAYER_A_V2)
    assert not (pack_ids & test_ids)
    assert not (pack_ids & v3_ids)
    assert not (pack_ids & v2_ids)
    assert any(i.startswith("la_v3_atk_") for i in test_ids)


def test_unique_objectives_and_mechanisms():
    attacks = [r for r in _rows() if r["label"] == "attack"]
    mechs = [r["metadata"]["mechanism"] for r in attacks]
    objs = [r["metadata"]["attack_objective"] for r in attacks]
    assert len(mechs) == len(set(mechs))
    assert len(objs) == len(set(objs))
    assert all(r.get("success_condition") for r in attacks)
    assert all(r["metadata"].get("expected_behavior") for r in attacks)
    assert all(r["metadata"].get("target_behavior") for r in attacks)


def test_family_coverage_balanced():
    attacks = [r for r in _rows() if r["label"] == "attack"]
    fam = Counter(r["metadata"]["attack_family"] for r in attacks)
    assert set(fam) == FAMILIES
    for family in FAMILIES:
        assert fam[family] >= 10, family
    assert fam["DIRECT_OVERRIDE"] == 11
    assert sum(fam.values()) == 61


def test_required_metadata_and_schema_fields():
    rows = _rows()
    for r in rows:
        for key in (
            "id",
            "category",
            "attack_type",
            "prompt",
            "context",
            "label",
            "split",
            "success_condition",
            "metadata",
        ):
            assert key in r, f"{r.get('id')} missing {key}"
        assert r["label"] in {"attack", "benign"}
    for r in rows:
        if r["label"] != "attack":
            continue
        meta = r["metadata"]
        for field in REQUIRED_ATK_META:
            assert field in meta, f"{r['id']} missing {field}"
        assert meta["difficulty"] in {"D1", "D2", "D3", "D4"}
        assert meta["attack_family"] in FAMILIES
        assert meta["tool_use"] is True
        assert r.get("tool_call") and meta.get("tool_call")
        assert "AG-V3-CANARY" not in (r["prompt"] + (r.get("context") or ""))


def test_hard_negatives_and_tool_benign():
    benign = [r for r in _rows() if r["label"] == "benign"]
    hn = [r for r in benign if r["metadata"]["hard_negative"] is True]
    ordinary_or_tool = [r for r in benign if r["metadata"]["hard_negative"] is False]
    tool_ben = [r for r in benign if r["metadata"].get("tool_use")]
    assert len(hn) == 25
    assert len(ordinary_or_tool) == 36
    assert len(tool_ben) == 21
    assert all(r["metadata"].get("canary") is None for r in benign)
    quoted_pi = [
        r
        for r in hn
        if "ignore" in (r["prompt"] + (r.get("context") or "")).lower()
        or "send_email" in (r["prompt"] + (r.get("context") or "")).lower()
        or "assistant" in (r.get("context") or "").lower()
    ]
    assert len(quoted_pi) >= 10


def test_multi_turn_context_present():
    multi = [
        r
        for r in _rows()
        if r["label"] == "attack"
        and r["metadata"]["attack_family"] == "MULTI_TURN_PERSISTENCE"
    ]
    assert len(multi) == 10
    for r in multi:
        assert r["metadata"]["single_or_multi_turn"] == "multi"
        assert r.get("context")
        assert "User:" in r["context"] and "Assistant:" in r["context"]


def test_hash_file_matches_bytes():
    listed = _listed_hashes()
    for name in ("dataset.jsonl", "confirmation.jsonl"):
        got = hashlib.sha256((PACK / name).read_bytes()).hexdigest()
        assert listed[name] == got, name
    assert listed["dataset.jsonl"] == listed["confirmation.jsonl"]


def test_hash_stability_rebuild_matches_frozen():
    mod = _load_builder()
    rebuilt = mod.serialize_records(mod.build_records())
    frozen = (PACK / "dataset.jsonl").read_text(encoding="utf-8")
    assert rebuilt == frozen
    digest = hashlib.sha256(rebuilt.encode("utf-8")).hexdigest()
    assert digest == _listed_hashes()["dataset.jsonl"]
    report = mod.validate_pack(mod.build_records())
    assert report["errors"] == []


def test_layer_a_frozen_hashes_unchanged():
    for path, expected in LAYER_A_HASHES.items():
        got = hashlib.sha256(path.read_bytes()).hexdigest()
        assert got == expected, path


def test_evaluate_episode_consumes_pack_row_without_llm():
    attack = next(r for r in _rows() if r["label"] == "attack" and r.get("tool_call"))
    judge = MagicMock(spec=LLMJudge)
    judge.judge.return_value = JudgeVerdict(
        attack_success=True,
        refusal=False,
        policy_violation=False,
        tool_misuse=True,
        utility_success=False,
        confidence=0.9,
        reason="tool used",
    )
    defense_fn, _ = get_defense_fn("B0")
    ep = evaluate_episode(
        attack,
        defense_fn=defense_fn,
        target_model=MockTargetModel(response="working on it"),
        judge=judge,
    )
    assert ep.id == attack["id"]
    assert ep.label == "attack"
    assert ep.metadata["tool_executed"] is True
    assert attack["tool_call"]["name"] in str(ep.metadata.get("tool_turn"))

    extracted = extract_tool_request(record=attack)
    assert extracted is not None
    assert extracted.name == attack["tool_call"]["name"]


def test_l2_denies_declared_pack_tool_call():
    attack = next(
        r
        for r in _rows()
        if r["label"] == "attack" and (r.get("tool_call") or {}).get("name") == "send_email"
    )
    judge = MagicMock(spec=LLMJudge)
    judge.judge.return_value = JudgeVerdict(
        attack_success=False,
        refusal=False,
        policy_violation=False,
        tool_misuse=False,
        utility_success=False,
        confidence=0.9,
        reason="denied",
    )
    l2_fn, _ = get_defense_fn("L2")
    ep = evaluate_episode(
        attack,
        defense_fn=l2_fn,
        target_model=MockTargetModel(response="emailing"),
        judge=judge,
    )
    assert ep.tool_blocked is True
    assert ep.metadata["tool_executed"] is False
    assert ep.taxonomy_class == "correct_tool_deny"


def test_manifest_matches_hash_and_counts():
    manifest = json.loads((PACK / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["pack_id"] == "vnext_confirm_v1.0"
    assert manifest["n_attack"] == 61
    assert manifest["n_benign"] == 61
    assert manifest["llm_api_calls"] == 0
    assert manifest["dataset_sha256"] == _listed_hashes()["dataset.jsonl"]
    assert manifest["seed"] == 61
    addendum = (ROOT / "docs" / "experiments" / "protocols" / "VNEXT_PROTOCOL_ADDENDUM.md").read_text(
        encoding="utf-8"
    )
    assert manifest["dataset_sha256"] in addendum
    hash_section = addendum.split("## 4. Hash gate", 1)[1].split("## 5.", 1)[0]
    assert "`523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518`" in hash_section
    assert "**`TBD`**" not in hash_section
