# FINAL Q1 SCIENTIFIC AUDIT

**Overall:** `FAIL`

Primary publication quantitative claims for real-LLM ADAPTI-GUARD evaluation are
**not** supported by a VALID full experiment. Infrastructure and smoke evidence exist;
the full Gemini benchmark is **BLOCKED** by free-tier HTTP 429.

---

## Checklist

| Question | Finding |
|---|---|
| Is ASR based on real model outputs? | **Only for smoke (n=2 samples under B0).** Full matrix absent. |
| Is evaluation independent? | Judge is a **separate blind call**; OpenRouter Claude unavailable → **same model family** (`gemini-3.6-flash`). Documented limitation. |
| Is the judge blind? | **Yes** — no B0/B1/B2/B3 identity in judge payload. |
| Are baselines identical across conditions? | **Intended yes** (same samples/seed/model); not executed for all defenses. |
| Is the benchmark held out? | **Yes** — `benchmark_q1` test split, hash recorded. |
| Is dataset provenance recorded? | **Yes** in EXP005 config/provenance. |
| Is the model identifier recorded? | **Yes** — `gemini-3.6-flash`, api=`interactions`. |
| Is the API configuration recorded? | **Yes** — unsupported temperature/top_p documented; seed/max_tokens recorded. |
| Are raw outputs preserved? | Smoke: yes. Full: only `target_error` row(s); aborted 081824 partials retained but **not** publication-grade. |
| Are failed requests preserved? | **Yes** (errors / predictions with `api_status=target_error`). |
| Are confidence intervals reported? | **No** (BLOCKED — no complete data). |
| Are multiple comparisons corrected? | **No** (BLOCKED). |
| Are effect sizes reported? | **No** (BLOCKED). |
| Are simulation and real results separated? | **Yes** — reports and manuscript gate simulation vs Real LLM Evaluation. |
| Can every paper number be traced to raw data? | **N/A for full ASR claims** — no such numbers asserted as VALID. |
| Can another researcher reproduce the experiment? | Pipeline **yes**; outcome currently **BLOCKED** without additional Gemini quota / paid plan or alternate provider. |

---

## Claim control

| Claim type | Status |
|---|---|
| Gemini provider integration works | **PASS** (preflight + smoke VALID) |
| Full B0–B3 real-LLM ASR comparison | **FAIL** (BLOCKED on quota) |
| OpenRouter EXP-004 multi-model | **FAIL** (HTTP 401) |
| Simulation / heuristic ablations | Allowed only as **Simulation / Infrastructure Validation**, not primary evidence |

---

## Required unblock path (honest)

1. Increase Gemini quota (paid billing) **or** restore a working OpenRouter key for target+judge.
2. Re-run `experiments/EXP005_GEMINI_FLASH/run.py` (or EXP-004) without fabricating rows.
3. Only then promote manuscript Results from `[BLOCKED]` to numbers traced from `raw_outputs.jsonl` → judge → metrics → statistics.

---

## Audit verdict

```text
FAIL
```

Reason: no VALID full real-LLM evaluation matrix for the predefined scientific protocol.
Smoke VALID proves the pipeline; it does **not** authorize ASR tables.
