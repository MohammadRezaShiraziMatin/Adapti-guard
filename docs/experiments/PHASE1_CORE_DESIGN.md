# Phase 1 core defense design (offline)

Implements the audit in [`PHASE1_CORE_AUDIT.md`](PHASE1_CORE_AUDIT.md). Not a VNEXT re-run. Not a security-performance claim.

```
EpisodeInput (no gold labels)
  → ContextBuilder (prompt, context, tool name/args/output, privilege flag)
  → Detector v4 (prompt+context; optional tool channels)
  → RiskEngineCore (p bands + observable privilege features)
  → CorePolicyEngine (inspectable table)
  → DefenseActionLayer
  → ToolPermissionGate (outside prompt text)
  → EpisodeTrace
```

## Modules

| Piece | Module | Notes |
| --- | --- | --- |
| Input / builder / trace | `core/episode.py` | Rejects gold keys if passed |
| Pipeline | `core/core_pipeline.py` | Single `run()` |
| Risk | `risk/risk_engine_core.py` | Same 0.25/0.60 bands as v4; extra features only |
| Policy | `policy/core_policy.py` | New table; does not edit historical `DefensePolicyEngine.decide` |
| Gate | `defense/tool_permission.py` | Wraps `run_tool_turn` |
| Factory | `make_core_defense` / `PHASE1-CORE` | Not `VNEXT-ADAPT` |

## Privilege (observable, not labels)

`send_email`, `create_record`, `retrieve_document` are privileged (side-effect or document fetch). `search` is not.

## Core policy table

| Risk | Privileged tool? | Action | Why |
| --- | --- | --- | --- |
| HIGH | no | A3 | Block execution |
| HIGH | yes | A2 | Deny the tool; still an action-level control |
| MEDIUM | yes | A2 | Close Detection→A1→tool-still-runs |
| MEDIUM | no | A1 (level ≤1); A2 (level 2); A3 (level 3) | Text-only remaining limitation |
| LOW | yes or no | A0 at level 0; A1 if level ≥1 and no privileged tool; **A0 if privileged** | Benign tool workflows |

LOW never selects A3.

## Detector

`detect_episode(..., *, tool_name=None, tool_output=None)`. If both omitted, scores match frozen v4 prompt-only behavior.

## What we will not do

- Change VNEXT-ADAPT / `make_b3_adaptive_v4`
- Edit frozen JSONL or AUDIT
- Call LLM APIs
- Report offline counts as ASR wins
