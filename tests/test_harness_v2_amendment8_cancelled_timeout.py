"""Amendment 8 item 2 — cancelled_timeout ledger + placeholder cap (mock HTTP only)."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

import httpx
import pytest

from adapti_guard.evaluation.harness_v2.cancelled_timeout_billing import (
    cancelled_timeout_placeholder_usd,
)
from adapti_guard.evaluation.harness_v2.cancelled_timeout_ledger import (
    harness_call_record_from_cancelled_timeout,
)
from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop
from adapti_guard.evaluation.harness_v2.openrouter_async_attempt import (
    CancelledTimeoutAttemptResult,
    one_billed_openrouter_attempt,
)
from adapti_guard.evaluation.harness_v2.pilot_budget import PilotBudgetExceeded
from adapti_guard.evaluation.harness_v2.pilot_incremental_store import (
    PilotIncrementalStore,
    serialize_call_for_stream,
)
from adapti_guard.evaluation.openrouter_panel_pricing import ModelPrice, OpenRouterPricingTable


class _HangTransport(httpx.AsyncBaseTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        await asyncio.Event().wait()
        return httpx.Response(200, json={})


MODEL_ID = "test/cancel-model"
PROMPT_TOKENS = 100
MAX_TOKENS = 512
INPUT_PRICE = 0.00001
OUTPUT_PRICE = 0.00002
EXPECTED_PLACEHOLDER = PROMPT_TOKENS * INPUT_PRICE + MAX_TOKENS * OUTPUT_PRICE


def _pricing() -> OpenRouterPricingTable:
    return OpenRouterPricingTable(
        {MODEL_ID: ModelPrice(prompt_usd_per_token=INPUT_PRICE, completion_usd_per_token=OUTPUT_PRICE)}
    )


async def _run_hanging_attempt(*, wall_timeout_s: float = 0.2) -> CancelledTimeoutAttemptResult:
    transport = _HangTransport()
    placeholder = cancelled_timeout_placeholder_usd(
        model_id=MODEL_ID,
        prompt_tokens=PROMPT_TOKENS,
        max_tokens=MAX_TOKENS,
        pricing=_pricing(),
    )
    req_body = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": MAX_TOKENS,
    }
    result = await one_billed_openrouter_attempt(
        base_url="http://127.0.0.1:59999/v1",
        api_key="mock-key-no-network",
        req_body=req_body,
        model_id=MODEL_ID,
        prompt_tokens=PROMPT_TOKENS,
        billed_placeholder_usd=placeholder,
        http_transport=transport,
        wall_timeout_s=wall_timeout_s,
    )
    assert isinstance(result, CancelledTimeoutAttemptResult)
    return result


def test_cancelled_timeout_ledger_row_and_connection_closed(tmp_path: Path):
    async def _main() -> CancelledTimeoutAttemptResult:
        return await _run_hanging_attempt()

    outcome = run_harness_event_loop(_main)
    assert outcome.billed_placeholder_usd == pytest.approx(EXPECTED_PLACEHOLDER)

    store = PilotIncrementalStore(tmp_path / "out", usd_cap=1.0, http_cap=640)
    rec = harness_call_record_from_cancelled_timeout(
        outcome,
        scenario_id="s1",
        model_id=MODEL_ID,
        call_index=1,
        episode_round=1,
    )
    ser = serialize_call_for_stream(rec, http_index=1)
    store.append_http_call(episode_id="s1/i0/q/A0", record=rec, serialized=ser)

    stream_row = json.loads(store.http_stream_path.read_text().strip())
    ledger_row = json.loads(store.ledger_rows_path.read_text().strip())
    assert stream_row["status"] == "cancelled_timeout"
    assert stream_row["cost_usd"] is None
    assert stream_row["billed_placeholder_usd"] == pytest.approx(EXPECTED_PLACEHOLDER)
    assert stream_row["reconciliation_source"] == "pending"
    assert ledger_row["status"] == "cancelled_timeout"
    assert ledger_row["cost_usd"] is None
    assert ledger_row["billed_placeholder_usd"] == pytest.approx(EXPECTED_PLACEHOLDER)
    assert ledger_row["reconciliation_source"] == "pending"
    assert store.spent_usd() == pytest.approx(EXPECTED_PLACEHOLDER)


def test_placeholder_pushes_usd_cap_and_raises(tmp_path: Path):
    cap = EXPECTED_PLACEHOLDER * 0.5
    store = PilotIncrementalStore(tmp_path / "out", usd_cap=cap, http_cap=640)

    async def _main() -> CancelledTimeoutAttemptResult:
        return await _run_hanging_attempt()

    outcome = run_harness_event_loop(_main)
    rec = harness_call_record_from_cancelled_timeout(
        outcome,
        scenario_id="s1",
        model_id=MODEL_ID,
        call_index=1,
        episode_round=1,
    )
    ser = serialize_call_for_stream(rec, http_index=1)
    store.append_http_call(episode_id="ep", record=rec, serialized=ser)
    assert store.spent_usd() == pytest.approx(EXPECTED_PLACEHOLDER)
    assert store.usd_budget_exhausted()


def test_placeholder_pushes_usd_cap_via_pilot_async(tmp_path: Path, monkeypatch):
    import importlib.util
    import sys
    from pathlib import Path as P

    root = P(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    spec = importlib.util.spec_from_file_location(
        "run_harness_v2_pilot",
        root / "scripts" / "run_harness_v2_pilot.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    class _HangTransport(httpx.AsyncBaseTransport):
        def __init__(self) -> None:
            self.request_count = 0

        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            self.request_count += 1
            await asyncio.Event().wait()
            return httpx.Response(200, json={})

    transport = _HangTransport()
    monkeypatch.setenv("OPENROUTER_BASE_URL", "http://127.0.0.1:59996/v1")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    schedule = [
        {
            "scenario_id": "benign_weather_v1",
            "instance_index": 0,
            "family": "qwen3",
            "condition": "A0",
        },
    ]

    async def _run():
        return await mod.run_pilot_async(
            tmp_path / "cap_pack",
            usd_cap=0.001,
            http_transport=transport,
            schedule_override=schedule,
            wall_timeout_s=0.2,
            rate_limit_backoffs=(0.0, 0.0),
            skip_preflight=True,
        )

    run_harness_event_loop(_run)
    assert transport.request_count == 1
    row = json.loads((tmp_path / "cap_pack" / "http_stream.jsonl").read_text().strip())
    assert row.get("status") == "cancelled_timeout"
    assert row.get("billed_placeholder_usd", 0) > 0.001
    PilotIncrementalStore = __import__(
        "adapti_guard.evaluation.harness_v2.pilot_incremental_store",
        fromlist=["PilotIncrementalStore"],
    ).PilotIncrementalStore
    store = PilotIncrementalStore(tmp_path / "cap_pack", usd_cap=0.001, http_cap=640)
    assert store.usd_budget_exhausted()
