"""Harness v2 max_tokens policy per target family."""
from __future__ import annotations

# Smoke #1 call 3 (qwen3 indirect): max_tokens=512 with finish_reason=length and
# completion_tokens=512 — model filled budget with reasoning, no tool_calls.
# Raise qwen3 headroom for reasoning + tool JSON while keeping other primaries at 512.
QWEN3_HARNESS_MAX_TOKENS = 2048
DEFAULT_HARNESS_MAX_TOKENS = 512
LLAMA_HARNESS_MAX_TOKENS = 1024


def max_tokens_for_model_id(model_id: str) -> int:
    if model_id.startswith("qwen/") or "qwen3" in model_id:
        return QWEN3_HARNESS_MAX_TOKENS
    if model_id.startswith("meta-llama/") or "llama" in model_id:
        return LLAMA_HARNESS_MAX_TOKENS
    return DEFAULT_HARNESS_MAX_TOKENS
