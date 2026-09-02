# ADAPTI-GUARD — Phase 2 Experiment Manifest

**Created:** 2026-09-02  
**Git commit (audit time):** `612f577118a19949b4862a3b27b801db8c7eef65`  
**Rule:** Status updated only after artifacts verified on disk. No fabricated results.

---

## Global Infrastructure Status

| Component | Status | Validity | Notes |
|-----------|--------|----------|-------|
| OpenRouter API | **BLOCKED** | INVALID | Key missing `sk-or-v1-` prefix |
| Ollama daemon | **BLOCKED** | INVALID | Client v0.33.2 installed; server not running |
| Real LLM smoke (n=5) | **NOT_STARTED** | — | Blocked by API + Ollama |
| attack_dataset ≥700 | **BLOCKED** | — | Current: 528; 2 category gaps |
| B5 real Llama Guard | **NOT_STARTED** | — | Code uses regex fallback |
| B1 true sanitization | **NOT_STARTED** | — | B1 = threshold block today |
| B6 alias in pipeline | **NOT_STARTED** | — | Adaptive = `B3` in code only |
| HUMAN-EVAL | **NOT_STARTED** | NOT_RUN | Protocol in `docs/HUMAN_EVALUATION.md` |

---

## Experiment Tracker

| Experiment | Status | Dataset | Model(s) | N (target) | Type | Validity | Last updated |
|------------|--------|---------|----------|----------:|------|----------|--------------|
| **INFRA-SMOKE-001** | **COMPLETE** | benchmark_q1 test (5) | openai/gpt-4o-mini | 5 | REAL_LLM | **REAL_LLM** | 2026-09-02 PASS |
| **INFRA-LOCAL-SMOKE** | NOT_STARTED | benchmark_q1 test (5) | ollama qwen2.5:3b | 5 | REAL_LLM | — | 2026-09-02 |
| **DATASET-FREEZE** | **BLOCKED** | benchmark_q1 + attack_dataset | — | ≥700 | — | **FREEZE_BLOCKED** | 2026-09-02 audit |
| **DETECTOR-AUDIT** | NOT_STARTED | NotInject / benchmark_q1 | — | — | offline | — | 2026-09-02 |
| **EXP-004-A** (smoke) | NOT_STARTED | frozen test | model_a | 5 | REAL_LLM | — | 2026-09-02 |
| **EXP-004-B** (pilot) | NOT_STARTED | frozen test | model_a | 20 | REAL_LLM | — | 2026-09-02 |
| **EXP-004-C** (medium) | NOT_STARTED | frozen test | model_a | 100 | REAL_LLM | — | 2026-09-02 |
| **EXP-004-D** (main) | NOT_STARTED | frozen test | model_a,b,c | ≥500 | REAL_LLM | — | 2026-09-02 |
| **EXP-003** | NOT_STARTED | frozen test | model_a | ≥500 | REAL_LLM | — | 2026-09-02 |
| **EXP-006** | NOT_STARTED | frozen test | model_a | ≥300 | REAL_LLM | — | 2026-09-02 |
| **EXP-009** | NOT_STARTED | phased stream | model_a | ≥1000 | REAL_LLM | — | 2026-09-02 |
| **HUMAN-EVAL** | NOT_STARTED | stratified sample | — | ≥200 | HUMAN_VALIDATED | NOT_RUN | 2026-09-02 |
| **EXP-AGENT** | NOT_STARTED | AgentDojo | — | ≥100 | REAL_LLM | — | Optional |
| EXP-002 (legacy) | **FAILED** | test | target_3 | 5 | REAL_LLM | **INVALID** | 401×5 |
| EXP-005 | COMPLETE | sim stream | — | 20 | SIMULATION_ONLY | SIMULATION_ONLY | Do not cite |
| EXP-006 (legacy sim) | COMPLETE | sim stream | — | 20 | SIMULATION_ONLY | SIMULATION_ONLY | Do not cite |
| EXP-008 | COMPLETE | sim | — | 150 | SIMULATION_ONLY | SIMULATION_ONLY | Do not cite |

---

## Validity Legend

| Validity | Meaning |
|----------|---------|
| `REAL_LLM` | Target + judge API/Ollama calls succeeded; provenance complete |
| `HUMAN_VALIDATED` | Human labels + κ reported |
| `SIMULATION_ONLY` | harmonized_runner / regex ASR — not for manuscript |
| `INVALID` | Auth errors, missing outputs, or stale/misleading artifacts |
| `NOT_RUN` | Never executed |

---

## Status Update Protocol

After each run, verify before marking COMPLETE:

1. `metrics.json` has `evaluation_mode: real_llm_judge`
2. `auth_errors == 0` and `n_judge_errors == 0` (or documented partial)
3. `predictions.jsonl` row count == declared n
4. `prompt_tokens_total > 0` for non-blocked episodes
5. Git commit + dataset hash in run metadata
6. No fallback to `LEGACY_SIMULATION_ONLY`

---

## Artifact Locations (target layout)

```
experiments/EXP004_MULTI_MODEL/
├── manifest.json
├── model_a/
│   ├── B0/
│   │   ├── B0_predictions.jsonl
│   │   ├── metrics.json
│   │   └── logs.json
│   └── B6/
│       └── ...
├── statistical_analysis.json
├── tables/primary_comparison.csv
└── figures/
```

---

## Historical Invalid Runs (quarantine)

| Path | Issue | Action |
|------|-------|--------|
| `experiments/EXP002_REAL_LLM/target_3/metrics.json` | Reclassified INVALID | OK |
| `results/experiment_runs/EXP-002/RUN-*/metrics.json` | May show ASR=0 with 401s | **Quarantine in Phase 2.1** |
| `experiments/registry.csv` | May list EXP-002 COMPLETED | **Fix in Phase 2.1** |

---

*Update this file after each experiment stage. Never mark REAL_LLM without artifact verification.*
