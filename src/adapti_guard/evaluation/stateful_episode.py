"""Stateful multi-turn episode engine (offline). No live LLM."""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence
from adapti_guard.core.episode import ContextBuilder, EpisodeInput
from adapti_guard.core.models import DefenseAction
from adapti_guard.defense.tool_loop import MockToolRegistry, extract_tool_request, run_tool_turn

TurnTargetFn = Callable[[list[dict[str, str]], str], str]
DefenseFn = Callable[..., tuple[DefenseAction | str, dict[str, Any]]]

@dataclass(frozen=True)
class TurnSpec:
    user_message: str
    context_prefix: str = ""
    tool_call: dict[str, Any] | None = None

@dataclass
class ConversationState:
    messages: list[dict[str, str]] = field(default_factory=list)
    attack_state: dict[str, Any] = field(default_factory=dict)
    defense_state: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class TurnRecord:
    turn_index: int
    user_message: str
    model_response: str
    defense_action: str
    tool_executed: bool
    tool_observation: str
    privileged_tool_executed: bool
    log: dict[str, Any]

@dataclass(frozen=True)
class StatefulEpisodeResult:
    experiment_id: str
    seed: int
    config_hash: str
    n_turns: int
    turns: tuple[TurnRecord, ...]
    episode_harmful_action: bool
    cumulative_tool_executions: int

def _config_hash(config: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(dict(config), sort_keys=True, default=str).encode()).hexdigest()[:16]

class StatefulEpisodeRunner:
    def __init__(self, experiment_id: str = "stateful_offline") -> None:
        self.experiment_id = experiment_id
        self._builder = ContextBuilder()
        self._privileged = ContextBuilder.privileged_tools

    def run(self, turn_specs: Sequence[TurnSpec], *, target: TurnTargetFn, defense: DefenseFn,
            seed: int = 0, config: Mapping[str, Any] | None = None,
            registry: MockToolRegistry | None = None) -> StatefulEpisodeResult:
        cfg = dict(config or {})
        cfg.setdefault("seed", seed)
        ch = _config_hash(cfg)
        state = ConversationState()
        reg = registry or MockToolRegistry()
        records: list[TurnRecord] = []
        harmful = False
        tool_exec_count = 0
        for idx, spec in enumerate(turn_specs):
            state.messages.append({"role": "user", "content": spec.user_message})
            response = target(list(state.messages), spec.user_message)
            state.messages.append({"role": "assistant", "content": response})
            built = self._builder.build(EpisodeInput(prompt=spec.user_message,
                context=spec.context_prefix + "\n".join(f"{m['role']}: {m['content']}" for m in state.messages[:-1])))
            action, defense_meta = defense(prompt=built.prompt, context=built.context)
            action_str = action.value if isinstance(action, DefenseAction) else str(action)
            record_stub = {"tool_call": spec.tool_call} if spec.tool_call else {}
            requested = extract_tool_request(model_response=response, record=record_stub if spec.tool_call else None)
            tool_turn = run_tool_turn(requested=requested, action=action_str, registry=reg)
            if tool_turn.executed:
                tool_exec_count += 1
                if requested and requested.name in self._privileged:
                    harmful = True
            records.append(TurnRecord(idx, spec.user_message, response, action_str, tool_turn.executed,
                tool_turn.observation, bool(tool_turn.executed and requested and requested.name in self._privileged),
                {"turn_index": idx, "defense_meta": defense_meta, "tool": tool_turn.log}))
            state.defense_state["last_action"] = action_str
        return StatefulEpisodeResult(self.experiment_id, seed, ch, len(records), tuple(records), harmful, tool_exec_count)
