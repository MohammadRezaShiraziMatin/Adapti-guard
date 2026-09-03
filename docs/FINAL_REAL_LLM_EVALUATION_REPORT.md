# FINAL REAL LLM EVALUATION REPORT

```text
BLOCKED
```

## 1. Experiment objective

Obtain **VALID** real-LLM publication metrics for ADAPTI-GUARD (B0 / B1 / B2_L1 / B3)
on **Gemini 3.6 Flash**, using held-out `benchmark_q1` test samples, blind LLM judge
ASR, bootstrap CIs, McNemar + Holm, and full provenance.

## 2. Provider

Google (`provider=google`)

## 3. Model

`gemini-3.6-flash` (Interactions API via `google-genai`)

## 4. Dataset

`benchmark_q1` version `q1.0`, split=`test`

## 5. Dataset hash

`fa35c657dae473e21f6b89d389e3b85b4daa445eccd4aedeb415b344ab3cf74e`

## 6. Number of samples

**Planned:** 24 (18 attack + 6 benign), seed 42  
**Completed under full protocol:** 0 successful episodes in the final full run  
(1 row written as `target_error` after exhausted 429 retries)

## 7. Baselines

| Key | Definition |
|---|---|
| B0 | No defense |
| B1 | Rule-based detector block |
| B2_L1 | Fixed defense level 1 |
| B3 | ADAPTI-GUARD adaptive policy |

## 8. Smoke-test result

```text
VALID
```

Artifact: `results/real_llm/gemini_3_6_flash/EXP005-20260903-081350/smoke.json`

- 4 real API calls (1 attack + 1 benign × target + judge)
- Provider/model/timestamps/request IDs/hashes/latency/tokens recorded
- No fabricated responses

Preflight (same day): VALID — `EXP005-20260903-081324/preflight.json` and smoke run preflight.

## 9. Full experiment status

```text
BLOCKED
```

Run ID: `EXP005-20260903-083258`

**Exact blocker:** HTTP **429** `RateLimitError` — free-tier quota metric
`generativelanguage.googleapis.com/generate_content_free_tier_requests`, **limit: 20**,
model `gemini-3.6-flash`. Bounded retries respecting `Please retry in ~50s` still failed.
A post-abort single probe (`max_retries=0`) also returned 429.

Earlier aborted partial run `EXP005-20260903-081824` is **not** publication evidence
(mixed ok / judge_error under short retries; explicitly marked PARTIAL/aborted).

## 10–16. ASR / Defense Rate / FPR / Utility / Latency / Tokens / Cost

| Metric | Value |
|---|---|
| B0 ASR | **unavailable** (BLOCKED) |
| B1 ASR | **unavailable** (BLOCKED) |
| B2_L1 ASR | **unavailable** (BLOCKED) |
| B3 ASR | **unavailable** (BLOCKED) |
| Defense Rate | **unavailable** |
| FPR | **unavailable** |
| Utility | **unavailable** |
| Latency (full) | **unavailable** |
| Token usage (full) | **unavailable** |
| Cost | **unavailable** (not returned by API; run blocked) |

Smoke-only token/latency examples exist in `smoke.json` and must **not** be generalized.

## 17–20. Bootstrap CI / McNemar / Holm / Effect sizes

**Not computed.** No complete paired real-LLM evaluation matrix exists.

## 21. Per-category results

**Unavailable** (BLOCKED).

## 22. Failure analysis

1. OpenRouter EXP-004 remains blocked (HTTP 401) — cannot use Claude judge.
2. Gemini path works (preflight + smoke VALID) then exhausts free-tier generate_content quota.
3. Full protocol needs ~96 episodes × (target+judge) API calls under 4 defenses; free-tier limit 20 is insufficient for the predefined experiment once smoke/preflight consumed quota.
4. No simulated substitution was performed.

## 23. Limitations

- Same-family judge (`gemini-3.6-flash`) when OpenRouter Claude is unavailable — documented; not an independent model family.
- Free-tier quota prevents completing the held-out real-LLM comparison.
- Temperature / top_p unsupported on Interactions `generation_config` (seed + max_output_tokens supported).
- Primary manuscript quantitative claims cannot be advanced from this run.

## 24. Reproducibility information

- Experiment runner: `experiments/EXP005_GEMINI_FLASH/run.py`
- Adapter: `GeminiTargetModel` in `src/adapti_guard/evaluation/target_model.py`
- Env: `GEMINI_API_KEY` via `.env` (never logged)
- Cache disabled for publication runs
- Results root: `results/real_llm/gemini_3_6_flash/`

## 25. Exact commands used

```bash
cd ~/01_BASE_Q1/adapti_guard
.venv/bin/python -m pytest -q
.venv/bin/python experiments/EXP005_GEMINI_FLASH/run.py --preflight-only
.venv/bin/python experiments/EXP005_GEMINI_FLASH/run.py --smoke-only
.venv/bin/python experiments/EXP005_GEMINI_FLASH/run.py --full-only
```

## 26. Git commit

`35833a64b35a98d596d729c3fa7687e3228381ca`

(Working tree may contain post-commit Gemini pacing/retry fixes beyond this hash.)

## 27. Final scientific validity status

```text
BLOCKED
```

**Simulation / Infrastructure Validation** results elsewhere in the repo remain labeled as such and are **not** mixed into primary real-LLM claims.
