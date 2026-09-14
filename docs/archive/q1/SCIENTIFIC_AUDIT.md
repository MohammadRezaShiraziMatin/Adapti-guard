# ADAPTI-GUARD Full Scientific Audit (Part 1)

**Audit date:** 2026-09-02  
**Audit version:** 1.0.0  
**Git commit:** `612f577118a19949b4862a3b27b801db8c7eef65`  
**Auditor:** Automated (`scripts/scientific_audit.py`) + manual review  
**Regenerate:** `python scripts/scientific_audit.py`

---

## Executive Summary

ADAPTI-GUARD has **strong engineering infrastructure** but is **not Q1 publication-ready**. The real LLM evaluation pipeline exists and is scientifically sound in design, but **no valid real-LLM experimental results** currently support security claims.

| Dimension | Score | Status |
|---|---:|---|
| Defense architecture | 8/10 | Implemented |
| Real LLM pipeline | 8/10 | Implemented, not validated |
| **Real LLM results** | **0/10** | **No valid artifacts** |
| Dataset (benchmark_q1) | 8/10 | 15,053 samples, hashed |
| Simulation experiments | 6/10 | Complete but separated |
| Provenance logging | 7/10 | Framework exists |
| Statistical validation | 4/10 | Tools exist, not applied to real data |
| Human validation | 1/10 | Protocol only |
| **Overall Q1 readiness** | **5.4/10** | **NOT READY** |

**Submission recommendation: NO**

---

## Audit Scope

This audit covers:

1. Scientific validity of all experiment artifacts
2. Provenance completeness (dataset, model, seed, commit, timestamp)
3. Separation of simulation vs real LLM evidence
4. Claim–evidence alignment
5. Critical integrity issues (mislabeled results, circular ASR)

---

## Architecture Assessment

### Implemented (SUPPORTED)

```
Input → PromptInjectionDetector → RiskEngine → PolicyEngine
     → DefenseActionLayer → [Target LLM] → [LLM Judge] → Metrics
```

| Component | File | Status |
|---|---|---|
| Target LLM adapter | `evaluation/target_model.py` | OpenRouter + Ollama |
| Independent judge | `evaluation/llm_judge.py` | JSON verdict, no detector logic |
| Real eval episodes | `evaluation/attack_success.py` | Judge-driven ASR |
| Real LLM pipeline | `experiments/real_llm_pipeline.py` | B0–B3 baselines |
| Provenance validation | `evaluation/provenance.py` | Validity classification |
| Experiment logging | `evaluation/experiment_logging.py` | Full artifact tree |
| Statistical tools | `evaluation/statistics.py` | Bootstrap, McNemar |

### Legacy Simulation (NOT for publication claims)

| Component | File | ASR Source |
|---|---|---|
| Harmonized runner | `experiments/harmonized_runner.py` | `attack_outcome.py` heuristics |
| Attack outcome | `evaluation/attack_outcome.py` | Substring matching on sanitized text |
| EXP-005 ablation | `experiments/EXP005_ADAPTATION/` | Simulation |
| EXP-008 adaptive attack | `experiments/EXP008_ADAPTIVE_ATTACK/` | Detector block rate only |

---

## Experiment Inventory

### Real LLM Experiments

| ID | File Status | Scientific Validity | N | Issue |
|---|---|---|---:|---|
| EXP-002 (target_3) | COMPLETED | **INVALID** | 5 | 100% API/judge errors (401) |
| EXP-003 | NOT_RUN | NOT_RUN | 0 | Never executed |
| REAL-LLM-EVAL | BLOCKED | BLOCKED | 0 | Invalid API key format |
| EXP-000 | BLOCKED | BLOCKED | 2 | API key missing |

**Critical finding:** EXP-002 `metrics.json` reports `status: COMPLETED` and `asr: 0.0`, but all 5 predictions show `[TARGET_ERROR: AuthenticationError 401]` and `judge_reason: judge_api_error`. These metrics are **scientifically invalid** and must not appear in any manuscript.

### Simulation Experiments (valid for engineering, not for LLM security claims)

| ID | Mode | N | Usable for ASR claims |
|---|---|---:|---|
| EXP-005 | HARMONIZED_SIMULATION | 500 (5×100) | **NO** |
| EXP-008 | DETECTOR_SIMULATION | 150 | **NO** (block rate only) |
| Benchmark v2 defense-sim | defense_simulation | 2000 | **NO** |

### Detector-Only Experiments

| ID | Metric | Value | Notes |
|---|---|---:|---|
| EXP-017 | F1 (smoke) | 0.802 | NotInject train |
| EXP-018 | F1 (held-out) | 0.410 | Poor generalization |

---

## Dataset Provenance

| Dataset | Records | SHA256 (test split prefix) | Location |
|---|---:|---|---|
| benchmark_q1/test | 2,258 | `fa35c657dae473e2...` | `datasets/benchmark_q1/` |
| benchmark_q1 (total) | 15,053 | See `hashes.json` | 7 categories |
| unified_security_dataset | 12,799 | See benchmark v2 | External path |

Builder: `scripts/build_benchmark_q1.py`  
Seed: 42 (70/15/15 split)  
Benign ratio: 21.2%

---

## Provenance Requirements

Every publication-grade experiment MUST record:

| Field | Required | Current compliance |
|---|---|---|
| `experiment_id` | ✅ | Partial |
| `dataset` + `dataset_hash` | ✅ | EXP-002 has hash |
| `seed` | ✅ | Recorded |
| `git_commit` | ✅ | EXP-002 has commit |
| `timestamp` | ⚠️ | Missing in some artifacts |
| `target_model` + version | ✅ | configs/models.yaml |
| `judge_model` + version | ✅ | configs/models.yaml |
| `evaluation_mode` | ✅ | Now enforced |
| `n_judge_errors` | ✅ | Must be checked before COMPLETED |

---

## Claim–Evidence Audit

| Claim | Evidence Required | Current Status |
|---|---|---|
| Real ASR reduction vs no-defense | EXP-003, real judge | **UNSUPPORTED** |
| Adaptive policy improves security | EXP-005 with real LLM | **SIMULATION ONLY** |
| Multi-model evaluation | EXP-002 × 3 targets | **INVALID/BLOCKED** |
| Beats SOTA baselines | EXP-003 + real Llama Guard | **NOT_RUN** |
| 15K benchmark | benchmark_q1 manifest | **SUPPORTED** |
| Agent/RAG security | Dedicated eval | **UNSUPPORTED** |

See `docs/CLAIM_EVIDENCE_MATRIX.md` for full matrix.

---

## Critical Integrity Issues

### 1. Mislabeled EXP-002 Results (FIXED in runner)

Previously: `status: COMPLETED` with `asr: 0.0` despite 100% API failures.  
Fix: `real_llm_runner.py` now returns `status: INVALID` when all judge/target calls fail.  
Action: Re-label existing EXP-002 artifacts as INVALID in registry.

### 2. Simulation Results Near Publication Materials

EXP-005 and EXP-008 results exist and could be mistaken for real LLM results.  
Fix: All simulation artifacts now tagged `evaluation_mode`. See `docs/SIMULATION_VS_REAL_LLM.md`.

### 3. Invalid API Key

`.env` contains 36-char key without `sk-or-v1-` prefix.  
Blocks: EXP-002, EXP-003, REAL-LLM-EVAL.

### 4. SOTA Baseline Fallbacks

`llama_guard`, `prompt_guard`, `nemo_guard` baselines use regex fallback when models unavailable.  
Results from these are **not** SOTA comparisons.

---

## API Infrastructure Status

```
python scripts/preflight_api.py → BLOCKED (invalid key format)
Ollama localhost:11434 → not running
```

Pipeline correctly returns BLOCKED/INVALID — no fabricated metrics.

---

## Gap Analysis: Path to Q1 (≥8.0/10)

| Priority | Task | Effort | Impact |
|---|---|---|---|
| P0 | Fix OpenRouter API key | 5 min | Unblocks all real eval |
| P0 | Re-run EXP-002 smoke (n=5), verify VALID | 30 min | Proves pipeline |
| P0 | Run REAL-LLM-EVAL pilot (n=50, B0+B3) | 2–4 hrs | First valid ASR |
| P1 | Full EXP-003 baseline comparison (n=500) | 1–2 days | Core results table |
| P1 | Multi-target (3 models) | 2–3 days | Generalization claim |
| P1 | Re-run EXP-005 with real LLM | 1 day | Valid ablation |
| P2 | Human judge validation (n=100) | 1 week | κ agreement |
| P2 | Real Llama Guard baseline | 2 days | SOTA comparison |
| P2 | Agent/RAG category eval | 1 week | Domain claims |

**Estimated time to submission-ready: 2–4 weeks** (with valid API, ~$50–200 API cost)

---

## Automated Audit Artifacts

| File | Description |
|---|---|
| `docs/SCIENTIFIC_AUDIT_REPORT.json` | Machine-readable inventory |
| `docs/SCIENTIFIC_AUDIT_REPORT.md` | Auto-generated summary |
| `docs/EXPERIMENT_STATUS.md` | Auto-updated status table |
| `docs/SIMULATION_VS_REAL_LLM.md` | Evidence classification guide |

---

## Part 1 Deliverables Checklist

- [x] `docs/SCIENTIFIC_AUDIT.md` — this document
- [x] `scripts/scientific_audit.py` — automated audit
- [x] `src/adapti_guard/evaluation/provenance.py` — validity schema
- [x] `docs/SIMULATION_VS_REAL_LLM.md` — simulation/real separation
- [x] `tests/test_provenance.py` — validity classification tests
- [x] EXP-002 mislabeling fix in `real_llm_runner.py`
- [x] Auto-updated `docs/EXPERIMENT_STATUS.md`

---

## Next Parts (Pending User Specification)

The user task message was truncated at "PART 1 — Full Scientific Audit Create:".  
Likely subsequent parts include:

- Part 2: Execute real LLM experiments
- Part 3: Statistical validation package
- Part 4: Manuscript evidence integration
- Part 5: Human evaluation execution

---

*This audit contains no fabricated results. All numbers trace to artifacts on disk or explicit NOT_RUN/BLOCKED/INVALID status.*
