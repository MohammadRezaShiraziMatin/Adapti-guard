# Q1 Review Audit — Final (Hostile Reviewer Perspective)

**Project:** ADAPTI-GUARD — Adaptive and Utility-Aware Defense Against Evolving Prompt Injection Attacks in LLM-Based Agents  
**Audit date:** 2026-09-01  
**Auditor stance:** Hostile Q1 journal reviewer (LLM Security / Trustworthy AI)  
**Repository:** `/home/mohammadreza/01_BASE_Q1/adapti_guard` @ `612f577`  
**Post-upgrade assessment:** Infrastructure improved; publication evidence still incomplete

---

## Executive Verdict

| Dimension | Pre-upgrade | Post-upgrade | Q1 bar |
|---|---:|---:|---|
| **Overall readiness** | 3.2/10 | **5.8/10** | ≥8.0 |
| **Novelty** | Weak | Weak–Moderate | Strong |
| **Methodology** | Circular ASR | Dual-path (sim + real) | Real only |
| **Experiments** | Missing | Partially scaffolded | Complete |
| **Datasets** | 11-row smoke | 15,053 benchmark_q1 | Diverse + held-out |
| **Baselines** | Internal only | 7 methods (3 ML fallbacks) | SOTA real |
| **Statistics** | None | Bootstrap + McNemar | Full |
| **Reproducibility** | Poor | Good scaffolding | Artifact-complete |

**Recommendation:** **NOT READY FOR SUBMISSION.** Infrastructure now exists; real LLM experiments remain BLOCKED without API execution.

---

## 1. Novelty Evaluation

### Claimed contribution
Adaptive, utility-aware defense that escalates/de-escalates L0–L3 policy levels based on attack feedback while preserving benign task utility.

### Reviewer assessment: **WEAK–MODERATE**

**Prior art overlap:**
- Rule-based prompt injection detection (Rebuff, LLM-Guard, NeMo Guardrails) — well-established
- Discrete policy escalation (L0–L3) — resembles tiered moderation pipelines
- Counter-based adaptation (`PolicyUpdateEngine`: attack_threshold=2, legitimate_threshold=2) — **not Bayesian** despite naming in ablation labels
- Harmonized evaluation protocol — methodologically sound but not novel

**What would be novel (if proven):**
- Demonstrated utility–security Pareto improvement under evolving attacks vs fixed baselines
- Statistically significant ASR reduction with <5% utility loss on real LLMs
- Adaptive attacker robustness across ≥3 model families

**Current evidence for novelty:** INSUFFICIENT. Ablation shows ASR differences of 1–3% on simulation metrics only.

---

## 2. Methodology Weaknesses

| Issue | Severity | Status |
|---|---|---|
| **Circular ASR** via `attack_succeeded()` substring matching | CRITICAL | Real LLM path added (`attack_success.py` + `LLMJudge`) but harmonized runner still uses heuristics |
| **"Bayesian Risk" ablation mislabeled** | HIGH | `DE_ESCALATION_ONLY` is counter-based, not Bayesian |
| **Detector is regex/heuristic** (~1,386 LOC) | HIGH | No ML generalization beyond NotInject smoke (F1=0.80) / held-out (F1=0.41) |
| **No agent-environment evaluation** | HIGH | AgentDojo vectors only (28 samples in benchmark) |
| **Judge independence** | MEDIUM | Gemma-2-9B judge is appropriate family separation; not yet validated vs human |
| **Threat model underspecified** | MEDIUM | No formal attacker capability bounds in code |

---

## 3. Experimental Weaknesses

| Experiment | Status | Issue |
|---|---|---|
| EXP-002 Real LLM | **BLOCKED** | `OPENROUTER_API_KEY` not available in CI/sandbox; 0 completed 500-sample runs |
| EXP-003 Baselines | **BLOCKED** | Same API dependency; Llama/Prompt/NeMo use regex fallback |
| EXP-005 Adaptation | **COMPLETED (sim)** | ASR 0–2.7% on 100-episode heuristic; seeds identical (deterministic) |
| EXP-008 Adaptive attack | **COMPLETED (sim)** | Detector-only; no LLM in loop |
| EXP-017/018 NotInject | **PARTIAL** | Held-out F1=0.41; dataset absent on disk |
| Phase 7–8 harmonized | **NOT ON DISK** | Scripts exist; `results/phase8/` missing from clone |

**Missing for Q1:**
- 500+ test samples × 3 target models with real judge
- Multi-seed LLM evaluation (API cost ~$50–200)
- Cross-dataset generalization (NotInject, BIPIA)
- Agent tool injection at scale

---

## 4. Dataset Weaknesses

### benchmark_q1 (NEW — 15,053 samples)

| Category | Count | Issue |
|---|---:|---|
| direct_prompt_injection | 263 | Small |
| indirect_prompt_injection | ~1,037* | *after rebuild with promote_indirect |
| rag_injection | ~1,927 | Adequate |
| agent_tool_injection | 28 | **Critically small** |
| jailbreak | 6,104 | Dominated by BeaverTails safety relabeling |
| benign_tasks | 3,194 | 25.5% — acceptable |
| adaptive_attacks | 2,500 | Template-generated, not human-validated |

**Unavailable sources (adapters marked):** NotInject, BIPIA, InjecAgent, TensorTrust, PIArena

**Contamination:** Group-level split assignment; 0 cross-split overlap detected.

**Balance concern:** `jailbreak` category inflated by mapping `safety` → `jailbreak` (BeaverTails harmful prompts are safety violations, not jailbreaks).

---

## 5. Baseline Weaknesses

| Method | Implementation | Q1 adequacy |
|---|---|---|
| No Defense | Pass-through | OK |
| Regex Detector | ADAPTI-GUARD detector | OK (internal) |
| TF-IDF ML | sklearn on train split | OK |
| Llama Guard | **Regex fallback** | NOT ACCEPTABLE for publication |
| Prompt Guard | **Regex fallback** | NOT ACCEPTABLE |
| NeMo Guard | **Regex fallback** | NOT ACCEPTABLE |
| ADAPTI-GUARD | Full pipeline | OK |

**Reviewer comment:** "Comparing against regex-labeled 'Llama Guard' is misleading and would warrant desk rejection."

---

## 6. Statistical Weaknesses

**Implemented:** `bootstrap_ci`, `mcnemar_test`, `wilcoxon_signed_rank` in `statistics.py`

**Not yet applied to real results:**
- No paired tests on real LLM ASR
- EXP-005 seeds produce identical ASR (deterministic harmonized runner — seed parameter unused)
- No effect size (Cohen's d) reported
- No multiple-comparison correction across 7 baselines
- No power analysis

---

## 7. Reproducibility Weaknesses

**Strengths (post-upgrade):**
- `ExperimentRunContext` with config, git commit, dataset hashes
- `experiments/registry.csv` tracking
- `configs/models.yaml`, `configs/datasets.yaml`
- Per-experiment README + config.json
- 74 tests passing

**Weaknesses:**
- `results/` gitignored — no committed primary results
- API key required — experiments BLOCKED without `.env`
- benchmark_q1 builder depends on benchmark_v2 copy (provenance chain unclear)
- 15 detector `.v*` backup files pollute tree
- No Docker/conda lock for full ML baseline stack

---

## 8. Claim Overstatement Risks

| Claim (README/docs) | Evidence | Risk |
|---|---|---|
| "Adaptive defense against evolving attacks" | EXP-008 sim only | **HIGH** |
| "Utility-aware" | Harmonized utility metric on 8 benign templates | **HIGH** |
| "Q1 harmonized evaluation" | Phase 8 results not on disk | **CRITICAL** |
| "Detector generalizes" | NotInject F1=0.41 held-out | **HIGH** |
| "Multi-seed statistical validation" | Seeds identical in sim | **HIGH** |
| "Publication-grade benchmark" | 28 agent samples, no BIPIA/NotInject | **MEDIUM** |

---

## Hostile Reviewer Summary

> "The authors present a well-engineered rule-based defense pipeline with a thoughtful harmonized evaluation protocol. However, the primary empirical claims rest on circular string-matching ASR or have not been executed against real LLMs. The 'Bayesian' adaptation is a misnomer for threshold counters. Baseline comparisons against regex-labeled industry guards are scientifically invalid. The benchmark lacks agent-scale coverage and key public datasets. I recommend **major revision** requiring: (1) real LLM+judge evaluation on ≥500 test samples across ≥2 models, (2) genuine SOTA baseline execution, (3) honest limitation of adaptation to counter-based policy, (4) NotInject/BIPIA generalization, and (5) human judge validation subset."

---

## Priority Fix List (ordered)

1. Execute EXP-002 with `OPENROUTER_API_KEY` — 500 samples × 3 models
2. Install and run real Llama Guard / Prompt Guard baselines
3. Acquire NotInject + BIPIA datasets
4. Expand agent_tool_injection to ≥200 samples
5. Wire harmonized runner to real LLM judge (deprecate `attack_outcome.py` for publication)
6. Human evaluation on 100 samples (protocol in `docs/HUMAN_EVALUATION.md`)
7. Commit `results/summaries/` with aggregate metrics only
