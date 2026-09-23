# Decision lock Q1-P2 — Evidence design (Q1 cycle scope)

**Decision ID:** Q1-P2  
**Status:** **LOCKED**  
**Date (UTC):** 2026-09-23  
**Author:** Seyed Mohammadreza Shirazi Matin  
**Scope:** Documentation and design locks for the **current Q1 manuscript cycle** only. **API=0.** No dataset bytes, no SAP execution, no live eval, no AUDIT edits.

**Companion:** [`Q1_ROADMAP_4PHASE.md`](Q1_ROADMAP_4PHASE.md) · [`Q1_BLOCKER_MATRIX.md`](Q1_BLOCKER_MATRIX.md) · D-22 names [`DECISION_LOCK_D22_CONFIRMATORY_V2_TAXONOMY.md`](DECISION_LOCK_D22_CONFIRMATORY_V2_TAXONOMY.md)

---

## A. Confirmatory V2 for this Q1 cycle

**LOCK:** For the **current Q1 manuscript cycle**, the following are **Future Work** (not in scope for the paper’s confirmatory evidence base):

- Confirmatory V2 **episode bodies**
- **151** attack **allocation table** (any family counts for V2)
- Confirmatory V2 **statistical analysis plan (SAP)** as an executed pre-registration
- **New frozen pack bytes** under `datasets/frozen/**` for V2

**LOCK (paper evidence base):** The Q1 findings story uses **only**:

- **Track A** — `vnext_confirm_v1.0`, n_attack = **61** (+61 benign), outcome **FAIL** (immutable AUDIT)
- **Track B** — `phase1_confirm_v1`, **SUPPORTED_IMPROVEMENT** (scoped; does not reverse Track A)

**Naming (unchanged):** D-22 six `family_id` strings remain **locked** for **future** V2 metadata if/when a pack is authorized later. This Q1-P2 lock does **not** build V2.

---

## B. D-22 remainder rule (design only; no pack build)

**Applies when** Confirmatory V2 is **later** authorized — **not** in this Q1 cycle (see §A).

**LOCK Researcher rule** for planned attack total **N = 151** across the six D-22 families:

\[
151 = 6 \times 25 + 1
\]

| Rule | Value |
| --- | --- |
| Base allocation | **25** episodes per `family_id` (six families → 150) |
| Remainder **+1** | Assigned to **`PRIVILEGE_EXFIL`** → **26** for that family; **25** for each of the other five |

**Rationale (design, not data-mined):** `PRIVILEGE_EXFIL` is the security-critical exfiltration family; fixed tie-break for the indivisible remainder.

**Does not change:** Track A historical `family_counts` on `vnext_confirm_v1.0` (n_attack = **61**). Those counts remain **descriptive** for Track A only per D-22.

**Still Future Work when V2 runs:** Episode text, SAP registration, benign/hard-negative sizing, MSID for V2, freeze PR, live eval gate.

---

## C. Track A δ̂ 95% CI

**LOCK:** Track A δ̂ **95% CI** remains a **BLOCKING GAP** in the official VNEXT AUDIT artifact.

| Allowed in manuscript (this cycle) | Forbidden |
| --- | --- |
| Cite point **δ̂ = 0.0820** from AUDIT | Invent or imply a CI not present in AUDIT |
| State explicitly that **95% CI is not reported** in `VNEXT_CONFIRM/20260914-133147/AUDIT.md` | Present interval estimates without an approved recompute artifact |

**Offline CI (PR #74 lineage):** [`scripts/recompute_vnext_delta_ci.py`](../../scripts/recompute_vnext_delta_ci.py) + [`artifacts/vnext_delta_ci_offline.json`](../paper/q1_findings/artifacts/vnext_delta_ci_offline.json) — bootstrap on per-episode contributions (`n_bootstrap=5000`, `seed=42`). **Not** in original AUDIT; cite as recomputed only.

---

## D. Must-have vs Future Work (Q1 findings story)

| Item | This cycle | Rationale |
| --- | --- | --- |
| External SOTA baselines (third-party defense arms) | **Future Work** (optional **P3** if budget + protocol lock) | No commensurate baseline AUDIT on tip; avoid casual SOTA comparisons |
| AgentDojo-class multi-step tool loops | **Future Work** | Harness is single-turn confirmatory; no AgentDojo integration |
| Multi-turn live (Phase-2 protocol) | **Future Work** | [`PHASE2_PROTOCOL.md`](protocols/PHASE2_PROTOCOL.md) unevaluated; no live AUDIT |
| Confirmatory V2 pack + live eval | **Future Work** (after budget + §A–B locks when authorized) | Paper uses Track A/B n=61 evidence only for this cycle |
| `p1_mechanism_v1.0.0` live eval | **Future Work** / optional **P3** | Frozen on tip; **`live_evaluated=false`** until [`LIVE_EVALUATION_GATE.md`](../research/LIVE_EVALUATION_GATE.md) + budget |
| Dual-track claim discipline + workshop packet docs | **Must-have** | On tip `e4870b9` ([`CLAIMS_CHECKLIST.md`](../paper/CLAIMS_CHECKLIST.md), [`workshop_vnext_fail/`](../paper/workshop_vnext_fail/README.md)) |
| Honest Track A **FAIL** + Track B **scoped** wording | **Must-have** | [`DUAL_TRACK_STATUS.md`](../paper/dual_track/DUAL_TRACK_STATUS.md); no FAIL→PASS |
| Offline repro / hash pins | **Must-have** | [`REPRODUCIBILITY_PACKAGE.md`](REPRODUCIBILITY_PACKAGE.md), [`APPENDIX_HASHES.md`](../paper/workshop_vnext_fail/APPENDIX_HASHES.md) |
| Venue camera-ready + submit | **Must-have in P4** (**human-only**) | Venue TBD; agents do not upload |

---

## E. Exit mapping (blocker matrix dispositions)

Every row in [`Q1_BLOCKER_MATRIX.md`](Q1_BLOCKER_MATRIX.md) carries a **P2 disposition** tag:

| Tag | Meaning |
| --- | --- |
| **immutable** | Cannot change (e.g. Track A FAIL); honest framing only |
| **docs-fixed** | Addressed by this lock + matrix/claims docs for this cycle |
| **P3-if-budget** | Optional live work after human budget; not required for Q1 story |
| **Future Work** | Out of scope for current cycle; limitations prose only |

Science locks unchanged: Track A **FAIL**, Track B **SUPPORTED_IMPROVEMENT**, no frozen/AUDIT edits, **API=0**.

**Navigation:** [`STATUS.md`](STATUS.md) · [`Q1_ROADMAP_4PHASE.md`](Q1_ROADMAP_4PHASE.md)
