from adapti_guard.core.models import DefenseAction
from adapti_guard.evaluation.stateful_episode import StatefulEpisodeRunner, TurnSpec

def _target(h, m):
    return f'ACK TOOL_REQUEST: {{"name":"send_email","arguments":{{"to":"a","body":"b"}}}}'

def _noop(**_):
    return DefenseAction.NO_INTERVENTION, {}

def test_stateful_replay():
    r = StatefulEpisodeRunner().run([TurnSpec("hi")], target=_target, defense=_noop, seed=1)
    assert r.n_turns == 1 and r.config_hash
