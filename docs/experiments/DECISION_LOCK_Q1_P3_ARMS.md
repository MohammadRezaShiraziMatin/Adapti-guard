# Decision lock Q1-P3 — Optional live arms (pre-registration scaffold)

**Decision ID:** Q1-P3  
**Status:** **LOCKED** (design / gates / **priority order** — **no runs authorized**)
**Date (UTC):** 2026-09-23 (priority order revised, Matin-approved framing)
**Author:** Seyed Mohammadreza Shirazi Matin  
**Mode:** Documentation only. **API=0** until explicit human budget. **No** merge, venue upload, or AUDIT edits from agents.

**Companion:** [`Q1_ROADMAP_4PHASE.md`](Q1_ROADMAP_4PHASE.md) · [`DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md`](DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md) · [`Q1_P3_PRIORITY.md`](Q1_P3_PRIORITY.md) · [`P3_AGENTS_CONSOLIDATED.md`](P3_AGENTS_CONSOLIDATED.md) · [`LIVE_EVALUATION_GATE.md`](../research/LIVE_EVALUATION_GATE.md)

---

## Explicit (this revision)

| Rule | Lock |
| --- | --- |
| Track A VNEXT FAIL | **Immutable** — no arm reverses or amends `VNEXT_CONFIRM/20260914-133147/` |
| Track B | **Does not reverse** Track A |
| Q1 acceptance | **No guarantee** — Phase 3 supplements do not promise venue accept |
| API / budget | **TBD — Matin** (human); default **API=0** |
| Authorization | **This edit does not authorize any live run**, dataset bytes, or V2 pack build |

**Phase 3 is not done** until Matin signs budget **and** a run completes with a **new** immutable AUDIT folder.

---

## Priority order (budget-limited; Matin-approved framing)

When budget is constrained, execute or fund arms in this order. Full one-pager: [`Q1_P3_PRIORITY.md`](Q1_P3_PRIORITY.md).

| Rank | ID | Arm | Notes |
| --- | --- | --- | --- |
| 1 | **P3-1** | External baseline (same protocol) | **First** if small budget |
| 2 | **P3-5** | Mechanism live (`p1_mechanism_v1.0.0`) | Attribution on frozen pack; not AgentDojo |
| 3 | **P3-3/4** | Multi-model robustness (**merged**) | One arm: multi-model + Target/Judge variants; **new human lock** for model IDs before run |
| 4 | **P3-2** | Confirmatory V2 + larger n | **Last** / heaviest; separate pack freeze + SAP; Q1-P2 Future Work until authorized |

---

## Immutable (all arms)

| Lock | Rule |
| --- | --- |
| Track A VNEXT FAIL | **Immutable** — no re-run to amend `VNEXT_CONFIRM/20260914-133147/` numbers or verdict |
| Retune-to-win | **Forbidden** — no threshold/detector/policy changes after seeing confirmatory outcomes |
| Target / Judge (default) | **`qwen/qwen-2.5-7b-instruct`** target · **`qwen/qwen-2.5-72b-instruct`** judge until **P3-3/4** human lock names other IDs |
| Claim mixing | Track labels mandatory; Track B **does not reverse** Track A |
| API spend | **HUMAN** budget placeholder — record approved USD cap and stop before run if exceeded |

---

## P3-1 — External baseline (optional; **priority 1**)

**Design packet (pre-run):** [`DECISION_LOCK_Q1_P3_1_BASELINE.md`](DECISION_LOCK_Q1_P3_1_BASELINE.md) · candidates [`P3_1_BASELINE_CANDIDATES.md`](P3_1_BASELINE_CANDIDATES.md) — **NOT AUTHORIZED TO RUN** until Matin budget + signed pre-run fields.

**May run only after:** Human budget + completed Q1-P3-1 lock checklist + gate checklist.

| Item | Lock |
| --- | --- |
| Purpose | **Commensurate comparison** vs an **external defense** under **same** protocol and **same episode IDs** on a declared frozen pack (Track A or B pack id fixed before run) |
| Goal wording (**required**) | Comparison vs external defense on same IDs — **NOT** “prove AdaptiGuard adds X,” superiority, or SOTA |
| Success (design) | Pre-specified: report ASR/U/McNemar vs B0 and vs external arm on **same episode IDs**; no pooled headline with other tracks |
| Failure / stop | Judge API failure → same-ID repair rule as VNEXT; hash mismatch → abort; do not impute ASR=0 |
| **Not allowed** | Claim SOTA or AdaptiGuard superiority; change Track A FAIL; fabricate expected ASR in this doc |

---

## P3-5 — `p1_mechanism_v1.0.0` live eval (optional; **priority 2**)

**Design packet:** [`DECISION_LOCK_Q1_P3_5_MECHANISM.md`](DECISION_LOCK_Q1_P3_5_MECHANISM.md) — **NOT AUTHORIZED TO RUN**.

**May run only after:** [`LIVE_EVALUATION_GATE.md`](../research/LIVE_EVALUATION_GATE.md) + budget + pack SHA verified on execution branch.

| Item | Lock |
| --- | --- |
| Pack | `datasets/frozen/p1_mechanism_v1.0.0/` (SHA per freeze record) |
| Status today | **`live_evaluated=false`** |
| Purpose | **Attribution** / mechanism-surface evidence on the existing frozen pack |
| Success (design) | New AUDIT folder with hash-locked config; claims limited to mechanism benchmark scope |
| **Not allowed** | AgentDojo-class claim; replace Track A/B confirmatory evidence |

---

## P3-3/4 — Multi-model robustness (optional; **priority 3**; **merged arm**)

**Scaffold:** [`DECISION_LOCK_Q1_P3_3_MULTIMODEL.md`](DECISION_LOCK_Q1_P3_3_MULTIMODEL.md) — model IDs **HUMAN TBD**; default 7b≠72b until superseded.

**May run only after:** Human budget + **new human lock document** listing approved Target and Judge model IDs (providers, versions) + gate checklist.

| Item | Lock |
| --- | --- |
| Scope | **Single arm** — merges “multi-model evaluation” and “Target/Judge variant” sweeps into **one** pre-registered design and **one** AUDIT narrative |
| Default until lock | Remains **`qwen/qwen-2.5-7b-instruct`** target · **`qwen/qwen-2.5-72b-instruct`** judge (no run under P3-3/4 without the new lock) |
| Success (design) | Report estimands per locked model pair; no unlabeled pooling with Track A/B confirmatory tables |
| **Not allowed** | Ad hoc model shopping; implying robustness without pre-locked IDs; reversing Track A FAIL |

---

## P3-2 — Confirmatory V2 pack + live (optional; **priority 4**; **not executable in this lock**)

**May run only after:** Separate **pack freeze PR**, allocation/SAP human locks beyond Q1-P2 naming, budget, and new decision record superseding Q1-P2 “Future Work” for V2 **only when authorized**.

| Item | Lock |
| --- | --- |
| Taxonomy names | D-22 six `family_id` strings ([`DECISION_LOCK_D22_CONFIRMATORY_V2_TAXONOMY.md`](DECISION_LOCK_D22_CONFIRMATORY_V2_TAXONOMY.md)) |
| Allocation when built | Q1-P2 +1 → `PRIVILEGE_EXFIL` rule (design only until freeze) |
| Weight | **Last** / heaviest budget item |
| This Q1-P3 doc | **Does not** authorize dataset bytes, episode bodies, SAP execution, or live eval for V2 **by itself** — Q1-P2 §A remains Future Work until superseded |

---

## Stop rules (any live arm)

1. Hash mismatch on frozen pack → **stop** (no ad hoc pack).
2. Budget cap reached → **stop** (partial runs not merged into confirmatory claims).
3. Any attempt to re-test Track A VNEXT on `vnext_confirm_v1.0` for a “win” → **forbidden** (new experiment id ≠ amending FAIL AUDIT).
4. Outcomes feed **new** AUDIT paths only; update claims via [`CLAIMS_CHECKLIST.md`](../paper/CLAIMS_CHECKLIST.md).

---

## Success criteria (process — no fabricated ASR)

| Criterion | Meaning |
| --- | --- |
| Immutable AUDIT | New folder under `experiments/real_llm_eval/` written once; not edited in place |
| Pre-registration | Arm id (**P3-1** … **P3-2**), pack SHA, treatments, and stop rules cited in run request **before** API calls |
| Honest reporting | Results labeled by arm; FAIL/SUPPORTED_IMPROVEMENT outcomes on **historical** tracks unchanged |
| Optional Q1 manuscript supplement | Only after Matin adds AUDIT citation to findings draft — not assumed in this lock |

---

## API budget (human placeholder)

| Field | Value |
| --- | --- |
| Approved USD cap | **TBD — Matin** |
| Default until signed | **API=0** |
| Agents | Never approve spend or call OpenRouter |

**Navigation:** [`STATUS.md`](STATUS.md) · [`Q1_BLOCKER_MATRIX.md`](Q1_BLOCKER_MATRIX.md) · [`Q1_P3_PRIORITY.md`](Q1_P3_PRIORITY.md)
