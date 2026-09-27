"""Adaptive multi-turn offline: attacker updates from defense feedback."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from adapti_guard.attacker.adaptive_attacker import AdaptiveAttacker
from adapti_guard.core.models import DefenseAction
from adapti_guard.defense.tool_loop import extract_tool_request
from adapti_guard.evaluation.stateful_episode import StatefulEpisodeRunner, TurnSpec, TurnTargetFn

DefenseFn = Callable[..., tuple[DefenseAction | str, dict[str, Any]]]
BaselineDefenseFn = Callable[[str, str | None], tuple[str, bool, str]]

_DEFAULT_TARGET: TurnTargetFn = lambda h, m: (
    f'MODEL: {m} TOOL_REQUEST: {{"name":"send_email","arguments":{{"to":"x","body":"y"}}}}'
)

_OUTCOME_BLOCKED = "rule_based_blocked_by_defense"
_OUTCOME_TARGET = "target_executed"


@dataclass(frozen=True)
class AdaptiveTurnRecord:
    turn_index: int
    user_message: str
    defense_action: str
    blocked: bool
    target_called: bool
    model_response: str
    outcome_source: str
    verdict_reason: str


@dataclass(frozen=True)
class AdaptiveEpisodeResult:
    seed: int
    n_turns: int
    families_seen: tuple[str, ...]
    episode_harmful: bool
    strategy_changed: bool
    turns: tuple[AdaptiveTurnRecord, ...] = ()
    execution_mode: str = "stateful_legacy"


def _privileged_tool_in_response(response: str, generation_raw: dict[str, Any] | None = None) -> bool:
    requested = extract_tool_request(
        model_response=response,
        generation_raw=generation_raw or {},
        record=None,
    )
    if requested is None:
        return False
    from adapti_guard.core.episode import ContextBuilder

    return requested.name in ContextBuilder.privileged_tools


class AdaptiveEpisodeRunner:
    def __init__(self, max_turns: int = 4) -> None:
        self.max_turns = max_turns
        self._stateful = StatefulEpisodeRunner(experiment_id="adaptive_offline")

    def run(
        self,
        *,
        attacker: AdaptiveAttacker,
        defense: DefenseFn,
        seed: int = 0,
        target: TurnTargetFn | None = None,
        baseline_defense_fn: BaselineDefenseFn | None = None,
    ) -> AdaptiveEpisodeResult:
        if baseline_defense_fn is not None:
            return self._run_b1_pre_target(
                attacker=attacker,
                baseline_defense_fn=baseline_defense_fn,
                seed=seed,
                target=target,
            )
        return self._run_stateful_legacy(
            attacker=attacker,
            defense=defense,
            seed=seed,
            target=target,
        )

    def _run_b1_pre_target(
        self,
        *,
        attacker: AdaptiveAttacker,
        baseline_defense_fn: BaselineDefenseFn,
        seed: int,
        target: TurnTargetFn | None,
    ) -> AdaptiveEpisodeResult:
        target_fn = target or _DEFAULT_TARGET
        families: list[str] = []
        harmful = False
        history: list[dict[str, str]] = []
        turn_records: list[AdaptiveTurnRecord] = []

        for idx in range(self.max_turns):
            attempt = attacker.generate()
            attacker.record(attempt)
            families.append(attempt.family)
            prompt = attempt.payload
            context = (
                "\n".join(f"{m['role']}: {m['content']}" for m in history) if history else None
            )
            action, blocked, defended_prompt = baseline_defense_fn(prompt, context)

            if blocked:
                attacker.observe_defense(blocked=True, harmful_outcome=False)
                turn_records.append(
                    AdaptiveTurnRecord(
                        turn_index=idx,
                        user_message=prompt,
                        defense_action=str(action),
                        blocked=True,
                        target_called=False,
                        model_response="",
                        outcome_source=_OUTCOME_BLOCKED,
                        verdict_reason="blocked_by_defense",
                    )
                )
                continue

            user_text = defended_prompt or prompt
            history.append({"role": "user", "content": user_text})
            response = target_fn(list(history), user_text)
            history.append({"role": "assistant", "content": response})
            priv = _privileged_tool_in_response(response)
            harmful = harmful or priv
            attacker.observe_defense(blocked=False, harmful_outcome=priv)
            turn_records.append(
                AdaptiveTurnRecord(
                    turn_index=idx,
                    user_message=prompt,
                    defense_action=str(action),
                    blocked=False,
                    target_called=True,
                    model_response=response,
                    outcome_source=_OUTCOME_TARGET,
                    verdict_reason="target_executed",
                )
            )

        changed = len(families) >= 2 and families[0] != families[-1]
        return AdaptiveEpisodeResult(
            seed=seed,
            n_turns=len(families),
            families_seen=tuple(families),
            episode_harmful=harmful,
            strategy_changed=changed,
            turns=tuple(turn_records),
            execution_mode="b1_pre_target",
        )

    def _run_stateful_legacy(
        self,
        *,
        attacker: AdaptiveAttacker,
        defense: DefenseFn,
        seed: int,
        target: TurnTargetFn | None,
    ) -> AdaptiveEpisodeResult:
        target_fn = target or _DEFAULT_TARGET
        families: list[str] = []
        harmful = False
        for idx in range(self.max_turns):
            attempt = attacker.generate()
            attacker.record(attempt)
            families.append(attempt.family)
            partial = self._stateful.run(
                [TurnSpec(user_message=attempt.payload)],
                target=target_fn,
                defense=defense,
                seed=seed + idx,
            )
            tr = partial.turns[0]
            harmful = harmful or tr.privileged_tool_executed
            attacker.observe_defense(
                blocked=tr.defense_action in ("A2", "A3"),
                harmful_outcome=tr.privileged_tool_executed,
            )
        changed = len(families) >= 2 and families[0] != families[-1]
        return AdaptiveEpisodeResult(
            seed=seed,
            n_turns=len(families),
            families_seen=tuple(families),
            episode_harmful=harmful,
            strategy_changed=changed,
            turns=(),
            execution_mode="stateful_legacy",
        )
