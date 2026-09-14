# Claim–Evidence Matrix

Every manuscript claim must map to an experiment ID and metric.  
**Rule:** Claims without COMPLETED real-LLM evidence are marked **UNSUPPORTED**.

| # | Claim | Experiment | Metric | Status | Value |
|---|---|---|---|---|---|
| C1 | ADAPTI-GUARD detects prompt injection | EXP-017 | F1 (smoke) | PARTIAL | 0.802 |
| C2 | Detector generalizes to held-out data | EXP-018 | F1 (valid) | PARTIAL | 0.410 |
| C3 | Adaptive policy reduces ASR vs fixed | EXP-005 | ASR Δ | SIM ONLY | ≤0.027 |
| C4 | Utility preserved under adaptation | EXP-005 | utility | SIM ONLY | TBD |
| C5 | Beats no-defense baseline (real LLM) | EXP-003 | ASR reduction | **NOT_RUN** | — |
| C6 | Beats regex baseline (real LLM) | EXP-003 | ASR reduction | **NOT_RUN** | — |
| C7 | Beats Llama Guard (real LLM) | EXP-003 | ASR reduction | **NOT_RUN** | — |
| C8 | Real ASR on GPT-4o-mini | EXP-002 | ASR | **INVALID** | 401 errors (n=5) |
| C9 | Real ASR on Llama-3.1-8B | EXP-002 | ASR | **NOT_RUN** | — |
| C10 | Real ASR on Qwen2.5-7B | EXP-002 | ASR | **NOT_RUN** | — |
| C11 | Robust against evolving attacks | EXP-008 | block_rate | SIM ONLY | TBD |
| C12 | Publication benchmark ≥10K | benchmark_q1 | n_samples | **SUPPORTED** | 15,053 |
| C13 | Balanced benign class | benchmark_q1 | benign % | **SUPPORTED** | 21.2% |
| C14 | Judge agrees with humans | HUMAN_EVAL | Cohen κ | **NOT_RUN** | — |
| C15 | Low defense cost overhead | cost_analysis | latency_ms | ESTIMATED | ~8ms |
| C16 | Multi-seed significance | EXP-005 | bootstrap CI | INVALID | identical seeds |

## Manuscript sections — evidence requirements

| Section | Minimum evidence needed | Current |
|---|---|---|
| Abstract | C5, C8, C12 | **INSUFFICIENT** |
| Introduction | Problem + gap | OK (narrative) |
| Related Work | Literature matrix | Partial (docs only) |
| Method | Architecture + threat model | OK (code) |
| Experiments | C5–C11 all COMPLETED | **0/7 real** |
| Results | Tables from EXP-002/003 | **MISSING** |
| Ablation | C3, C4 with real LLM | SIM ONLY |
| Limitations | Honest gaps | Required |
| Conclusion | Supported claims only | **Cannot write** |

## Unsupported claims to REMOVE from manuscript

1. "State-of-the-art defense performance" — no SOTA comparison executed
2. "Bayesian risk adaptation" — counter-based, not Bayesian
3. "Validated across multiple LLM families" — BLOCKED
4. "Publication-ready results" — Phase 8 bundles absent
5. "Strong generalization" — NotInject F1=0.41 contradicts
