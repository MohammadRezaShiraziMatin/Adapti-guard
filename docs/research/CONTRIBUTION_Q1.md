# Contribution statement (Q1 program)

**Flow:** Literature gap (Phase 1) → RQ (this phase) → method/framework (Phase 3+) → evidence → claims.

Immutable historical results: **Track A = FAIL**; **Track B = SUPPORTED_IMPROVEMENT** (scoped, disjoint pack). Do not retro-fit.

---

## Methodological contributions (supported by artifact / protocol)

| ID | Contribution | Evidence |
| --- | --- | --- |
| M1 | Unified, configuration-driven **evaluation protocol** for prompt-injection defenses (Target ≠ Judge, separate utility gate) | `EXPERIMENT_PROTOCOL.md`, Q1 findings MANUSCRIPT §5, frozen AUDITs |
| M2 | **Detector–policy decomposition** estimand (defense-attributed McNemar cells, MSID) | Track A/B AUDIT, `METRICS_AND_STATISTICS.md` |
| M3 | **Tool-HASR vs Judge-ASR** separation for agent-style episodes | P1 threat model, confirm packs |
| M4 | Extension-ready **interaction/adaptivity/agent** definitions without conflating dimensions | `THREAT_MODEL_EXTENSIONS.md`, `RESEARCH_QUESTIONS.md` |
| M5 | Reproducibility locks (pack SHA, run metadata schema) | `REPRODUCIBILITY.md`, `EVIDENCE_SCHEMA.md` |

---

## Empirical contributions (live evidence only where stated)

| ID | Finding | Evidence | Status |
| --- | --- | --- | --- |
| E1 | Track A VNEXT-ADAPT **does not** meet pre-registered qualified win | `VNEXT_CONFIRM/.../AUDIT.md` | **SUPPORTED** |
| E2 | Track B PHASE1-CORE shows **scoped** improvement vs B0 on **different** pack | `PHASE1_CONFIRM/.../AUDIT.md` | **SUPPORTED** |
| E3 | Multi-turn / adaptive / agentic / cross-model / baseline **comparative** outcomes | Phase 7 + matrix | **PLANNED** |

No SOTA, universal, or production-ready claims.

---

## Analytical contributions (interpretation bounded by evidence)

| ID | Contribution | Status |
| --- | --- | --- |
| A1 | Security–utility–cost trade-off reporting under dual-track separation | **PARTIAL** (Track B utility eligible; Track A utility fail) |
| A2 | Cross-condition narrative linking literature gaps to planned extensions | **SUPPORTED** (Phase 1–2 docs) |
| A3 | Trustworthy / human-in-the-loop cyber-agent **problem boundary** | **PLANNED** (`PHASE5_TRUSTWORTHY_APPLICATION.md`) |

---

## Non-contributions (explicit)

- Novel ML detector architecture as primary claim (heuristic detector in confirmatory tracks).
- AgentDojo leaderboard or external baseline superiority.
- Solving prompt injection globally.
