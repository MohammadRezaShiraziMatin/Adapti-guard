# ADAPTI-GUARD — Hostile Novelty Audit

**Phase 1 Audit | Date:** 2026-09-02  
**Stance:** Assume rejection unless novelty is precise and evidenced.

---

## 1. What Is Genuinely Novel?

| Element | Novelty assessment |
|---------|-------------------|
| **Harmonized security+utility+ cost metrics on shared episode population** | Incremental but **defensible** if real-LLM evidence produced — closest to methodological novelty |
| **Explicit cost-gated de-escalation tied to action cost table** | Minor — idea exists in IDS/adaptive firewalls; implementation is a single threshold |
| **Provenance-gated eval modes separating simulation from real LLM** | Good engineering practice; not research novelty |
| **Frozen attack stream + policy replay** | Standard in RL/security eval; not novel |

**Verdict:** No single component is fundamentally new. The **combination** of mixed-workload harmonized eval + discrete level adaptation + blind LLM judge **may** be publishable as a **systems/evaluation paper** if experiments are strong — not as a breakthrough defense paper.

---

## 2. What Is Incremental?

| Component | Prior art |
|-----------|-----------|
| Regex/heuristic injection detection | Rebuff, LLM-Guard, Garak probes, hundreds of OSS filters |
| Linear risk score → discrete action | NeMo Guardrails rails, Azure Prompt Shields |
| L0–L3 escalation | WAF sensitivity levels, Guardrails colang policies |
| LLM-as-judge for safety | MT-Bench, LLM eval literature, HarmBench judges |
| Dataset aggregation | AgentDojo, BIPIA, InjecAgent composites |
| TF-IDF baseline | Classical ML baseline — exists in repo but unused in main eval |

---

## 3. What Already Exists (Direct Overlap)

| System | Overlap with ADAPTI-GUARD |
|--------|---------------------------|
| **LLM-Guard / Prompt Guard** | Input scanning + block — ADAPTI-GUARD detector is regex cousin |
| **NeMo Guardrails** | Policy rails + action types — similar L-level concept |
| **Rebuff** | Heuristic + model detection pipeline |
| **Instruction hierarchy (OpenAI/etc.)** | System > user — not implemented here |
| **StruQ / SecAlign** | Training-time defense — out of scope but stronger scientifically |
| **AgentDojo** | Agent + tool injection benchmark — **strict superset** of agent claims |
| **BIPIA / InjecAgent / PIArena** | Indirect/agent injection benchmarks — sources marked UNAVAILABLE |
| **Garak** | Probe taxonomy including leakage — not integrated |
| **Adaptive attacks (Crescendo, PAIR)** | LLM-based mutation — ADAPTI-GUARD has 12 static strings |

---

## 4. Misleading Terminology — Must Remove

| Term | Reality in code | Action |
|------|-----------------|--------|
| **Bayesian** | Zero priors/posteriors; linear sum | **Remove everywhere** including EXP-005 label `C_bayesian_risk` |
| **injection_probability** | Unnormalized regex score clipped to [0,1] | Rename to `detection_score` in paper |
| **Adaptive attacker** | Round-robin over 12 strings | Call "template rotator" or integrate real adaptive attack |
| **Evolving attacks** | Frozen stream replay | "Diverse static attack corpus" |
| **Agent defense** | No tool loop | Remove from title until AgentDojo |
| **SOTA baseline comparison** | Regex pretending to be Llama Guard | **Remove** or wire real models |
| **Publication-ready results** | 0 valid real-LLM runs | **Remove** |

---

## 5. If Adaptation Is the Real Novelty — What Makes It Distinct?

**Candidate distinct claim (must be proven):**

> "Counter-based defense-level hysteresis, coupled with a LOW-risk utility cap (max A1 on benign) and BLOCK-cost de-escalation gate, yields a better empirically measured security–utility–cost Pareto frontier than fixed levels under mixed workloads."

**What would make this scientifically distinct:**
- Proof that **level adaptation** matters **after** controlling for detector (not just threshold tuning)
- Demonstration that cost gate reduces FPR vs always-L3 **on real tasks**
- Evidence escalation helps under **distribution shift** (EXP-009 phases) — not yet run

**Current simulation ablation contradicts this:** F_no_escalation beats full system on ASR in EXP-006 sim.

---

## 6. Comparison Matrix (Conceptual)

| Feature | ADAPTI-GUARD | LLM-Guard | NeMo | AgentDojo eval |
|---------|--------------|-----------|------|----------------|
| Input regex/heuristic | Yes | Yes | Partial | N/A |
| Learned guard model | No | Yes | Yes | Uses defenses |
| Discrete policy levels | Yes L0–L3 | No | Yes rails | Varies |
| Adaptation over time | Counter-based | No | Limited | N/A |
| Utility metric in eval | Yes (weak) | Rare | Rare | Yes (task success) |
| Tool execution eval | **No** | No | Partial | **Yes** |
| Real LLM results in repo | **0** | Published | Published | Published |

---

## 7. Novelty Verdict

| Category | Score (0–10) | Notes |
|----------|-------------|-------|
| Algorithmic novelty | **2** | Classical hysteresis + regex |
| Evaluation methodology | **6** | Harmonized mixed workload + judge — if executed |
| Dataset novelty | **4** | Aggregation |
| Agent security novelty | **0** | Not implemented |
| Overall novelty for Q1 defense track | **3–4** | Evaluation/systems angle stronger than algorithm |

**Recommended positioning:** Top-tier **workshop / mid-tier journal** on LLM security evaluation unless real experiments show large, significant gains vs strong baselines on agents.

---

## 8. Claims That Must Be Removed Before Submission

1. Bayesian risk adaptation  
2. State-of-the-art defense performance  
3. Validated agent/tool security  
4. Evolving adaptive adversary co-evolution  
5. Strong detector generalization  
6. Multi-model validation (until EXP-004 completes)  
7. Any ASR number from simulation or INVALID EXP-002  
