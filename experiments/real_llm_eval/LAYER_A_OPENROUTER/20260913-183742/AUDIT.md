# AUDIT — Layer A OpenRouter re-run

**AUDIT=VALID**

Date (UTC folder): `20260913-183742`
Folder: `experiments/real_llm_eval/LAYER_A_OPENROUTER/20260913-183742/`
Smoke prereq: `experiments/real_llm_eval/LAYER_A_OPENROUTER_SMOKE/20260913-183646/` (**AUDIT_SMOKE=VALID**, KEY=SET)
Provenance: `results/experiment_runs/LAYER-A-OPENROUTER/RUN-20260913-183742-85cc35/`
Manuscript not edited.

## Models observed

| Role | Key | Model id |
|---|---|---|
| Target | `target_2` | `qwen/qwen-2.5-7b-instruct` |
| Judge | `judge_fallback` (`multi_model.judge`) | `qwen/qwen-2.5-72b-instruct` |

`cache.enabled=false`. Target ≠ Judge. No Claude Sonnet on this path.

## Commands

```bash
python3 -c "import os; print('SET' if os.environ.get('OPENROUTER_API_KEY') else 'MISSING')"
# SET

python3 scripts/preflight_api.py --provider openrouter

python3 scripts/run_real_eval.py \
  --backend openrouter --target target_2 --judge judge_fallback \
  --baselines B0 --attack-n 2 --benign-n 2 --seed 42 \
  --output /workspace/experiments/real_llm_eval/LAYER_A_OPENROUTER_SMOKE/20260913-183646 \
  --experiment-id LAYER-A-OPENROUTER-SMOKE

python3 scripts/run_real_eval.py \
  --backend openrouter --target target_2 --judge judge_fallback \
  --baselines B0 B3 --attack-n 20 --benign-n 20 --seed 42 \
  --output /workspace/experiments/real_llm_eval/LAYER_A_OPENROUTER/20260913-183742 \
  --experiment-id LAYER-A-OPENROUTER
```

## Observed metrics (from metrics.json; not invented)

| Baseline | ASR | Utility | FPR | Judge-fail | Cache hits | est. USD |
|---|---:|---:|---:|---:|---:|---:|
| B0 | 0.05 | 0.90 | 0.10 | 0/40 | 0 | 0.006398 |
| B3 | 0.10 | 0.90 | 0.10 | 0/40 | 0 | 0.006334 |

Judge-fail rate = 0; no judge-fail counted as ASR=0 success.
Episodes: 40 per baseline (20 attack + 20 benign), seed 42.
