"""Bridge StatefulEpisodeRunner to TargetModel (no live unless model provided)."""
from __future__ import annotations

from adapti_guard.evaluation.provider_errors import classify_generation_result
from adapti_guard.evaluation.stateful_episode import TurnTargetFn
from adapti_guard.evaluation.target_model import GenerationRequest, TargetModel


class TargetModelExecutionError(Exception):
    def __init__(self, detail: dict) -> None:
        self.detail = detail
        super().__init__(detail.get("failure_kind") or detail.get("status"))


def target_fn_from_model(model: TargetModel, *, model_id: str = "") -> TurnTargetFn:
    def _fn(history: list[dict[str, str]], user_message: str) -> str:
        parts = [f"{m['role']}: {m['content']}" for m in history]
        prompt = "\n".join(parts + [f"user: {user_message}"])
        result = model.generate(GenerationRequest(prompt=prompt, model_id=model_id))
        failure = classify_generation_result(result)
        if failure["status"] != "ok":
            raise TargetModelExecutionError(failure)
        return result.text or ""

    return _fn
