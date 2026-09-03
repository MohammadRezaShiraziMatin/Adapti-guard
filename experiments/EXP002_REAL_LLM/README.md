# EXP-002: Real LLM Evaluation

## Purpose
Replace simulation-only ASR with real target LLM + independent judge pipeline.

## Pipeline
```
Attack Prompt -> ADAPTI-GUARD Defense -> Target LLM -> LLM Judge -> Metrics
```

## Models
| Key | Model |
|-----|-------|
| target_1 | Llama-3.1-8B-Instruct |
| target_2 | Qwen2.5-7B-Instruct |
| target_3 | GPT-4o-mini |
| judge | Gemma-2-9B-IT |

## Run
```bash
# Requires OPENROUTER_API_KEY in .env
python experiments/EXP002_REAL_LLM/run.py --target target_3 --n-samples 500
```

## Outputs
- `predictions.jsonl` — per-sample predictions
- `metrics.json` — aggregate metrics + bootstrap CI
- `latency.json` — per-episode latency
- `cost.json` — token usage
- `logs.json` — execution log

## Status
BLOCKED without `OPENROUTER_API_KEY`. Never uses simulated results.
