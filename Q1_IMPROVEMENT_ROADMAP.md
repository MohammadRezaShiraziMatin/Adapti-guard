# ADAPTI-GUARD: Q1 Improvement Roadmap

**Generated:** 2026-09-02  
**Full review:** [docs/Q1_PRE_SUBMISSION_REVIEW.md](docs/Q1_PRE_SUBMISSION_REVIEW.md)  
**Readiness:** 4.8/10 → target 8.5/10 for submission

---

## Priority 1 — Must Implement Before Submission

| # | Task | Artifact | Est. effort | Blocker |
|---|------|----------|-------------|---------|
| P1.1 | Fix `OPENROUTER_API_KEY` (must start with `sk-or-v1-`) | `.env` | 5 min | User action |
| P1.2 | Pass preflight gate | `PHASE1_SCIENTIFIC_AUDIT.md` → `experiments_cleared: YES` | 30 min | P1.1 |
| P1.3 | Complete attack_dataset: ≥100 per category, ≥700 total | `datasets/attack_dataset/attack_dataset.json` | 3–5 days | Import AgentDojo + Garak leakage |
| P1.4 | EXP-004 real-LLM: B0 vs B6, n≥500, 3 API models | `experiments/EXP004_MULTI_MODEL/` | 2–3 days | P1.2, ~$150 API |
| P1.5 | EXP-003 full baselines B0–B6 on GPT-4o-mini | `comparison_table.csv` (filled) | 2 days | P1.2 |
| P1.6 | Wire real B5 Llama-Guard-3-8B (remove regex fallback) | `defense_baselines.py` | 1 day | API access |
| P1.7 | Statistical analysis on all main claims | `statistical_analysis.json` | 4 hrs | P1.4 |
| P1.8 | Remove unsupported claims from manuscript | `docs/MANUSCRIPT_DRAFT.md` | 2 hrs | — |
| P1.9 | Human judge validation n=200, report Cohen's κ | `docs/HUMAN_EVALUATION.md` results | 1 week | Annotators |
| P1.10 | Per-category stratified results table | Manuscript Table 3 | 4 hrs | P1.4 |

### P1 Execution Sequence

```bash
# Day 1: Unblock
export OPENROUTER_API_KEY=sk-or-v1-...
python scripts/preflight_api.py
python scripts/phase1_preflight_audit.py

# Day 2-3: Dataset
# Import tool_abuse + system_prompt_leakage samples
python scripts/build_attack_dataset.py --split all --min-per-category 100

# Day 4-7: Main experiments
python experiments/EXP004_MULTI_MODEL/run.py \
  --targets model_a model_b model_c \
  --baselines B0 B1 B2_L2 B4 B5 B6 \
  --n-samples 500 --seed 42

# Day 8: Statistics + tables
python scripts/statistical_analysis.py --input experiments/EXP004_MULTI_MODEL

# Day 9-14: Human eval + manuscript update
```

---

## Priority 2 — Strongly Recommended

| # | Task | Artifact | Est. effort |
|---|------|----------|-------------|
| P2.1 | Local model matrix (4 Ollama models) | `model_generalization_matrix.csv` | 2 days |
| P2.2 | EXP-006 ablation (real LLM, 3 models) | `experiments/EXP006_ABLATION/` | 2 days |
| P2.3 | EXP-009 long-term adaptation (1000 ep) | `figures/asr_over_time.png` etc. | 3 days |
| P2.4 | EXP-010 failure analysis (10+10 cases) | `docs/FAILURE_ANALYSIS.md` | 1 day |
| P2.5 | Efficiency report (measured, not estimated) | `docs/efficiency_report.md` | 1 day |
| P2.6 | Implement B1 (sanitization) and B3 (tool restriction) | `defense_baselines.py` | 1 day |
| P2.7 | Expand adaptive attacker to 50+ templates, 7 families | `adaptive_attacker.py` | 2 days |
| P2.8 | Formal threat model with utility function | `docs/THREAT_MODEL.md` | 1 day |
| P2.9 | Multi-seed runs (42, 123, 456) with fixed seed bugs | EXP-004 × 3 seeds | 1 day |
| P2.10 | Related work table (15+ systems) | Manuscript §2 | 1 day |
| P2.11 | Replace 8 hardcoded benign tasks with dataset benign | `harmonized_runner.py` | 4 hrs |
| P2.12 | One-command reproduction (`make reproduce`) | `Makefile` | 4 hrs |

---

## Priority 3 — Optional (Strengthens but Not Blocking)

| # | Task | Artifact |
|---|------|----------|
| P3.1 | EXP-007 agent tool emulation with mock tools | `experiments/EXP007_AGENT_TOOL/` |
| P3.2 | Gemini 2.0 Flash + Claude Sonnet 4 as extra API targets | `configs/models.yaml` |
| P3.3 | Cross-dataset detector transfer analysis | Manuscript appendix |
| P3.4 | FastAPI production middleware demo | `defenses/middleware_example.py` |
| P3.5 | Docker reproducibility environment | `Dockerfile` |
| P3.6 | Zenodo DOI for benchmark_q1 | External |
| P3.7 | RL-based adaptive attacker | Research extension |
| P3.8 | Comparison with NeMo Guardrails / Rebuff | Related experiments |

---

## Expected Manuscript Tables & Figures

| ID | Type | Content | Priority |
|----|------|---------|----------|
| Table 1 | Dataset | Category counts + sources | P1 |
| Table 2 | Setup | Models and providers | P1 |
| Table 3 | Main | B0–B6 comparison + stats | P1 |
| Table 4 | Per-category | ASR by attack type | P1 |
| Table 5 | Ablation | Component removal | P2 |
| Table 6 | Efficiency | Latency/cost overhead | P2 |
| Fig 1 | Pareto | ASR vs utility | P1 |
| Fig 2 | Heatmap | Category × baseline ASR | P1 |
| Fig 3 | Bars | Cross-model generalization | P2 |
| Fig 4 | Bars | Ablation ASR delta | P2 |
| Fig 5-7 | Time series | EXP-009 adaptation | P2 |
| Fig 8 | Pie | Failure taxonomy | P2 |

---

## Claim Readiness Tracker

| Claim | Required experiment | Status |
|-------|---------------------|--------|
| Reduces ASR vs no defense | EXP-004 B0 vs B6 | BLOCKED |
| Preserves utility | EXP-004 utility metric | BLOCKED |
| Beats static baselines | EXP-003 B0–B5 | BLOCKED |
| Model-independent | EXP-004 7 models | BLOCKED |
| Adaptation helps | EXP-006 A vs E | BLOCKED |
| Cost-aware | EXP-006 A vs C | BLOCKED |
| Long-term robustness | EXP-009 | BLOCKED |
| Statistically significant | statistical_analysis.py | BLOCKED |
| Dataset scale ≥10K | benchmark_q1 | **SUPPORTED** |
| Human-judge agreement | HUMAN_EVAL | NOT_RUN |

**Supported claims: 1/10**

---

## Budget Estimate

| Item | Cost |
|------|------|
| EXP-004 (3 models × 500 ep × 2 baselines × judge) | ~$120–200 |
| EXP-003 (7 baselines × 500 ep) | ~$80–150 |
| EXP-006 ablation (6 variants × 300 ep) | ~$60–100 |
| EXP-009 (1000 ep × 1 model) | ~$40–80 |
| Human annotation (200 cases × $0.50) | ~$100 |
| **Total** | **~$400–630** |

Local models (Ollama): $0 compute if existing hardware.

---

## Definition of Done (Submission-Ready)

- [ ] `phase1_preflight_audit.py` → all gates PASS
- [ ] attack_dataset ≥700 samples, 7/7 categories ≥100
- [ ] EXP-004 complete: 3+ models, B0+B6, n≥500
- [ ] EXP-003 complete: B0–B6, statistical significance reported
- [ ] All manuscript numbers traceable to `experiments/` artifacts
- [ ] Zero `LEGACY_SIMULATION_ONLY` numbers in manuscript
- [ ] Human κ ≥ 0.6 on judge validation subset
- [ ] Failure analysis with 10+10 real cases
- [ ] Reproduction package with one-command script
- [ ] Limitations section addresses detector F1=0.41 and tool-abuse gap

**Target readiness score after P1+P2: 8.5/10**
