"""Amendment 6 — pilot lock + incremental store tests."""
from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from adapti_guard.evaluation.harness_v2.http_budget import HttpCompletionBudget
from adapti_guard.evaluation.harness_v2.pilot_incremental_store import PilotIncrementalStore
from adapti_guard.evaluation.harness_v2.pilot_run_lock import PilotRunLock


def test_lock_refuses_second_live_holder(tmp_path: Path):
    lock_path = tmp_path / "lock.json"
    out1 = tmp_path / "run1"
    out2 = tmp_path / "run2"
    PilotRunLock.try_acquire(out_dir=out1, path=lock_path)
    with pytest.raises(RuntimeError, match="pilot_run_lock_held"):
        PilotRunLock.try_acquire(out_dir=out2, path=lock_path)


def test_lock_stale_after_pid_dead(tmp_path: Path):
    lock_path = tmp_path / "lock.json"
    lock_path.write_text(json.dumps({"pid": 999999999, "out_dir": "/tmp/x"}) + "\n")
    lock = PilotRunLock.try_acquire(out_dir=tmp_path / "run", path=lock_path)
    assert lock.payload["pid"] == os.getpid()
    lock.release()
    assert not lock_path.exists()


def test_incremental_http_and_ledger_fsync(tmp_path: Path):
    store = PilotIncrementalStore(tmp_path / "out", usd_cap=0.05, http_cap=640)
    rec = SimpleNamespace(
        call_index=1,
        request={},
        raw_response={},
        cost_usd=0.001,
        usage={},
        scenario_id="s",
        model_id="m",
        provider_error=None,
        finish_reason="stop",
        tool_calls=[],
        assistant_content="",
        latency_ms=1.0,
        episode_round=1,
    )
    ser = {
        "call_index": 1,
        "cost_usd": 0.001,
        "usage": {},
        "model_id": "m",
        "request": {},
        "raw_response": {},
    }
    store.append_http_call(episode_id="sc/i0/q/A0", record=rec, serialized=ser)
    assert store.http_used() == 1
    assert store.spent_usd() == pytest.approx(0.001)
    assert (tmp_path / "out" / "http_stream.jsonl").read_text().count("\n") == 1


def test_resume_skips_completed_episodes(tmp_path: Path):
    store = PilotIncrementalStore(tmp_path / "out", usd_cap=0.05, http_cap=640)
    store.write_episode_complete({"episode_id": "a/i0/q/A0", "status": "COMPLETE", "calls": [], "final_messages": []})
    assert "a/i0/q/A0" in store.completed_episode_ids()
    budget = HttpCompletionBudget(640, initial_used=store.http_used())
    assert budget.used == 0


def test_append_http_call_skips_duplicate_request_id(tmp_path: Path):
    store = PilotIncrementalStore(tmp_path / "out", usd_cap=0.05, http_cap=640)
    rec = SimpleNamespace(
        call_index=1,
        request_id="dup-rid-1",
        request={},
        raw_response={},
        cost_usd=0.001,
        usage={},
        scenario_id="s",
        model_id="m",
        provider_error=None,
        finish_reason="stop",
        tool_calls=[],
        assistant_content="",
        latency_ms=1.0,
        episode_round=1,
    )
    ser = {
        "call_index": 1,
        "request_id": "dup-rid-1",
        "cost_usd": 0.001,
        "usage": {},
        "model_id": "m",
        "request": {},
        "raw_response": {},
    }
    store.append_http_call(episode_id="sc/i0/q/A0", record=rec, serialized=ser)
    store.append_http_call(episode_id="sc/i0/q/A0", record=rec, serialized=ser)
    assert store.http_used() == 1
    assert len(store.ledger_rows_path.read_text().strip().splitlines()) == 1


def test_mark_episode_rows_superseded(tmp_path: Path):
    store = PilotIncrementalStore(tmp_path / "out", usd_cap=0.05, http_cap=640)
    rec = SimpleNamespace(
        call_index=1,
        request_id="r1",
        request={},
        raw_response={},
        cost_usd=0.001,
        usage={},
        scenario_id="s",
        model_id="m",
        provider_error=None,
        finish_reason="stop",
        tool_calls=[],
        assistant_content="",
        latency_ms=1.0,
        episode_round=1,
    )
    ser = {
        "call_index": 1,
        "request_id": "r1",
        "cost_usd": 0.001,
        "usage": {},
        "model_id": "m",
        "request": {},
        "raw_response": {},
    }
    store.append_http_call(episode_id="ep/partial", record=rec, serialized=ser)
    new_attempt = "attempt-new"
    n = store.mark_episode_rows_superseded("ep/partial", superseded_by_attempt_id=new_attempt)
    assert n == 1
    row = json.loads(store.ledger_rows_path.read_text().strip())
    assert row["superseded_by_resume"] is True
    assert row["superseded_by_attempt_id"] == new_attempt
    led = store.ledger()
    assert led["billed_spent_usd"] == pytest.approx(0.001)
    assert led["analysis_spent_usd"] == pytest.approx(0.0)


def test_usd_cap_from_ledger(tmp_path: Path):
    store = PilotIncrementalStore(tmp_path / "out", usd_cap=0.01, http_cap=640)
    led = store.ledger()
    led["spent_usd"] = 0.01
    store._write_ledger(led)
    assert store.usd_budget_exhausted()
