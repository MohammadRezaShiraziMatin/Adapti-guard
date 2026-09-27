from adapti_guard.core.models import DefenseAction
from adapti_guard.defense.tool_loop import ToolCall
from adapti_guard.evaluation.agent_environment import AgentEnvironment

def test_agent_environment_offline_mock_label():
    assert AgentEnvironment.execution_mode == "OFFLINE_MOCK"


def test_agent_privileged_execution():
    env = AgentEnvironment(seed=1)
    req = ToolCall(name="send_email", arguments={"to": "a", "body": "b"})
    r = env.step(req, DefenseAction.NO_INTERVENTION)
    assert r.tool_executed and r.privileged_executed

def test_agent_denied():
    env = AgentEnvironment(seed=1)
    req = ToolCall(name="send_email", arguments={"to": "a", "body": "b"})
    r = env.step(req, DefenseAction.TOOL_RESTRICTION)
    assert not r.tool_executed
