# Phase 1 core defense design (offline)

Implements the audit in [`PHASE1_CORE_AUDIT.md`](../../archive/phase1_closeouts/PHASE1_CORE_AUDIT.md). Not a VNEXT re-run. Not a security-performance claim.

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

## Detector (Phase 1)

`PromptInjectionDetectorPhase1` (`evidence_phase1.0`) extends frozen v4 with:

- hierarchy / control-plane cues (`PRIORITY=SYSTEM+1`, developer_message, FOLLOWUP_INSTRUCTION)
- tool-invoke patterns (`send_email`, `create_record`, `retrieve_document`, `function_result`)
- obfuscation decode (unicode escapes, nested b64→hex, HTML entities, labeled ROT13)
- hard-negative E10 (count/analyze/redact/contrast/quoted payloads)

Frozen `PromptInjectionDetectorV4` (`evidence_v4.0`) remains the VNEXT-ADAPT identity.

## Risk

Same 0.25 / 0.60 bands. Optional privilege floors only when attack-like evidence is present (not E4_tool alone).

## Policy

Minimum effective intervention:

| Risk | Declared tool | Action |
| --- | --- | --- |
| HIGH | none | A3 |
| HIGH | any / privileged | A2 |
| MEDIUM | any / privileged | A2 |
| MEDIUM | none | A1 |
| LOW | any | A0 |

## Legacy path

`AdaptiGuard.run` is historical regex-v3 compatibility (garak/MVP). Not Phase 1 core.