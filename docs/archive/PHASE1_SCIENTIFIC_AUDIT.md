# Phase 1: Pre-Experiment Scientific Audit

**Generated:** 2026-09-02T06:18:59.583787+00:00
**Git commit:** `612f577118a19949b4862a3b27b801db8c7eef65`
**Experiments cleared to run:** NO

## Blocking Failures

- API-001: OpenRouter API key — OPENROUTER_API_KEY format invalid (expected sk-or-v1-... prefix). Get a key at https://openrouter.ai/keys

## Api

| Gate | Status | Detail |
|---|---|---|
| OpenRouter API key ⛔ | BLOCKED | OPENROUTER_API_KEY format invalid (expected sk-or-v1-... prefix). Get a key at h |
| Ollama fallback | WARN | not running |

## Artifacts

| Gate | Status | Detail |
|---|---|---|
| Artifact EXP-002 | FAIL | All 5 episodes had judge errors |
| Artifact EXP-004 | BLOCKED | No backend available. OpenRouter: OPENROUTER_API_KEY format invalid (expected sk |
| Artifact EXP-005 | WARN | LEGACY_SIMULATION_ONLY — not for publication (COMPLETED) |
| Artifact REAL-LLM-EVAL | BLOCKED | No backend available. OpenRouter: OPENROUTER_API_KEY format invalid (expected sk |

## Dataset

| Gate | Status | Detail |
|---|---|---|
| Dataset benchmark_q1/test | PASS | n=2259, sha256=fa35c657dae473e2... |
| Dataset unified | PASS | n=12799, sha256=3d3ae9e4863c0288... |

## Judge

| Gate | Status | Detail |
|---|---|---|
| Blind judge payload ⛔ | PASS | forbidden_fields_in_payload=[] |
| Judge model config ⛔ | PASS | primary=Claude Sonnet 4, fallback=GPT-4o |

## Metric Integrity

| Gate | Status | Detail |
|---|---|---|
| Real path: attack_success.py ⛔ | PASS | LLMJudge=True, no_simulation_asr=True |
| Real path: real_llm_pipeline.py ⛔ | PASS | LLMJudge=True, no_simulation_asr=True |
| Real path: multi_model_eval.py ⛔ | PASS | LLMJudge=True, no_simulation_asr=True |
| Legacy labeled: harmonized_runner.py | PASS | LEGACY_SIMULATION_ONLY present=True |
| Legacy labeled: run.py | PASS | LEGACY_SIMULATION_ONLY present=True |

## Models

| Gate | Status | Detail |
|---|---|---|
| Target model_a ⛔ | PASS | openai/gpt-4o-mini |
| Target model_b ⛔ | PASS | qwen/qwen3-30b-a3b |
| Target model_c ⛔ | PASS | deepseek/deepseek-chat-v3-0324 |

## Sota

| Gate | Status | Detail |
|---|---|---|
| SOTA baseline llama_guard | WARN | uses regex fallback when model unavailable — NOT valid SOTA comparison |
| SOTA baseline prompt_guard | WARN | uses regex fallback when model unavailable — NOT valid SOTA comparison |
| SOTA baseline nemo_guardrails | WARN | uses regex fallback when model unavailable — NOT valid SOTA comparison |

## Statistics

| Gate | Status | Detail |
|---|---|---|
| Module statistics | PASS | bootstrap + mcnemar available |
| Module multi_model_statistics | PASS | bootstrap + mcnemar available |

## Tests

| Gate | Status | Detail |
|---|---|---|
| Scientific integrity tests | PASS | 4 test modules present |

## Pre-Run Checklist

Before executing EXP-004 multi-model evaluation:

1. [ ] `python scripts/phase1_preflight_audit.py` — all blocking gates PASS
2. [ ] `python scripts/preflight_api.py` — API key valid
3. [ ] Smoke test: `python experiments/EXP004_MULTI_MODEL/run.py --n-samples 5 --targets model_a --baselines B0 B3`
4. [ ] Verify `validity: VALID` in output metrics
5. [ ] Full run only after smoke test passes

---
*Regenerate: `python scripts/phase1_preflight_audit.py`*
