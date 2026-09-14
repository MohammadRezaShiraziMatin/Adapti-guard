# ADAPTI-GUARD — Research Questions

**Phase 1 Audit | Date:** 2026-09-02

Five RQs selected based on **what the implementation can actually test** after removing agent/Bayesian overclaims.

---

## RQ Table

| RQ | Hypothesis | IV | DV | Dataset | Models | Baselines | Experiment | Statistical Test |
|----|------------|----|----|---------|--------|-----------|------------|------------------|
| **RQ1** | ADAPTI-GUARD (B6) reduces ASR vs no defense (B0) on real LLM outputs | Defense method | ASR, Defense Rate | attack_dataset + benchmark_q1 benign (n≥500) | model_a, model_b, model_c + 2 local | B0, B6 | EXP-004 | McNemar paired; bootstrap 95% CI on ASR diff |
| **RQ2** | Adaptive policy beats best fixed level on security–utility trade-off | Policy type (adaptive vs fixed L*) | ASR, Utility, Reward | Same + W1 schedule | model_a (primary) | B2_L0–L3, B6 | EXP-003 + Pareto | Wilcoxon on reward; McNemar on ASR vs best fixed |
| **RQ3** | Risk engine, cost gate, and escalation contribute measurably | Ablation variant | ASR, Utility, Cost | attack_dataset (n≥300) | model_a | A–F ablations | EXP-006 | McNemar vs full; Holm across variants |
| **RQ4** | Effect generalizes across model families | Target LLM | ASR, Utility | Stratified test split | ≥3 API + ≥2 local | B0, B6 | EXP-004 matrix | Per-model CI; Cochran Q or separate McNemar per model |
| **RQ5** | Adaptation reduces unnecessary high-cost defense vs fixed L3 | Policy type | Cost, FPR, Latency | Mixed workload W1 | model_a | B2_L3, B6 | EXP-003 + efficiency | Wilcoxon on cost & latency; FPR chi-square or McNemar |

---

## RQ1 — Security vs No Defense

**Question:** Does ADAPTI-GUARD reduce attack success rate compared to an undefended LLM?

**Hypothesis H1:** ASR(B6) < ASR(B0) with paired McNemar p < 0.05.

**Falsification:** If ASR(B6) ≥ ASR(B0) or difference not significant at n≥500.

**Status:** `BLOCKED — REAL LLM EVIDENCE REQUIRED`

---

## RQ2 — Adaptive vs Static

**Question:** Does counter-based level adaptation outperform the best fixed defense level on combined security and utility?

**Hypothesis H2:** B6 dominates at least one fixed level on Pareto frontier (lower ASR at equal utility, or higher utility at equal ASR).

**Falsification:** Fixed L2 or L3 Pareto-dominates B6 on real LLM eval.

**Status:** `SIMULATION-ONLY — NOT PUBLICATION EVIDENCE` (EXP-005: 20 episodes, 1 seed; full adaptive ASR=0.1333)

---

## RQ3 — Component Contribution

**Question:** Which architectural components drive security/utility outcomes?

**Hypothesis H3:** Removing cost gate (C) or escalation (F) significantly changes ASR or utility vs full system (A).

**Falsification:** All ablations statistically indistinguishable from full system.

**Status:** `SIMULATION-ONLY` — EXP-006 shows F_no_escalation (ASR 0.067) **beats** A_full (ASR 0.133) in simulation; B_no_risk identical to A — **contradicts risk-engine contribution claim**

---

## RQ4 — Model Generalization

**Question:** Is defense effectiveness stable across LLM families?

**Hypothesis H4:** ASR(B6) coefficient of variation across models < 0.15.

**Falsification:** Any model shows ASR(B6) > ASR(B0) or category-specific collapse.

**Status:** `BLOCKED — REAL LLM EVIDENCE REQUIRED`

---

## RQ5 — Cost / Over-Defense

**Question:** Does adaptation avoid unnecessary blocking relative to always-on maximum defense?

**Hypothesis H5:** FPR(B6) < FPR(B2_L3) and Cost(B6) < Cost(B2_L3) with utility(B6) ≥ utility(B2_L3).

**Falsification:** B6 blocks more benign tasks than L3 without ASR gain.

**Status:** `BLOCKED` — requires real latency/token measurement (`efficiency_report.md` template only)

---

## RQs Removed or Deferred

| Removed RQ | Reason |
|------------|--------|
| "Beats Llama Guard SOTA" | Baselines are regex fallbacks — invalid until real guard API wired |
| "Robust to evolving adaptive attacker" | Attacker not adaptive at eval time |
| "Agent tool security" | No tool execution in harness |
| "Bayesian risk improves detection" | No Bayesian mechanism exists |

---

## Primary vs Secondary

**Primary (paper core):** RQ1, RQ2, RQ5  
**Secondary:** RQ3, RQ4  
**Deferred to future work:** Agent/tool RQ, defense-aware adaptive attacker RQ
