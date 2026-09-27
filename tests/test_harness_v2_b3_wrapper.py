"""Tests for harness v2 B3 append-once wrapper."""
from __future__ import annotations

from adapti_guard.evaluation.harness_v2.harness_v2_b3_pretarget_wrapper import (
    HarnessV2B3EpisodeContext,
    append_tool_message,
    append_user_message,
    count_user_tool_messages,
)


def test_b3_calls_defense_once_per_append_not_on_resend() -> None:
    ctx = HarnessV2B3EpisodeContext.for_condition("B3")
    messages: list = [{"role": "system", "content": "sys"}]
    append_user_message(messages, "hello user", ctx)
    n1 = ctx.defense_fn_call_count
    # Simulate API round — messages list sent as-is; no re-append
    append_tool_message(messages, tool_call_id="tc1", content='{"x":1}', ctx=ctx)
    n2 = ctx.defense_fn_call_count
    assert n2 == n1 + 1
    assert count_user_tool_messages(messages) == n2


def test_a0_zero_defense_calls() -> None:
    ctx = HarnessV2B3EpisodeContext.for_condition("A0")
    messages: list = [{"role": "system", "content": "sys"}]
    append_user_message(messages, "hi", ctx)
    append_tool_message(messages, tool_call_id="t", content="{}", ctx=ctx)
    assert ctx.defense_fn_call_count == 0
