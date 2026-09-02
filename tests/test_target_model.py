"""Tests for target model (mock only — no API key required)."""

import pytest

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


def test_build_target_model_rejects_mock_without_flag():
    with pytest.raises(RuntimeError):
        build_target_model("target_1", allow_mock=False)
