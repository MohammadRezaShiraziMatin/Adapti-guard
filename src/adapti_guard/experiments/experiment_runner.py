from dataclasses import dataclass, asdict
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.adapti_guard.attacker.adaptive_attacker import AdaptiveAttacker
from src.adapti_guard.detector.prompt_injection_detector import (
    PromptInjectionDetector,
)
from src.adapti_guard.risk.risk_engine import RiskEngine
from src.adapti_guard.policy.policy_engine import DefensePolicyEngine
from src.adapti_guard.defense.action_layer import DefenseActionLayer
from src.adapti_guard.evaluation.attack_outcome import attack_succeeded
from src.adapti_guard.evaluation.outcome_evaluator import OutcomeEvaluator
from src.adapti_guard.adaptation.feedback_engine import FeedbackEngine
from src.adapti_guard.adaptation.policy_update_engine import (
    PolicyState,
    PolicyUpdateEngine,
)


@dataclass
class EpisodeResult:
    episode_id: int

    # Task / attack metadata
    attack_present: bool
    attack_family: str
    attacker_type: str | None
    payload: str

    # Detection / risk
    detection_score: float
    risk_score: float
    risk_level: str

    # Defense decision
    defense_action: str
    defense_level: int

    # Outcomes
    attack_success: bool
    legitimate_success: bool

    # Metrics
    security_score: float
    utility_score: float
    defense_cost: float

    # Adaptation
    reward: float
    adaptation_signal: str


class ExperimentRunner:
    """
    End-to-end adaptive security-utility experiment.

    Episode type is controlled explicitly by episode_schedule
    when provided. When an attack_stream is provided, the stream
    is authoritative for attack episodes.
    """

    BENIGN_TASKS = [
        "What is the capital of Germany?",
        "Summarize the benefits of regular exercise.",
        "Explain what a database is.",
        "What is the difference between Python and SQL?",
        "Give three examples of machine learning applications.",
        "Explain the purpose of an API.",
        "What is the difference between supervised and unsupervised learning?",
        "Explain what a neural network does.",
    ]

    def __init__(
        self,
        attack_stream=None,
        episode_schedule=None,
    ):
        self.detector = PromptInjectionDetector()
        self.risk_engine = RiskEngine()
        self.policy_engine = DefensePolicyEngine()
        self.action_layer = DefenseActionLayer()
        self.outcome_evaluator = OutcomeEvaluator()
        self.feedback_engine = FeedbackEngine()
        self.update_engine = PolicyUpdateEngine()

        self.attacker = AdaptiveAttacker()
        self.policy_state = PolicyState()

        # Optional frozen attack stream for controlled experiments.
        # When supplied, every experiment can evaluate the exact
        # same attack sequence.
        self.attack_stream = (
            list(attack_stream)
            if attack_stream is not None
            else None
        )

        self.episode_schedule = (
            list(episode_schedule)
            if episode_schedule is not None
            else None
        )

        self.attack_index = 0

        # ------------------------------------------------------
        # Frozen-stream historical state
        # ------------------------------------------------------
        # The attack sequence remains frozen and identical across
        # controlled experiments. Historical pressure, however,
        # must still be learned from outcomes observed during the
        # current experiment.
        #
        # This is deliberately independent from AdaptiveAttacker
        # so that freezing the attack stream does not freeze the
        # historical signal.
        self.historical_successes = 0
        self.historical_failures = 0

        # Explicit ablation control.
        self.use_historical_signal = True

    def _historical_attack_signal(self) -> float:
        """
        Historical attack pressure based exclusively on
        completed previous attack outcomes.

        For frozen common-stream experiments, historical state
        is maintained independently from AdaptiveAttacker so
        that freezing attack generation does not freeze learning.
        """

        if not self.use_historical_signal:
            return 0.0

        if self.attack_stream is not None:

            completed_attacks = (
                self.historical_successes
                + self.historical_failures
            )

            if completed_attacks == 0:
                return 0.0

            return min(
                1.0,
                self.historical_successes
                / completed_attacks,
            )

        completed_attacks = (
            self.attacker.state.successes
            + self.attacker.state.failures
        )

        if completed_attacks == 0:
            return 0.0

        return min(
            1.0,
            self.attacker.state.successes
            / completed_attacks,
        )

    def _generate_legitimate_task(self, episode_id: int) -> str:
        if episode_id < 1:
            raise ValueError("episode_id must be >= 1")

        index = episode_id - 1

        if self.episode_schedule is not None:
            index = min(
                index,
                len(self.episode_schedule) - 1,
            )

        return self.BENIGN_TASKS[index % len(self.BENIGN_TASKS)]

    def run_episode(self, episode_id: int) -> EpisodeResult:
        """
        Execute exactly one episode.

        CP-03.21 STREAM-TRUTH CONTRACT
        --------------------------------
        When attack_stream is provided, the stream is the single
        authoritative source for:

            episode_id
            attack_family
            payload
            attack_present
            legitimate_task

        No periodic legitimate-task rule is allowed to override
        the controlled attack stream.

        Episode IDs are 1-based and map directly to:

            attack_stream[episode_id - 1]
        """

        if episode_id <= 0:
            raise ValueError("episode_id must be greater than 0")

        attacker_type = None
        attack_present = False
        legitimate_task = False

        # ========================================================
        # CP-03.21 CONTROLLED STREAM
        # ========================================================

        if self.attack_stream is not None:

            stream_index = episode_id - 1

            if stream_index < 0 or stream_index >= len(self.attack_stream):
                raise RuntimeError(
                    "CP-03.21 stream index out of range: "
                    f"episode={episode_id}, "
                    f"stream_index={stream_index}, "
                    f"stream_size={len(self.attack_stream)}"
                )

            stream_episode = self.attack_stream[stream_index]

            stream_episode_id = int(
                stream_episode["episode_id"]
            )

            if stream_episode_id != episode_id:
                raise RuntimeError(
                    "CP-03.21 stream episode mismatch: "
                    f"runner_episode={episode_id}, "
                    f"stream_episode={stream_episode_id}"
                )

            # ----------------------------------------------------
            # STREAM IS AUTHORITATIVE FOR ATTACK CONTENT
            # Episode class comes from explicit episode_schedule
            # when provided; otherwise every stream slot is an
            # attack (common-stream Phase 7 contract).
            # ----------------------------------------------------

            if self.episode_schedule is not None:
                if episode_id > len(self.episode_schedule):
                    raise ValueError(
                        f"Episode {episode_id} is outside the configured "
                        f"episode schedule of length "
                        f"{len(self.episode_schedule)}."
                    )
                legitimate_task = bool(
                    self.episode_schedule[episode_id - 1]
                )
            else:
                legitimate_task = False

            attack_present = not legitimate_task

            # Controlled stream is frozen.
            # DO NOT call AdaptiveAttacker.generate() here.
            attempt = None
            attacker_type = stream_episode.get(
                "attacker_type",
                None,
            )

            if attack_present:
                attack_family = stream_episode["attack_family"]
                payload = stream_episode["payload"]
            else:
                attack_family = "legitimate"
                payload = self._generate_legitimate_task(
                    episode_id
                )

            print(
                "[CP-03.21 STREAM] "
                f"episode={episode_id} | "
                f"stream_index={stream_index} | "
                f"family={attack_family} | "
                f"attack_present={attack_present} | "
                f"legitimate_task={legitimate_task}"
            )

            print(
                "[CP-03.21 PAYLOAD] "
                f"episode={episode_id} | "
                f"family={attack_family} | "
                f"payload={payload}"
            )

        else:

            # ====================================================
            # NORMAL ADAPTIVE MODE
            # ====================================================

            if self.episode_schedule is not None:
                if episode_id < 1 or episode_id > len(self.episode_schedule):
                    raise ValueError(
                        f"Episode {episode_id} is outside the configured "
                        f"episode schedule of length {len(self.episode_schedule)}."
                    )

                legitimate_task = bool(
                    self.episode_schedule[episode_id - 1]
                )
            else:
                legitimate_task = False

            attack_present = not legitimate_task

            if legitimate_task:

                payload = self._generate_legitimate_task(
                    episode_id
                )

                attack_family = "legitimate"
                attempt = None

            else:

                # Use the REAL AdaptiveAttacker API.
                attempt = self.attacker.generate()

                payload = attempt.payload
                attack_family = attempt.family

                # AttackAttempt does not define attacker_type.
                attacker_type = None

        # ========================================================
        # DETECTION
        # ========================================================

        detection = self.detector.detect(payload)

        historical_attack = self._historical_attack_signal()

        risk = self.risk_engine.assess(
            detection=detection,
            metadata={
                "attack_type": attack_family,
            },
            historical_attack=historical_attack,
        )

        defense_level_before = self.policy_state.defense_level

        decision = self.policy_engine.decide(
            risk=risk,
            defense_level=defense_level_before,
        )

        defense = self.action_layer.execute(
            decision.action,
            payload,
        )

        # ========================================================
        # ATTACK / LEGITIMATE OUTCOME
        # ========================================================

        if attack_present:
            attack_ok = attack_succeeded(
                decision.action,
                attack_family,
                defense,
            )
        else:
            attack_ok = False

        if legitimate_task:
            legitimate_succeeded = (
                decision.action.value in {"A0", "A1", "A2"}
            )
        else:
            legitimate_succeeded = False

        outcome = self.outcome_evaluator.evaluate(
            action=decision.action,
            allowed=defense.allowed,
            attack_present=attack_present,
            attack_succeeded=attack_ok,
            legitimate_task=legitimate_task,
            legitimate_succeeded=legitimate_succeeded,
        )

        # ========================================================
        # FEEDBACK / ADAPTATION
        # ========================================================

        feedback = self.feedback_engine.generate(outcome)

        self.policy_state = self.update_engine.update(
            self.policy_state,
            feedback,
        )

        if attack_present:

            if self.attack_stream is None:

                # Normal adaptive attacker:
                # record and observe the actual generated attempt.
                if attempt is None:
                    raise RuntimeError(
                        "CP-03.21 internal error: "
                        "attack episode has no generated attempt."
                    )

                self.attacker.record(attempt)

                self.attacker.observe(
                    outcome.attack_success
                )

            else:

                # Frozen common stream:
                # update historical signals only.
                if outcome.attack_success:
                    self.historical_successes += 1
                else:
                    self.historical_failures += 1

        # ========================================================
        # FINAL EPISODE DIAGNOSTICS
        # ========================================================

        print(
            "[CP-03.21 EPISODE] "
            f"episode={episode_id} | "
            f"family={attack_family} | "
            f"attack_present={attack_present} | "
            f"legitimate_task={legitimate_task} | "
            f"attack_success={outcome.attack_success} | "
            f"legitimate_success={outcome.legitimate_success} | "
            f"action={decision.action.value} | "
            f"risk={risk.score:.4f} | "
            f"reward={feedback.reward:.4f}"
        )

        return EpisodeResult(
            episode_id=episode_id,
            attack_present=attack_present,
            attack_family=attack_family,
            attacker_type=attacker_type,
            payload=payload,
            detection_score=detection.score,
            risk_score=risk.score,
            risk_level=risk.level.value,
            defense_action=decision.action.value,
            attack_success=outcome.attack_success,
            legitimate_success=outcome.legitimate_success,
            security_score=outcome.security_score,
            utility_score=outcome.utility_score,
            defense_cost=outcome.defense_cost,
            reward=feedback.reward,
            adaptation_signal=feedback.adaptation_signal,
            defense_level=defense_level_before,
        )

    def run(self, episodes: int = 10):
        if episodes <= 0:
            raise ValueError("episodes must be greater than 0")

        results = []

        for episode_id in range(1, episodes + 1):
            results.append(self.run_episode(episode_id))

        return results

    @staticmethod
    def save_results(
        results,
        path="results/episodes.json",
        manifest=None,
        overwrite=False,
    ):
        output_path = Path(path)
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if output_path.exists() and not overwrite:
            stamp = datetime.now(timezone.utc).strftime(
                "%Y%m%dT%H%M%SZ"
            )
            archived = output_path.with_name(
                f"{output_path.stem}_{stamp}{output_path.suffix}"
            )
            output_path.replace(archived)

        data = [asdict(result) for result in results]

        with output_path.open(
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False,
            )

        if manifest is not None:
            ExperimentRunner.save_manifest(
                manifest,
                output_path.with_name(
                    f"{output_path.stem}_manifest.json"
                ),
                overwrite=True,
            )

    @staticmethod
    def save_manifest(
        manifest: dict,
        path,
        overwrite=False,
    ):
        output_path = Path(path)
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if output_path.exists() and not overwrite:
            stamp = datetime.now(timezone.utc).strftime(
                "%Y%m%dT%H%M%SZ"
            )
            archived = output_path.with_name(
                f"{output_path.stem}_{stamp}{output_path.suffix}"
            )
            output_path.replace(archived)

        payload = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "timestamp_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            **manifest,
        }

        with output_path.open(
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                payload,
                f,
                indent=2,
                ensure_ascii=False,
            )
