# Phase 1 Ablation Protocol (Attribution)

**ID:** `PHASE1-ABL-0.1`  
**Spec:** `PHASE1-SCI-SPEC-0.1`  
**Date (UTC):** 2026-09-14  

Ablations are **pre-registered** for attribution. No post-hoc selection of favorable arms.

---

## Arms

| Key | Mechanism | Scientific question |
| --- | --- | --- |
| `PHASE1-CORE` | Full evidence → risk → action-sensitive policy | Full system |
| `ABL-NO-EVIDENCE` | Detector forced to empty/low evidence | Is evidence necessary? |
| `ABL-NO-RISK` | Skip risk engine; map detector hit→HIGH else LOW | Does risk banding matter? |
| `ABL-NO-ADAPTATION` | `defense_level=0` fixed; no level escalation path | Does adaptation slot matter in single-turn? |
| `ABL-NO-COST-GATE` | Escalate: MEDIUM text→A2, HIGH→A3 always | Does minimum-intervention/cost gate matter? |
| `ABL-NO-TOOL-SENSITIVITY` | Policy ignores declared/privileged tool flags | Does tool sensitivity matter? |
| `B0` / `STATIC-A1` / `STATIC-A2` / `STATIC-A3` | Fair paired references | External/static comparisons |

All arms are label-blind. Same confirm episodes. Same mock tools.

---

## Analysis rule

Primary confirmatory claim remains **B0 vs PHASE1-CORE** only.  
Ablations are **secondary attribution** (report all; do not cherry-pick).  
Dominance vs STATIC-* uses the pre-registered H3 rule in the scientific spec / SAP.
