# ADAPTI-GUARD — Phase 1 Gap Analysis

**Phase 1 Audit | Date:** 2026-09-02

---

## 1. Component Status Table

| Component | Exists? | Implemented? | Tested? | Real LLM? | Publication Valid? | Evidence |
|-----------|---------|--------------|---------|-----------|-------------------|----------|
| Threat model (narrative) | Yes | Partial | No | — | No | `docs/MANUSCRIPT_DRAFT.md` §3; rebuilt in `THREAT_MODEL.md` |
| Threat model (formal) | Yes | Partial | No | — | No | Phase 1 deliverable |
| Research questions | Yes | Yes | No | — | N/A | `RESEARCH_QUESTIONS.md` |
| Hypotheses | Yes | Yes | Partial | No | No | H6 falsified; H3/H7 contradicted in sim |
| Contributions (claimed) | Yes | Mixed | No | No | **1/8 supported** | `CONTRIBUTIONS.md` |
| benchmark_q1 dataset | Yes | Yes | Verified | — | **Yes** | 15,053, hashes match |
| attack_dataset.json | Yes | Yes | Built | — | Partial | 528/700+ target; 2 category gaps |
| Attack taxonomy (7 cat) | Yes | Partial | No | — | No | tool=28, leakage=0 |
| PromptInjectionDetector | Yes | Yes | Yes | N/A | Detector-only | F1=0.41 held-out |
| RiskEngine | Yes | Yes | Unit tests | No | No | Linear sum, not Bayesian |
| DefensePolicyEngine | Yes | Yes | Unit tests | No | No | |
| PolicyUpdateEngine | Yes | Yes | Sim | No | No | Counter hysteresis |
| FeedbackEngine / cost gate | Yes | Yes | Sim | No | No | Single threshold 0.50 |
| AdaptiveDefense (B6) | Yes | Yes | Unit | **No** | No | |
| AdaptiveAttacker | Yes | Yes | Sim | No | No | 12 static strings |
| Evaluation harness (real LLM) | Yes | Yes | Smoke | **INVALID** | No | EXP-002 401×5 |
| LLM judge (blind) | Yes | Yes | Unit tests | **No success** | No | API blocked |
| Baselines B0–B4 | Yes | Yes | Sim | No | No | |
| Baseline B5 (SOTA) | Yes | **Fake** | No | No | **No** | Regex fallback |
| Statistical analysis | Yes | Yes | No data | No | No | Code only |
| Ablation EXP-006 | Yes | Yes | Sim 20 ep | No | No | Unfavorable to full system |
| Long-term EXP-009 | Config | Partial | No | No | No | Empty dir |
| Failure analysis | Protocol | No data | No | No | No | 0 cases |
| Agent/tool eval | **No** | No | No | No | No | tool_sensitive=False |
| Local LLM (Ollama) | Config | Yes | No | No | No | Ollama down |
| API integration | Yes | Yes | **Failed** | **INVALID** | No | Bad API key |
| Reproducibility package | Partial | Partial | Partial | No | Partial | Hashes yes; no Docker |
| Manuscript | Yes | Draft | — | — | Blocked | All results [BLOCKED] |
| LaTeX | **No** | — | — | — | — | 0 .tex files |
| Figures (publication) | Stubs | No | No | No | No | README only |

---

## 2. Implementation vs Manuscript Contradictions

| Manuscript / doc claim | Code reality | Severity |
|------------------------|--------------|----------|
| Bayesian adaptation | No Bayesian code | **Critical** |
| Agent/tool security | No tool execution | **Critical** |
| Evolving adaptive attacker | Frozen stream replay | **Major** |
| SOTA baseline comparison | Same regex detector | **Critical** |
| Utility preserved | Utility = not blocked | **Major** |
| Multi-model validated | 0 real runs | **Critical** |
| EXP-002 success | INVALID reclassified | **Critical** (stale artifacts remain) |
| ASR ≤0.027 (EXP-005) | Actual sim 0.1333 | **Major** misreport |

---

## 3. Formal Adaptive Defense Summary (from code)

**State:** S_t ∈ {0,1,2,3} (defense level)

**Risk:** R_t = RiskEngine(detect(x_t), metadata) → {LOW, MED, HIGH}

**Action:** A_t = PolicyEngine(R_t, S_t) → {A0,A1,A2,A3}

**Feedback signal:** g_t ∈ {INCREASE, REDUCE, MAINTAIN} from FeedbackEngine(outcome)

**Transition:** S_{t+1} = S_t + sign(pressure) if pressure ≥ 2 else S_t

**Objective (descriptive, not optimized):** 0.5·security + 0.4·utility − 0.1·cost

See `NOVELTY_AUDIT.md` and `THREAT_MODEL.md` for full detail.

---

## 4. Cost Gate Audit Summary

| Question | Answer |
|----------|--------|
| What is "cost"? | Fixed table: A0=0, A1=0.1, A2=0.25, A3=0.5 |
| Measured from system? | **No** — not token/latency/$ |
| Gate rule | De-escalate only if cost ≥ 0.50 (= BLOCK only) |
| Scientifically meaningful? | **Marginally** — encodes "de-escalate after blocking" not resource budget |
| Recommendation | Rename to "post-block de-escalation gate"; add real token/$ cost in Phase 2 |

---

## 5. Agent Security Claims Audit

| Claim | Supported? | Required for support |
|-------|------------|---------------------|
| Tool abuse mitigation | **No** | AgentDojo + tool_sensitive=True + call traces |
| Agent in title | **No** | Remove or add agent eval |
| A2 TOOL_RESTRICTION works | **No** | Tool planner integration |
| System prompt leakage defense | **No** | Leakage dataset + metric |

---

## 6. Dataset Gap Summary

| Gap | Shortfall | Action |
|-----|-----------|--------|
| system_prompt_leakage | 100 samples | Garak import |
| tool_abuse_attacks | 72 samples | AgentDojo import |
| Total attack_dataset | 528 vs 700–1000 | Rebuild after import |
| Valid LLM eval count | **0** | Run EXP-004 |
| NotInject reproducibility | dataset/ missing | Restore or remove EXP-018 claim |

---

## 7. Phase 1 Scorecard (0–10)

| Dimension | Score | Rationale |
|-----------|------:|-----------|
| Research Problem | **6.0** | Real problem; over-scoped to agents |
| Threat Model | **4.5** | Narrative exists; formal gaps; agent mismatch |
| Research Questions | **6.5** | RQs ok after narrowing; untested |
| Hypotheses | **5.0** | Falsifiable; several already falsified/contradicted in sim |
| Novelty | **3.5** | Incremental; evaluation angle best path |
| Contributions | **3.0** | Mostly unsupported |
| Attack Taxonomy | **4.0** | 5/7 categories viable; imbalance |
| Experimental Design | **5.5** | Good blueprint; zero valid execution |
| Statistical Design | **7.0** | Pre-registered tools; no data |
| Reproducibility | **6.0** | Hashes, provenance; API blocked; stale artifacts |

### **Overall Research Foundation Score: 5.1 / 10**

**Classification:** **Weak (5–6.9)** — promising infrastructure, **not publication-ready**.

Q1-ready requires ≥8.0 on experimental execution alone, which is currently **~1.0**.

---

## 8. Phase 2 Dependency Graph

```
Fix API/Ollama
    → Preflight PASS
        → EXP-004 smoke (n=5)
            → EXP-004 full (n=500)
                → statistical_analysis
                    → EXP-003 baselines
                        → EXP-006 ablation (real)
                            → EXP-009 long-term
                                → failure analysis
                                    → HUMAN-EVAL
                                        → manuscript numbers
```

Parallel track: Dataset gaps → AgentDojo → EXP-AGENT (only if agent claims retained)

---

## 9. Do Not Start Phase 2 Until

1. API key valid OR Ollama running with pulled models
2. B5 baseline decision (real guard API chosen)
3. Utility metric upgraded (judge task-success)
4. Test set frozen with hash recorded
5. Stale EXP-002 artifacts quarantined

Phase 1 complete. **Do not modify core implementation** until Phase 2 plan approved.
