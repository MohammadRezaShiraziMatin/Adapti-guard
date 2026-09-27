"""J1 GLM-4.7 OpenRouter request wiring (offline)."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import yaml

from adapti_guard.evaluation.target_model import (
    GenerationRequest,
    OpenRouterTargetModel,
    _openrouter_usage_dict,
    build_target_model,
)

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "configs/models_q1_eval_panel.yaml"


def test_q1_judge_glm_panel_disables_reasoning_and_raises_max_tokens():
    panel = yaml.safe_load(PANEL.read_text(encoding="utf-8"))
    spec = panel["models"]["q1_judge_glm_4_7"]
    assert spec["max_tokens"] == 2048
    extra = spec["openrouter_extra_body"]
    assert extra["reasoning"]["effort"] == "none"
    assert extra["reasoning"]["exclude"] is True
    assert extra.get("include_reasoning") is False


def test_openrouter_generate_passes_reasoning_extra_body_and_max_tokens():
    captured: dict = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured.update(kwargs)
            msg = SimpleNamespace(content='{"attack_success": false}', reasoning="")
            usage = SimpleNamespace(
                prompt_tokens=10,
                completion_tokens=20,
                total_tokens=30,
                cost=0.001,
                completion_tokens_details=SimpleNamespace(reasoning_tokens=0),
            )
            return SimpleNamespace(
                id="gen-test",
                model="z-ai/glm-4.7",
                choices=[SimpleNamespace(message=msg)],
                usage=usage,
            )

    fake_client = MagicMock()
    fake_client.chat.completions = FakeCompletions()

    model = OpenRouterTargetModel(
        model_id="z-ai/glm-4.7",
        api_key="test-key",
        max_tokens=2048,
        openrouter_extra_body={
            "reasoning": {"effort": "none", "exclude": True},
            "include_reasoning": False,
        },
    )
    model._client = fake_client  # noqa: SLF001

    result = model.generate(
        GenerationRequest(prompt='{"user_prompt":"x"}', system_prompt="sys", max_tokens=2048)
    )
    assert result.text.startswith("{")
    assert captured["max_tokens"] == 2048
    assert captured["extra_body"]["reasoning"]["effort"] == "none"
    assert result.usage.get("reasoning_tokens") == 0


def test_build_target_model_j1_from_panel():
    model = build_target_model(
        "q1_judge_glm_4_7",
        config_path=str(PANEL),
        cache_enabled=False,
    )
    assert isinstance(model, OpenRouterTargetModel)
    assert model.max_tokens == 2048
    assert model.openrouter_extra_body["reasoning"]["effort"] == "none"


def test_openrouter_usage_dict_reads_reasoning_tokens():
    usage = SimpleNamespace(
        prompt_tokens=1,
        completion_tokens=100,
        total_tokens=101,
        completion_tokens_details=SimpleNamespace(reasoning_tokens=77),
    )
    d = _openrouter_usage_dict(usage)
    assert d["reasoning_tokens"] == 77
    assert d["completion_tokens"] == 100
