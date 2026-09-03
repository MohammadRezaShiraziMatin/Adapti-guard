# EXP005_GEMINI_FLASH — EXP005-20260903-083258

**Status:** `BLOCKED`

Label: **Real LLM Evaluation** (not simulation).

## Blocker

Google Gemini free-tier HTTP **429** on `gemini-3.6-flash` via Interactions API:

- metric: `generativelanguage.googleapis.com/generate_content_free_tier_requests`
- limit: **20**
- Retries honored `Please retry in ~50s` (up to 8 retries) and still returned 429
- Post-abort single probe with `max_retries=0` also returned 429

No ASR / FPR / utility / statistical claims are computed from this run.

## Protocol (intended)

- Provider: google
- Model: `gemini-3.6-flash`
- Dataset: `benchmark_q1` q1.0 split=test
- SHA-256: `fa35c657dae473e21f6b89d389e3b85b4daa445eccd4aedeb415b344ab3cf74e`
- Samples: 24 (18 attack / 6 benign), seed 42
- Baselines: B0, B1, B2_L1, B3
- Git: `35833a64b35a98d596d729c3fa7687e3228381ca`

## Prior smoke

VALID smoke (separate run): `../EXP005-20260903-081350/smoke.json`
