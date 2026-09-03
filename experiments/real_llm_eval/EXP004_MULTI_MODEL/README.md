# EXP-004: Multi-Model Real LLM Evaluation

## Pipeline

```
For each target model (target_1, target_2, target_3):
    For each baseline (B0–B3):
        Dataset (seed=42) → Defense → Target LLM → Judge → Metrics

Statistical analysis (post-hoc):
    - Bootstrap 95% CI per model × baseline
    - McNemar paired test: B0 vs B3 (per model)
    - Holm correction across models
    - Cross-model ASR comparison (not pooled)
```

## Models

| Key | Model | Family |
|---|---|---|
| target_1 | meta-llama/llama-3.1-8b-instruct | Llama |
| target_2 | qwen/qwen-2.5-7b-instruct | Qwen |
| target_3 | openai/gpt-4o-mini | GPT |
| judge | google/gemma-2-9b-it | Gemma (independent) |

## Run

```bash
# Preflight
python scripts/preflight_api.py

# Pilot (10 samples, 1 model, 2 baselines)
python experiments/EXP004_MULTI_MODEL/run.py \
  --n-samples 10 --targets target_2 --baselines B0 B3

# Full multi-model (500 samples, all baselines)
python experiments/EXP004_MULTI_MODEL/run.py --n-samples 500

# Unified dataset (1500 attack + 500 benign)
python experiments/EXP004_MULTI_MODEL/run.py \
  --unified-dataset ~/datasets/q1_llm_security/ADAPTI_GUARD_Benchmark_v2/processed/unified_security_dataset.jsonl

# Re-analyze existing artifacts
python experiments/EXP004_MULTI_MODEL/run.py --stats-only
```

## Outputs

```
experiments/EXP004_MULTI_MODEL/
├── config.json
├── metrics.json
├── raw_results.json
├── statistical_analysis.json
├── statistical_analysis.csv
├── target_1/
│   ├── model_info.json
│   ├── metrics.json
│   ├── B0/B0_predictions.jsonl
│   └── B3/...
├── target_2/...
└── target_3/...
```

## Status

See `metrics.json`. BLOCKED until valid API key or Ollama.
