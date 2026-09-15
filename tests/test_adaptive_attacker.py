from adapti_guard.attacker.adaptive_attacker import (
    AdaptiveAttacker,
)


def test_initial_attack_family():
    attacker = AdaptiveAttacker()

    attempt = attacker.generate()

    assert attempt.family == "direct_injection"
    assert attempt.attack_id == 1
    assert len(attempt.payload) > 0


def test_attacker_changes_strategy_after_failure():
    attacker = AdaptiveAttacker()

    attempt = attacker.generate()
    attacker.record(attempt)

    attacker.observe(False)

    next_attempt = attacker.generate()

    assert next_attempt.family == "indirect_injection"


def test_attacker_tracks_success():
    attacker = AdaptiveAttacker()

    attempt = attacker.generate()
    attacker.record(attempt)

    attacker.observe(True)

    assert attacker.state.successes == 1
    assert attacker.state.failures == 0


def test_attacker_cycles_attack_families():
    attacker = AdaptiveAttacker()

    families = []

    for _ in range(5):
        attempt = attacker.generate()
        families.append(attempt.family)

        attacker.record(attempt)
        attacker.observe(False)

    assert families == [
        "direct_injection",
        "indirect_injection",
        "context_manipulation",
        "tool_output_injection",
        "direct_injection",
    ]
