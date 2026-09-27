"""Amendment 7c — resume ledger / budget propagation (offline, no network)."""
from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from adapti_guard.evaluation.harness_v2.http_budget import HttpCompletionBudget
from adapti_guard.evaluation.harness_v2.mock_tool_executor import HarnessV2MockToolExecutor
from adapti_guard.evaluation.harness_v2.openrouter_tools_session import (
    HarnessV2CallRecord,
    run_tools_episode,
)
from adapti_guard.evaluation.harness_v2.pilot_budget import PilotBudgetExceeded
from adapti_guard.evaluation.harness_v2.pilot_incremental_store import (
    PilotIncrementalStore,
    serialize_call_for_stream,
)
from adapti_guard.evaluation.harness_v2.trajectory_store import serialize_trajectory_call


def _fake_openai_stop_response():
    usage = SimpleNamespace(
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15,
        cost=0.0001,
    )
    msg = SimpleNamespace(content="Done.", tool_calls=None, role="assistant")

    class _Choice:
        message = msg
        finish_reason = "stop"

    class _Response:
        choices = [_Choice()]
        usage = usage

        def model_dump(self, exclude_none=False):
            return {
                "choices": [
                    {
                        "message": {"role": "assistant", "content": "Done."},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                },
            }

    return _Response()


def test_pilot_budget_exceeded_propagates_and_records_once(tmp_path: Path, monkeypatch):
    """(a) PilotBudgetExceeded from on_http_record exits run_tools_episode; one stream/ledger row."""
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://127.0.0.1:9999/v1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    class FakeCompletions:
        async def create(self, **kwargs):
            return _fake_openai_stop_response()

    class FakeChat:
        completions = FakeCompletions()

    class FakeAsyncClient:
        chat = FakeChat()

        async def close(self):
            return None

    monkeypatch.setattr("openai.AsyncOpenAI", lambda **kwargs: FakeAsyncClient())

    store = PilotIncrementalStore(tmp_path / "out", usd_cap=0.05, http_cap=640)
    eid = "sc/i0/q/A0"
    recorded_ids: list[str] = []

    def on_http_record(rec: SimpleNamespace) -> None:
        ser = serialize_call_for_stream(rec, http_index=rec.call_index)
        recorded_ids.append(str(ser.get("request_id")))
        store.append_http_call(episode_id=eid, record=rec, serialized=ser)
        raise PilotBudgetExceeded("usd_cap")

    executor = HarnessV2MockToolExecutor()
    budget = HttpCompletionBudget(640)

    with pytest.raises(PilotBudgetExceeded):
        run_tools_episode(
            scenario_id="indirect_retrieved_doc_v1",
            model_id="test/model",
            config_key="test",
            system_prompt="sys",
            initial_user="user task",
            executor=executor,
            max_rounds=2,
            http_budget=budget,
            on_http_record=on_http_record,
        )

    stream_lines = [
        ln for ln in store.http_stream_path.read_text().splitlines() if ln.strip()
    ]
    ledger_lines = [
        ln for ln in store.ledger_rows_path.read_text().splitlines() if ln.strip()
    ]
    assert len(stream_lines) == 1
    assert len(ledger_lines) == 1
    stream_rid = json.loads(stream_lines[0])["request_id"]
    ledger_rid = json.loads(ledger_lines[0])["request_id"]
    assert stream_rid == ledger_rid
    assert stream_rid == recorded_ids[0]


def test_append_duplicate_request_id_is_no_op(tmp_path: Path):
    """(b) Second append with same request_id does not add a row."""
    store = PilotIncrementalStore(tmp_path / "out", usd_cap=0.05, http_cap=640)
    rec = SimpleNamespace(
        call_index=1,
        request_id="rid-dup",
        request={},
        raw_response={},
        cost_usd=0.002,
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
        "request_id": "rid-dup",
        "cost_usd": 0.002,
        "usage": {},
        "model_id": "m",
        "request": {},
        "raw_response": {},
    }
    store.append_http_call(episode_id="ep/a", record=rec, serialized=ser)
    store.append_http_call(episode_id="ep/a", record=rec, serialized=ser)
    assert len(store.ledger_rows_path.read_text().strip().splitlines()) == 1
    assert len(store.http_stream_path.read_text().strip().splitlines()) == 1
    led = store.ledger()
    assert led["billed_http_used"] == 1
    assert led["billed_spent_usd"] == pytest.approx(0.002)


def test_mark_superseded_billed_vs_analysis_exact(tmp_path: Path):
    """(c) Supersede flags only target episode; billed includes, analysis excludes."""
    store = PilotIncrementalStore(tmp_path / "out", usd_cap=1.0, http_cap=640)

    def add(episode_id: str, rid: str, cost: float, call_index: int = 1) -> None:
        rec = SimpleNamespace(
            call_index=call_index,
            request_id=rid,
            request={},
            raw_response={},
            cost_usd=cost,
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
            "call_index": call_index,
            "request_id": rid,
            "cost_usd": cost,
            "usage": {},
            "model_id": "m",
            "request": {},
            "raw_response": {},
        }
        store.append_http_call(episode_id=episode_id, record=rec, serialized=ser)

    add("partial/ep", "r-partial", 0.01)
    add("other/ep", "r-other", 0.02)
    new_attempt = "attempt-uuid-7c"
    n = store.mark_episode_rows_superseded("partial/ep", superseded_by_attempt_id=new_attempt)
    assert n == 1
    partial = json.loads(
        [ln for ln in store.ledger_rows_path.read_text().splitlines() if ln.strip()][0]
    )
    other = json.loads(
        [ln for ln in store.ledger_rows_path.read_text().splitlines() if ln.strip()][1]
    )
    assert partial["superseded_by_resume"] is True
    assert partial["superseded_by_attempt_id"] == new_attempt
    assert other.get("superseded_by_resume") is not True
    led = store.ledger()
    assert led["billed_spent_usd"] == pytest.approx(0.03)
    assert led["analysis_spent_usd"] == pytest.approx(0.02)
    assert led["billed_http_used"] == 2
    assert led["analysis_http_used"] == 1


def test_fresh_attempt_restarts_at_call_index_one(tmp_path: Path):
    """(d) After supersede, new attempt records call_index=1 (not stitched to call_index=2)."""
    store = PilotIncrementalStore(tmp_path / "out", usd_cap=1.0, http_cap=640)
    attempt_old = "old-attempt"
    attempt_new = "new-attempt"

    rec1 = HarnessV2CallRecord(
        call_index=1,
        scenario_id="s",
        model_id="m",
        messages_before=[],
        request={},
        raw_response={},
        assistant_content="",
        tool_calls=[],
        usage={},
        cost_usd=0.001,
        provider_error=None,
        latency_ms=1.0,
        request_id="req-old",
    )
    store.append_http_call(
        episode_id="ep/x",
        record=rec1,
        serialized=serialize_trajectory_call(rec1, http_index=1),
        episode_attempt_id=attempt_old,
    )
    store.mark_episode_rows_superseded("ep/x", superseded_by_attempt_id=attempt_new)

    rec2 = HarnessV2CallRecord(
        call_index=1,
        scenario_id="s",
        model_id="m",
        messages_before=[],
        request={},
        raw_response={},
        assistant_content="",
        tool_calls=[],
        usage={},
        cost_usd=0.002,
        provider_error=None,
        latency_ms=1.0,
        request_id="req-new",
    )
    store.append_http_call(
        episode_id="ep/x",
        record=rec2,
        serialized=serialize_trajectory_call(rec2, http_index=1),
        episode_attempt_id=attempt_new,
    )

    rows = [json.loads(ln) for ln in store.ledger_rows_path.read_text().splitlines() if ln.strip()]
    assert len(rows) == 2
    assert rows[0]["call_index"] == 1 and rows[0]["superseded_by_resume"] is True
    assert rows[1]["call_index"] == 1 and rows[1]["superseded_by_resume"] is False
    assert rows[1]["episode_attempt_id"] == attempt_new
    assert rows[0]["request_id"] != rows[1]["request_id"]
