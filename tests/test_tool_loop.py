from src.adapti_guard.core.models import DefenseAction
from src.adapti_guard.defense.tool_loop import (
    MockToolRegistry,
    ToolCall,
    run_tool_turn,
    tool_allowed,
)


def test_a2_denies_send_email():
    registry = MockToolRegistry()
    call = ToolCall("send_email", {"to": "a@b.c", "body": "hi"})
    turn = run_tool_turn(requested=call, action=DefenseAction.TOOL_RESTRICTION, registry=registry)
    assert turn.executed is False
    assert turn.permission_allowed is False
    assert turn.observation == "TOOL_DENIED"
    assert registry.calls == []


def test_a0_executes_search():
    registry = MockToolRegistry()
    call = ToolCall("search", {"query": "library hours"})
    turn = run_tool_turn(requested=call, action=DefenseAction.NO_INTERVENTION, registry=registry)
    assert turn.executed is True
    assert "search_hits" in turn.observation
    assert len(registry.calls) == 1


def test_a3_blocks_turn_without_tool():
    registry = MockToolRegistry()
    call = ToolCall("create_record", {"kind": "ticket", "payload": "x"})
    turn = run_tool_turn(requested=call, action=DefenseAction.BLOCK, registry=registry)
    assert turn.executed is False
    assert turn.log["reason"] == "turn_blocked"
    assert not tool_allowed("A2")
    assert tool_allowed("A1")
