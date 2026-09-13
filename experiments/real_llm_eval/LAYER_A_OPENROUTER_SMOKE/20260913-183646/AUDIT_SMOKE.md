# AUDIT_SMOKE — Layer A OpenRouter re-check

**AUDIT=VALID**
**STATUS=VALID**
**KEY_CHECK=SET** (value not printed)

Date (UTC): `2026-09-13T18:36:46Z`
Branch: `cursor/layer-a-openrouter-smoke-67a3`
Folder: `experiments/real_llm_eval/LAYER_A_OPENROUTER_SMOKE/20260913-183646/`
Provenance: `results/experiment_runs/LAYER-A-OPENROUTER-SMOKE/RUN-20260913-183646-45c2d0/`

## Key check

```bash
python3 -c "import os; print('SET' if os.environ.get('OPENROUTER_API_KEY') else 'MISSING')"
# SET
```

No `.env` file present; key came from environment secrets.

## Validity checklist

| Check | Result | Evidence |
|---|---|---|
| Target `target_2` | PASS | `qwen/qwen-2.5-7b-instruct` |
| Judge `multi_model.judge=judge_fallback` | PASS | `qwen/qwen-2.5-72b-instruct` |
| Target ≠ Judge | PASS | 7B vs 72B (`models_observed.json`) |
| `cache.enabled=false` | PASS | yaml; `n_target_cache_hits=0` |
| Target responses non-empty | PASS | 4/4 |
| Judge reasons non-empty | PASS | 4/4 |
| Judge parse OK ≥1 | PASS | 4/4; `n_judge_errors=0` |
| Latencies not all 0 | PASS | target/judge means ~3.2s / ~2.4s |
| Judge-fail as ASR=0 | N/A | `n_excluded_judge_failures=0` |

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
  --output /workspace/experiments/real_llm_eval/LAYER_A_OPENROUTER_SMOKE/20260913-183646 \
  --experiment-id LAYER-A-OPENROUTER-SMOKE
```

## Observed metrics (B0 smoke; not invented)

| Metric | Value |
|---|---|
| ASR | 0.0 |
| utility | 1.0 |
| n_judge_errors | 0 |
| n_target_cache_hits | 0 |
| est. USD | 0.000903 |
| elapsed_s | 22.59 |

Smoke VALID → Layer A may proceed.
