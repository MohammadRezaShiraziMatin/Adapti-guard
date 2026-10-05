import math
import threading
from dataclasses import dataclass, field, replace

from adapti_guard.adaptation.feedback_engine import (
    AdaptationSignal,
    FeedbackSignal,
)
from adapti_guard.core.models import DefenseAction

MIN_DEFENSE_LEVEL = 0
MAX_DEFENSE_LEVEL = 3


@dataclass
class PolicyState:
    defense_level: int = 0

    # Adaptation pressure counters.
    attack_pressure: int = 0
    legitimate_pressure: int = 0

    # Consecutive benign-and-allowed episodes (opt-in time-based
    # de-escalation, see ``PolicyUpdateEngine.benign_streak_threshold``).
    benign_streak: int = 0

    # Number of genuinely successful attacks.
    successful_attacks: int = 0

    # Number of actual defense-level changes.
    total_updates: int = 0

    # Explicit audit trail of real defense-level transitions.
    # Each entry is (previous_level, new_level).
    transition_history: list[tuple[int, int]] = field(default_factory=list)


def _require_positive_int(name: str, value) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(
            f"{name} must be an int >= 1, got {value!r}"
        )
    if value <= 0:
        raise ValueError(f"{name} must be greater than 0")
    return value


def _require_non_negative_int(name: str, value) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(
            f"{name} must be an int >= 0, got {value!r}"
        )
    return value


def _validate_state(state: PolicyState) -> None:
    level = state.defense_level
    if (
        isinstance(level, bool)
        or not isinstance(level, int)
        or not MIN_DEFENSE_LEVEL <= level <= MAX_DEFENSE_LEVEL
    ):
        raise ValueError(
            f"defense_level must be an int in "
            f"[{MIN_DEFENSE_LEVEL}, {MAX_DEFENSE_LEVEL}], got {level!r}"
        )


class PolicyUpdateEngine:
    """Maps feedback signals to defense-level transitions.

    Defaults reproduce the historical (frozen-experiment) behaviour:
    pressure counters never decay and de-escalation requires explicit
    ``REDUCE_DEFENSE`` feedback. Two opt-in mechanisms address Q1 F1/F6:

    * ``pressure_decay``: on each ``MAINTAIN`` signal, attack/legitimate
      pressure is reduced by this amount (floor 0), so isolated events
      far apart in time no longer accumulate into a level change.
    * ``benign_streak_threshold``: after this many consecutive
      ``MAINTAIN`` episodes with a successful legitimate task, the level
      drops by one, independently of any defense cost. Any
      ``INCREASE_DEFENSE``/``REDUCE_DEFENSE`` signal resets the streak.

    Thread-safety: ``update`` takes an internal lock, so concurrent calls
    on one engine are serialised. State objects themselves are not
    shared: ``update`` returns a new ``PolicyState`` and never mutates the
    object passed in.
    """

    def __init__(
        self,
        attack_threshold: int = 2,
        legitimate_threshold: int = 2,
        *,
        pressure_decay: int = 0,
        benign_streak_threshold: int | None = None,
    ):
        for name, value in (
            ("attack_threshold", attack_threshold),
            ("legitimate_threshold", legitimate_threshold),
        ):
            if isinstance(value, float) and math.isnan(value):
                raise ValueError(f"{name} must not be NaN")
        self.attack_threshold = _require_positive_int(
            "attack_threshold", attack_threshold
        )
        self.legitimate_threshold = _require_positive_int(
            "legitimate_threshold", legitimate_threshold
        )
        self.pressure_decay = _require_non_negative_int(
            "pressure_decay", pressure_decay
        )
        self.benign_streak_threshold = (
            None
            if benign_streak_threshold is None
            else _require_positive_int(
                "benign_streak_threshold", benign_streak_threshold
            )
        )

        self.state = PolicyState()
        self._lock = threading.RLock()

    @staticmethod
    def _parse_signal(feedback) -> AdaptationSignal:
        raw = getattr(feedback, "adaptation_signal", None)
        try:
            return AdaptationSignal(raw)
        except ValueError:
            raise ValueError(
                f"Unknown adaptation_signal: {raw!r}; expected one of "
                f"{[s.value for s in AdaptationSignal]}"
            ) from None

    @staticmethod
    def _transition(state: PolicyState, delta: int) -> None:
        new_level = state.defense_level + delta
        if MIN_DEFENSE_LEVEL <= new_level <= MAX_DEFENSE_LEVEL:
            previous_level = state.defense_level
            state.defense_level = new_level
            state.total_updates += 1
            state.transition_history.append((previous_level, new_level))

    def update(
        self,
        state_or_feedback,
        feedback=None,
    ) -> PolicyState:

        # Supports:
        # update(feedback)
        # update(state, feedback)

        explicit_state = feedback is not None
        if not explicit_state:
            feedback = state_or_feedback

        if feedback is None:
            raise TypeError("feedback must not be None")
        signal = self._parse_signal(feedback)

        with self._lock:
            # self.state must be read under the lock, otherwise concurrent
            # callers start from the same base and lose updates.
            base = state_or_feedback if explicit_state else self.state
            if not isinstance(base, PolicyState):
                raise TypeError(
                    f"state must be a PolicyState, got {type(base).__name__}"
                )
            _validate_state(base)

            # Work on a copy: the caller's state is never aliased or
            # mutated (Q1 F11).
            state = replace(
                base,
                transition_history=list(base.transition_history),
            )

            # ----------------------------------------------------------
            # 1. Record genuinely successful attacks
            # ----------------------------------------------------------

            if feedback.attack_success:
                state.successful_attacks += 1

            # ----------------------------------------------------------
            # 2. Accumulate / decay adaptation pressure
            # ----------------------------------------------------------

            if signal is AdaptationSignal.INCREASE_DEFENSE:
                state.attack_pressure += 1
                state.legitimate_pressure = 0
                state.benign_streak = 0

            elif signal is AdaptationSignal.REDUCE_DEFENSE:
                state.legitimate_pressure += 1
                state.attack_pressure = 0
                state.benign_streak = 0

            else:
                # MAINTAIN creates no new pressure. With the default
                # ``pressure_decay=0`` existing pressure is preserved
                # (historical behaviour).
                if self.pressure_decay:
                    state.attack_pressure = max(
                        0, state.attack_pressure - self.pressure_decay
                    )
                    state.legitimate_pressure = max(
                        0, state.legitimate_pressure - self.pressure_decay
                    )
                if feedback.legitimate_success and not feedback.attack_success:
                    state.benign_streak += 1
                else:
                    state.benign_streak = 0

            # ----------------------------------------------------------
            # 3. Escalation
            # ----------------------------------------------------------

            if state.attack_pressure >= self.attack_threshold:
                self._transition(state, +1)
                state.attack_pressure = 0

            # ----------------------------------------------------------
            # 4. De-escalation
            # ----------------------------------------------------------

            if state.legitimate_pressure >= self.legitimate_threshold:
                self._transition(state, -1)
                state.legitimate_pressure = 0

            if (
                self.benign_streak_threshold is not None
                and state.benign_streak >= self.benign_streak_threshold
            ):
                self._transition(state, -1)
                state.benign_streak = 0

            self.state = state
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
