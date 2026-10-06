"""Fixed multi-turn attack sequence (ignores defense feedback; offline control arm)."""
from __future__ import annotations

from typing import Sequence

from adapti_guard.attacker.adaptive_attacker import AdaptiveAttacker, AttackAttempt, AttackerState


class FixedSequenceAttacker:
    """
    Pre-planned family sequence for controlled comparison with AdaptiveAttacker.

    Does not change family or payload index based on defense or target feedback.
    """

    def __init__(
        self,
        family_sequence: Sequence[str],
        *,
        sophistication_index: int = 0,
    ) -> None:
        seq = tuple(family_sequence)
        for family in seq:
            if family not in AdaptiveAttacker.ATTACK_FAMILIES:
                raise ValueError(f"unknown attack family: {family}")
        if not seq:
            raise ValueError("family_sequence must be non-empty")
        self._family_sequence = seq
        self._sophistication_index = max(0, int(sophistication_index))
        self.state = AttackerState(current_family=seq[0])

    def generate(self) -> AttackAttempt:
        self.state.attempts += 1
        turn_idx = self.state.attempts - 1
        family = self._family_sequence[min(turn_idx, len(self._family_sequence) - 1)]
        self.state.current_family = family
        payloads = AdaptiveAttacker.PAYLOADS[family]
        soph = min(self._sophistication_index, len(payloads) - 1)
        payload = payloads[soph]
        return AttackAttempt(
            attack_id=self.state.attempts,
            family=family,
            payload=payload,
            successful=False,
        )

    def observe_defense(self, *, blocked: bool, harmful_outcome: bool) -> None:
        """Fixed control: no policy update from defense or target feedback."""

    def record(self, attempt: AttackAttempt) -> None:
        self.state.history.append(attempt)


def default_fixed_family_sequence(max_turns: int) -> tuple[str, ...]:
    """First N ATTACK_FAMILIES in repository order (planning helper)."""
    families = AdaptiveAttacker.ATTACK_FAMILIES
    n = max(1, min(max_turns, len(families)))
    return tuple(families[:n])
