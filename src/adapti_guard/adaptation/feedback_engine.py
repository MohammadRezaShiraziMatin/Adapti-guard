from dataclasses import dataclass

from src.adapti_guard.evaluation.outcome_evaluator import (
    OutcomeResult,
)


@dataclass
class FeedbackSignal:
    reward: float
    security_feedback: float
    utility_feedback: float
    cost_penalty: float
    adaptation_signal: str
    attack_success: bool
    legitimate_success: bool


class FeedbackEngine:

    def __init__(
        self,
        security_weight: float = 0.5,
        utility_weight: float = 0.4,
        cost_weight: float = 0.1,
    ):
        self.security_weight = security_weight
        self.utility_weight = utility_weight
        self.cost_weight = cost_weight

    def generate(
        self,
        outcome: OutcomeResult,
    ) -> FeedbackSignal:

        security_feedback = outcome.security_score
        utility_feedback = outcome.utility_score
        cost_penalty = outcome.defense_cost

        reward = (
            self.security_weight * security_feedback
            + self.utility_weight * utility_feedback
            - self.cost_weight * cost_penalty
        )

        # ---------------------------------------------------------
        # UTILITY-AWARE ADAPTATION
        # ---------------------------------------------------------

        # 1. Legitimate task succeeded, but the defense action
        #    was maximally restrictive/expensive.
        #
        #    Example:
        #        legitimate task
        #        + BLOCK
        #        + cost = 0.50
        #
        #    This indicates potential over-defense.
        if (
            outcome.legitimate_task
            and outcome.legitimate_success
            and cost_penalty >= 0.50
        ):
            signal = "REDUCE_DEFENSE"

        # 2. Legitimate task failed under an expensive defense.
        elif (
            outcome.legitimate_task
            and not outcome.legitimate_success
            and utility_feedback == 0.0
            and cost_penalty >= 0.50
        ):
            signal = "REDUCE_DEFENSE"

        # 3. Attack successfully bypassed the defense.
        elif outcome.attack_success:
            signal = "INCREASE_DEFENSE"

        # 4. Attack was contained while the current defense
        #    still incurs relatively low cost.
        elif (
            outcome.attack_present
            and security_feedback >= 1.0
            and utility_feedback == 0.0
            and cost_penalty < 0.50
        ):
            signal = "INCREASE_DEFENSE"

        # 5. Legitimate task succeeded with acceptable cost.
        elif outcome.legitimate_success:
            signal = "MAINTAIN"

        else:
            signal = "MAINTAIN"

        return FeedbackSignal(
            reward=round(reward, 4),
            security_feedback=security_feedback,
            utility_feedback=utility_feedback,
            cost_penalty=cost_penalty,
            adaptation_signal=signal,
            attack_success=outcome.attack_success,
            legitimate_success=outcome.legitimate_success,
        )
