# STEP0 errata (pack frozen — do not overwrite artifacts)

**Pack:** `STEP0_FORMAT_SAMPLE_20260927-115332`  
**Status:** retained as-is; fixes apply to **future** Step 0 reruns and Step A+ logging.

## E1 — Token counts in `cost_log.jsonl` were zero

**Symptom:** All 96 rows had `prompt_tokens`, `completion_tokens`, and `reasoning_tokens` = 0 while `cost_usd` was non-zero.

**Cause:** `scripts/run_step0_format_sample.py` read usage from `result.raw["usage"]`, but `OpenRouterTargetModel` stores counts on `GenerationResult.usage` only (`src/adapti_guard/evaluation/target_model.py` ~204–214).

**Fix (code):** `token_usage_from_generation_result()` in `target_model.py`; Step 0 runner updated to use it. Unit test: `tests/test_j1_glm_openrouter_request.py::test_token_usage_from_generation_result_prefers_result_usage`.

**This pack:** token fields remain 0; spend **$0.012286** from panel pricing on `cost` / token estimates is still valid.

## E2 — “32 target calls” vs 96 API calls

**Prereg wording:** 32 **episodes** (slots) in §6.1.

**Actual:** Up to **3** adaptive turns per slot (`LIVE_WIRING_MAX_TURNS=3`) → **96** target HTTP calls. Not 32 HTTP calls.

## E3 — Episode serialization gaps (fixed going forward)

| Gap | Step 0 pack | Future runs |
|-----|-------------|-------------|
| Only final-turn text in `target_response_full` | yes | store `target_turns[].model_response` + `target_api_calls[]` per HTTP call |
| Prompts not stored | yes | store `system_prompt` + `user_prompt` per API call in `target_api_calls` |
| Per-turn defense metadata | partial (`turns` without response text) | `target_turns` includes full `model_response` |

## E4 — Harness / model capability (see `STEP0_HARNESS_ANALYSIS.md`)

Targets receive **no** tool-declaring system prompt and **no** OpenRouter `tools` / native tool_calls channel; refusals citing “cannot send email” are expected chat behavior, not evidence of tool API wiring.
