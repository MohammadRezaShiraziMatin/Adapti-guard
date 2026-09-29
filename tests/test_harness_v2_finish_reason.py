"""finish_reason extraction tests."""
from __future__ import annotations

from adapti_guard.evaluation.harness_v2.finish_reason import (
    finish_metadata_from_raw_response,
    response_complete_for_attack_eval,
)


def test_finish_metadata_from_choice():
    raw = {
        "choices": [
            {
                "finish_reason": "length",
                "native_finish_reason": "length",
                "message": {"role": "assistant", "content": "x"},
            }
        ]
    }
    meta = finish_metadata_from_raw_response(raw)
    assert meta["finish_reason"] == "length"
    assert meta["native_finish_reason"] == "length"


def test_attack_eval_invalid_on_length():
    assert response_complete_for_attack_eval(finish_reason="length", provider_error=None) is False
    assert response_complete_for_attack_eval(finish_reason="stop", provider_error=None) is True
