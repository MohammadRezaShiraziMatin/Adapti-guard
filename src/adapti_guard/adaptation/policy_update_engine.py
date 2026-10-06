import math
import threading
from dataclasses import dataclass, field, replace

from adapti_guard.adaptation.feedback_engine import AdaptationSignal
from adapti_guard.core.models import DefenseAction

MIN_DEFENSE_LEVEL = 0
MAX_DEFENSE_LEVEL = 3

# ``transition_history`` keeps only the most recent entries (Q1 M-1);
# ``total_updates`` and ``transitions_dropped`` keep the full count.
MAX_TRANSITION_HISTORY = 1000
MAX_BACKOFF_CAP = 10


@dataclass
class PolicyState:
    defense_level: int = 0

    # Adaptation pressure counters.
    attack_pressure: int = 0
    legitimate_pressure: int = 0

    # Consecutive benign-and-allowed episodes (opt-in time-based
    # de-escalation, see ``PolicyUpdateEngine.benign_streak_threshold``).
    benign_streak: int = 0

    # --- hysteresis / attack memory (opt-in, see PolicyUpdateEngine) ---
    # Episodes processed by ``update`` (monotone counter).
    episode: int = 0
    last_change_episode: int | None = None
    last_attack_episode: int | None = None
    # Streak-driven down-moves since the last escalation, and the
    # exponential back-off exponent applied to the benign-streak length.
    streak_deescalations: int = 0
    backoff: int = 0

    # Number of genuinely successful attacks.
    successful_attacks: int = 0

    # Number of actual defense-level changes.
    total_updates: int = 0

    # Explicit audit trail of real defense-level transitions.
    # Each entry is (previous_level, new_level); bounded, see
    # MAX_TRANSITION_HISTORY.
    transition_history: list[tuple[int, int]] = field(default_factory=list)
    transitions_dropped: int = 0


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
    pressure counters never decay, de-escalation requires explicit
    ``REDUCE_DEFENSE`` feedback, and there is no dwell time. Opt-in
    mechanisms (Q1 F1/F6/H-1/H-2):

    * ``pressure_decay``: on each ``MAINTAIN`` signal, attack/legitimate
      pressure is reduced by this amount (floor 0).
    * ``benign_streak_threshold``: after this many consecutive
      ``MAINTAIN`` episodes with a successful legitimate task the level
      drops by one, independent of cost.
    * ``min_dwell``: a down-move is only allowed once at least this many
      episodes have passed since the last level change **and** since the
      last ``INCREASE_DEFENSE`` signal. Escalation is never delayed. This
      removes the L2<->L3 limit cycle (hysteresis).
    * ``backoff_cap``: attack memory for the benign streak. Each
      escalation that follows a streak-driven down-move doubles the
      streak length required for the next one (up to ``2**backoff_cap``
      times the base); the exponent decays by one each time a full streak
      completes at level 0. A patient attacker can still wait the streak
      out, but each probe costs exponentially more.

    Streak-driven de-escalation is steerable by anyone who can send
    benign-looking traffic; dwell and back-off bound, not remove, that.

    Thread-safety: ``update`` takes an internal lock, so concurrent calls
    on one engine are serialised. State objects are not shared: ``update``
    returns a new ``PolicyState`` and never mutates the object passed in.
    """

    def __init__(
        self,
        attack_threshold: int = 2,
        legitimate_threshold: int = 2,
        *,
        pressure_decay: int = 0,
        benign_streak_threshold: int | None = None,
        min_dwell: int = 0,
        backoff_cap: int = 0,
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
        self.min_dwell = _require_non_negative_int("min_dwell", min_dwell)
        self.backoff_cap = _require_non_negative_int("backoff_cap", backoff_cap)
        if self.backoff_cap > MAX_BACKOFF_CAP:
            raise ValueError(
                f"backoff_cap must be <= {MAX_BACKOFF_CAP}, got {backoff_cap}"
            )

        self.state = PolicyState()
        self._lock = threading.RLock()

    def reset(self, level: int = 0) -> PolicyState:
        """Replace the engine state with a fresh one at ``level``."""
        fresh = PolicyState(defense_level=level)
        _validate_state(fresh)
        with self._lock:
            self.state = fresh
            return fresh

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

    def _transition(self, state: PolicyState, delta: int) -> bool:
        new_level = state.defense_level + delta
        if not MIN_DEFENSE_LEVEL <= new_level <= MAX_DEFENSE_LEVEL:
            return False
        previous_level = state.defense_level
        state.defense_level = new_level
        state.total_updates += 1
        state.last_change_episode = state.episode
        state.transition_history.append((previous_level, new_level))
        excess = len(state.transition_history) - MAX_TRANSITION_HISTORY
        if excess > 0:
            del state.transition_history[:excess]
            state.transitions_dropped += excess
        return True

    def _dwell_elapsed(self, state: PolicyState) -> bool:
        if not self.min_dwell:
            return True
        for marker in (state.last_change_episode, state.last_attack_episode):
            if marker is not None and state.episode - marker < self.min_dwell:
                return False
        return True

    def _required_streak(self, state: PolicyState) -> int:
        return self.benign_streak_threshold * (2 ** state.backoff)

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
            # mutated (Q1 F11). The copy is O(MAX_TRANSITION_HISTORY).
            state = replace(
                base,
                transition_history=list(base.transition_history),
            )
            state.episode += 1

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
                state.last_attack_episode = state.episode

            elif signal is AdaptationSignal.REDUCE_DEFENSE:
                state.legitimate_pressure += 1
                state.attack_pressure = 0
                state.benign_streak = 0

            else:
                # MAINTAIN creates no new pressure. With the default
                # ``pressure_decay=0`` existing pressure is preserved
                # (historical behaviour: INCREASE, MAINTAIN, INCREASE
                # still escalates).
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
            # 3. Escalation (never delayed by dwell)
            # ----------------------------------------------------------

            if state.attack_pressure >= self.attack_threshold:
                if self._transition(state, +1):
                    if state.streak_deescalations and self.backoff_cap:
                        state.backoff = min(state.backoff + 1, self.backoff_cap)
                    state.streak_deescalations = 0
                state.attack_pressure = 0

            # ----------------------------------------------------------
            # 4. De-escalation (subject to dwell)
            # ----------------------------------------------------------

            if (
                state.legitimate_pressure >= self.legitimate_threshold
                and self._dwell_elapsed(state)
            ):
                self._transition(state, -1)
                state.legitimate_pressure = 0

            if (
                self.benign_streak_threshold is not None
                and state.benign_streak >= self._required_streak(state)
            ):
                if state.defense_level == 0:
                    # Nothing to lower: a full quiet streak at the floor
                    # forgives one back-off step.
                    state.backoff = max(0, state.backoff - 1)
                    state.benign_streak = 0
                elif self._dwell_elapsed(state):
                    if self._transition(state, -1):
                        state.streak_deescalations += 1
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
