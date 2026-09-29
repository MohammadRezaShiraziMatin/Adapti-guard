# J1 / J2 / J3 judge output schema — field diff

Source of truth for logical fields: `JudgeVerdict` in `src/adapti_guard/evaluation/llm_judge.py`.  
J1 (OpenRouter `z-ai/glm-4.7`) and J2 (OpenRouter `x-ai/grok-4.7`) parse JSON from assistant text.  
J3 (Anthropic `claude-haiku-4-5-20251001`) uses API-enforced `output_config.format` JSON schema in `anthropic_j3_judge.py`.

| field | J1 glm-4.7 | J2 grok-4.7 | J3 Haiku 4.5 |
|-------|------------|-------------|--------------|
| `attack_success` | boolean | boolean | boolean (json_schema) |
| `refusal` | boolean | boolean | boolean |
| `policy_violation` | boolean | boolean | boolean |
| `tool_misuse` | boolean | boolean | boolean |
| `utility_success` | boolean | boolean | boolean |
| `confidence` | number 0–1 | number 0–1 | number |
| `reason` | string | string | string |

**Diff:** none on field names or types; J3 adds server-side schema enforcement (no markdown-fence text parsing).

Programmatic table: `judge_schema_field_diff_table()` in `anthropic_j3_judge.py`.
