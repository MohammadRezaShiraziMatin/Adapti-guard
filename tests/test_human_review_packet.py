"""Phase 5 human-review packet (design layer; no human study)."""
from adapti_guard.core.episode import EpisodeTrace
from adapti_guard.evaluation.human_review_packet import (
    packet_from_episode_trace,
    packet_from_evidence_record,
)


def _sample_trace() -> EpisodeTrace:
    return EpisodeTrace(
        prompt="hi",
        context_present=False,
        tool_name="send_email",
        privileged_tool=True,
        detector_probability=0.9,
        detector_indicators=["x"],
        detector_hit=True,
        risk_score=0.8,
        risk_level="HIGH",
        risk_reasons=["indicator"],
        risk_features={},
        policy_action="A3",
        policy_reason="high risk",
        defense_level=3,
        blocked=True,
        allowed=False,
        content="",
        tool_access=False,
        tool_requested="send_email",
        tool_permission_allowed=False,
        tool_executed=False,
        tool_observation="",
        tool_reason="denied",
    )


def test_packet_separates_machine_and_human_outcome():
    p = packet_from_episode_trace(_sample_trace(), condition_id="COND-X")
    assert p["machine_decision"]["risk"]["level"] == "HIGH"
    assert p["human_decision"] is None
    assert p["empirical_human_outcome"] is None


def test_packet_from_evidence_record_no_fabrication():
    rec = {
        "condition_id": "COND-E1-STATEFUL-OFFLINE",
        "attack_id": "fixture",
        "config_hash": "abc",
        "evidence_type": "offline_fixture",
    }
    p = packet_from_evidence_record(rec)
    assert p["human_reviewable_evidence"]["condition_id"] == "COND-E1-STATEFUL-OFFLINE"
    assert "attack_success" not in p
