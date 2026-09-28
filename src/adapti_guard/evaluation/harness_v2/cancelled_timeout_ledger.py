"""Build ledger records for cancelled-timeout HTTP attempts."""
from __future__ import annotations

from typing import Any

from adapti_guard.evaluation.harness_v2.openrouter_async_attempt import CancelledTimeoutAttemptResult
from adapti_guard.evaluation.harness_v2.openrouter_tools_session import HarnessV2CallRecord


def harness_call_record_from_cancelled_timeout(
    result: CancelledTimeoutAttemptResult,
    *,
    scenario_id: str,
    model_id: str,
    call_index: int,
    episode_round: int,
    messages_before: list[dict[str, Any]] | None = None,
    request_wire_body: bytes | None = None,
) -> HarnessV2CallRecord:
    return HarnessV2CallRecord(
        call_index=call_index,
        scenario_id=scenario_id,
        model_id=model_id,
        messages_before=messages_before or [],
        request=result.req_body,
        raw_response={},
        assistant_content="",
        tool_calls=[],
        usage={"prompt_tokens": result.prompt_tokens, "completion_tokens": 0},
        cost_usd=None,
        provider_error="HarnessAttemptTimeout",
        latency_ms=result.latency_ms,
        finish_reason=None,
        native_finish_reason=None,
        episode_round=episode_round,
        request_id=result.request_id,
        ledger_status="cancelled_timeout",
        billed_placeholder_usd=result.billed_placeholder_usd,
        reconciliation_source="pending",
        request_wire_body=request_wire_body if request_wire_body is not None else result.request_wire_body,
        request_wire_sent_unconfirmed=result.request_wire_sent_unconfirmed,
    )
