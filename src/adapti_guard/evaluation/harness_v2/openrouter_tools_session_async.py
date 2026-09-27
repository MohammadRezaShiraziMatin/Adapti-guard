"""Async harness v2 tool episodes — Amendment 8 wired HTTP path."""
from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from typing import Any

import httpx

from adapti_guard.evaluation.harness_v2.cancelled_timeout_billing import (
    cancelled_timeout_placeholder_usd,
)
from adapti_guard.evaluation.harness_v2.cancelled_timeout_ledger import (
    harness_call_record_from_cancelled_timeout,
)
from adapti_guard.evaluation.harness_v2.episode_wall_clock import EpisodeWallClock
from adapti_guard.evaluation.harness_v2.finish_reason import finish_metadata_from_raw_response
from adapti_guard.evaluation.harness_v2.harness_rate_limit_retry import (
    HARNESS_RATE_LIMIT_BACKOFF_S,
    HARNESS_RATE_LIMIT_MAX_RETRIES,
)
from adapti_guard.evaluation.harness_v2.harness_v2_b3_pretarget_wrapper import (
    HarnessV2B3EpisodeContext,
    append_tool_message,
    append_user_message,
)
from adapti_guard.evaluation.harness_v2.mock_tool_executor import HarnessV2MockToolExecutor
from adapti_guard.evaluation.harness_v2.openrouter_async_attempt import (
    DEFAULT_HTTP_ATTEMPT_WALL_TIMEOUT_S,
    CancelledTimeoutAttemptResult,
    one_billed_openrouter_attempt,
)
from adapti_guard.evaluation.harness_v2.openrouter_request_policy import build_harness_v2_extra_body
from adapti_guard.evaluation.harness_v2.openrouter_tools_session import (
    HarnessV2CallRecord,
    HarnessV2EpisodeTrajectory,
    _response_to_dict,
)
from adapti_guard.evaluation.harness_v2.pilot_budget import PilotBudgetExceeded
from adapti_guard.evaluation.harness_v2.provider_incomplete_response_policy import (
    HARNESS_RETRY_PROVIDER_ERROR_CODES,
)
from adapti_guard.evaluation.harness_v2.tool_definitions import HARNESS_V2_TOOLS
from adapti_guard.evaluation.harness_v2.token_limits import max_tokens_for_model_id
from adapti_guard.evaluation.openrouter_panel_pricing import OpenRouterPricingTable
from adapti_guard.evaluation.target_model import _openrouter_assistant_text, _openrouter_usage_dict

_ASSUMED_UNBILLED_429 = "assumed_unbilled_429"


def _estimate_prompt_tokens(messages: list[dict[str, Any]]) -> int:
    blob = json.dumps(messages, ensure_ascii=False)
    return max(1, len(blob) // 4)


def _openrouter_client_config() -> tuple[str, str]:
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    base_url = (
        os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip()
        or "https://openrouter.ai/api/v1"
    )
    if not api_key:
        if "127.0.0.1" in base_url or "localhost" in base_url:
            api_key = "mock-local-no-openrouter-key"
        else:
            raise RuntimeError("OPENROUTER_API_KEY not set")
    return base_url, api_key


def _is_rate_limit_error(exc: BaseException) -> bool:
    name = type(exc).__name__
    if "RateLimit" in name or name == "RateLimitError":
        return True
    status = getattr(exc, "status_code", None)
    if status == 429:
        return True
    resp = getattr(exc, "response", None)
    if resp is not None and getattr(resp, "status_code", None) == 429:
        return True
    return False


def _error_payload(raw: dict[str, Any]) -> dict[str, Any]:
    err = raw.get("error")
    return err if isinstance(err, dict) else {}


def _is_rate_limit_error_body(raw: dict[str, Any]) -> bool:
    err = _error_payload(raw)
    code = err.get("code")
    if code in HARNESS_RETRY_PROVIDER_ERROR_CODES:
        return True
    msg = str(err.get("message") or "")
    return "429" in msg and "rate" in msg.lower()


def _provider_error_message(raw: dict[str, Any]) -> str:
    err = _error_payload(raw)
    if err:
        return f"OpenRouterError: code={err.get('code')} message={err.get('message')}"
    if not raw.get("choices"):
        return "OpenRouterError: missing choices in response"
    return "OpenRouterError: unknown provider error"


def _cost_from_raw(
    raw: dict[str, Any],
    *,
    model_id: str,
    pricing_cost_fn: Any | None,
) -> float | None:
    usage_raw = raw.get("usage") or {}
    if pricing_cost_fn and usage_raw:
        usage = {
            "prompt_tokens": usage_raw.get("prompt_tokens"),
            "completion_tokens": usage_raw.get("completion_tokens"),
            "cost": usage_raw.get("cost"),
        }
        if usage.get("cost") is not None or (
            usage.get("prompt_tokens") is not None and usage.get("completion_tokens") is not None
        ):
            return float(pricing_cost_fn(usage, model_id=model_id))
    if usage_raw.get("cost") is not None:
        return float(usage_raw["cost"])
    return None


def _rate_limit_retry_record(
    *,
    call_index: int,
    scenario_id: str,
    model_id: str,
    messages_before: list[dict[str, Any]],
    req_body: dict[str, Any],
    raw_response: dict[str, Any],
    provider_error: str,
    latency_ms: float,
    episode_round: int,
    request_id: str,
) -> HarnessV2CallRecord:
    return HarnessV2CallRecord(
        call_index=call_index,
        scenario_id=scenario_id,
        model_id=model_id,
        messages_before=messages_before,
        request=req_body,
        raw_response=raw_response,
        assistant_content="",
        tool_calls=[],
        usage={},
        cost_usd=None,
        provider_error=provider_error,
        latency_ms=latency_ms,
        episode_round=episode_round,
        request_id=request_id,
        retried_after_rate_limit=True,
        billed_placeholder_usd=0.0,
        reconciliation_source=_ASSUMED_UNBILLED_429,
    )


def _provider_error_record(
    *,
    call_index: int,
    scenario_id: str,
    model_id: str,
    messages_before: list[dict[str, Any]],
    req_body: dict[str, Any],
    raw_response: dict[str, Any],
    provider_error: str,
    latency_ms: float,
    episode_round: int,
    request_id: str,
    cost_usd: float | None,
    billed_placeholder_usd: float | None,
) -> HarnessV2CallRecord:
    return HarnessV2CallRecord(
        call_index=call_index,
        scenario_id=scenario_id,
        model_id=model_id,
        messages_before=messages_before,
        request=req_body,
        raw_response=raw_response,
        assistant_content="",
        tool_calls=[],
        usage=raw_response.get("usage") or {},
        cost_usd=cost_usd,
        provider_error=provider_error,
        latency_ms=latency_ms,
        episode_round=episode_round,
        request_id=request_id,
        ledger_status="provider_error",
        billed_placeholder_usd=billed_placeholder_usd,
    )


async def run_tools_episode_async(
    *,
    scenario_id: str,
    model_id: str,
    config_key: str,
    system_prompt: str,
    initial_user: str,
    executor: HarnessV2MockToolExecutor,
    family: str,
    max_rounds: int = 4,
    max_tokens: int | None = None,
    temperature: float = 0.0,
    pricing_cost_fn: Any | None = None,
    pricing_table: OpenRouterPricingTable | None = None,
    call_index_start: int = 1,
    http_budget: Any | None = None,
    b3_context: HarnessV2B3EpisodeContext | None = None,
    on_http_record: Any | None = None,
    http_transport: httpx.AsyncBaseTransport | None = None,
    http_client: httpx.AsyncClient | None = None,
    wall_timeout_s: float = DEFAULT_HTTP_ATTEMPT_WALL_TIMEOUT_S,
    rate_limit_backoffs: tuple[float, ...] = HARNESS_RATE_LIMIT_BACKOFF_S,
    rate_limit_max_retries: int = HARNESS_RATE_LIMIT_MAX_RETRIES,
    episode_wall: EpisodeWallClock | None = None,
) -> HarnessV2EpisodeTrajectory:
    if http_transport is None and http_client is not None:
        http_transport = http_client._transport
    base_url, api_key = _openrouter_client_config()
    messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]
    append_user_message(messages, initial_user, b3_context)
    traj = HarnessV2EpisodeTrajectory(
        scenario_id=scenario_id,
        model_id=model_id,
        config_key=config_key,
        system_prompt=system_prompt,
    )
    wall = episode_wall or EpisodeWallClock(family)
    call_index = call_index_start
    tokens_cap = max_tokens if max_tokens is not None else max_tokens_for_model_id(model_id)
    extra_body = build_harness_v2_extra_body(model_id)

    for round_idx in range(max_rounds):
        episode_round = round_idx + 1
        if not wall.before_round_allowed():
            traj.invalid_timeout = True
            break
        req_body = {
            "model": model_id,
            "messages": messages,
            "tools": HARNESS_V2_TOOLS,
            "tool_choice": "auto",
            "temperature": temperature,
            "max_tokens": tokens_cap,
            "extra_body": json.loads(json.dumps(extra_body)),
        }
        messages_before = json.loads(json.dumps(messages))
        prompt_tokens = _estimate_prompt_tokens(messages)
        placeholder = 0.0
        if pricing_table is not None:
            placeholder = cancelled_timeout_placeholder_usd(
                model_id=model_id,
                prompt_tokens=prompt_tokens,
                max_tokens=tokens_cap,
                pricing=pricing_table,
            )

        next_round = False
        episode_done = False
        for retry_idx in range(rate_limit_max_retries + 1):
            if http_budget is not None and not http_budget.acquire():
                if traj.calls:
                    traj.calls[-1].episode_incomplete = True
                episode_done = True
                break

            request_id = str(uuid.uuid4())
            start = time.perf_counter()
            try:
                outcome = await one_billed_openrouter_attempt(
                    base_url=base_url,
                    api_key=api_key,
                    req_body=req_body,
                    model_id=model_id,
                    prompt_tokens=prompt_tokens,
                    billed_placeholder_usd=placeholder,
                    http_transport=http_transport,
                    wall_timeout_s=wall_timeout_s,
                    request_id=request_id,
                )
            except PilotBudgetExceeded:
                raise
            except Exception as exc:
                latency_ms = (time.perf_counter() - start) * 1000.0
                if _is_rate_limit_error(exc) and retry_idx < rate_limit_max_retries:
                    fail_rec = _rate_limit_retry_record(
                        call_index=call_index,
                        scenario_id=scenario_id,
                        model_id=model_id,
                        messages_before=messages_before,
                        req_body=req_body,
                        raw_response={},
                        provider_error=f"{type(exc).__name__}: {exc}",
                        latency_ms=latency_ms,
                        episode_round=episode_round,
                        request_id=request_id,
                    )
                    traj.calls.append(fail_rec)
                    if on_http_record:
                        on_http_record(fail_rec)
                    call_index += 1
                    backoff = rate_limit_backoffs[retry_idx] if retry_idx < len(rate_limit_backoffs) else 0.0
                    if backoff > 0:
                        await asyncio.sleep(backoff)
                    continue
                provider_error = f"{type(exc).__name__}: {exc}"
                err_rec = HarnessV2CallRecord(
                    call_index=call_index,
                    scenario_id=scenario_id,
                    model_id=model_id,
                    messages_before=messages_before,
                    request=req_body,
                    raw_response={},
                    assistant_content="",
                    tool_calls=[],
                    usage={},
                    cost_usd=None,
                    provider_error=provider_error,
                    latency_ms=latency_ms,
                    episode_round=episode_round,
                    request_id=request_id,
                    ledger_status="provider_error",
                    billed_placeholder_usd=placeholder,
                )
                traj.calls.append(err_rec)
                if on_http_record:
                    on_http_record(err_rec)
                call_index += 1
                traj.invalid_provider_error = True
                episode_done = True
                break

            if isinstance(outcome, CancelledTimeoutAttemptResult):
                cancelled = harness_call_record_from_cancelled_timeout(
                    outcome,
                    scenario_id=scenario_id,
                    model_id=model_id,
                    call_index=call_index,
                    episode_round=episode_round,
                    messages_before=messages_before,
                )
                traj.calls.append(cancelled)
                if on_http_record:
                    on_http_record(cancelled)
                call_index += 1
                episode_done = True
                break

            latency_ms = (time.perf_counter() - start) * 1000.0
            if isinstance(outcome, str):
                raw_incomplete = {"raw": outcome}
                err_rec = _provider_error_record(
                    call_index=call_index,
                    scenario_id=scenario_id,
                    model_id=model_id,
                    messages_before=messages_before,
                    req_body=req_body,
                    raw_response=raw_incomplete,
                    provider_error=f"OpenRouterError: incomplete response (non-JSON body)",
                    latency_ms=latency_ms,
                    episode_round=episode_round,
                    request_id=request_id,
                    cost_usd=None,
                    billed_placeholder_usd=placeholder,
                )
                traj.calls.append(err_rec)
                if on_http_record:
                    on_http_record(err_rec)
                call_index += 1
                traj.invalid_provider_error = True
                episode_done = True
                break

            raw = _response_to_dict(outcome)
            if raw.get("error") or not getattr(outcome, "choices", None):
                if _is_rate_limit_error_body(raw) and retry_idx < rate_limit_max_retries:
                    fail_rec = _rate_limit_retry_record(
                        call_index=call_index,
                        scenario_id=scenario_id,
                        model_id=model_id,
                        messages_before=messages_before,
                        req_body=req_body,
                        raw_response=raw,
                        provider_error=_provider_error_message(raw),
                        latency_ms=latency_ms,
                        episode_round=episode_round,
                        request_id=request_id,
                    )
                    traj.calls.append(fail_rec)
                    if on_http_record:
                        on_http_record(fail_rec)
                    call_index += 1
                    backoff = rate_limit_backoffs[retry_idx] if retry_idx < len(rate_limit_backoffs) else 0.0
                    if backoff > 0:
                        await asyncio.sleep(backoff)
                    continue

                pe_msg = _provider_error_message(raw)
                cost_usd = _cost_from_raw(raw, model_id=model_id, pricing_cost_fn=pricing_cost_fn)
                bill_ph = placeholder if cost_usd is None else None
                err_rec = _provider_error_record(
                    call_index=call_index,
                    scenario_id=scenario_id,
                    model_id=model_id,
                    messages_before=messages_before,
                    req_body=req_body,
                    raw_response=raw,
                    provider_error=pe_msg,
                    latency_ms=latency_ms,
                    episode_round=episode_round,
                    request_id=request_id,
                    cost_usd=cost_usd,
                    billed_placeholder_usd=bill_ph,
                )
                traj.calls.append(err_rec)
                if on_http_record:
                    on_http_record(err_rec)
                call_index += 1
                traj.invalid_provider_error = True
                episode_done = True
                break

            finish_meta = finish_metadata_from_raw_response(raw)
            msg = outcome.choices[0].message
            assistant_content = _openrouter_assistant_text(msg)
            usage = _openrouter_usage_dict(outcome.usage)
            cost_usd = pricing_cost_fn(usage, model_id=model_id) if pricing_cost_fn else None
            tool_calls_serialized: list[dict[str, Any]] = []
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    fn = tc.function
                    tool_calls_serialized.append(
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {"name": fn.name, "arguments": fn.arguments},
                        }
                    )
                assistant_msg: dict[str, Any] = {
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": tool_calls_serialized,
                }
                messages.append(assistant_msg)
                for tc in msg.tool_calls:
                    args = json.loads(tc.function.arguments or "{}")
                    obs = executor.execute(name=tc.function.name, arguments=args)
                    append_tool_message(
                        messages,
                        tool_call_id=tc.id,
                        content=obs,
                        ctx=b3_context,
                    )
                ok_rec = HarnessV2CallRecord(
                    call_index=call_index,
                    scenario_id=scenario_id,
                    model_id=model_id,
                    messages_before=messages_before,
                    request=req_body,
                    raw_response=raw,
                    assistant_content=assistant_content,
                    tool_calls=tool_calls_serialized,
                    usage=usage,
                    cost_usd=cost_usd,
                    provider_error=None,
                    latency_ms=latency_ms,
                    finish_reason=finish_meta["finish_reason"],
                    native_finish_reason=finish_meta["native_finish_reason"],
                    episode_round=episode_round,
                    request_id=request_id,
                )
                traj.calls.append(ok_rec)
                if on_http_record:
                    on_http_record(ok_rec)
                call_index += 1
                if http_budget is not None and not http_budget.can_continue():
                    traj.calls[-1].episode_incomplete = True
                    episode_done = True
                    break
                next_round = True
                break
            messages.append({"role": "assistant", "content": assistant_content})
            stop_rec = HarnessV2CallRecord(
                call_index=call_index,
                scenario_id=scenario_id,
                model_id=model_id,
                messages_before=messages_before,
                request=req_body,
                raw_response=raw,
                assistant_content=assistant_content,
                tool_calls=[],
                usage=usage,
                cost_usd=cost_usd,
                provider_error=None,
                latency_ms=latency_ms,
                finish_reason=finish_meta["finish_reason"],
                native_finish_reason=finish_meta["native_finish_reason"],
                episode_round=episode_round,
                request_id=request_id,
            )
            traj.calls.append(stop_rec)
            if on_http_record:
                on_http_record(stop_rec)
            call_index += 1
            episode_done = True
            break
        if next_round:
            continue
        if episode_done:
            break

    traj.final_messages = messages
    traj.mock_tool_log = list(executor.call_log)
    if b3_context is not None:
        traj.b3_log = list(b3_context.b3_log)
        traj.condition = b3_context.condition
    return traj
