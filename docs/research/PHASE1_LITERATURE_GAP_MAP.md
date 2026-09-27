# Phase 1 — Literature Gap Map

**Status:** DONE (see `PHASE1_COMPLETION.json`).  
**Corpus:** 19 records — `LITERATURE_CORPUS.yaml` + `references.bib` + `references_extension.bib`.  
**Extractions:** `LITERATURE_EXTRACTIONS.yaml` (nine fields × 19).

## Taxonomy coverage (literature-supported)

| Attack / defense family | Representative keys |
| --- | --- |
| Direct PI | `perez2022ignore`, `liu2023prompt`, `toyer2023tensortrust` |
| Indirect PI | `greshake2023not`, `yi2023bipia`, `zhan2024injecagent` |
| RAG-oriented | `yi2023bipia` |
| Instruction hierarchy | `wallace2024instruction` |
| Context / structure defense | `chen2024struq` |
| Runtime / rails | `rebedea2023nemo` |
| Input guard / detection | `inan2023llama`, `li2024injecguard` |
| Multi-turn (stateful) | `russinovich2024crescendo`, `chang2025chatinject` |
| Adaptive offense | `chao2023pair`, `zou2023gcg` |
| Agent / tool benchmarks | `debenedetti2024agentdojo`, `zhan2024injecagent` |
| Statistics methods | `mcnemar1947note` |
| Standards | `owasp2023llm` |

## Gap chain

```text
Existing Literature (PI, guards, agent benchmarks, adaptive jailbreaks, MT attacks)
       ↓
Well studied: single-turn PI, guard models, agent benchmark suites, offensive adaptation
       ↓
Partially studied: security–utility–cost under one protocol; defense-aware adaptive red team; operational tool harm vs judge ASR
       ↓
Missing / underexplored: pre-registered detector–policy decomposition across MT + adaptive + agentic conditions with shared evidence schema
       ↓
AdaptiGuard contribution (evidence-scoped): unified evaluation framework/protocol; dual-track confirmatory results (immutable); extension harness offline-validated only
```

## RQ consistency (read-only)

| Literature gap | RQ |
| --- | --- |
| Runtime intervention vs risk/utility/cost | RQ-Core-1, RQ-Core-2 |
| MT realism | RQ-Ext-1 |
| Adaptive attacker | RQ-Ext-2 |
| Tool/state vs text metrics | RQ-Ext-3 |
| Cross-model / baselines / trust | RQ-Ext-4–6, RQ-Trust-1 |

No RQ text changed in this phase.
