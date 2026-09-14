# ADAPTI-GUARD Q1 Upgrade Baseline

**Generated:** 2026-09-01 (Phase 0 inventory)  
**Purpose:** Immutable reference of repository state *before* Q1 scientific upgrade.  
**Git commit:** `612f577118a19949b4862a3b27b801db8c7eef65`  
**Branch:** `main`

---

## Repository state

| Item | Value |
|------|-------|
| Git commit | `612f577118a19949b4862a3b27b801db8c7eef65` |
| Branch | `main` |
| Python (system) | 3.12.3 |
| Python (documented in REPRODUCIBILITY.md) | 3.12.10 (Windows) |
| OS | Linux 6.18.33.2-microsoft-standard-WSL2 (x86_64) |
| Virtual environment | `.venv` — **NOT PRESENT in workspace clone** (user reports configured locally) |
| `.env` | **NOT PRESENT in workspace clone** (gitignored; user reports `OPENROUTER_API_KEY` configured locally) |
| GPU | NOT_AVAILABLE (NVML blocked in WSL2 sandbox) |
| CUDA / PyTorch | NOT_AVAILABLE (torch not installed in system Python) |
| Repository files (excl. `.git`, `.venv`) | 243 |
| Python source files | 83 |
| Test modules (`tests/test_*.py`) | 20 |
| Historical experiment run folders (`experiments/runs/EXP-*`) | 18 |
| Dataset files in clone (`dataset/`, `datasets/`, `BIPIA/`) | **0** (gitignored / absent) |
| `results/` artifacts in clone | **0** (gitignored / absent) |
| `experiments/registry.csv` rows | 0 (header only) |

### Key package versions (`requirements.txt`, pinned)

| Package | Version |
|---------|---------|
| openai | 2.54.0 |
| python-dotenv | 1.2.3 |
| pandas | 3.0.5 |
| numpy | 2.5.2 |
| pytest | 9.1.1 |
| scikit-learn | **NOT PINNED** |
| scipy | **NOT PINNED** |

Full pin list: 222 packages (includes Garak, Inspect AI, PyTorch/CUDA — heavy Windows-oriented lockfile).

---

## Architecture

### CURRENT IMPLEMENTATION

```
Input (text)
    → PromptInjectionDetector (regex/heuristic, ~1,387 lines)
    → RiskEngine (weighted linear score)
    → DefensePolicyEngine (risk level × defense level → action)
    → DefenseActionLayer (sanitize / block / tool restrict)
    → OutcomeEvaluator (SIMULATED — no target LLM)
         └── attack_succeeded() — substring matching on sanitized text
    → FeedbackEngine (rule-based signals)
    → PolicyUpdateEngine (counter thresholds: attack=2, legitimate=2)
    → Metrics (compute_metrics)
```

**No Target LLM. No Independent Judge. No real ASR.**

### TARGET SCIENTIFIC ARCHITECTURE

```
Input (attack / benign prompt)
    → Detector (pluggable: Regex / Classifier / LLM)
    → Risk Engine
    → Adaptive Policy (L0–L3)
    → Defense Action (block / sanitize / allow)
    → [if allowed] Target LLM (OpenRouter / local)
    → Independent LLM Judge (separate model family)
    → Outcome + Metrics (real ASR, utility, latency, cost)
    → Feedback → Threshold-Based Adaptive Controller
```

---

## Scientific status by component

| Component | Status | Evidence |
|-----------|--------|----------|
| Regex detector (`PromptInjectionDetector`) | **IMPLEMENTED** | `src/adapti_guard/detector/prompt_injection_detector.py` |
| ML / LLM detector | **MISSING** | No classifier or LLM moderation module |
| Risk engine | **IMPLEMENTED** | `src/adapti_guard/risk/risk_engine.py` — heuristic |
| Policy engine | **IMPLEMENTED** | `src/adapti_guard/policy/policy_engine.py` — rule-based |
| Defense action layer | **IMPLEMENTED** | `src/adapti_guard/defense/action_layer.py` |
| Adaptive controller | **IMPLEMENTED** | `PolicyUpdateEngine` — **SIMULATED** feedback only |
| Target LLM pipeline | **MISSING** | No `target_model.py` (pre-upgrade) |
| Independent LLM judge | **MISSING** | No `llm_judge.py` (pre-upgrade) |
| ASR (primary) | **SIMULATED** | `src/adapti_guard/evaluation/attack_outcome.py` |
| Outcome evaluator | **IMPLEMENTED** | Binary security/utility on simulated outcomes |
| Harmonized runner | **IMPLEMENTED** | `harmonized_runner.py` — simulation path |
| Adaptive attacker | **PARTIAL** | 4 families, 8 unique template strings |
| External datasets | **MISSING** in clone | Scripts reference NotInject, BIPIA, InjecAgent, etc. |
| benchmark_v2 dataset | **MISSING** | Not yet created (Phase 1) |
| SOTA baselines (Llama Guard, etc.) | **MISSING** | Not implemented |
| Garak integration | **BROKEN** | Imports non-existent `DefensePipeline` |
| Inspect AI integration | **BROKEN** | Same `DefensePipeline` import error |
| Statistical inference | **MISSING** | No CIs, no paired tests in codebase |
| RAG evaluation | **MISSING** | `RAG_ATTACK` weight only in risk engine |
| Agent evaluation | **MISSING** | Schema fields only in `data/schema.py` |
| Experiment provenance (new standard) | **PARTIAL** | `artifact_standard.py` exists; no `experiment_runs/` layout |
| API / OpenRouter client | **NOT VERIFIED in clone** | User reports OK locally; `.env` absent here |

---

## Known limitations (pre-upgrade audit summary)

1. No real LLM evaluation in primary pipeline.
2. ASR is circular simulation (detector ↔ sanitizer ↔ substring judge).
3. External SOTA baselines not executed.
4. RAG and agent evaluation not implemented.
5. Statistical validation insufficient (single seed, no CIs).
6. Datasets and `results/` gitignored — clone not self-contained.
7. Detector is historical patch-stack with duplicated V18 block.
8. Garak / Inspect integrations broken.
9. Held-out NotInject validation: F1≈0.41 (committed metrics in `EXP-017/018`).
10. Manuscript-grade evidence insufficient for Q1.

---

## Pre-upgrade Q1 readiness (evidence-based)

**2.8 / 10** — research prototype (simulation-first).

---

## Upgrade phases (execution plan)

| Phase | Focus | Status at baseline |
|-------|-------|-------------------|
| 0 | Repository audit | IN PROGRESS |
| 1 | Dataset validation (`benchmark_v2`) | NOT_RUN |
| 2 | Real target LLM adapter | NOT_RUN |
| 3 | Independent LLM judge | NOT_RUN |
| 4 | End-to-end real ASR (EXP-003) | NOT_RUN |
| 5 | Baselines | NOT_RUN |
| 6 | Adaptive controller experiments | NOT_RUN |
| 7 | RAG | NOT_RUN |
| 8 | Agent | NOT_RUN |
| 9 | Statistics | NOT_RUN |
| 10 | Reproducibility docs | PARTIAL |
| 11 | Claim audit | NOT_RUN |
| 12 | Manuscript evidence package | NOT_RUN |

---

## Files preserved (not to delete blindly)

- All `src/adapti_guard/detector/prompt_injection_detector.py.v*` backups
- `experiments/runs/EXP-*` historical provenance
- `experiments/experiment_history.md`
- Existing harmonized / sensitivity scripts (legacy simulation path retained as `LEGACY_SIMULATION_METRIC`)
