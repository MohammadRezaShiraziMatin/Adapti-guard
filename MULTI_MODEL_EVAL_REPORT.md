# Multi-Model Real LLM Evaluation Report

**Experiment:** EXP-004  
**Date:** 2026-09-02  
**Status:** BLOCKED — infrastructure ready, no valid results  
**Git commit:** `612f577118a19949b4862a3b27b801db8c7eef65`

---

## Objective

Upgrade ADAPTI-GUARD from single-model to rigorous **multi-model LLM security benchmark** with statistical analysis suitable for Q1 manuscript evidence.

---

## Evaluation Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ADAPTI-Bench Dataset                      │
│              (benchmark_q1 or unified, seed=42)              │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ target_1 │    │ target_2 │    │ target_3 │
    │ Llama3.1 │    │ Qwen2.5  │    │ GPT-4o-m │
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         │               │               │
    For each model × baseline (B0–B3):
         │               │               │
         ▼               ▼               ▼
    ┌─────────────────────────────────────────┐
    │  Defense → Target LLM → Gemma-2-9B Judge  │
    └─────────────────────┬───────────────────┘
                          ▼
              Per-episode predictions.jsonl
                          │
                          ▼
    ┌─────────────────────────────────────────┐
    │         Statistical Analysis             │
    │  • Bootstrap 95% CI (ASR, FPR, utility)  │
    │  • McNemar paired test (B0 vs B3)        │
    │  • Holm correction (multi-model)           │
    │  • Cross-model comparison (not pooled)     │
    └─────────────────────────────────────────┘
```

---

## Implementation Deliverables

| Component | Path | Status |
|---|---|---|
| Multi-model orchestrator | `src/adapti_guard/experiments/multi_model_eval.py` | ✅ |
| Statistical analysis | `src/adapti_guard/evaluation/multi_model_statistics.py` | ✅ |
| Holm correction | `src/adapti_guard/evaluation/statistics.py` | ✅ |
| Wilson proportion CI | `statistics.py` | ✅ |
| EXP-004 CLI | `experiments/EXP004_MULTI_MODEL/run.py` | ✅ |
| Config | `experiments/EXP004_MULTI_MODEL/config.json` | ✅ |
| Unit tests | `tests/test_multi_model_statistics.py` | ✅ 4 passed |

---

## Execution Status

### Attempted run (2026-09-02)

```bash
python experiments/EXP004_MULTI_MODEL/run.py \
  --n-samples 10 --targets target_2 --baselines B0 B3
```

**Result:** `BLOCKED`

```json
{
  "status": "BLOCKED",
  "reason": "No backend available. OpenRouter: invalid key format. Ollama: not running.",
  "models_requested": ["target_2"],
  "evaluation_mode": "real_llm_judge"
}
```

**No metrics were fabricated.**

### Artifacts on disk

| File | Content |
|---|---|
| `experiments/EXP004_MULTI_MODEL/metrics.json` | BLOCKED status + provenance |
| `experiments/EXP004_MULTI_MODEL/config.json` | Run configuration |
| `experiments/EXP004_MULTI_MODEL/statistical_analysis.json` | BLOCKED (no data) |

---

## Statistical Methods (implemented, awaiting data)

| Analysis | Method | Implementation |
|---|---|---|
| ASR confidence interval | Bootstrap 95% (5000 resamples) | `bootstrap_ci()` |
| ASR confidence interval | Wilson score interval | `proportion_ci_wilson()` |
| B0 vs B3 paired comparison | McNemar exact test | `mcnemar_test()` |
| Multiple models | Holm-Bonferroni correction | `holm_correction()` |
| Cross-model ASR | Per-model reporting (not pooled) | `cross_model_comparison()` |
| Effect size | Cohen's d | `cohens_d()` |

Per `docs/STATISTICAL_PROTOCOL.md`: episodes are the unit of analysis; models are **not** pooled as independent samples.

---

## Provenance Requirements (enforced)

Every completed run records:

- `experiment_id`, `timestamp`, `git_commit`
- `dataset_path`, `dataset_hash` (SHA256)
- `seed`, `n_samples`
- `model_info.json` per target (provider, model ID, temperature)
- `evaluation_mode: real_llm_judge`
- `validity` classification per baseline run

---

## Planned Results Tables (when unblocked)

### Table 1: ASR by Model × Baseline

| Model | B0 | B1 | B2_L1 | B2_L2 | B2_L3 | B3 |
|---|---:|---:|---:|---:|---:|---:|
| Llama-3.1-8B | TODO | TODO | TODO | TODO | TODO | TODO |
| Qwen2.5-7B | TODO | TODO | TODO | TODO | TODO | TODO |
| GPT-4o-mini | TODO | TODO | TODO | TODO | TODO | TODO |

### Table 2: B0 vs B3 McNemar (per model)

| Model | ASR(B0) | ASR(B3) | Δ ASR | p (raw) | p (Holm) | Significant |
|---|---:|---:|---:|---:|---:|---|
| Llama-3.1-8B | TODO | TODO | TODO | TODO | TODO | TODO |
| Qwen2.5-7B | TODO | TODO | TODO | TODO | TODO | TODO |
| GPT-4o-mini | TODO | TODO | TODO | TODO | TODO | TODO |

*All cells marked TODO until experiment executes with valid API.*

---

## Commands to Unblock

```bash
# 1. Fix API key
echo 'OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY' >> .env
python scripts/preflight_api.py

# 2. Smoke test (1 model, 10 samples)
python experiments/EXP004_MULTI_MODEL/run.py \
  --n-samples 10 --targets target_2 --baselines B0 B3

# 3. Verify validity in output
python -c "
import json
m = json.load(open('experiments/EXP004_MULTI_MODEL/metrics.json'))
print(m['status'])
"

# 4. Full multi-model run
python experiments/EXP004_MULTI_MODEL/run.py --n-samples 500

# 5. Regenerate statistics only
python experiments/EXP004_MULTI_MODEL/run.py --stats-only

# 6. Update audit
python scripts/scientific_audit.py
```

### Ollama alternative

```bash
ollama pull llama3.2:3b
python experiments/EXP004_MULTI_MODEL/run.py \
  --backend ollama --targets ollama_target --n-samples 50
```

---

## Cost Estimate (when unblocked)

| Configuration | API calls | Est. cost |
|---|---:|---|
| Pilot (n=10, 1 model, 2 baselines) | ~40 | < $0.50 |
| Full (n=500, 3 models, 6 baselines) | ~18,000 | $50–150 |

---

## Q1 Readiness Impact

| Before EXP-004 | After EXP-004 |
|---|---|
| Single-model pipeline only | Multi-model orchestrator |
| No cross-model statistics | McNemar + Holm + bootstrap CI |
| No EXP-004 artifacts | BLOCKED artifacts with provenance |
| Real LLM results: 0 | Real LLM results: **still 0** |

**Manuscript impact:** Infrastructure ready. Results tables remain empty until API executes.

---

*This report contains no fabricated metrics. Re-run after fixing API credentials.*
