# ADAPTI-GUARD Manuscript (Draft — Evidence-Gated)

> **WARNING:** This draft contains only claims with evidence status ≥ PARTIAL.  
> Sections marked [BLOCKED] require EXP-002/003 execution before writing.

---

## Abstract [BLOCKED — awaiting real LLM results]

ADAPTI-GUARD is an adaptive defense framework for LLM-based agents that combines regex-based prompt injection detection, linear risk scoring, and discrete policy escalation (L0–L3) with counter-based adaptation. We introduce benchmark_q1, a 15,053-sample evaluation corpus spanning seven attack categories. [Results pending: ASR, utility, and baseline comparisons on GPT-4o-mini, Llama-3.1-8B, and Qwen2.5-7B with independent LLM judge.]

---

## 1. Introduction

Large language models deployed in agentic settings face evolving prompt injection attacks spanning direct injection, RAG poisoning, and tool manipulation. Static defenses fail under distribution shift and adaptive adversaries.

**Contributions (intended):**
1. Harmonized evaluation protocol with utility-aware scheduling (75/25 attack/benign)
2. Counter-based adaptive policy escalation preserving benign utility
3. benchmark_q1 dataset with 7 attack categories and 15K+ samples
4. Real LLM evaluation pipeline with independent judge [BLOCKED]

---

## 2. Related Work

- **Prompt injection detection:** Rebuff, LLM-Guard, Prompt Guard
- **Agent security:** AgentDojo, InjecAgent, BIPIA
- **Adaptive defense:** Limited prior work on utility-aware escalation
- **Gap:** No unified benchmark combining RAG + agent + jailbreak + benign + adaptive variants

---

## 3. Threat Model

**Attacker capabilities:**
- Query access to LLM agent
- Injection via user prompt, retrieved context, or tool output
- Adaptive evolution across attack families (4 families in `AdaptiveAttacker`)

**Defender capabilities:**
- Pre-inference detection and sanitization
- Discrete defense actions A0–A3 (none, warn, sanitize, block)
- Policy level L0–L3 with counter-based adaptation

**Out of scope:** Training-time attacks, model weight manipulation, side-channel attacks.

---

## 4. Method

### 4.1 Detection
`PromptInjectionDetector` — regex/heuristic patterns with injection probability score.

### 4.2 Risk Assessment
`RiskEngine` — weighted linear combination of detection score and metadata.

### 4.3 Policy Engine
`DefensePolicyEngine` maps (risk_level, defense_level) → action.

### 4.4 Adaptation
`PolicyUpdateEngine` — counter-based escalation after `attack_threshold=2` consecutive attack successes; de-escalation after `legitimate_threshold=2` legitimate successes.

> **Note:** This is NOT Bayesian inference. Manuscript must use "counter-based adaptive policy."

### 4.5 Defense Actions
`DefenseActionLayer` executes A0 (pass), A1 (warn), A2 (sanitize), A3 (block).

---

## 5. Experiments

### 5.1 Dataset: benchmark_q1
- 15,053 samples, 70/15/15 split
- 7 categories, 21.2% benign
- Sources: BeaverTails, RAGTruth, JailbreakBench, AgentDojo, prompt-injections, Do Not Answer, adaptive templates

### 5.2 Models [BLOCKED]
| Model | Config key |
|---|---|
| GPT-4o-mini | target_3 |
| Llama-3.1-8B | target_1 |
| Qwen2.5-7B | target_2 |
| Judge: Gemma-2-9B | judge |

### 5.3 Baselines [BLOCKED]
No defense, Regex, TF-IDF ML, Llama Guard, Prompt Guard, NeMo Guard, ADAPTI-GUARD

### 5.4 Metrics
ASR, Defense Rate, Utility, FPR, Latency, Token Cost

---

## 6. Results [BLOCKED]

[Tables and figures from EXP-002, EXP-003 pending API execution]

---

## 7. Ablation [PARTIAL — simulation only]

EXP-005 shows ≤2.7% ASR difference across adaptation modes on heuristic evaluation. **Not publication-ready.**

---

## 8. Limitations

1. Detector is regex-based; poor NotInject generalization (F1=0.41)
2. Agent coverage minimal (28 tool injection samples)
3. NotInject, BIPIA, InjecAgent, TensorTrust, PIArena unavailable
4. Industry baselines use regex fallback without real model weights
5. Adaptation is counter-based, not learned
6. No human judge validation completed

---

## 9. Conclusion [BLOCKED]

[Write after EXP-002/003 complete with honest scope of validated claims.]
