"""J3 judge — Claude Haiku 4.5 via Anthropic Messages API (structured outputs).

Structured decoding uses `output_config.format` JSON schema per Anthropic docs:
https://docs.anthropic.com/en/docs/build-with-claude/structured-outputs

Migrating from beta: `output_config.format` replaces deprecated `output_format`; beta headers
are not required for JSON schema outputs (legacy `output_format` needs header
`structured-outputs-2025-11-13` per same doc).

No OpenRouter; no text-parse fallback — API must return schema-valid JSON.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from adapti_guard.evaluation.llm_judge import JUDGE_SYSTEM_PROMPT, JudgeInput, JudgeVerdict

# Same logical fields as J1 (glm-4.7) / J2 (grok-4.7) via JudgeVerdict in llm_judge.py
J3_JUDGE_OUTPUT_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "attack_success": {"type": "boolean"},
        "refusal": {"type": "boolean"},
        "policy_violation": {"type": "boolean"},
        "tool_misuse": {"type": "boolean"},
        "utility_success": {"type": "boolean"},
        "confidence": {"type": "number"},
        "reason": {"type": "string"},
    },
    "required": [
        "attack_success",
        "refusal",
        "policy_violation",
        "tool_misuse",
        "utility_success",
        "confidence",
        "reason",
    ],
    "additionalProperties": False,
}

J3_MODEL_ID = "claude-haiku-4-5-20251001"
ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"


@dataclass
class AnthropicJ3Judge:
    model: str = J3_MODEL_ID
    max_tokens: int = 512
    temperature: float = 0.0

    def _api_key(self) -> str:
        key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        return key

    def judge(self, sample: JudgeInput, *, system_prompt: str | None = None) -> JudgeVerdict:
        payload = sample.to_blind_payload()
        sys_prompt = system_prompt or JUDGE_SYSTEM_PROMPT
        body = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system": sys_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": json.dumps(payload, ensure_ascii=False, indent=2),
                }
            ],
            "output_config": {
                "format": {
                    "type": "json_schema",
                    "schema": J3_JUDGE_OUTPUT_JSON_SCHEMA,
                }
            },
        }
        req = urllib.request.Request(
            ANTHROPIC_MESSAGES_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "content-type": "application/json",
                "x-api-key": self._api_key(),
                "anthropic-version": ANTHROPIC_VERSION,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode() if exc.fp else ""
            return JudgeVerdict(
                attack_success=False,
                refusal=False,
                policy_violation=False,
                tool_misuse=False,
                utility_success=False,
                confidence=0.0,
                reason="judge_api_error",
                raw_text=err_body,
                parse_error=str(exc),
                judge_model=self.model,
            )

        blocks = data.get("content") or []
        text_parts = [b.get("text", "") for b in blocks if b.get("type") == "text"]
        raw_text = "".join(text_parts)
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            return JudgeVerdict(
                attack_success=False,
                refusal=False,
                policy_violation=False,
                tool_misuse=False,
                utility_success=False,
                confidence=0.0,
                reason="judge_parse_error",
                raw_text=raw_text,
                parse_error=f"structured_output_decode: {exc}",
                judge_model=self.model,
            )

        return JudgeVerdict(
            attack_success=bool(parsed["attack_success"]),
            refusal=bool(parsed["refusal"]),
            policy_violation=bool(parsed["policy_violation"]),
            tool_misuse=bool(parsed["tool_misuse"]),
            utility_success=bool(parsed["utility_success"]),
            confidence=float(parsed["confidence"]),
            reason=str(parsed["reason"]),
            raw_text=raw_text,
            parse_error=None,
            judge_model=self.model,
            usage=data.get("usage"),
        )


def judge_schema_field_diff_table() -> list[dict[str, str]]:
    """J1/J2/J3 share JudgeVerdict; OpenRouter judges parse same JSON keys."""
    fields = J3_JUDGE_OUTPUT_JSON_SCHEMA["required"]
    return [
        {
            "field": f,
            "J1_glm_4_7": "same",
            "J2_grok_4_7": "same",
            "J3_haiku_4_5": "same (Anthropic json_schema enforced)",
        }
        for f in fields
    ]
