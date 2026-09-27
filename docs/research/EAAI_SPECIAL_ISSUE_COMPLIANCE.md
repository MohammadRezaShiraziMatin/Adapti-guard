# EAAI Special Issue — Compliance Contract (AdaptiGuard)

**Canonical venue contract** for manuscript standardization. **Does not authorize live execution.**

| Field | Value |
| --- | --- |
| Journal | Engineering Applications of Artificial Intelligence |
| Publisher | Elsevier |
| Special Issue | Human-Centered and Trustworthy AI for Cybersecurity in Cyber-Physical Systems |
| Article type | AI for Cybersecurity (empirical + engineering methodology) |
| Submission window | 1 October 2026 – 31 January 2027 |

**Cross-cutting:** maps onto `Q1_EIGHT_PHASE_PROGRAM.md` (Phases 1–8); not a ninth phase.

---

## B. Scientific positioning (bounded)

**Positioning statement (design-level):** AdaptiGuard is a **human-centered and trustworthy runtime security evaluation framework** for **LLM-based cybersecurity systems**, with confirmatory evidence on locked single-turn packs (Track A/B) and **offline-validated** extension harnesses (multi-turn, adaptive, agentic mock).

**Wording discipline:** Until Phase 7 live extension evidence exists, do **not** use *demonstrated*, *empirically validated*, *improved*, *reduced*, *robust*, or *effective* for extension arms or CPS deployment.

**Immutable empirical state:** Track A **FAIL**, Track B **SUPPORTED_IMPROVEMENT** (scoped), frozen AUDITs — do not rewrite.

---

## C. EAAI requirement matrix

| EAAI requirement | AdaptiGuard component | Status | Evidence required |
| --- | --- | --- | --- |
| AI for cybersecurity | `CoreDefensePipeline`, confirmatory eval | **PARTIAL** | Track A/B AUDIT (live historical); extensions Phase 7 |
| Generative AI security | PI detector + confirm packs | **DONE** | Track A/B AUDIT, frozen packs |
| Adversarial attacks | Attack packs / `AdaptiveAttacker` (offline) | **PARTIAL** | Confirm packs live; adaptive live **BLOCKED** |
| Trustworthy AI | Runtime defense, verifier, judge separation | **PARTIAL** | Protocol + Track A/B; ext live **BLOCKED** |
| Human-centered AI | `human_review_packet`, Phase 5 doc | **DESIGN ONLY** | Human study **BLOCKED** |
| Human-in-the-loop | `LIVE_EVALUATION_GATE`, sign-off template | **DESIGN ONLY** | Operator study **NOT IMPLEMENTED** |
| Explainability | `EpisodeTrace`, policy/risk reasons | **PARTIAL** | Trace export; no user-study validation |
| Engineering application | Layer below (mapped to code) | **PARTIAL** | Mock tool env; no CPS deployment |
| Cyber-physical relevance | CPS validation | **BLOCKED** | No OT/CPS environment in repo |
| Real-world validation | Phase 7 campaign | **BLOCKED** | `PHASE7_LIVE_BLOCKED`, auth PENDING |
| Reproducibility | `EVIDENCE_SCHEMA.yaml`, `REPRODUCIBILITY.md` | **PARTIAL** | Schema + offline runs; full campaign pending |
| Statistical validation | McNemar / δ̂ / gates (confirmatory) | **PARTIAL** | Track A/B complete; extension stats **DESIGN ONLY** |

---

## D. Official research scope (one program)

### Core evaluation (confirmatory — historical live)

1. Direct PI — confirm packs  
2. Indirect / RAG PI — pack design  
3. Runtime intervention — B0 / VNEXT / PHASE1-CORE  
4. Deterministic verification — tool gate / Tool-HASR where applicable  
5. LLM judge — `llm_judge.py`, confirmatory  
6. Target ≠ Judge — matrix + resolver  
7. Security–utility–cost — RQ-Core-2, AUDIT fields  

### Official extensions (offline harness; live **PLANNED**)

8. Stateful multi-turn — `stateful_episode.py`  
9. Adaptive-to-defense — `adaptive_episode.py`, `AdaptiveAttacker`  
10. Agentic / tool + state — `agent_environment.py`  

### Robustness dimensions

11. Multi-model — `EAAI_TARGET_MODELS.yaml` (**PLANNED**)  
12. Repeated trials / seeds — matrix design; live **BLOCKED**  
13. Multilingual — **NOT IMPLEMENTED** in matrix  
14. External baselines — `external_baseline_protocol.py` (**DESIGN ONLY**)  

---

## E. Engineering application layer (component map)

```text
Attacker          → attack packs / AdaptiveAttacker / matrix attack_id
Attack Engine     → episode input + `component_resolver`
Target LLM        → `target_model.py` (live gated)
Runtime Defense   → `CoreDefensePipeline`, defense baselines
Agent / Tool      → `tool_loop`, `MockToolRegistry`, `AgentEnvironment`
Engineering Env   → mock tool state (no CPS plant model in repo)
Verifier          → tool permission / privileged tool outcome
Human Operator  → `human_review_packet` (design only)
Outcomes          → ASR, Tool-HASR, utility, cost fields
Statistics        → `statistics.py` + AUDIT aggregates
```

Multi-turn / adaptive / agentic flows: see `PHASE5_TRUSTWORTHY_APPLICATION.md` §3 and `UNIFIED_RESEARCH_FRAMEWORK.md`.

---

## F. Human-centered / trustworthy (status)

| Topic | Status |
| --- | --- |
| Human-centered design | **DESIGN ONLY** (`PHASE5_TRUSTWORTHY_APPLICATION.md`) |
| Human review protocol | **DESIGN ONLY** (`human_review_packet.py`) |
| Human empirical study | **BLOCKED** |
| Trust calibration / automation bias empirical | **BLOCKED** |

---

## G. CPS engineering validation

```text
CPS engineering validation: BLOCKED / NOT YET VALIDATED
```

**Minimum future evidence (no domain invented):** operational environment spec, state model, safety/security constraints, action consequences, authorization log, state transitions, outcome verification, reproducible traces — **none present as deployed CPS**.

---

## H. Target models (EAAI quartet)

See [`EAAI_TARGET_MODELS.yaml`](EAAI_TARGET_MODELS.yaml). All four: **`PLANNED`** — not evaluated under EAAI extension campaign.

---

## I. Experimental evidence contract

Required chain (no reversal):

```text
Raw Evidence → Derived Evidence → Statistics → Scientific Claim
```

Fields: per `EVIDENCE_SCHEMA.yaml`, `EXPERIMENT_PROTOCOL.md`, Phase 4 `evidence_record.json` / `raw_evidence.json`.

---

## J. Claim discipline (lifecycle)

| Stage | Meaning |
| --- | --- |
| DESIGNED | Protocol/matrix only |
| IMPLEMENTED | Code/harness exists |
| VALIDATED | Offline tests or fixture pipeline pass |
| LIVE EVALUATED | Phase 7+ live traces in evidence_path |

| Capability | DESIGNED | IMPLEMENTED | VALIDATED | LIVE EVALUATED |
| --- | --- | --- | --- | --- |
| Stateful multi-turn | ✓ | ✓ | ✓ (offline) | **no** |
| Adaptive attack | ✓ | ✓ | ✓ (offline) | **no** |
| Agentic security | ✓ | ✓ | ✓ (offline) | **no** |
| Human trust calibration | ✓ | partial | **no** | **no** |
| CPS security | ✓ | **no** | **no** | **no** |
| EAAI 4-model robustness | ✓ | partial (`configs/models.yaml` partial overlap) | **no** | **no** |

Program claims: [`CLAIMS_MAP.md`](CLAIMS_MAP.md). Manuscript-frozen: `docs/paper/q1_findings/CLAIMS_MAP.md`.

---

## K. Phase 7 / authorization (unchanged)

```text
PHASE 7 LIVE EXECUTION: BLOCKED
API SPEND: FORBIDDEN
Human authorization: PENDING
Budget authorization: PENDING (live_budget_authorization.yaml template)
```

Validator: `scripts/validate_phase7_live_authorization.py`.

---

## L. Phase ↔ EAAI mapping

| Phase | EAAI role |
| --- | --- |
| 1 | Literature, gap, venue fit |
| 2 | RQ, threat, contribution |
| 3 | Unified framework, methodology |
| 4 | Infrastructure |
| 5 | Trustworthy + human-centered |
| 6 | Pre-experiment / statistical readiness |
| 7 | Empirical campaign (**BLOCKED**) |
| 8 | Manuscript + submission (`EAAI_MANUSCRIPT_ALIGNMENT.md`) |
