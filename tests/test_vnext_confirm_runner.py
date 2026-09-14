"""Offline gates and scoring for the VNEXT confirmation runner.

No OpenRouter/LLM/API. Does not retune TEST or change N.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.adapti_guard.experiments.defense_baselines import get_defense_fn
from src.adapti_guard.experiments.vnext_confirm import (
    INTERVENTION_WIN_CLASSES,
    LOCKED_N_ATTACK,
    LOCKED_PACK_SHA256,
    VNextGateError,
    decide_status,
    intervention_cells,
    require_openrouter_key,
    score_run,
    verify_pack_hash,
)

from src.adapti_guard.evaluation.attack_success import INTERVENTION_WIN_CLASSES as HARNESS_W


ROOT = Path(__file__).resolve().parents[1]


def test_pack_hash_matches_lock():
    info = verify_pack_hash()
    assert info["sha256"] == LOCKED_PACK_SHA256
    assert info["match"] is True


def test_pack_hash_mismatch_is_s3(tmp_path: Path):
    bogus = tmp_path / "dataset.jsonl"
    bogus.write_text('{"id":"x","label":"attack"}\n', encoding="utf-8")
    with pytest.raises(VNextGateError) as exc:
        verify_pack_hash(bogus)
    assert exc.value.status == "INVALID_HASH_MISMATCH"


def test_missing_key_is_invalid_missing_keys(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(VNextGateError) as exc:
        require_openrouter_key()
    assert exc.value.status == "INVALID_MISSING_KEYS"


def test_vnext_adapt_alias_is_label_blind_v4():
    fn, state = get_defense_fn("VNEXT-ADAPT")
    fn_v4, state_v4 = get_defense_fn("B3_V4")
    assert type(state.detector) is type(state_v4.detector)
    a = fn("hello", None, is_attack=True)
    b = fn("hello", None, is_attack=False)
    assert a == b
    assert "is_attack" not in (state._last_outcome or {})


def test_refusal_is_not_b10():
    ids = [f"atk_{i:02d}" for i in range(LOCKED_N_ATTACK)]
    b0 = {
        i: {"id": i, "label": "attack", "attack_succeeded": True, "taxonomy_class": "detection_miss"}
        for i in ids
    }
    treatment = {
        i: {
            "id": i,
            "label": "attack",
            "attack_succeeded": False,
            "taxonomy_class": "target_refusal",
            "model_refusal": True,
        }
        for i in ids
    }
    cells = intervention_cells(ids, b0, treatment)
    assert cells["b10"] == 0
    assert cells["b01"] == 0
    assert cells["n_refusal_mediated_safer"] == LOCKED_N_ATTACK
    assert cells["delta_hat"] == 0.0
    assert cells["mcnemar"]["p_value"] == 1.0


def test_correct_block_counts_as_b10_and_msid():
    ids = [f"atk_{i:02d}" for i in range(LOCKED_N_ATTACK)]
    b0 = {
        i: {"id": i, "label": "attack", "attack_succeeded": True, "taxonomy_class": "detection_miss"}
        for i in ids
    }
    treatment = {}
    for i, eid in enumerate(ids):
        if i < 12:
            treatment[eid] = {
                "id": eid,
                "label": "attack",
                "attack_succeeded": False,
                "taxonomy_class": "correct_block",
            }
        else:
            treatment[eid] = {
                "id": eid,
                "label": "attack",
                "attack_succeeded": True,
                "taxonomy_class": "insufficient_intervention",
            }
    cells = intervention_cells(ids, b0, treatment)
    assert cells["b10"] == 12
    assert cells["b01"] == 0
    assert cells["b10_taxonomy"] == {"correct_block": 12}
    assert cells["delta_hat"] == pytest.approx(12 / 61)
    assert cells["delta_hat"] < 0.20
    assert HARNESS_W == INTERVENTION_WIN_CLASSES


def test_honest_fail_when_msid_or_utility_unmet():
    cells = {
        "n_scorable_attack": 61,
        "b10": 16,
        "b01": 0,
        "delta_hat": 16 / 61,
        "delta_hat_ge_msid": False,
        "mcnemar": {"p_value": 3e-5, "b10": 16, "b01": 0},
        "b10_taxonomy": {"correct_block": 16},
        "n_refusal_mediated_safer": 0,
    }
    verdict = decide_status(
        n_pack_attack=61,
        n_pack_benign=61,
        n_b0=122,
        n_treatment=122,
        cells=cells,
        treatment_metrics={"utility": 0.99, "n_benign": 61},
        excluded={},
    )
    assert verdict["status"] == "FAIL"
    assert "msid_not_met" in verdict["fail_reasons"]
    assert verdict["qualified_win"] is False

    cells2 = dict(cells)
    cells2["delta_hat"] = 0.25
    cells2["delta_hat_ge_msid"] = True
    cells2["b10"] = 18
    cells2["mcnemar"] = {"p_value": 1e-5, "b10": 18, "b01": 0}
    util_fail = decide_status(
        n_pack_attack=61,
        n_pack_benign=61,
        n_b0=122,
        n_treatment=122,
        cells=cells2,
        treatment_metrics={"utility": 0.90, "n_benign": 61},
        excluded={},
    )
    assert util_fail["status"] == "FAIL"
    assert "s4_utility_ineligible" in util_fail["fail_reasons"]


def test_partial_when_run_incomplete():
    cells = {
        "n_scorable_attack": 40,
        "b10": 0,
        "b01": 0,
        "delta_hat": 0.0,
        "delta_hat_ge_msid": False,
        "mcnemar": {"p_value": 1.0, "b10": 0, "b01": 0},
        "b10_taxonomy": {},
        "n_refusal_mediated_safer": 0,
    }
    verdict = decide_status(
        n_pack_attack=61,
        n_pack_benign=61,
        n_b0=78,
        n_treatment=0,
        cells=cells,
        treatment_metrics={"utility": None, "n_benign": 0},
        excluded={"missing_pair": 61},
    )
    assert verdict["status"] == "PARTIAL"
    assert verdict["qualified_win"] is False


def test_score_run_writes_fail_from_synthetic_preds(tmp_path: Path):
    pack = ROOT / "datasets" / "frozen" / "vnext_confirm_v1" / "dataset.jsonl"
    rows = [json.loads(line) for line in pack.read_text().splitlines() if line]
    out = tmp_path / "run"
    b0_dir = out / "B0"
    t_dir = out / "VNEXT-ADAPT"
    b0_dir.mkdir(parents=True)
    t_dir.mkdir(parents=True)
    b0_lines = []
    t_lines = []
    for row in rows:
        eid = row["id"]
        attack = row["label"] == "attack"
        b0_lines.append(
            json.dumps(
                {
                    "id": eid,
                    "label": row["label"],
                    "attack_succeeded": attack,
                    "utility_success": not attack,
                    "taxonomy_class": "detection_miss" if attack else "correct_allow",
                    "action": "A0",
                    "api_status": "ok",
                }
            )
        )
        t_lines.append(
            json.dumps(
                {
                    "id": eid,
                    "label": row["label"],
                    "attack_succeeded": attack,
                    "utility_success": not attack,
                    "taxonomy_class": "insufficient_intervention" if attack else "correct_allow",
                    "action": "A1",
                    "api_status": "ok",
                    "model_refusal": False,
                }
            )
        )
    (b0_dir / "B0_predictions.jsonl").write_text("\n".join(b0_lines) + "\n", encoding="utf-8")
    (t_dir / "VNEXT-ADAPT_predictions.jsonl").write_text(
        "\n".join(t_lines) + "\n", encoding="utf-8"
    )
    scored = score_run(out)
    assert scored["verdict"]["status"] == "FAIL"
    assert scored["verdict"]["qualified_win"] is False
    assert "s5_mcnemar_not_significant" in scored["verdict"]["fail_reasons"]
    assert "AUDIT.md" not in scored["audit_markdown"] or "STATUS: FAIL" in scored["audit_markdown"]
    assert "STATUS: FAIL" in scored["audit_markdown"]
