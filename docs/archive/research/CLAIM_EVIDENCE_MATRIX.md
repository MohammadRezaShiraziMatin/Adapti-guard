# ADAPTI-GUARD — Master Claim–Evidence Matrix

**Phase 1 Audit | Date:** 2026-09-02  
**Rule:** No evidence → no claim.

---

| # | Claim | Required Evidence | Experiment | Metric | Statistical Test | Figure/Table | Status |
|---|-------|-------------------|------------|--------|------------------|--------------|--------|
| C1 | Regex detector detects injection (in-distribution) | NotInject smoke eval | EXP-017 | F1, FPR | Bootstrap CI | Table D1 | **PARTIAL** F1=0.802 n=1000 |
| C2 | Detector generalizes held-out | NotInject valid split | EXP-018 | F1=0.41 | CI | Table D2 | **NEGATIVE** |
| C3 | ADAPTI-GUARD reduces ASR vs B0 (real LLM) | Judge-labeled paired outcomes | EXP-004 | ASR | McNemar p<0.05 | Table 2, Fig 1 | **BLOCKED** |
| C4 | Adaptive beats fixed on security–utility | Pareto + reward | EXP-003 | ASR, utility, reward | Wilcoxon | Fig 2 Pareto | **BLOCKED** |
| C5 | Cost gate improves utility vs no gate | Ablation A vs C | EXP-006 | FPR, utility, ASR | McNemar | Table 5 | **SIMULATION-ONLY** |
| C6 | Risk engine improves outcomes | Ablation A vs B | EXP-006 | ASR | McNemar | Table 5 | **SIMULATION FALSIFIED** (identical) |
| C7 | Escalation helps under attack pressure | A vs F | EXP-006/009 | ASR, level trace | Time-series | Fig 5–7 | **SIMULATION CONTRADICTS** (F better) |
| C8 | Multi-model generalization | ≥3 models B0 vs B6 | EXP-004 | ASR per model | Per-model McNemar | Table 3 | **BLOCKED** |
| C9 | Beats strong guard baseline | Real B5 API | EXP-003 | ASR, FPR | McNemar + Holm | Table 2 | **BLOCKED** (fake B5) |
| C10 | benchmark_q1 ≥10K balanced corpus | statistics.json | Dataset audit | n, % benign | — | Table 1 | **SUPPORTED** 15,053 / 21.2% |
| C11 | 7 attack categories covered | attack_dataset counts | build script | per-category n | — | Table 1b | **UNSUPPORTED** (2 gaps) |
| C12 | Robust to evolving attacks | EXP-009 phases | EXP-009 | ASR over time | Trend test | Fig 6 | **NOT_RUN** |
| C13 | Agent/tool defense | Tool trace eval | EXP-AGENT | tool misuse rate | — | — | **UNSUPPORTED** |
| C14 | System prompt leakage defense | Leakage ASR | Leakage eval | leak rate | — | — | **UNSUPPORTED** (0 samples) |
| C15 | Low deployment overhead | Latency/token/cost | EXP-004 profiling | p95 latency, $/1K | CI | Table 6 | **BLOCKED** |
| C16 | Judge agrees with humans | Annotated subset | HUMAN-EVAL | Cohen's κ | κ test | Appx A | **NOT_RUN** |
| C17 | Blind judge prevents leakage | Field audit | Unit tests | pass rate | — | — | **PARTIAL** tests pass |
| C18 | Reproducible one-command pipeline | Makefile + hashes | Repro audit | hash match | — | README | **PARTIAL** |
| C19 | Statistical significance multi-baseline | Holm report | EXP-004 stats | p-values | Holm | Footnote | **BLOCKED** |
| C20 | Publication-valid real results exist | Any metrics.json valid | All real LLM | auth_errors=0 | — | — | **FALSE** (0 valid) |

---

## Evidence Classification Legend

| Label | Meaning |
|-------|---------|
| **SUPPORTED** | Artifact verified on disk |
| **PARTIAL** | Some evidence; insufficient for claim strength |
| **NEGATIVE** | Evidence contradicts claim |
| **BLOCKED** | Infrastructure ready; execution blocked |
| **SIMULATION-ONLY** | Not publication evidence |
| **UNSUPPORTED** | No valid artifact |
| **NOT_RUN** | Never executed |
| **FALSE** | Claim is factually wrong |

---

## Manuscript Section Gate

| Section | Minimum claims supported | Current |
|---------|-------------------------|---------|
| Abstract | C3, C4, C10 | **0/3** |
| Introduction gap | C10 + problem narrative | **1/2** |
| Method | Architecture docs | OK |
| Experiments setup | C10, C11 | **1/2** |
| Main results | C3, C4, C9 | **0/3** |
| Ablation | C5, C6, C7 | **0/3** (sim only) |
| Generalization | C8 | **0/1** |
| Agent security | C13 | **0/1** |
| Limitations | C2, C6, C13 | Can write honestly |
| Conclusion | Subset of supported | **Cannot write positive conclusion** |

---

## Stale / Dangerous Artifacts (Do Not Cite)

| Path | Problem |
|------|---------|
| `results/experiment_runs/EXP-002/.../metrics.json` | May still show ASR=0 with 401 errors |
| `experiments/registry.csv` | EXP-002 may show COMPLETED |
| EXP-005 `C_bayesian_risk` label | Misleading name |
| Any harmonized_runner summary ASR | SIMULATION-ONLY |

---

## Supported Claims Safe for Draft

1. benchmark_q1 contains 15,053 samples with documented splits and hashes (**C10**).
2. Evaluation infrastructure separates real vs simulation modes with provenance labels (**C17 partial**).
3. Held-out detector F1 is ~0.41 — honest negative result (**C2**).
4. No valid real-LLM defense ASR has been measured yet (**C20**).

Everything else requires Phase 2 execution.

---

## Phase 2 Tracking (updated 2026-09-02)

| Claim | Evidence | Experiment | Phase 2 Status |
|-------|----------|------------|----------------|
| ADAPTI-GUARD reduces ASR | REAL_LLM predictions | EXP-004-D | **NOT_STARTED** — API blocked |
| Adaptive policy improves utility | REAL_LLM + judge utility_success | EXP-003 | **NOT_STARTED** |
| Components contribute independently | REAL_LLM ablation | EXP-006 | **NOT_STARTED** (sim only exists) |
| Generalizes across models | 3+ API models | EXP-004-D | **NOT_STARTED** |
| Cost-aware trade-off | Cost/latency logs | EXP-003/009 | **NOT_STARTED** |
| Long-term adaptation stable | Time series | EXP-009 | **NOT_STARTED** |
| Judge validity | Cohen's κ | HUMAN-EVAL | **NOT_RUN** |

**Execution plan:** `docs/research/PHASE2_EXECUTION_PLAN.md`  
**Manifest:** `docs/research/PHASE2_EXPERIMENT_MANIFEST.md`  
**Stop gate:** INFRA-SMOKE n=5 must pass before EXP-004 main.
