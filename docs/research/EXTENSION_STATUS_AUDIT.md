# Extension implementation audit

| ID | Criterion | Status | Evidence |
| --- | --- | --- | --- |
| E1 | Conversation state, multi-turn, replay | **PARTIAL** | `stateful_episode.py`, `offline_experiment_runner.py` (COND-E1) |
| E2 | Feedback → strategy change | **PARTIAL** | `adaptive_episode.py`, `observe_defense`, `test_adaptive_episode.py` |
| E3 | Auth, deny, execute, state, observation | **PARTIAL** | `agent_environment.py` (mock env; not AgentDojo) |
| E4 | Target ≠ judge metadata | **PARTIAL** | `execution_metadata.py`, `target_model.py` |
| E5 | Seed × trial structure | **DESIGN ONLY** | matrix columns; no campaign |
| E6 | Baseline registry | **DESIGN ONLY** | `external_baseline_protocol.py` |

Live-evaluated extensions: **none** (Phase 7 blocked).
