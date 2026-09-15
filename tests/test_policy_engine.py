from adapti_guard.core.models import DefenseAction, RiskLevel
from adapti_guard.policy.policy_engine import DefensePolicyEngine
from adapti_guard.risk.risk_engine import RiskAssessment


def make_risk(level, score):
    return RiskAssessment(
        score=score,
        level=level,
        reasons=[],
    )


def test_low_risk_no_intervention():
    engine = DefensePolicyEngine()

    risk = make_risk(RiskLevel.LOW, 0.10)

    decision = engine.decide(risk)

    assert decision.action == DefenseAction.NO_INTERVENTION


def test_medium_risk_sanitize():
    engine = DefensePolicyEngine()

    risk = make_risk(RiskLevel.MEDIUM, 0.50)

    decision = engine.decide(risk)

    assert decision.action == DefenseAction.SANITIZE


def test_high_risk_blocks():
    engine = DefensePolicyEngine()

    risk = make_risk(RiskLevel.HIGH, 0.90)

    decision = engine.decide(risk)

    assert decision.action == DefenseAction.BLOCK


def test_high_risk_sensitive_tool():
    engine = DefensePolicyEngine()

    risk = make_risk(RiskLevel.HIGH, 0.90)

    decision = engine.decide(
        risk,
        tool_sensitive=True,
    )

    assert decision.action == DefenseAction.TOOL_RESTRICTION
