from adapti_guard.attacker.adaptive_attacker import AdaptiveAttacker
from adapti_guard.core.models import DefenseAction
from adapti_guard.evaluation.adaptive_episode import AdaptiveEpisodeRunner

def _block(**_):
    return DefenseAction.TOOL_RESTRICTION, {}

def test_adaptive_strategy_changes():
    r = AdaptiveEpisodeRunner(4).run(attacker=AdaptiveAttacker(), defense=_block, seed=0)
    assert r.strategy_changed
