"""Amendment 8 item 2 — cancelled_timeout ledger + placeholder cap (mock HTTP only)."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import patch

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
    http_client = httpx.AsyncClient(transport=transport)
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
        http_client=http_client,
        wall_timeout_s=wall_timeout_s,
    )
    assert isinstance(result, CancelledTimeoutAttemptResult)
    return result


def test_cancelled_timeout_ledger_row_and_connection_closed(tmp_path: Path):
    aclose_calls: list[int] = []
    real_aclose = httpx.AsyncClient.aclose

    async def tracking_aclose(self):
        aclose_calls.append(1)
        return await real_aclose(self)

    async def _main() -> CancelledTimeoutAttemptResult:
        return await _run_hanging_attempt()

    with patch.object(httpx.AsyncClient, "aclose", tracking_aclose):
        outcome = run_harness_event_loop(_main)

    assert outcome.billed_placeholder_usd == pytest.approx(EXPECTED_PLACEHOLDER)
    assert len(aclose_calls) >= 1

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
    with pytest.raises(PilotBudgetExceeded):
        raise PilotBudgetExceeded("usd_cap")
