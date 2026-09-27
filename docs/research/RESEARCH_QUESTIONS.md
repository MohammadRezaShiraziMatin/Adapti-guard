# Research Questions (Q1 program)

**Upstream:** Phase 1 gap map (`PHASE1_LITERATURE_GAP_MAP.md`).
**Trace:** RQ → condition (`EXPERIMENT_MATRIX.yaml`) → metric (`METRICS_AND_STATISTICS.md`) → evidence → claim (`CLAIMS_MAP.md`).

## Definitions (do not conflate)

| Term | Definition |
| --- | --- |
| **Multi-turn** | Stateful interaction across turns; later turns depend on prior messages/state. |
| **Adaptive** | Attacker updates strategy from observed defense/target feedback (closed loop). |
| **Agentic** | Harm via tool requests, environment state, authorization — not text-only endpoints. |

Adaptive ≠ multi-turn; agentic ≠ adaptive.

---

## Core RQs

| ID | Question | Gap motivation | IV / condition | DV / metrics | Evidence path | Analysis (locked where noted) | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **RQ-Core-1** | Under locked confirmatory protocol, does runtime intervention reduce prompt-injection risk while meeting pre-registered utility gates? | Detector–policy decomposition; MSID + McNemar hygiene (Lit. gap) | Defense arm vs B0; frozen packs | Tool-HASR / judge ASR; defense-attributed McNemar cells; utility U | Track A AUDIT; Track B AUDIT | McNemar; δ̂ vs MSID; separate tracks | **SUPPORTED** (scoped): A **FAIL**, B improvement |
| **RQ-Core-2** | What security–utility–cost trade-offs appear under the same protocol? | Limited joint reporting in prior work | Policy/defense level; workload mix | ASR, utility, intervention cost | Track A/B AUDIT + cost fields | Descriptive + gated co-primary utility | **PARTIALLY SUPPORTED** |

## Extension RQs (empirical answers require Phase 7 unless noted)

| ID | Question | Gap motivation | IV / condition | DV / metrics | Evidence path | Status |
| --- | --- | --- | --- | --- | --- | --- |
| **RQ-Ext-1** | How does defense effectiveness differ under **stateful multi-turn** vs single-turn episodes? | MT attacks (Crescendo/ChatInject); frozen transcript ≠ live MT | Interaction: single vs multi-turn | Per-turn / cumulative ASR, Tool-HASR | `stateful_episode.py` (offline); Phase 7 TBD | **PLANNED** |
| **RQ-Ext-2** | Under **adaptive** attacker feedback, does operational risk increase vs static attacks? | PAIR/GCG-style offense; defense-aware eval underexplored | Attacker: static vs adaptive | ASR, Tool-HASR, strategy shift | `adaptive_episode.py` (offline); Phase 7 TBD | **PLANNED** |
| **RQ-Ext-3** | Are judge/text metrics sufficient vs **tool/state** outcomes in agentic episodes? | Agent benchmarks vs episode judges (Lit.) | Endpoint: judge vs tool outcome | Judge-ASR vs Tool-HASR | Confirm packs + `agent_environment.py` (offline) | **PLANNED** |
| **RQ-Ext-4** | Is defense-related effect **directionally consistent** across target models? | Cross-model generalization gap | Target model ID | Δ security metrics per model | Q2 run **not in workspace** | **BLOCKED** (local evidence) |
| **RQ-Ext-5** | How stable are estimates across **seeds/trials**? | Repeated-trial rigor | Seed × trial | CI width; variance | Matrix design only | **PLANNED** |
| **RQ-Ext-6** | How does AdaptiGuard compare to **external baselines** under one protocol? | Baseline parity gap (InjecGuard/TensorTrust not run) | Baseline adapter | Same metrics as core | `external_baseline_protocol.py`; no live arms | **PLANNED** |
| **RQ-Trust-1** | Where can **human oversight** enter the cyber-agent loop without breaking evaluation integrity? | EAAI-aligned problem sketch only | Operator policy (design) | Override rate, explainability hooks (TBD) | `PHASE5_TRUSTWORTHY_APPLICATION.md`, `human_review_packet.py` | **DESIGN_ONLY** (Phase 5; no human study) |

Legacy audit: [`docs/archive/research/RESEARCH_QUESTIONS.md`](../archive/research/RESEARCH_QUESTIONS.md).

---

## RQ coverage matrix (research dimensions)

| RQ | Attack surface | Interaction | Adaptivity | Agent state | Defense | Target≠Judge | Stats |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RQ-Core-1 | Direct/indirect/RAG packs | Single-turn (confirm) | Defense level adapt (VNEXT/CORE) | Mock tools | Runtime A0–A3 | Yes (live) | McNemar, MSID |
| RQ-Core-2 | Same | Same | Same | Same | Same | Yes | Utility gate + cost |
| RQ-Ext-1 | PI families | **Multi-turn** | Optional | Optional | Runtime | Planned | Paired / CI (TBD) |
| RQ-Ext-2 | PI | Single or MT | **Adaptive attacker** | Optional | Runtime | Planned | Compare static vs adaptive |
| RQ-Ext-3 | Tool-mediated | Agent episode | Optional | **Yes** | Runtime + auth | Planned | Tool-HASR primary |
| RQ-Ext-4 | Locked arms | — | — | — | — | Multi-target | Cross-model |
| RQ-Ext-5 | — | — | — | — | — | — | Seed aggregation |
| RQ-Ext-6 | — | — | — | — | External baselines | — | Same as core |
| RQ-Trust-1 | — | — | — | Human loop (design) | — | — | Not specified |

---

## Overclaim guard

Open empirical questions only — no “best defense,” “solves PI,” or universal generalization in RQ wording.
