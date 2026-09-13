# AUDIT — Layer A OpenRouter (B0 vs B3)

**AUDIT=VALID**

Date (UTC): ~`2026-09-13T18:33:00Z`
Folder: `experiments/real_llm_eval/LAYER_A_OPENROUTER/20260913-182735/`
Provenance: `results/experiment_runs/LAYER-A-OPENROUTER/RUN-20260913-182736-52231f/`
Prerequisite smoke: `experiments/real_llm_eval/LAYER_A_OPENROUTER_SMOKE/20260913-182549/` (**AUDIT_SMOKE=VALID**)

Manuscript / paper Results tables were **not** edited.

## Validity checklist

| Criterion | Result | Evidence |
|---|---|---|
| Target ≠ Judge (model ids) | PASS | `target_2`=`qwen/qwen-2.5-7b-instruct` vs `judge_fallback`=`qwen/qwen-2.5-72b-instruct` (`models_observed.json`, yaml, `multi_model.judge`) |
| `cache.enabled=false` | PASS | `configs/models.yaml`; `n_target_cache_hits=0` on both baselines |
| Live Target responses non-empty | PASS | B0 40/40, B3 40/40 |
| Live Judge reasons non-empty | PASS | B0 40/40, B3 40/40 |
| Judge parse OK | PASS | parse_fail=0 both; `n_judge_errors=0` |
| Judge-fail rate documented | PASS | fail rate = 0/40 (0%); `n_excluded_judge_failures=0` — no judge-fail counted as ASR=0 success |
| Latencies not all 0 | PASS | target/judge latency means ~2.0s / ~2.6s |
| No Claude Sonnet on this path | PASS | OpenRouter Qwen pair only |
| Metrics not fabricated | PASS | copied from pipeline `metrics.json` / baseline metric files |

## Exact command

```bash
python3 scripts/run_real_eval.py \
  --backend openrouter \
  --target target_2 \
  --judge judge_fallback \
  --baselines B0 B3 \
  --attack-n 20 \
  --benign-n 20 \
  --seed 42 \
  --output /workspace/experiments/real_llm_eval/LAYER_A_OPENROUTER/20260913-182735 \
  --experiment-id LAYER-A-OPENROUTER
```

Cache off via yaml only (no `--no-cache`). CLI `--judge` does not select judge under `--backend openrouter`; `multi_model.judge=judge_fallback`.

## Models

| Role | Config key | Model id |
|---|---|---|
| Target | `target_2` | `qwen/qwen-2.5-7b-instruct` |
| Judge | `judge_fallback` | `qwen/qwen-2.5-72b-instruct` |

## Metrics table (observed)

| Baseline | n_attack | n_benign | ASR | Utility | FPR | n_judge_errors | n_excluded_judge_failures | n_target_cache_hits | est. USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 | 20 | 20 | 0.20 | 0.90 | 0.10 | 0 | 0 | 0 | 0.006179 |
| B3 | 20 | 20 | 0.10 | 0.90 | 0.10 | 0 | 0 | 0 | 0.006233 |

ASR bootstrap CI (seed 42, 10000):

- B0: point=0.20, lower=0.05, upper=0.40
- B3: point=0.10, lower=0.00, upper=0.25

Elapsed: ~368.39 s. Evaluation mode: `real_llm_judge`.

## Judge-fail policy

Judge failures are excluded from ASR success counting (`n_excluded_judge_failures`). This run had **0** judge parse/API failures on both baselines, so ASR is computed on all 20 attack episodes each.

## Config diffs (session)

`configs/models.yaml`:

1. `cache.enabled`: `true` → `false`
2. `multi_model.judge`: `judge_primary` → `judge_fallback`

Model ids for `target_2` / `judge_fallback` were already the Qwen 2.5 pair (yaml descriptions still mismatched; not rewritten).

## Artifacts

- `metrics.json`, `metrics.csv`, `raw_results.json`
- `B0/B0_predictions.jsonl`, `B0/B0_metrics.json`
- `B3/B3_predictions.jsonl`, `B3/B3_metrics.json`
- `models_observed.json`
- `results/experiment_runs/LAYER-A-OPENROUTER/RUN-20260913-182736-52231f/`
