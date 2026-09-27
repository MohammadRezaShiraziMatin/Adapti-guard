"""Phase 4 infrastructure contract tests (offline only)."""
import json
from pathlib import Path

import pytest

from adapti_guard.attacker.adaptive_attacker import AdaptiveAttacker
from adapti_guard.evaluation.component_resolver import (
    AttackKind,
    ComponentResolutionError,
    resolve_attack,
    resolve_defense,
    resolve_offline_target,
)
from adapti_guard.evaluation.condition_resolver import (
    config_hash,
    resolve_condition,
)
from adapti_guard.evaluation.offline_experiment_runner import OfflineRunnerError, run_offline
from adapti_guard.evaluation.target_model import MockTargetModel

MATRIX = Path("docs/research/EXPERIMENT_MATRIX.yaml")


def test_config_hash_deterministic():
    a = config_hash({"condition_id": "x", "seed": 1})
    b = config_hash({"seed": 1, "condition_id": "x"})
    assert a == b


def test_resolve_offline_condition():
    row, ctx = resolve_condition("COND-E1-STATEFUL-OFFLINE", matrix_path=MATRIX)
    assert row["interaction_mode"] == "multi_turn"
    assert ctx.config_hash


def test_target_eq_judge_blocked():
    _, ctx = resolve_condition("COND-TRACK-A-B0", matrix_path=MATRIX)
    assert ctx.target_model_id != ctx.judge_id


def test_attack_id_resolves_to_real_implementation():
    atk = resolve_attack("adaptive_attacker_fixture")
    assert atk.kind == AttackKind.ADAPTIVE
    assert "AdaptiveAttacker" in atk.implementation
    assert isinstance(AdaptiveAttacker(), AdaptiveAttacker)


def test_defense_id_resolves_runtime_fixture():
    d = resolve_defense("runtime_fixture", adaptivity="static")
    assert d.stateful_fn is not None
    action, _ = d.stateful_fn(prompt="x", context="")
    assert action is not None


def test_offline_target_mock_uses_target_model():
    t = resolve_offline_target("mock_target")
    assert t.provider == "mock"
    assert isinstance(t.model, MockTargetModel)


def test_offline_run_writes_raw_before_derived(tmp_path):
    out = run_offline("COND-E1-STATEFUL-OFFLINE", seed=1, runs_root=tmp_path / "runs")
    raw = out / "raw_evidence.json"
    derived = out / "derived_metrics.json"
    assert raw.is_file() and derived.is_file()
    raw_doc = json.loads(raw.read_text())
    assert raw_doc["pipeline"] == "stateful"
    assert raw_doc["target_execution"]["execution_status"] == "ok"
    assert "derived_from" in json.loads(derived.read_text())


def test_evidence_provenance_fields(tmp_path):
    out = run_offline("COND-E1-STATEFUL-OFFLINE", seed=2, trial=1, runs_root=tmp_path / "runs")
    rec = json.loads((out / "evidence_record.json").read_text())
    for key in (
        "run_id",
        "condition_id",
        "config_hash",
        "seed",
        "trial",
        "repository_revision",
        "attack_id",
        "defense_id",
    ):
        assert key in rec and rec[key] is not None


def test_target_failure_not_attack_success(tmp_path):
    out = run_offline(
        "COND-E1-STATEFUL-OFFLINE",
        seed=1,
        runs_root=tmp_path / "runs",
        allow_error_target=True,
    )
    raw = json.loads((out / "raw_evidence.json").read_text())
    assert raw["outcome"] == "target_failure"
    assert raw["target_execution"]["execution_status"] == "provider_error"
    assert "attack_success" not in raw


def test_historical_live_not_rerunnable_offline():
    with pytest.raises(OfflineRunnerError):
        run_offline("COND-TRACK-A-B0", runs_root=Path("/tmp/adapti_phase4_test_runs"))


def test_live_attack_pack_blocked_offline():
    with pytest.raises(ComponentResolutionError):
        resolve_attack("phase1_confirm_v1")
