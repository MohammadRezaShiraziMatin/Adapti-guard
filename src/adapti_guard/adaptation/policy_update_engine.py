import math
from dataclasses import dataclass, field

from adapti_guard.adaptation.feedback_engine import FeedbackSignal
from adapti_guard.core.models import DefenseAction


MAX_DEFENSE_LEVEL = 3

VALID_SIGNALS = frozenset(
    {"INCREASE_DEFENSE", "REDUCE_DEFENSE", "MAINTAIN"}
)


def _validate_threshold(name: str, value) -> None:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
    ):
        raise ValueError(
            f"{name} must be an int greater than 0, got {value!r}"
        )


@dataclass
class PolicyState:
    defense_level: int = 0

    # Adaptation pressure counters (float: they decay on MAINTAIN).
    attack_pressure: float = 0.0
    legitimate_pressure: float = 0.0

    # Number of genuinely successful attacks.
    successful_attacks: int = 0

    # Number of actual defense-level changes.
    total_updates: int = 0

    # Explicit audit trail of real defense-level transitions.
    # Each entry is (previous_level, new_level).
    transition_history: list[tuple[int, int]] = field(default_factory=list)

    def __post_init__(self):
        level = self.defense_level
        if (
            isinstance(level, bool)
            or not isinstance(level, int)
            or not 0 <= level <= MAX_DEFENSE_LEVEL
        ):
            raise ValueError(
                f"defense_level must be an int in "
                f"[0, {MAX_DEFENSE_LEVEL}], got {level!r}"
            )


class PolicyUpdateEngine:

    def __init__(
        self,
        attack_threshold: int = 2,
        legitimate_threshold: int = 2,
        pressure_decay: float = 0.5,
    ):
        _validate_threshold("attack_threshold", attack_threshold)
        _validate_threshold("legitimate_threshold", legitimate_threshold)

        # Multiplier applied to both pressure counters on every
        # MAINTAIN signal (exponential decay). 1.0 disables decay.
        if (
            isinstance(pressure_decay, bool)
            or not isinstance(pressure_decay, (int, float))
            or not math.isfinite(pressure_decay)
            or not 0.0 <= pressure_decay <= 1.0
        ):
            raise ValueError(
                f"pressure_decay must be in [0, 1], got {pressure_decay!r}"
            )

        self.pressure_decay = float(pressure_decay)

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

        if feedback is None or not hasattr(feedback, "adaptation_signal"):
            raise TypeError(
                "update() requires a FeedbackSignal, "
                f"got {type(feedback).__name__}"
            )

        if feedback.adaptation_signal not in VALID_SIGNALS:
            raise ValueError(
                "Unknown adaptation_signal "
                f"{feedback.adaptation_signal!r}; "
                f"expected one of {sorted(VALID_SIGNALS)}"
            )

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

        else:
            # MAINTAIN creates no new pressure and lets existing
            # pressure decay exponentially, so isolated events
            # separated by long quiet periods do not accumulate.
            state.attack_pressure *= self.pressure_decay
            state.legitimate_pressure *= self.pressure_decay

        # --------------------------------------------------
        # 3. Escalation
        # --------------------------------------------------

        if state.attack_pressure >= self.attack_threshold:

            if state.defense_level < MAX_DEFENSE_LEVEL:
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
