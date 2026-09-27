# Literature gap audit — Multi-turn / Adaptive / Agentic

**Machine-readable extractions:** `LITERATURE_EXTRACTIONS.yaml` (19 records, nine fields each).  
**Evidence cache:** `phase1_sources/abs_*.{meta.json,abstract.txt}`.

## Definitions (binding)

| Term | Meaning in this audit |
| --- | --- |
| **Stateful multi-turn** | Live or explicit multi-turn dialogue where later turns depend on earlier model outputs (not single blob of frozen transcript only). |
| **Adaptive attacker** | Attacker updates strategy from observed target/defense feedback (closed loop). |
| **Agentic** | Tool invocation / environment execution with state, not text-only harm. |

## Extension coverage (from abstract evidence)

| Branch | Papers (keys) | Evidence |
| --- | --- | --- |
| Multi-turn stateful | `russinovich2024crescendo`, `chang2025chatinject` | Abstract states multi-turn dialogue / template-based multi-turn variant |
| Adaptive iterative | `zou2023gcg` | Adversarial suffix optimization |
| Adaptive feedback-guided | `chao2023pair` | Attacker LLM iteratively refines jailbreak from target responses |
| Agent environment | `debenedetti2024agentdojo`, `zhan2024injecagent` | Agent/tool benchmarks |
| **Not** stateful MT | `chao2023pair`, `zou2023gcg` | Iterative on prompts; not cross-turn conversation state in abstract |
| **Not** adaptive | Most PI benchmark papers | Static payloads / datasets |

Per-paper flags: see `multi_turn_audit`, `adaptive_audit`, `agentic_audit` in `LITERATURE_EXTRACTIONS.yaml`.

## Research gaps (literature-backed)

| Gap | Evidence | AdaptiGuard response (design/planned) | Remaining limitation |
| --- | --- | --- | --- |
| Detector vs policy isolation | Manuscript §2; guard papers focus on block/detect | Locked dual-track + Tool-HASR vs Judge-ASR | Track A FAIL; scoped Track B only |
| Unified security–utility–cost | Limited pre-registered co-primary gates in prior work | MSID + McNemar + utility gate | n=61; single target in confirmatory tracks |
| Stateful MT defense eval | Crescendo/ChatInject emphasize offense | E1 offline harness; **not live-evaluated** | No empirical MT campaign |
| Closed-loop adaptive attacker vs defense | PAIR/GCG adapt offense, not defense-aware agent | E2 offline feedback loop | **NOT TESTED** live |
| Agentic operational endpoints | AgentDojo/InjecAgent vs text ASR | E3 mock env; frozen packs | Not AgentDojo leaderboard |
| External baseline parity | InjecGuard/TensorTrust not run under AdaptiGuard protocol | E6 registry; Q1-P2 future | **DESIGN ONLY** |

No claim that AdaptiGuard has **live-evaluated** extension results.
