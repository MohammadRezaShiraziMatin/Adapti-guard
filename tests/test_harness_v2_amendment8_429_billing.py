"""Amendment 8 item H — 429 retry rows: assumed unbilled ledger fields."""
from __future__ import annotations

from adapti_guard.evaluation.harness_v2.pilot_incremental_store import (
    PilotIncrementalStore,
    serialize_call_for_stream,
)
from adapti_guard.evaluation.harness_v2.openrouter_tools_session import HarnessV2CallRecord


def test_rate_limit_retry_row_serialization(tmp_path):
    rec = HarnessV2CallRecord(
        call_index=1,
        scenario_id="s",
        model_id="m",
        messages_before=[],
        request={"model": "m"},
        raw_response={"error": {"code": 429}},
        assistant_content="",
        tool_calls=[],
        usage={},
        cost_usd=None,
        provider_error="OpenRouterError: code=429",
        latency_ms=1.0,
        retried_after_rate_limit=True,
        billed_placeholder_usd=0.0,
        reconciliation_source="assumed_unbilled_429",
    )
    ser = serialize_call_for_stream(rec, http_index=1)
    assert ser["cost_usd"] is None
    assert ser["billed_placeholder_usd"] == 0.0
    assert ser["reconciliation_source"] == "assumed_unbilled_429"

    store = PilotIncrementalStore(tmp_path, usd_cap=1.0, http_cap=10)
    store.append_http_call(episode_id="s/i0/q/A0", record=rec, serialized=ser)
    assert store.spent_usd() == 0.0
    assert store.http_used() == 1
