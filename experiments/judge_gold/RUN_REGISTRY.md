# Run registry (append-only)

**Policy:** Every live or aborted eval run gets one row here. **Never delete or overwrite** run directories; add new rows and new paths only. Invalid / aborted / pilot runs stay listed with status.

**Cost logging (required for all future authorized runs):** Each run subdirectory must include `cost_log.jsonl` with one JSON object per API call:

| Field | Description |
|-------|-------------|
| `call_index` | 1-based sequence |
| `role` | `target` \| `judge` \| `j2` |
| `model_id` | OpenRouter model id |
| `prompt_tokens` | int |
| `completion_tokens` | int |
| `reasoning_tokens` | int (must be 0 for DeepInfra-pinned J1) |
| `cost_usd` | float from usage or panel estimate |
| `cumulative_usd` | running sum for the run |
| `arm` | optional schema / variant label |

Also write `cost_summary.json`: `{ "api_calls", "spent_usd", "cap_usd", "stopped_reason" }`.

After each run completes, **append a summary row** to the table below and link `cost_log.jsonl`.

---

## Registered runs

| Path | Status | API calls | Spent USD | Notes |
|------|--------|----------:|----------:|-------|
| `experiments/real_llm_eval/Q1_P1_RQ1_20260926-235657` | **INVALID** | 2050 (ledger requests) | **$1.403402** | J1 parse fail 239/488 — not RQ1 evidence; see `Q1_P1_RQ1_20260926-235657_DIAGNOSIS.md`; episodes metadata-only |
| `experiments/real_llm_eval/Q1_P1_RQ1_ABORTED_20260925` | ABORTED | 177 | 0.279 | Owner stop; NOT_RQ1_EVIDENCE |
| `experiments/real_llm_eval/MT1/r1` | unknown | — | — | MT1 episodes.jsonl |
| `experiments/real_llm_eval/P1_MECHANISM_L1/DIAGNOSTIC_B0_B1/DIAG-B0-B1-LAYER-A-V2-20260924` | diagnostic | — | — | Layer A B0/B1 |
| `experiments/real_llm_eval/P1_MECHANISM_L1/DIAGNOSTIC_MULTI_TARGET/DIAG-MULTI-TARGET-20260924` | diagnostic_pilot | — | — | NOT paper Results |
| `experiments/real_llm_eval/P1_MECHANISM_L1/DIAGNOSTIC_MULTI_TARGET/DIAG-MULTI-TARGET-20260924/gpt-oss-120b` | diagnostic_pilot | — | — | Subpack |
| `experiments/real_llm_eval/P1_MECHANISM_L1/DIAGNOSTIC_MULTI_TARGET/DIAG-MULTI-TARGET-20260924/llama-3.1-8b` | diagnostic_pilot | — | — | Subpack |
| `experiments/real_llm_eval/P1_MECHANISM_L1/DIAGNOSTIC_MULTI_TARGET/DIAG-MULTI-TARGET-20260924/qwen-2.5-7b` | diagnostic_pilot | — | — | Subpack |
| `experiments/real_llm_eval/P1_MECHANISM_L1/DIAGNOSTIC_MULTI_TARGET/DIAG-MULTI-TARGET-20260924/qwen3-30b` | diagnostic_pilot | — | — | Subpack |
| `experiments/real_llm_eval/P1_MECHANISM_L1/LIVE-PRO-PI-B2-EVAL-20260924-182806-8aac6be3` | pilot_invalid | — | — | PILOT_NOT_EVIDENCE |
| `experiments/judge_gold/J1_GOLD_EVAL_20260927-063849` | invalid_partial | 18 | 0.0177 | parse_error_rate=0.5 |
| `experiments/judge_gold/J1_GOLD_EVAL_20260927-064512` | incomplete_no_summary | — | — | per_item only |
| `experiments/judge_gold/J1_GOLD_EVAL_20260927-064602` | development | 18 | 0.0042 | gold v1.1 J1 probe |
| `experiments/judge_gold/J1_V2_ABLATION_20260927-065949` | invalid_judge_calibration | 160 | 0.0578 | no variant passed prereg |
| `experiments/judge_gold/J1_V2_ABLATION_20260927-070101` | invalid_judge_calibration | 160 | 0.0448 | no variant passed prereg |
| `experiments/judge_gold/STEP0_FORMAT_SAMPLE_20260927-115332` | COMPLETE | 96 target | 0.012286 | PREREG Step 0; `cost_log.jsonl`; qwen3 5/8 texts (3× empty content) |
| `experiments/harness_v2/HARNESS_V2_SMOKE_20260927-124451` | smoke_complete | 6 HTTP (see RUN_NOTE) | 0.0008245 | Harness v2 smoke; DeepInfra; `cost_log.jsonl`; PASS structured tool_calls |
| `experiments/harness_v2/HARNESS_V2_SMOKE2_20260927-125041` | incomplete_plan | 4 HTTP | 0.00020195 | gemma-only; multi-round before Amendment 1 fix; see RUN_NOTE |
| `experiments/harness_v2/HARNESS_V2_SMOKE2_20260927-125200` | smoke2_complete | 4 HTTP | 0.00040828 | gemma+deepseek; 1 HTTP/scenario; `cost_log.jsonl` |

**Offline (API $0):** `experiments/judge_gold/RULE_BASELINE_v1.1.json`, `RULE_BASELINE_v2.json` — rule judge baseline, not live runs.

---

## Placeholder rows (authorized by prereg, not executed)

| Planned id | Step | Calls cap | Spend cap |
|------------|------|----------:|----------:|
| `STEP0_FORMAT_SAMPLE_*` | Step 0 | 32 | $0.04 |
| `J1_V3_STEPA_*` | Step A | 120 | $0.05 |
| `HARNESS_V2_SMOKE_*` | Harness v2 smoke | 3 (prereg) | $0.01 |
| `J1_V3_STEPB_*` | Step B | 40 | $0.05 |

When created, register path + cost logs here.

---

## Registry corrections (append-only audit)

| UTC date | Path | Change |
|----------|------|--------|
| 2026-09-27 | `Q1_P1_RQ1_20260926-235657` | Status **COMPLETE → INVALID** (239/488 J1 `judge_parse_error`; diagnosis D1). Spend corrected: authoritative **`budget_ledger.json` / `run_summary.json` → `spent_usd` = 1.403401984240001** (2050 requests). Prior registry note “~1.79” was erroneous (not pack ledger final). Do **not** use OpenRouter account cumulative usage as pack spend. |
| 2026-09-27 | `STEP0_FORMAT_SAMPLE_20260927-115332` | Step 0 live (Matin auth); 96 target API calls; ledger **$0.012286** / cap $0.04 |
