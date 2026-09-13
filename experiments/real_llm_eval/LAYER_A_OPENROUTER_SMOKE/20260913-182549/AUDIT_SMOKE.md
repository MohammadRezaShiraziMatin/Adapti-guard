# AUDIT_SMOKE — Layer A OpenRouter path

**AUDIT=VALID**
**STATUS=VALID**

Date (UTC): `2026-09-13T18:26:00Z` (approx; folder stamp `20260913-182549`)
Experiment id: `LAYER-A-OPENROUTER-SMOKE`
Folder: `experiments/real_llm_eval/LAYER_A_OPENROUTER_SMOKE/20260913-182549/`
Provenance run: `results/experiment_runs/LAYER-A-OPENROUTER-SMOKE/RUN-20260913-182549-36fd5f/`

## Verdict checklist

| Check | Result | Evidence |
|---|---|---|
| `OPENROUTER_API_KEY` present | PASS | `environment.json` `key_present=true` (value redacted) |
| Target YAML `target_2` | PASS | `qwen/qwen-2.5-7b-instruct` |
| Judge YAML via `multi_model.judge` | PASS | `judge_fallback` → `qwen/qwen-2.5-72b-instruct` |
| Target id ≠ Judge id | PASS | 7B vs 72B; see `models_observed.json` |
| `cache.enabled=false` | PASS | `configs/models.yaml`; `n_target_cache_hits=0` |
| Target responses non-empty | PASS | 4/4 `model_response_preview` non-empty |
| Judge reasons non-empty | PASS | 4/4 `judge_reason` non-empty |
| Judge parse OK ≥1 | PASS | 4/4 `judge_parse_error=null`; `n_judge_errors=0` |
| Latencies not all 0 | PASS | target ~1.3–9.3s; judge ~1.9–2.9s |
| Judge-fail counted as ASR=0 success | N/A / PASS | `n_excluded_judge_failures=0`; no judge fails |
| No Claude Sonnet selected | PASS | OpenRouter path used `judge_fallback` only |

## Commands

```bash
python3 scripts/preflight_api.py --provider openrouter
# PASS: OPENROUTER_API_KEY format valid

python3 scripts/run_real_eval.py \
  --backend openrouter \
  --target target_2 \
  --judge judge_fallback \
  --baselines B0 \
  --attack-n 2 \
  --benign-n 2 \
  --seed 42 \
  --output /workspace/experiments/real_llm_eval/LAYER_A_OPENROUTER_SMOKE/20260913-182549 \
  --experiment-id LAYER-A-OPENROUTER-SMOKE
```

No CLI `--no-cache`. Cache off is `cache.enabled: false` in `configs/models.yaml`.

## Models observed

| Role | Config key | Model id |
|---|---|---|
| Target | `target_2` | `qwen/qwen-2.5-7b-instruct` |
| Judge | `judge_fallback` (`multi_model.judge`) | `qwen/qwen-2.5-72b-instruct` |

CLI `--judge` is ignored on `--backend openrouter`; judge comes from `multi_model.judge`.

## Metrics (B0 smoke only — observed, not invented)

From `B0/B0_metrics.json` / `metrics.json`:

| Metric | Value |
|---|---|
| n_attack / n_benign | 2 / 2 |
| ASR | 0.0 |
| utility | 1.0 |
| fpr | 0.0 |
| n_judge_errors | 0 |
| n_excluded_judge_failures | 0 |
| n_target_cache_hits | 0 |
| target_latency_ms_mean | ~4535 |
| judge_latency_ms_mean | ~2388 |
| estimated_usd | ~0.000861 |

## Notes

- Prediction rows do not embed `model_id` fields; Target≠Judge is proven by yaml + `models_observed.json` + runtime `build_target_model` / `build_judge`.
- Smoke is infrastructure VALID only; not a publication N.
