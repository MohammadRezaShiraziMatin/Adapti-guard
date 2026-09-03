# ADAPTI-GUARD Manuscript (Draft — Evidence-Gated)

> **WARNING:** This draft contains only claims with evidence status ≥ PARTIAL.  
> Sections marked [BLOCKED] require EXP-002/003 execution before writing.

---

## Abstract [BLOCKED — awaiting valid real-LLM completion]

ADAPTI-GUARD is an adaptive defense framework for LLM-based agents combining prompt-injection detection, risk scoring, and counter-based policy escalation (B3/B6). The intended primary evaluation compares ASR of B0 / B1 / B2_L1 / B3 on held-out `benchmark_q1` test samples with a blind LLM judge.

**[BLOCKED]** Final ASR, McNemar/Holm, and effect sizes are **not** available:

1. **EXP-004 (OpenRouter multi-model):** blocked by HTTP **401**.
2. **EXP005 (Gemini 3.6 Flash):** provider preflight and smoke are **VALID**, but the full protocol is **BLOCKED** by free-tier HTTP **429** (`generate_content_free_tier_requests`, limit 20). See `docs/FINAL_REAL_LLM_EVALUATION_REPORT.md`.

A 15-sample infrastructure pilot (PHASE2_7_PILOT) and any simulation/heuristic runs are **Simulation / Infrastructure Validation** only — **not** final evidence.

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

### 5.2 Models [BLOCKED — quota / auth]
| Model | Role | Status |
|---|---|---|
| `gemini-3.6-flash` (Google Interactions) | Target (+ same-family blind judge when OpenRouter unavailable) | Smoke VALID; full EXP005 **BLOCKED** (HTTP 429 free-tier) |
| GPT-4o-mini / Qwen / DeepSeek (OpenRouter) | EXP-004 targets | **BLOCKED** (HTTP 401) |
| Claude Sonnet 4 (OpenRouter) | Preferred independent judge | **BLOCKED** (HTTP 401) |

Generation (Gemini Interactions): `seed` and `max_output_tokens` supported; **temperature and top_p unsupported** (documented).

### 5.3 Baselines (EXP005 canonical)
B0 no defense; B1 rule-based; B2_L1 fixed defense; B3 ADAPTI-GUARD adaptive.

### 5.4 Metrics
ASR (blind LLM judge), Defense Rate, Utility, FPR, Latency, Token usage; cost only if API returns pricing (currently unavailable).

---

## 6. Results [BLOCKED]

**Real LLM Evaluation:** no VALID full-protocol ASR table. Do not insert simulated numbers here.

Infrastructure smoke (Gemini, B0 only, n=2 prompts, not a baseline comparison): see
`results/real_llm/gemini_3_6_flash/EXP005-20260903-081350/smoke.json`.

**Simulation / Infrastructure Validation** (heuristic ablations, pilots) remains out of the primary results claim set.

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
7. Real-LLM full evaluation blocked: OpenRouter 401; Gemini free-tier 429 after VALID smoke
8. Gemini judge is same-family when Claude OpenRouter judge is unavailable

---

## 9. Conclusion [BLOCKED]

[Write after a VALID real-LLM run with numbers traced from raw outputs → judge → metrics → statistics.]

Reproducibility and audit: `docs/FINAL_REAL_LLM_EVALUATION_REPORT.md`, `docs/FINAL_Q1_SCIENTIFIC_AUDIT.md`.
