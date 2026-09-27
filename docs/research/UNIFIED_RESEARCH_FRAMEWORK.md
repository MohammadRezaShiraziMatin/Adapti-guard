# Unified Research Framework (Phase 3)

**Upstream:** Phase 1 literature · Phase 2 RQ/threat/contribution.  
**Downstream (Phase 4):** runners, providers, collectors — not defined here.

## Pipeline (canonical)

```text
Threat Model → Attack Condition → Defense → Target Model → Judge / Verifier
  → Episode Execution → Metrics → Statistics → Evidence → Finding → Claim
```

## Phase boundary

| Phase 3 (this doc) | Phase 4 |
| --- | --- |
| Matrix, protocol, evidence schema, dimensions, gates | Infrastructure execution |

## Configuration dimensions

| Dimension | Canonical key | Definition | Phase 3 mode |
| --- | --- | --- | --- |
| `attack` | `attack_id` | Attack surface / family / episode payload | contract |
| `defense` | `defense_id` | Runtime policy arm (e.g. B0, VNEXT-ADAPT, PHASE1-CORE) | contract |
| `target_model` | `target_model_id` | Model producing agent response / tool call | contract; live only with gate |
| `judge` | `judge_id` | Independent evaluator (LLM judge) | **must ≠ target** on confirmatory live |
| `interaction` | `interaction_mode` | `single_turn` \| `multi_turn` (stateful) | contract |
| `adaptivity` | `adaptivity` | `static` \| `adaptive` (attacker feedback loop) | contract; ≠ interaction |
| `agent_state` | `agent_state` | `none` \| `conversational` \| `environment` | contract |
| `tool` | `tool_state` | `none` \| `mock` \| `real` | contract; confirmatory = mock |
| `seed` | `seed` | RNG / episode seed | contract |
| `trial` | `trial` | Repeat index within seed | contract |
| `dataset` | `dataset_id` | Frozen pack + version/hash | contract |
| `condition` | `condition_id` | Stable ID for matrix row (see `EXPERIMENT_MATRIX.yaml`) | contract |

**Do not conflate:** `adaptivity=adaptive` ≠ `interaction_mode=multi_turn`; `agent_state=environment` ≠ tool injection alone.

## Documents

| Artifact | Role |
| --- | --- |
| `EXPERIMENT_PROTOCOL.md` | Execution + failure semantics + live gate |
| `EXPERIMENT_MATRIX.yaml` | RQ ↔ condition ↔ evidence status |
| `EVIDENCE_SCHEMA.yaml` | Machine-readable provenance |
| `REPRODUCIBILITY.md` | Lock fields |
| `METRICS_AND_STATISTICS.md` | Metric definitions (archive + extensions) |
| `CLAIMS_MAP.md` | Finding → claim status |
| `PHASE5_TRUSTWORTHY_APPLICATION.md` | Human-centered / trustworthy layer (design; Phase 5) |

## Phase 5 boundary (human-centered / trustworthy)

| In scope (Phase 5) | Out of scope |
| --- | --- |
| Decision-layer signals from `EpisodeTrace` / evidence_record | HITL UI, operator override logging |
| `human_review_packet` (machine vs human outcome separation) | Human study, trust calibration metrics |
| Trustworthy dimension map tied to existing metrics | CPS / OT validation claims |
