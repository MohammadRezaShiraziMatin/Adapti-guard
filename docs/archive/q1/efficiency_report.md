# ADAPTI-GUARD Efficiency Report

> **Status:** TEMPLATE — populate after real-LLM runs (EXP-003/004/006).  
> Do not cite estimated numbers as measured results.

## 1. Measurement Protocol

| Metric | Definition | Instrumentation |
|--------|------------|-----------------|
| Latency (p50/p95) | End-to-end per episode: detect → risk → policy → action → LLM | `experiment_logging.py` timestamps |
| Token overhead | Extra tokens vs B0 (system prompts, sanitization, judge) | OpenRouter usage headers |
| Memory | Peak RSS during batch eval | `scripts/run_cost_analysis.py --profile-memory` |
| API cost | USD per 1,000 episodes | Model pricing × (input + output tokens) |
| Interventions | Count of A1/A2/A3 actions per 1,000 episodes | Defense action logs |

**Seeds:** 42, 123, 456 (report mean ± bootstrap 95% CI).

## 2. Results (TODO — BLOCKED)

### 2.1 Latency Breakdown (ms)

| Component | B0 | B6 (ADAPTI-GUARD) | Δ |
|-----------|-----|-------------------|---|
| Detection | — | TODO | — |
| Risk + Policy | — | TODO | — |
| Defense action | — | TODO | — |
| Target LLM call | — | TODO | — |
| Judge call | — | TODO | — |
| **Total p50** | — | TODO | — |
| **Total p95** | — | TODO | — |

### 2.2 Token Overhead

| Baseline | Avg input tokens | Avg output tokens | Judge tokens | Total/episode |
|----------|------------------|-------------------|--------------|---------------|
| B0 | TODO | TODO | TODO | TODO |
| B6 | TODO | TODO | TODO | TODO |

### 2.3 Cost Projection (USD per 1K episodes)

| Model | B0 | B6 | Overhead % |
|-------|-----|-----|------------|
| GPT-4o-mini | TODO | TODO | TODO |
| Qwen3-30B-A3B | TODO | TODO | TODO |
| Local Qwen2.5-3B | $0 | TODO | TODO |

### 2.4 Intervention Rate

| Defense level | A0 (pass) | A1 (warn) | A2 (sanitize) | A3 (block) |
|---------------|-----------|-----------|---------------|------------|
| L0 | TODO | TODO | TODO | TODO |
| L1 | TODO | TODO | TODO | TODO |
| L2 | TODO | TODO | TODO | TODO |
| L3 | TODO | TODO | TODO | TODO |

## 3. Deployment Feasibility Assessment

### Acceptable thresholds (proposed for paper)

- Latency overhead ≤ 2× B0 p95 on API models
- Token overhead ≤ 30% for agent workloads
- False positive rate ≤ 5% on benign utility tasks
- Cost ≤ $X per 1K episodes (set after pricing audit)

### Current blockers

1. `OPENROUTER_API_KEY` invalid — no measured latency/cost
2. Ollama not running — no local model measurements
3. B5 (Llama Guard) not wired to real API — regex fallback only

## 4. Commands

```bash
# Preflight
python scripts/preflight_api.py
python scripts/phase1_preflight_audit.py

# Cost estimates (theoretical)
python scripts/run_cost_analysis.py --output results/efficiency/

# After EXP-004 completes
python scripts/statistical_analysis.py --input experiments/EXP004_MULTI_MODEL
```

## 5. Manuscript Table Target

**Table X: Deployment overhead of ADAPTI-GUARD vs no-defense baseline**

Columns: Model | Params | Latency Δ% | Token Δ% | Cost Δ% | FPR | Utility

---

*Generated: 2026-09-02 | Evidence status: NO_DATA*
