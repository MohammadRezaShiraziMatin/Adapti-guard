# ADAPTI-GUARD — Research Problem Reconstruction

**Phase 1 Audit | Date:** 2026-09-02  
**Evidence basis:** Repository inspection only. No fabricated results.

---

## 1. Concrete Security Problem

LLM-based applications and agents that consume **untrusted external text** (user prompts, retrieved documents, tool outputs) are vulnerable to **prompt injection**: adversarial content that subverts system instructions, exfiltrates secrets, or triggers unsafe tool use.

The operational problem is not merely "detect malicious strings" but **maintaining task utility under mixed workloads** while an adversary may adapt attack families over time. Static always-on blocking reduces attack success but can destroy legitimate utility; always-off defense preserves utility but fails under injection.

---

## 2. Existing Limitations (Why Current Defenses Are Insufficient)

| Limitation | Evidence from literature / repo |
|------------|--------------------------------|
| Static thresholds ignore workload composition | Fixed L0–L3 modes exist in code but not validated on real LLMs |
| Guard models evaluated in isolation from utility | Most benchmarks report ASR without benign task degradation |
| Agent/tool injection underrepresented in evaluation | benchmark_q1: 28 agent_tool samples; no tool execution in eval harness |
| Adaptive attackers evolve faster than static defenses | EXP-008 simulation: 0% block rate (detector bypass) — **simulation only** |
| Detector generalization weak | EXP-018 held-out F1 = **0.4096** on NotInject (when data available) |
| SOTA baselines not actually compared | llama_guard/prompt_guard/nemo are regex fallbacks to same detector |

---

## 3. Research Gap

> **Existing runtime defenses optimize for detection accuracy or block rate on attack-only benchmarks, but do not provide a harmonized, utility-aware evaluation of adaptive escalation policies under mixed attack/benign agent workloads with independent outcome judging.**

Specific gaps:

1. **Utility-aware adaptation:** Few systems jointly measure ASR and benign task success under the same episode schedule.
2. **Policy-level adaptation vs detection-only:** ADAPTI-GUARD adapts defense *level* (L0–L3), not the detector — this distinction is under-theorized in the manuscript.
3. **Agent/tool security:** OWASP LLM01/LLM07 cover injection and insecure plugin design; this repo does not yet evaluate tool invocation behavior (AgentDojo-style).
4. **Valid multi-model evidence:** No publication-valid real-LLM runs exist in this repository.

---

## 4. What ADAPTI-GUARD Actually Proposes

**Implemented mechanism (verified in code):**

1. **Regex/heuristic detector** → scalar `injection_probability` (misnamed; not calibrated probability)
2. **Linear risk engine** → LOW / MEDIUM / HIGH (with family-specific floors)
3. **Policy engine** → maps (risk, defense_level) → action A0–A3
4. **Counter-based policy update** → escalate/de-escalate L after sustained pressure (threshold=2)
5. **Cost-gated de-escalation** → de-escalate only when `defense_cost ≥ 0.50` (structurally: only after BLOCK)

**NOT implemented despite naming:**
- Bayesian inference
- RL / reward-driven control (reward computed but not used for decisions)
- Defense-aware adaptive attacker during evaluation (frozen stream replay)
- Real agent/tool sandbox

---

## 5. Scientific Mechanism — Why It *Should* Work (Theory)

**Hypothesis chain:**

> Under mixed attack/benign workloads, a discrete defense level S_t ∈ {0,1,2,3} that escalates after repeated attack successes and de-escalates after sustained benign success should reduce unnecessary high-cost interventions (BLOCK, TOOL_RESTRICTION) compared to fixed maximum defense, while maintaining lower ASR than no defense — **provided** the detector/risk pipeline correctly identifies attack episodes.

**Critical dependency:** The entire adaptive mechanism is downstream of detector quality. With held-out F1 ≈ 0.41, the mechanism's security benefit is **unproven** on real LLM behavior.

**Known structural limitation (from code):** `DefensePolicyEngine` caps LOW-risk episodes at A1, while cost-gate de-escalation requires cost ≥ 0.50 (BLOCK only). On benign traffic (typically LOW risk), de-escalation may never activate — undermining "utility-aware de-escalation" claims.

---

## 6. Evaluation Requirement — What Would Prove It Works

Minimum proof bundle:

| Requirement | Status |
|-------------|--------|
| Real target LLM responses (not regex simulation) | **BLOCKED** |
| Independent blind LLM judge for ASR | Implemented, **not executed successfully** |
| Mixed attack/benign schedule (≥500 episodes) | Protocol exists; **not run at scale** |
| Comparison vs no-defense + fixed-level + real guard baseline | **NOT_RUN** |
| Per-category stratified ASR | **NOT_RUN** |
| Utility metric on benign tasks (task success, not "not blocked") | **Weak** — current legitimate success = "action ≠ A3" |
| Statistical significance (McNemar, CI, Holm) | Code exists; **no valid input data** |
| Multi-model generalization (≥3 families) | **BLOCKED** |

---

## 7. Formal Problem Statement

> **Existing runtime prompt-injection defenses are typically evaluated on attack-only or detection-only metrics and do not jointly optimize security and benign utility under evolving, category-diverse injection attacks in LLM serving settings. The literature lacks harmonized, judge-based evidence that counter-based defense-level adaptation improves the security–utility–cost trade-off compared to fixed policies and strong guard baselines across model families. ADAPTI-GUARD proposes a modular pipeline (detection → linear risk → discrete policy → counter-based level adaptation with cost-gated de-escalation) evaluated under a mixed workload protocol. We hypothesize that full adaptation (PolicyMode.FULL_ADAPTIVE) achieves lower ASR than B0 and better utility than fixed L3 under conditions of mixed benign/attack traffic, with statistically significant paired differences on real LLM outputs.**

---

## 8. Problem Statement Validity Assessment

| Element | Verdict |
|---------|---------|
| Problem is real | **Strong** — aligned with OWASP LLM01, agent security literature |
| Gap is accurately scoped | **Moderate** — gap exists but is incremental, not revolutionary |
| Proposed mechanism matches code | **Strong** — after removing Bayesian/agent overclaims |
| Evaluation can test hypothesis | **Conditional** — requires real-LLM + fixed utility metric + real baselines |
| Current evidence supports hypothesis | **Unsupported** — zero valid real-LLM experiments |

**Recommendation:** Narrow the paper from "adaptive defense against evolving attacks in LLM agents" to **"utility-aware harmonized evaluation of counter-based defense-level adaptation for prompt injection under mixed workloads"** unless agent/tool experiments are added.
