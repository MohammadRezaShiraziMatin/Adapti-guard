"""Run multi-turn OpenRouter chat with native tools + trajectory capture."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from adapti_guard.evaluation.harness_v2.harness_v2_b3_pretarget_wrapper import HarnessV2B3EpisodeContext
from adapti_guard.evaluation.harness_v2.mock_tool_executor import HarnessV2MockToolExecutor
from adapti_guard.evaluation.harness_v2.pilot_budget import PilotBudgetExceeded


@dataclass
class HarnessV2CallRecord:
    call_index: int
    scenario_id: str
    model_id: str
    messages_before: list[dict[str, Any]]
    request: dict[str, Any]
    raw_response: dict[str, Any]
    assistant_content: str
    tool_calls: list[dict[str, Any]]
    usage: dict[str, Any]
    cost_usd: float | None
    provider_error: str | None
    latency_ms: float
    finish_reason: str | None = None
    native_finish_reason: str | None = None
    episode_incomplete: bool = False
    episode_round: int = 0
    request_id: str | None = None
    ledger_status: str | None = None
    billed_placeholder_usd: float | None = None
    reconciliation_source: str | None = None
    retried_after_rate_limit: bool = False


@dataclass
class HarnessV2EpisodeTrajectory:
    scenario_id: str
    model_id: str
    config_key: str
    system_prompt: str
    calls: list[HarnessV2CallRecord] = field(default_factory=list)
    final_messages: list[dict[str, Any]] = field(default_factory=list)
    mock_tool_log: list[dict[str, Any]] = field(default_factory=list)
    b3_log: list[dict[str, Any]] = field(default_factory=list)
    condition: str = "A0"
    invalid_timeout: bool = False


def _message_to_dict(msg: Any) -> dict[str, Any]:
    if hasattr(msg, "model_dump"):
        return msg.model_dump(exclude_none=True)
    out: dict[str, Any] = {"role": getattr(msg, "role", None), "content": getattr(msg, "content", None)}
    tcs = getattr(msg, "tool_calls", None)
    if tcs:
        out["tool_calls"] = [_message_to_dict(tc) if hasattr(tc, "model_dump") else tc for tc in tcs]
    return out


def _response_to_dict(response: Any) -> dict[str, Any]:
    if hasattr(response, "model_dump"):
        return response.model_dump(exclude_none=True)
    return json.loads(response.model_dump_json()) if hasattr(response, "model_dump_json") else {"raw": str(response)}


def run_tools_episode(
    *,
    scenario_id: str,
    model_id: str,
    config_key: str,
    system_prompt: str,
    initial_user: str,
    executor: HarnessV2MockToolExecutor,
    max_rounds: int = 4,
    max_tokens: int | None = None,
    temperature: float = 0.0,
    pricing_cost_fn: Any | None = None,
    call_index_start: int = 1,
    http_budget: Any | None = None,
    b3_context: HarnessV2B3EpisodeContext | None = None,
    on_http_record: Any | None = None,
    family: str = "qwen3",
    **kwargs: Any,
) -> HarnessV2EpisodeTrajectory:
    """Legacy entry: runs ``run_tools_episode_async`` in a one-off event loop (tests/smokes only)."""
    from adapti_guard.evaluation.harness_v2.harness_event_loop import run_harness_event_loop
    from adapti_guard.evaluation.harness_v2.openrouter_tools_session_async import (
        run_tools_episode_async,
    )

    async def _main() -> HarnessV2EpisodeTrajectory:
        return await run_tools_episode_async(
            scenario_id=scenario_id,
            model_id=model_id,
            config_key=config_key,
            system_prompt=system_prompt,
            initial_user=initial_user,
            executor=executor,
            family=family,
            max_rounds=max_rounds,
            max_tokens=max_tokens,
            temperature=temperature,
            pricing_cost_fn=pricing_cost_fn,
            call_index_start=call_index_start,
            http_budget=http_budget,
            b3_context=b3_context,
            on_http_record=on_http_record,
            **kwargs,
        )

    return run_harness_event_loop(_main)
