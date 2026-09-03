"""Offline unit tests for Groq provider adapter (no live API)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from src.adapti_guard.evaluation.target_model import (
    GenerationRequest,
    GroqTargetModel,
    build_target_model,
)
from src.adapti_guard.experiments.env_loader import validate_groq_key
from src.adapti_guard.experiments.real_llm_pipeline import (
    EvaluationBackend,
    resolve_backend,
)


def test_validate_groq_key_missing(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(
        "src.adapti_guard.experiments.env_loader.load_project_env",
        lambda: False,
    )
    ok, reason = validate_groq_key()
    assert ok is False
    assert "not set" in reason


def test_validate_groq_key_too_short(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "short")
    monkeypatch.setattr(
        "src.adapti_guard.experiments.env_loader.load_project_env",
        lambda: True,
    )
    ok, reason = validate_groq_key()
    assert ok is False
    assert "too short" in reason
    assert "short" not in reason or reason == "GROQ_API_KEY too short (invalid)"


def test_groq_blocks_without_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(
        "src.adapti_guard.experiments.env_loader.load_project_env",
        lambda: False,
    )
    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        GroqTargetModel("openai/gpt-oss-120b", api_key=None)


def test_build_groq_from_yaml(monkeypatch, tmp_path: Path):
    captured: dict[str, object] = {}

    class FakeGroq:
        def __init__(self, model_id: str, **kwargs):
            captured["model_id"] = model_id
            captured["kwargs"] = kwargs
            self.model_id = model_id
            self.provider = "groq"
            self.cache = kwargs.get("cache")

    monkeypatch.setattr(
        "src.adapti_guard.evaluation.target_model.GroqTargetModel",
        FakeGroq,
    )
    cfg = {
        "models": {
            "groq_target": {
                "provider": "groq",
                "model": "openai/gpt-oss-120b",
                "temperature": 0.0,
                "max_tokens": 512,
                "reasoning_effort": "low",
            }
        },
        "groq": {
            "base_url": "https://api.groq.com/openai/v1",
            "max_retries": 3,
            "reasoning_effort": "low",
        },
        "cache": {"enabled": True, "directory": ".llm_cache"},
    }
    path = tmp_path / "models.yaml"
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    model = build_target_model("groq_target", config_path=path, cache_enabled=False)
    assert captured["model_id"] == "openai/gpt-oss-120b"
    assert captured["kwargs"]["reasoning_effort"] == "low"
    assert captured["kwargs"]["base_url"] == "https://api.groq.com/openai/v1"
    assert model.cache is None


def test_groq_generate_passes_reasoning_effort(monkeypatch):
    calls: list[dict] = []

    class FakeUsage:
        prompt_tokens = 5
        completion_tokens = 2
        total_tokens = 7

    class FakeChoice:
        class Msg:
            content = "GROQ_OK"

        message = Msg()
        finish_reason = "stop"

    class FakeResponse:
        id = "chatcmpl-test"
        model = "openai/gpt-oss-120b"
        usage = FakeUsage()
        choices = [FakeChoice()]

    class FakeCompletions:
        def create(self, **kwargs):
            calls.append(kwargs)
            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        def __init__(self, **kwargs):
            self.chat = FakeChat()
            self.kwargs = kwargs

    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_key_not_real_0123456789abcdef")
    monkeypatch.setattr("openai.OpenAI", FakeClient)

    model = GroqTargetModel(
        "openai/gpt-oss-120b",
        api_key="gsk_test_key_not_real_0123456789abcdef",
        reasoning_effort="low",
        max_retries=0,
    )
    result = model.generate(GenerationRequest(prompt="Reply exactly: GROQ_OK"))
    assert result.error is None
    assert result.text == "GROQ_OK"
    assert result.usage["total_tokens"] == 7
    assert result.raw["provider"] == "groq"
    assert result.raw["http_status"] == 200
    assert calls[0]["model"] == "openai/gpt-oss-120b"
    assert calls[0]["extra_body"]["reasoning_effort"] == "low"
    assert calls[0]["temperature"] == 0.0


def test_resolve_backend_groq(monkeypatch):
    monkeypatch.setattr(
        "src.adapti_guard.experiments.real_llm_pipeline.validate_groq_key",
        lambda: (True, "ok"),
    )
    backend, reason = resolve_backend(EvaluationBackend.GROQ)
    assert backend == EvaluationBackend.GROQ
    assert reason is None


def test_resolve_backend_auto_does_not_select_groq(monkeypatch):
    monkeypatch.setattr(
        "src.adapti_guard.experiments.real_llm_pipeline.validate_gemini_key",
        lambda: (False, "no"),
    )
    monkeypatch.setattr(
        "src.adapti_guard.experiments.real_llm_pipeline.validate_openrouter_key",
        lambda: (False, "no"),
    )
    monkeypatch.setattr(
        "src.adapti_guard.experiments.real_llm_pipeline.OllamaTargetModel.is_available",
        lambda: False,
    )
    monkeypatch.setattr(
        "src.adapti_guard.experiments.real_llm_pipeline.validate_groq_key",
        lambda: (True, "ok"),
    )
    backend, reason = resolve_backend(EvaluationBackend.AUTO)
    assert backend == EvaluationBackend.AUTO
    assert reason is not None
    assert "backend=groq" in reason
