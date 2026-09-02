# ADAPTI-GUARD — Falsifiable Hypotheses

**Phase 1 Audit | Date:** 2026-09-02

Every hypothesis maps to a specific experiment and falsification criterion.  
**No hypothesis is currently supported by publication-valid evidence.**

---

## H1 — Security Improvement vs No Defense

**Statement:** ADAPTI-GUARD (B6) significantly reduces attack success rate compared to no defense (B0) on real LLM outputs.

| Field | Value |
|-------|-------|
| **IV** | Defense: {B0, B6} |
| **DV** | ASR (judge-labeled) |
| **Dataset** | attack_dataset test holdout, n≥500, seed 42 |
| **Models** | model_a (primary), model_b, model_c |
| **Experiment** | EXP-004 |
| **Metric** | ASR = #(attack_success) / #(attack episodes) |
| **Test** | McNemar on paired episode outcomes; bootstrap 95% CI |
| **Falsification** | p ≥ 0.05 OR ASR(B6) ≥ ASR(B0) |
| **Status** | **BLOCKED — REAL LLM EVIDENCE REQUIRED** |

---

## H2 — Adaptive vs Fixed Trade-off

**Statement:** Full adaptive policy achieves a better security–utility trade-off than any single fixed level L0–L3.

| Field | Value |
|-------|-------|
| **IV** | PolicyMode: {fixed_l0…l3, full_adaptive} |
| **DV** | ASR, Utility, Reward = 0.5·S + 0.4·U − 0.1·C |
| **Dataset** | Mixed W1 schedule, n≥500 |
| **Models** | model_a |
| **Experiment** | EXP-003 harmonized + real LLM |
| **Test** | Pareto dominance; Wilcoxon on reward vs best fixed |
| **Falsification** | Some fixed L* Pareto-dominates full_adaptive |
| **Status** | **SIMULATION-ONLY** — EXP-005 n=20, 1 seed; not valid |

---

## H3 — Risk Engine Contribution

**Statement:** The linear RiskEngine improves ASR vs using raw detector score alone.

| Field | Value |
|-------|-------|
| **IV** | With vs without RiskEngine (ablation B) |
| **DV** | ASR |
| **Experiment** | EXP-006 variant B_no_risk_engine |
| **Falsification** | Identical ASR to full system |
| **Status** | **SIMULATION-ONLY** — EXP-006: B_no_risk ASR=0.1333 = A_full ASR=0.1333 → **H3 falsified in simulation** |

---

## H4 — Cost Gate Reduces Over-Blocking

**Statement:** Cost-gated de-escalation reduces FPR vs ablation without cost gate, without increasing ASR.

| Field | Value |
|-------|-------|
| **IV** | PolicyMode: {full_adaptive, no_cost_gate} |
| **DV** | FPR, ASR, de-escalation count |
| **Experiment** | EXP-006 A vs C |
| **Falsification** | no_cost_gate has lower ASR AND lower FPR |
| **Status** | **SIMULATION-ONLY** — EXP-006: C_no_cost_gate ASR=0.333 > A_full 0.133 → cost gate **helps ASR in sim** but hurts utility path; needs real LLM |

---

## H5 — Multi-Model Generalization

**Statement:** ASR(B6) improvement over B0 is consistent across ≥3 model families (CV < 0.15).

| Field | Value |
|-------|-------|
| **IV** | Target model |
| **DV** | ΔASR = ASR(B0) − ASR(B6) |
| **Experiment** | EXP-004 matrix |
| **Falsification** | Any family shows ΔASR ≤ 0 with significance |
| **Status** | **BLOCKED — REAL LLM EVIDENCE REQUIRED** |

---

## H6 — Detector Generalization (Negative Result)

**Statement:** Regex detector generalizes to held-out prompt injection data with F1 ≥ 0.70.

| Field | Value |
|-------|-------|
| **IV** | Data split (smoke vs held-out) |
| **DV** | F1, FPR, FNR |
| **Experiment** | EXP-017 (smoke), EXP-018 (held-out) |
| **Falsification** | F1 < 0.70 on held-out |
| **Status** | **FALSIFIED** — EXP-018 F1=**0.4096**, Recall=0.3542, FNR=0.6458 |

---

## H7 — Escalation Mechanism Security Benefit

**Statement:** Escalation-only adaptation (without de-escalation) increases defense rate under sustained attack without collapsing benign utility below 0.90.

| Field | Value |
|-------|-------|
| **IV** | PolicyMode: {full_adaptive, de_escalation_only, escalation_only} |
| **DV** | ASR, Utility, defense_level distribution |
| **Experiment** | EXP-006 A vs F |
| **Falsification** | de_escalation_only beats full_adaptive on ASR |
| **Status** | **SIMULATION-ONLY** — EXP-006: F_no_escalation ASR=0.067 **better than** A_full 0.133 → **challenges escalation narrative**

---

## Hypotheses That Must Be Removed

| Hypothesis | Reason |
|------------|--------|
| "Bayesian risk improves adaptation" | No Bayesian code |
| "Adaptive attacker evades defense over rounds" | EXP-008: 0% block in sim; attacker not adaptive at replay |
| "Agent tool attacks mitigated" | No tool eval |
| "Detector achieves SOTA F1" | Held-out F1 = 0.41 |

---

## Testing Priority (Phase 2)

1. H1 (real LLM) — **mandatory**
2. H2, H5 (real LLM) — **mandatory**
3. H3, H4, H7 (ablation real LLM) — **mandatory**
4. H6 — report honestly as limitation
