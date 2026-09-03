# Q1 Scientific Upgrade — Changelog

## 2026-09-01 — Full Q1 Upgrade (Phases 1–11)

### Phase 1: Review Audit
- `docs/Q1_REVIEW_AUDIT_FINAL.md` — hostile reviewer perspective

### Phase 2: Dataset Upgrade
- `datasets/benchmark_q1/` — 15,053 samples, 7 categories
- `scripts/build_benchmark_q1.py`
- `configs/datasets.yaml` — source adapters + availability
- Artifacts: `dataset_card.md`, `statistics.json`, `hashes.json`, `distribution_report.md`

### Phase 3: Real LLM Evaluation
- `src/adapti_guard/evaluation/attack_success.py`
- `src/adapti_guard/experiments/real_llm_runner.py`
- `experiments/EXP002_REAL_LLM/` — BLOCKED without API key

### Phase 4: Baseline Comparison
- `baselines/` — 7 methods (no_defense, regex, tfidf_ml, llama_guard, prompt_guard, nemo_guard, adapti_guard)
- `experiments/EXP003_BASELINES/`

### Phase 5: Adaptation Ablation
- `experiments/EXP005_ADAPTATION/` — 5 seeds, simulation mode

### Phase 6: Adaptive Attack
- `experiments/EXP008_ADAPTIVE_ATTACK/` — 3 rounds × 50 attacks

### Phase 7–9: Protocols
- `docs/HUMAN_EVALUATION.md`
- `scripts/run_cost_analysis.py`
- `docs/STATISTICAL_REPORT.md`

### Phase 10–11: Manuscript + Readiness
- `docs/MANUSCRIPT_DRAFT.md` (evidence-gated)
- `docs/CLAIM_EVIDENCE_MATRIX.md`
- `docs/Q1_FINAL_READINESS_REPORT.md`

### Readiness: 3.2 → 5.8 / 10
### Submission: NO (pending real LLM execution)
