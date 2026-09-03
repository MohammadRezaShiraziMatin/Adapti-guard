# ADAPTI-GUARD Real LLM Evaluation Upgrade Report

**Date:** 2026-09-02  
**Status:** IMPLEMENTED — awaiting live API execution for results

---

## Objective

Upgrade ADAPTI-GUARD from simulation-only ASR to publication-grade real LLM evaluation with independent judge validation and full provenance.

## What Changed

### New Components

| Component | Path | Purpose |
|---|---|---|
| Real LLM pipeline | `src/adapti_guard/experiments/real_llm_pipeline.py` | Orchestrates B0–B3 with target+judge |
| Defense baselines | `src/adapti_guard/experiments/defense_baselines.py` | B0–B3 defense factories |
| Ollama adapter | `src/adapti_guard/evaluation/target_model.py` | Local inference without API cost |
| Unified dataset loader | `src/adapti_guard/evaluation/attack_success.py` | ADAPTI-Bench 1500+500 split |
| Experiment CLI | `experiments/REAL_LLM_EVAL/run.py` | Main entry point |
| Convenience script | `scripts/run_real_eval.py` | Wrapper |
| Unit tests | `tests/test_real_llm_pipeline.py` | 6 tests, no live API |
| Documentation | `docs/REAL_LLM_EVALUATION.md` | Scientific contract |

### Enhanced Components

| Component | Change |
|---|---|
| `configs/models.yaml` | Added `ollama_target` + `ollama` config block |
| `baselines/baseline_runner.py` | Uses `validate_openrouter_key()` |
| `attack_success.py` | `load_unified_dataset_records()` for benchmark v2 |

### Unchanged (Legacy Simulation)

| Component | Notes |
|---|---|
| `harmonized_runner.py` | Retained for ablation/simulation |
| `attack_outcome.py` | Defense-simulation ASR only |
| `experiments/EXP005_*`, `EXP008_*` | Historical simulation results |

---

## Scientific Pipeline

```
Input → Defense (B0–B3) → Target LLM → Independent Judge → Metrics → Provenance
```

**ASR source:** `LLMJudge.judge()` returns `attack_success` boolean.  
**Never used in real mode:** `attack_outcome.py`, regex refusal patterns, defense-simulation heuristics.

---

## Verification

```
pytest tests/test_real_llm_pipeline.py → 6 passed
```

Tests confirm:
- Judge verdict drives ASR (not regex)
- Blocked episodes skip target LLM and judge API calls
- Pipeline writes BLOCKED status without fake metrics when no backend

---

## Execution Status

| Check | Result |
|---|---|
| `python scripts/preflight_api.py` | BLOCKED — `OPENROUTER_API_KEY not set` |
| Ollama | Not running |
| Live evaluation | **NOT RUN** — no fabricated results |

### To Run Real Evaluation

```bash
# 1. Configure API key
echo 'OPENROUTER_API_KEY=sk-or-v1-...' >> .env

# 2. Preflight
python scripts/preflight_api.py

# 3. Smoke test
python experiments/REAL_LLM_EVAL/run.py --n-samples 5 --baselines B0 B3

# 4. Full run
python experiments/REAL_LLM_EVAL/run.py \
  --unified-dataset ~/datasets/q1_llm_security/ADAPTI_GUARD_Benchmark_v2/processed/unified_security_dataset.jsonl
```

Or with Ollama:
```bash
ollama pull llama3.2:3b
python experiments/REAL_LLM_EVAL/run.py --backend ollama --n-samples 50
```

---

## Output Artifacts (when run)

- `experiments/REAL_LLM_EVAL/metrics.json`
- `experiments/REAL_LLM_EVAL/metrics.csv`
- `experiments/REAL_LLM_EVAL/raw_results.json`
- `experiments/REAL_LLM_EVAL/<baseline>/*_predictions.jsonl`
- `results/experiment_runs/REAL-LLM-EVAL/<run_id>/` (full provenance)

---

## Relationship to Phase 9 (Benchmark v2)

| Location | Mode | Status |
|---|---|---|
| `ADAPTI_GUARD_Benchmark_v2/experiments/` | Defense-simulation | Ran (seed=42) |
| `adapti_guard/experiments/REAL_LLM_EVAL/` | Real LLM + judge | Ready, not run |

The adapti_guard pipeline supersedes simulation for Q1 claims. Benchmark v2 defense-simulation results remain valid for defense-layer comparison only.

---

## Open TODOs

- [ ] Configure valid `OPENROUTER_API_KEY` and run smoke test (n=5)
- [ ] Full unified dataset evaluation (2000 samples × 6 baselines)
- [ ] Multi-target comparison (target_1, target_2, target_3)
- [ ] Judge agreement study (human vs LLM, 100 samples)
- [ ] Bootstrap CI across 5 seeds

---

*No metrics in this report are fabricated. All numbers will come from executed `REAL_LLM_EVAL` runs.*
