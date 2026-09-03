"""Tests for target model (mock only — no API key required)."""

import pytest
import yaml

from src.adapti_guard.evaluation.target_model import (
    GenerationRequest,
    MockTargetModel,
    build_target_model,
)


def test_mock_target_model():
    model = MockTargetModel("hello")
    result = model.generate(GenerationRequest(prompt="test"))
    assert result.text == "hello"
    assert result.cache_hit is False


def test_build_target_model_rejects_mock_without_flag(tmp_path):
    cfg = {
        "models": {"target_mock": {"provider": "mock", "model": "mock"}},
        "cache": {"enabled": False},
    }
    path = tmp_path / "models.yaml"
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    with pytest.raises(RuntimeError):
        build_target_model("target_mock", config_path=path, allow_mock=False)
