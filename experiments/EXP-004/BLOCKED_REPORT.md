# EXP-004 — BLOCKED

**Updated:** 2026-09-02  
**Status:** FINAL EMPIRICAL EVALUATION NOT COMPLETE

---

## Current blocker

**HTTP 401 — Authentication failure**

OpenRouter API response:

```json
{"error":{"message":"User not found.","code":401}}
```

Verified on:

- `openai/gpt-4o-mini` (target)
- `anthropic/claude-sonnet-4` (judge)

Local `OPENROUTER_API_KEY` passes **format** validation (`sk-or-…`) but is **not accepted** by OpenRouter at call time.

**Action required:** Replace or re-authenticate the API key at https://openrouter.ai/keys before any real LLM experiment.

---

## Partial run (INVALID — do not use)

An interrupted attempt exists:

| Artifact | State |
|----------|--------|
| `config.json` | Written (n=150, seed=42, cache_enabled=false) |
| `model_a/B0/B0_predictions.jsonl` | **4 / 150** rows |
| `model_a/B0/B0_metrics.json` | **Missing** |
| B6, model_b, model_c | **Not started** |

All 4 partial predictions have:

- `judge_failure: true`
- `judge_reason: judge_api_error`
- `judge_fallback_used: true`

These rows are **not valid scientific evidence** (judge did not produce verdicts).

**Do NOT** use `--skip-existing` on this partial run. Remove or archive `model_a/` before a clean re-run after API recovery.

---

## Canonical design (unchanged)

| Parameter | Value |
|-----------|--------|
| n_samples | 150 |
| seed | 42 |
| baselines | B0, B6 |
| models | model_a, model_b, model_c |
| publication_mode | true |
| cache_enabled | false |
| dataset SHA-256 | `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24` |

---

## Command when unblocked

```bash
# 1. Verify judge probe returns HTTP 200
# 2. Remove invalid partial artifacts under experiments/EXP-004/model_*/
# 3. Clean run:
python experiments/EXP-004/run.py
python experiments/EXP-004/analyze.py
```

---

## No fabricated data

No EXP-004 ASR tables, McNemar p-values, or B6 improvement claims are reported in the manuscript until a complete valid run exists.
