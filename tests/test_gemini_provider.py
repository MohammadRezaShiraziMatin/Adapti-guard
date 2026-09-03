"""Offline tests for the Gemini provider adapter (no live API)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from src.adapti_guard.evaluation.target_model import (
    GeminiTargetModel,
    GenerationRequest,
    GenerationResult,
    build_target_model,
)


def test_build_target_model_rejects_mock_provider(tmp_path: Path):
    cfg = {
        "models": {"mock_only": {"provider": "mock", "model": "mock"}},
        "cache": {"enabled": False},
    }
    path = tmp_path / "models.yaml"
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    with pytest.raises(RuntimeError, match="not allowed"):
        build_target_model("mock_only", config_path=path, allow_mock=False)


def test_build_gemini_model_passes_cache_disabled(monkeypatch, tmp_path: Path):
    captured: dict[str, object] = {}

    class FakeGemini:
        def __init__(self, model_id: str, *, cache=None, **kwargs):
            captured["cache"] = cache
            captured["model_id"] = model_id
            captured["kwargs"] = kwargs
            self.cache = cache
            self.model_id = model_id
            self.provider = "google"
            self.api = "interactions"

    monkeypatch.setattr(
        "src.adapti_guard.evaluation.target_model.GeminiTargetModel",
        FakeGemini,
    )
    cfg = {
        "models": {
            "gemini_target": {
                "provider": "google",
                "model": "gemini-3.6-flash",
                "temperature": 0.0,
                "max_tokens": 512,
                "seed": 42,
            }
        },
        "google": {"max_retries": 2, "seed": 42},
        "cache": {"enabled": True, "directory": ".llm_cache"},
    }
    path = tmp_path / "models.yaml"
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    model = build_target_model("gemini_target", config_path=path, cache_enabled=False)
    assert captured["cache"] is None
    assert captured["model_id"] == "gemini-3.6-flash"
    assert model.api == "interactions"


def test_gemini_generate_uses_interactions_api(monkeypatch):
    calls: list[dict] = []

    class FakeUsage:
        total_input_tokens = 11
        total_output_tokens = 3
        total_tokens = 14
        total_thought_tokens = 0

    class FakeResponse:
        output_text = "GEMINI_OK"
        usage = FakeUsage()
        id = "int-test-1"
        status = "completed"
        errors = None

    class FakeInteractions:
        def create(self, **kwargs):
            calls.append(kwargs)
            return FakeResponse()

    class FakeClient:
        def __init__(self, api_key=None):
            self.interactions = FakeInteractions()
            self.api_key = api_key

    monkeypatch.setenv("GEMINI_API_KEY", "test-key-not-real-0123456789")
    monkeypatch.setattr("google.genai.Client", FakeClient)

    model = GeminiTargetModel("gemini-3.6-flash", api_key="test-key-not-real-0123456789")
    result = model.generate(
        GenerationRequest(
            prompt="Reply exactly: GEMINI_OK",
            system_prompt="You are a test assistant.",
        )
    )
    assert result.text == "GEMINI_OK"
    assert result.error is None
    assert result.usage["total_tokens"] == 14
    assert result.raw["provider"] == "google"
    assert result.raw["api"] == "interactions"
    assert result.raw["http_status"] == 200
    assert "temperature" in result.raw["unsupported_parameters"]
    assert calls[0]["model"] == "gemini-3.6-flash"
    assert "generation_config" in calls[0]
    assert "temperature" not in calls[0]["generation_config"]


def test_gemini_blocks_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(
        "src.adapti_guard.experiments.env_loader.load_project_env",
        lambda: False,
    )
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        GeminiTargetModel("gemini-3.6-flash", api_key=None)


def test_parse_retry_after_and_http_status():
    from src.adapti_guard.evaluation.target_model import (
        infer_http_status,
        parse_retry_after_seconds,
    )

    msg = (
        "Quota exceeded for metric: generativelanguage.googleapis.com/"
        "generate_content_free_tier_requests, limit: 20, model: gemini-3.6-flash\n"
        "Please retry in 31.325886782s."
    )
    assert parse_retry_after_seconds(msg) == pytest.approx(31.325886782)
    assert parse_retry_after_seconds("no delay") is None
    assert parse_retry_after_seconds(msg, cap_seconds=10.0) == 10.0

    class FakeExc(Exception):
        pass

    assert infer_http_status(FakeExc("Error code: 429 - quota")) == 429
    assert infer_http_status(FakeExc("Error code: 401")) == 401


def test_gemini_retries_429_using_retry_after(monkeypatch):
    sleeps: list[float] = []
    monkeypatch.setattr(
        "src.adapti_guard.evaluation.target_model.time.sleep",
        lambda s: sleeps.append(s),
    )
    GeminiTargetModel._last_request_monotonic = 0.0
    GeminiTargetModel._consecutive_429_failures = 0
    calls = {"n": 0}

    class FakeUsage:
        total_input_tokens = 1
        total_output_tokens = 1
        total_tokens = 2
        total_thought_tokens = 0

    class FakeResponse:
        output_text = "ok"
        usage = FakeUsage()
        id = "after-retry"
        status = "completed"
        errors = None

    class FakeInteractions:
        def create(self, **kwargs):
            calls["n"] += 1
            if calls["n"] == 1:
                raise RuntimeError(
                    "Error code: 429 - {'error': {'message': "
                    "'Please retry in 2.5s.', 'code': 'too_many_requests'}}"
                )
            return FakeResponse()

    class FakeClient:
        def __init__(self, api_key=None):
            self.interactions = FakeInteractions()

    monkeypatch.setattr("google.genai.Client", FakeClient)
    model = GeminiTargetModel(
        "gemini-3.6-flash",
        api_key="test-key-not-real-0123456789",
        max_retries=2,
        min_request_interval_seconds=0.0,
    )
    result = model.generate(GenerationRequest(prompt="hi"))
    assert result.error is None
    assert result.text == "ok"
    assert calls["n"] == 2
    assert any(s >= 3.5 for s in sleeps)


def test_openrouter_factory_unchanged(monkeypatch, tmp_path: Path):
    captured: dict[str, object] = {}

    class FakeOR:
        def __init__(self, model_id: str, **kwargs):
            captured["model_id"] = model_id
            captured["kwargs"] = kwargs
            self.model_id = model_id
            self.cache = kwargs.get("cache")

    monkeypatch.setattr(
        "src.adapti_guard.evaluation.target_model.OpenRouterTargetModel",
        FakeOR,
    )
    cfg = {
        "models": {
            "model_a": {"provider": "openrouter", "model": "openai/gpt-4o-mini"}
        },
        "openrouter": {},
        "cache": {"enabled": False},
    }
    path = tmp_path / "models.yaml"
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    model = build_target_model("model_a", config_path=path, cache_enabled=False)
    assert captured["model_id"] == "openai/gpt-4o-mini"
    assert model.cache is None
