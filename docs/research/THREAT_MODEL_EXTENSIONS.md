# Threat model — Q1 program (extensions overlay)

**Canonical base (unchanged):** [`P1_THREAT_MODEL.md`](P1_THREAT_MODEL.md) · Phase-1 live: [`docs/paper/phase1/PHASE1_THREAT_MODEL.md`](../paper/phase1/PHASE1_THREAT_MODEL.md) · Confirmatory: `docs/paper/q1_findings/MANUSCRIPT.md` §3.

**Status:** Research contract (Phase 2). **Not** an authorization to run live campaigns.

---

## 1. System, target, defender

| Role | Description |
| --- | --- |
| **Target** | LLM agent middleware episode: prompt + context (+ optional tool schema) → model → optional tool execution. |
| **Defender** | Runtime pipeline: detect → risk → policy → actions A0–A3 before/around tool execution. |
| **Judge / verifier** | Independent model (confirmatory: Target ≠ Judge) + deterministic tool-outcome checks where defined. |

---

## 2. Assets and security objectives

| Asset | Objective |
| --- | --- |
| System / developer instructions | **Integrity** (no override) |
| Sensitive context | **Confidentiality** |
| Tool authorization | **Authorization correctness** |
| Task / user intent | **Task adherence** |
| Agent / episode state | **Integrity** of state transitions |

Utility and benign task completion are **co-primary** where protocol locks a utility gate (Track A/B).

---

## 3. Trust boundaries

```text
System instruction / policy config     → TRUSTED (defender config)
Gold labels, success_condition, twins  → SCORER-ONLY (not at runtime)

User prompt                            → UNTRUSTED
Retrieved / RAG / document context     → UNTRUSTED
Tool observations in context           → UNTRUSTED
Prior conversation turns (when live)   → UNTRUSTED
Tool outputs fed back to model         → POTENTIALLY UNTRUSTED

Agent state / memory (when modeled)    → SECURITY-SENSITIVE
```

---

## 4. Attacker model (capability classes)

### 4.1 Static attacker (confirmatory packs today)

Fixed UTF-8 in prompt/context; black-box; no feedback from defender scores. Matches frozen Track A/B corpora.

### 4.2 Multi-turn attacker (extension design)

```text
Turn 1 → model/defense → state update → Turn 2 → … → cumulative harm
```

Not the same as a single concatenated transcript in one scoring step (P0 audit distinction).

### 4.3 Adaptive attacker (extension design)

```text
Attack → observe (block/harm signal) → update strategy → next attack
```

Distinct from static attack lists or offline template rotation without feedback.

### 4.4 Agentic attacker (extension design)

```text
Malicious instruction → tool request → (authorization) → state change → observation
```

Operational harm via privileged tools where `success_condition` / Tool-HASR applies.

---

## 5. Attack surface (research scope)

| Surface | In scope | Evidence today |
| --- | --- | --- |
| Direct PI | Yes | Confirm packs |
| Indirect / RAG-style context | Yes | Confirm packs |
| Tool-output-shaped injection | Yes (mock tools) | Confirm packs |
| Live multi-turn red team | Design | **No live eval** |
| Adaptive closed-loop | Design | Offline harness only |
| Full AgentDojo sandbox | Out of primary harness | **Not run** |

---

## 6. Out of scope (explicit)

- Training-time poisoning, weight access, white-box optimization (except cited literature context).
- Infrastructure / endpoint / network compromise.
- Production RAG retriever compromise (only frozen context strings evaluated).
- Claiming Target refusal alone as defense success (confirmatory taxonomy).
- Human-subject studies (Phase 5 problem definition only).

---

## 7. Extension overlay table

| Dimension | Core (P1 / confirm) | E1 Multi-turn | E2 Adaptive | E3 Agentic |
| --- | --- | --- | --- | --- |
| Attacker knowledge | Black-box | Black-box + history | + defense feedback | + tool/env API |
| Defense position | Pre-tool runtime | Per-turn | Per-turn | Auth + runtime |
| State | Frozen context | Message list | + attacker state | Env step log |
| Human operator | None | — | — | Design-only (RQ-Trust-1) |

Do not claim live extension evaluation until Phase 7 evidence exists.
