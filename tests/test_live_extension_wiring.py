"""Phase 7 pre-flight wiring (no live API)."""
import json
from pathlib import Path

import pytest

from adapti_guard.evaluation.live_extension_wiring import (
    LiveExtensionBlockedError,
    authorization_allows_live_spend,
    build_judge_evidence_record,
    plan_live_execution,
    resolve_offline_path,
    run_live_condition,
)


def test_offline_path_for_e1():
    assert resolve_offline_path("COND-E1-STATEFUL-OFFLINE") == "offline"


def test_live_plan_blocked_without_auth():
    with pytest.raises(LiveExtensionBlockedError):
        plan_live_execution("COND-E1-STATEFUL-OFFLINE")


def test_wiring_covers_extension_conditions():
    for cid in (
        "COND-E1-STATEFUL-OFFLINE",
        "COND-E2-ADAPTIVE-OFFLINE",
        "COND-E3-AGENT-OFFLINE",
        "COND-EXT6-BASELINE",
        "COND-PHASE7-CAMPAIGN",
    ):
        with pytest.raises(LiveExtensionBlockedError):
            plan_live_execution(cid)


def test_judge_evidence_record_not_run_without_llm():
    rec = build_judge_evidence_record(
        execution_mode="OFFLINE_MOCK",
        target_model_id="t",
        judge_model_id="j",
        judge_config_key="judge_primary",
        authorization_allows_spend=False,
    )
    assert rec["execution_status"] == "NOT_RUN"
    assert rec["target_raw_immutable"] is True


def test_authorization_blocks_live_spend():
    ok, _ = authorization_allows_live_spend()
    assert not ok


def test_live_mode_blocked_without_authorization(tmp_path: Path):
    with pytest.raises(LiveExtensionBlockedError):
        run_live_condition(
            "COND-E1-STATEFUL-OFFLINE",
            run_id="blocked-run",
            run_dir=tmp_path,
            execution_mode="LIVE",
        )


def test_offline_mock_stateful_canonical_runner(tmp_path: Path):
    result = run_live_condition(
        "COND-E1-STATEFUL-OFFLINE",
        run_id="mock-run",
        run_dir=tmp_path,
        execution_mode="OFFLINE_MOCK",
        turn_messages=["hello", "follow-up"],
    )
    assert result.status == "ok"
    raw = json.loads((tmp_path / "raw" / "episode_raw.json").read_text())
    assert raw["turn_count"] == 2
    assert Path(result.trace_path).is_file()
    assert Path(result.derived_metrics_path).is_file()
    assert (tmp_path / "raw" / "episode_raw.json").exists()


def test_offline_mock_agent_e3(tmp_path: Path):
    result = run_live_condition(
        "COND-E3-AGENT-OFFLINE",
        run_id="agent-mock",
        run_dir=tmp_path,
        execution_mode="OFFLINE_MOCK",
    )
    raw = json.loads((tmp_path / "raw" / "episode_raw.json").read_text())
    assert raw["episode_type"] == "agent"
    assert raw["environment_execution_mode"] == "OFFLINE_MOCK"
    judge = json.loads((tmp_path / "raw" / "judge_raw.json").read_text())
    assert judge["status"] == "NOT_RUN"
    assert judge["pipeline"].endswith("build_judge")
    assert len(result.raw_evidence_paths) == 2


def test_ext6_blocked_in_canonical_runner(tmp_path: Path):
    with pytest.raises(LiveExtensionBlockedError):
        run_live_condition(
            "COND-EXT6-BASELINE",
            run_id="x",
            run_dir=tmp_path,
            execution_mode="OFFLINE_MOCK",
        )


def test_offline_mock_adaptive_feedback(tmp_path: Path):
    result = run_live_condition(
        "COND-E2-ADAPTIVE-OFFLINE",
        run_id="adapt-mock",
        run_dir=tmp_path,
        execution_mode="OFFLINE_MOCK",
    )
    assert result.execution_mode == "OFFLINE_MOCK"
    raw = json.loads((tmp_path / "raw" / "episode_raw.json").read_text())
    assert raw["episode_type"] == "adaptive"
