"""Serialize harness v2 trajectories (Amendment 4: full request body per HTTP)."""
from __future__ import annotations

import base64
import json
from typing import Any

from adapti_guard.evaluation.harness_v2.openrouter_tools_session import HarnessV2CallRecord


def serialize_trajectory_call(
    record: HarnessV2CallRecord,
    *,
    http_index: int | None = None,
    content: str | None = None,
) -> dict[str, Any]:
    """Persist wire-accurate request body plus response metadata."""
    req = record.request or {}
    messages_sent = record.messages_before if record.messages_before is not None else req.get("messages")
    request_snapshot = json.loads(json.dumps({**req, "messages": messages_sent}))
    if record.request_wire_body is not None:
        request_snapshot = json.loads(record.request_wire_body.decode("utf-8"))
    usage = dict(record.usage or {})
    out: dict[str, Any] = {
        "http_index": http_index,
        "call_index": record.call_index,
        "episode_round": record.episode_round,
        "scenario_id": record.scenario_id,
        "model_id": record.model_id,
        "provider_error": record.provider_error,
        "finish_reason": record.finish_reason,
        "native_finish_reason": record.native_finish_reason,
        "episode_incomplete": record.episode_incomplete,
        "tool_calls": record.tool_calls,
        "content": content if content is not None else record.assistant_content,
        "assistant_content": record.assistant_content,
        "usage": usage,
        "cost_usd": record.cost_usd,
        "latency_ms": record.latency_ms,
        "request_id": record.request_id,
        "request": request_snapshot,
        "raw_response": record.raw_response,
    }
    if record.request_wire_body is not None:
        out["request_wire_body_base64"] = base64.standard_b64encode(record.request_wire_body).decode("ascii")
    if record.ledger_status is not None:
        out["status"] = record.ledger_status
    if record.billed_placeholder_usd is not None:
        out["billed_placeholder_usd"] = record.billed_placeholder_usd
    if record.reconciliation_source is not None:
        out["reconciliation_source"] = record.reconciliation_source
    if record.retried_after_rate_limit:
        out["retried_after_rate_limit"] = True
    if record.retry_blocked_by_http_cap:
        out["retry_blocked_by_http_cap"] = True
    return out


def assert_request_snapshot_complete(snapshot: dict[str, Any]) -> None:
    """Validate persisted request has required harness v2 fields."""
    for key in ("model", "messages", "tools", "tool_choice", "temperature", "max_tokens", "extra_body"):
        if key not in snapshot:
            raise ValueError(f"request snapshot missing {key!r}")
