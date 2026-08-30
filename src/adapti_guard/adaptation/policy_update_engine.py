from dataclasses import dataclass, field

from src.adapti_guard.adaptation.feedback_engine import FeedbackSignal
from src.adapti_guard.core.models import DefenseAction


@dataclass
class PolicyState:
    defense_level: int = 0

    # Adaptation pressure counters.
    attack_pressure: int = 0
    legitimate_pressure: int = 0

    # Number of genuinely successful attacks.
    successful_attacks: int = 0

    # Number of actual defense-level changes.
    total_updates: int = 0

    # Explicit audit trail of real defense-level transitions.
    # Each entry is (previous_level, new_level).
    transition_history: list[tuple[int, int]] = field(default_factory=list)


class PolicyUpdateEngine:

    def __init__(
        self,
        attack_threshold: int = 2,
        legitimate_threshold: int = 2,
    ):
        if attack_threshold <= 0:
            raise ValueError(
                "attack_threshold must be greater than 0"
            )

        if legitimate_threshold <= 0:
            raise ValueError(
                "legitimate_threshold must be greater than 0"
            )

        self.attack_threshold = attack_threshold
        self.legitimate_threshold = legitimate_threshold

        self.state = PolicyState()

    def update(
        self,
        state_or_feedback,
        feedback=None,
    ) -> PolicyState:

        # Supports:
        # update(feedback)
        # update(state, feedback)

        if feedback is None:
            feedback = state_or_feedback
            state = self.state
        else:
            state = state_or_feedback
            self.state = state

        # --------------------------------------------------
        # 1. Record genuinely successful attacks
        # --------------------------------------------------

        if feedback.attack_success:
            state.successful_attacks += 1

        # --------------------------------------------------
        # 2. Accumulate adaptation pressure
        # --------------------------------------------------

        if feedback.adaptation_signal == "INCREASE_DEFENSE":
            state.attack_pressure += 1
            state.legitimate_pressure = 0

        elif feedback.adaptation_signal == "REDUCE_DEFENSE":
            state.legitimate_pressure += 1
            state.attack_pressure = 0

        # MAINTAIN creates no new pressure.
        # Existing pressure is intentionally preserved.

        # --------------------------------------------------
        # 3. Escalation
        # --------------------------------------------------

        if state.attack_pressure >= self.attack_threshold:

            if state.defense_level < 3:
                previous_level = state.defense_level
                state.defense_level += 1
                state.total_updates += 1
                state.transition_history.append(
                    (previous_level, state.defense_level)
                )

            state.attack_pressure = 0

        # --------------------------------------------------
        # 4. De-escalation
        # --------------------------------------------------

        if state.legitimate_pressure >= self.legitimate_threshold:

            if state.defense_level > 0:
                previous_level = state.defense_level
                state.defense_level -= 1
                state.total_updates += 1
                state.transition_history.append(
                    (previous_level, state.defense_level)
                )

            state.legitimate_pressure = 0

        return state

    @staticmethod
    def action_for_level(
        level: int,
    ) -> DefenseAction:

        mapping = {
            0: DefenseAction.NO_INTERVENTION,
            1: DefenseAction.SANITIZE,
            2: DefenseAction.TOOL_RESTRICTION,
            3: DefenseAction.BLOCK,
        }

        if level not in mapping:
            raise ValueError(
                f"Unsupported defense level: {level}"
            )

        return mapping[level]
