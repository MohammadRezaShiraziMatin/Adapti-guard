# ADAPTI-GUARD — Formal Threat Model

**Phase 1 Audit | Date:** 2026-09-02  
**Scope:** Matches **implemented** evaluation harness unless noted as *aspirational*.

---

## 1. System Model

```
[User/Benign Task] ──┐
[Attacker Prompt]  ──┼──► [ADAPTI-GUARD Pipeline] ──► [Target LLM] ──► [Response]
[RAG/Context]      ──┘         │                              │
                                 └── detector → risk → policy → action
```

**Deployment point (implemented):** Pre-inference middleware on `(prompt, optional context)` string.  
**Not implemented:** Post-generation filtering, tool-call interception, model routing, memory isolation.

---

## 2. Attacker

### 2.1 Capabilities (as evaluated today)

| Capability | Supported in eval? | Notes |
|------------|-------------------|-------|
| Craft user-visible prompt | Yes | Primary input |
| Inject into retrieved context | Partial | `context` field concatenated; no live RAG pipeline |
| Multi-turn conversation | Partial | `multi_turn_attacks` category; single-turn API calls in harness |
| Tool output injection | **No** | No tool execution loop |
| Observe model responses | **No** (harmonized replay) | Frozen attack stream; AdaptiveAttacker not used at eval time |
| Adapt to defense policy | **No** | Attacker does not observe defense level during replay |
| Mutate prompts (LLM-based) | **No** | 12 fixed template strings in `adaptive_attacker.py` |
| Knowledge of defense policy | Assumed **none** | Reasonable for black-box |
| Knowledge of system prompt | Partial | `system_prompt_leakage` category intended but **0 samples** |

### 2.2 Attacker Model Classification

**Black-box query access** to the defended LLM endpoint, with ability to supply arbitrary UTF-8 text in user prompt and (optionally) context fields.

*Not in scope:* white-box weight access, training-data poisoning, side channels.

### 2.3 Attacker Goals (per attack category)

See `ATTACK_TAXONOMY.md` for category-specific goals.

---

## 3. Defender (ADAPTI-GUARD)

### 3.1 Observable

- User prompt text
- Optional context string (simulated RAG/tool output)
- Previous-episode outcome flags (attack_success, legitimate_success) for adaptation
- Historical attack/legitimate pressure counters
- Detector score, risk level, current defense level

### 3.2 Not Observable

- Target LLM internal activations
- True user intent (only task label in eval)
- Future attack content (non-adaptive replay)
- External tool state / filesystem / network

### 3.3 Defender Controls

| Control | Implemented? |
|---------|--------------|
| Input modification (sanitize) | Yes — A1 |
| Block request | Yes — A3 |
| Tool restriction flag | Yes — A2 (semantic only; no real tools) |
| Defense level L0–L3 | Yes |
| Model selection / routing | **No** |
| Output filtering | **No** |
| Rate limiting | **No** |

### 3.4 Defender Objective (as implemented)

Maximize a **scalar feedback reward** (logged only):
```
reward = 0.5·security_score + 0.4·utility_score − 0.1·defense_cost
```
Adaptation decisions use **discrete signals** (INCREASE_DEFENSE / REDUCE_DEFENSE / MAINTAIN), not reward optimization.

---

## 4. Assets

| Asset | Protected in current eval? | Formal objective |
|-------|-------------------------|------------------|
| System prompt secrecy | Intended (0 test samples) | Confidentiality |
| User/task integrity | Partial (benign tasks) | Integrity |
| Tool permissions / external systems | **Claimed, not evaluated** | Tool safety |
| Sensitive data in context | Partial (RAG category) | Confidentiality |
| Service availability | Partial (block = denial) | Availability |
| Agent state / memory | **Not in scope** | Integrity |

---

## 5. Attack Surface

| Surface | In benchmark_q1 | In eval harness |
|---------|-----------------|-----------------|
| Direct user prompt | 263 samples | Yes |
| Indirect (embedded in documents) | 1,037 | Yes (context concat) |
| RAG retrieved passages | 1,927 | Yes (static context field) |
| Jailbreak / role-play | 6,104 | Yes |
| Multi-turn / adaptive templates | 2,500 | Partial |
| Tool/plugin channel | 28 | **No execution** |
| System prompt channel | ~0 | **Not covered** |
| Agent memory | 0 | **Not covered** |

---

## 6. Security Objectives (Formal)

Let episode e have ground-truth label y_e ∈ {attack, benign}.

| Objective | Metric (target) | Current proxy |
|-----------|-----------------|-----------------|
| **Attack containment** | ASR ↓ | Judge: attack_success on real LLM (**BLOCKED**) |
| **Benign availability** | Benign task success ↑ | `action ≠ A3` (**weak proxy**) |
| **False intervention control** | FPR ↓ | Block rate on benign |
| **Prompt secrecy** | Leakage rate ↓ | **Not measured** |
| **Tool safety** | Unauthorized tool call rate ↓ | **Not measured** |

**Security success (publication-valid):** Judge labels `attack_success = false` for attack episodes AND task completes for benign episodes.

---

## 7. Trust Boundaries

```
TRUSTED:   ADAPTI-GUARD code, system prompt (fixed), judge protocol
UNTRUSTED: user prompt, context, target LLM output (for judge input)
ASSUMED:   judge model is independent and calibrated
```

---

## 8. Threat Model Gaps (Reviewer Risks)

1. **Agent threat model claimed but not evaluated** — remove or add AgentDojo.
2. **Adaptive adversary claimed but replay is static** — relabel as "diverse attack corpus" not "evolving adversary."
3. **Utility = not blocked** is insufficient for Q1 — need task-completion judge.
4. **HIGH risk bypasses defense level** — adaptation irrelevant when detector fires strongly.

---

## 9. Alignment with OWASP LLM Top 10

| OWASP Risk | Relevance to ADAPTI-GUARD |
|------------|---------------------------|
| LLM01 Prompt Injection | **Primary** — direct/indirect |
| LLM02 Sensitive Info Disclosure | Partial — leakage category empty |
| LLM06 Overreliance | Out of scope |
| LLM07 Insecure Plugin Design | **Claimed** — not evaluated |
| LLM08 Excessive Agency | Partial — tool restriction action exists but no tools |
