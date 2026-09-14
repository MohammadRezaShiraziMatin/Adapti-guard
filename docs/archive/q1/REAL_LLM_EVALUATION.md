# Real LLM Evaluation — Scientific Pipeline

**Status:** Implemented. Results require live target LLM + judge API.

## Scientific Contract

| Requirement | Implementation |
|---|---|
| Real target LLM responses | `TargetModel.generate()` via OpenRouter or Ollama |
| Independent judge | `LLMJudge` — separate model family, JSON verdict |
| No regex/simulation ASR | `evaluate_episode()` uses judge only; blocked → ASR=false |
| Full provenance | `ExperimentRunContext` → `results/experiment_runs/` |
| No fabricated metrics | BLOCKED status when API unavailable |

## Pipeline

```
Attack/Benign Prompt
    → Defense Layer (B0–B3)
    → [if not blocked] Target LLM
    → Independent LLM Judge
    → Metrics (ASR, Defense Rate, FPR, Utility, Latency, Cost)
    → Provenance artifacts
```

## Baselines

| ID | Method |
|---|---|
| B0 | No defense |
| B1 | Rule-based detector |
| B2_L1/L2/L3 | Fixed defense levels |
| B3 | ADAPTI-GUARD adaptive |

## Model Configuration

See `configs/models.yaml`:

| Key | Provider | Model |
|---|---|---|
| target_1 | OpenRouter | Llama-3.1-8B-Instruct |
| target_2 | OpenRouter | Qwen2.5-7B-Instruct |
| target_3 | OpenRouter | GPT-4o-mini |
| judge | OpenRouter | Gemma-2-9B-IT |
| ollama_target | Ollama | llama3.2:3b |

## Commands

```bash
# Preflight check
python scripts/preflight_api.py

# Smoke test (3 samples, 2 baselines)
python experiments/REAL_LLM_EVAL/run.py --n-samples 3 --baselines B0 B3

# Full benchmark_q1 evaluation
python experiments/REAL_LLM_EVAL/run.py --target target_2 --n-samples 500

# Unified ADAPTI-Bench dataset (1500 attack + 500 benign, seed=42)
python experiments/REAL_LLM_EVAL/run.py \
  --unified-dataset ~/datasets/q1_llm_security/ADAPTI_GUARD_Benchmark_v2/processed/unified_security_dataset.jsonl

# Local Ollama (no API cost)
python experiments/REAL_LLM_EVAL/run.py --backend ollama --n-samples 50

# Legacy EXP-002 (single baseline)
python experiments/EXP002_REAL_LLM/run.py --target target_2 --n-samples 500

# Baseline comparison EXP-003
python experiments/EXP003_BASELINES/run.py --n-samples 100
```

## Outputs

```
experiments/REAL_LLM_EVAL/
├── metrics.json           # Aggregate summary
├── metrics.csv            # Per-baseline metrics
├── raw_results.json       # Full provenance payload
├── B0/
│   ├── B0_predictions.jsonl
│   └── B0_metrics.json
├── B1/
│   └── ...
└── ...

results/experiment_runs/REAL-LLM-EVAL/<run_id>/
├── config.json
├── environment.json
├── dataset_manifest.json
├── model_config.json
├── metrics.json
├── responses.jsonl
├── stdout.log
└── summary.md
```

## Metrics

| Metric | Source |
|---|---|
| ASR | Judge `attack_success` on attack episodes |
| Defense Rate | 1 − ASR |
| FPR | Benign episodes with `utility_success=false` |
| Utility | Benign episodes with `utility_success=true` |
| Latency | Target + judge latency per episode |
| Cost | Token usage from target model |

## Simulation vs Real

| Mode | Module | ASR Source |
|---|---|---|
| **Simulation (legacy)** | `harmonized_runner.py`, `attack_outcome.py` | Defense bypass heuristics |
| **Real LLM (Q1)** | `real_llm_pipeline.py`, `attack_success.py` | Independent LLM judge |

Do not mix modes in scientific claims. Label results with `evaluation_mode: real_llm_judge`.

## Blocked Conditions

Experiments write `status: BLOCKED` (never fake numbers) when:

- `OPENROUTER_API_KEY` missing or invalid format
- Ollama not running (when `--backend ollama`)
- No backend available in `--backend auto`
- Dataset not found
