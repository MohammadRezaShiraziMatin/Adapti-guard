# Quality roadmap — five phases (docs / process)

**Tip baseline:** `main` @ `30ddc75` (2026-09-23 process unlock)  
**Scope:** Documentation and admin/process clarity only. **API=0.** No merge from agents.

This roadmap separates **process unlocks** (what contributors may do on tip without changing science) from **science locks** (immutable evidence and honest dual-track outcomes).

---

## Science locks (kept in every phase)

| Lock | Rule |
| --- | --- |
| Frozen packs | Do not edit `datasets/frozen/**` bytes or quoted SHA-256 in AUDIT/verdict. |
| Live eval artifacts | Do not edit `experiments/real_llm_eval/**` AUDIT, verdict, or reported numbers. |
| Track A | VNEXT confirmation **FAIL** remains FAIL (`vnext_confirm_v1.0`, SHA `523c8818…`). |
| Track B | Phase-1 LIVE **SUPPORTED_IMPROVEMENT** on `phase1_confirm_v1` — scoped; **does not reverse Track A**. |
| Live LLM | No OpenRouter / API calls unless explicit human budget sign-off (default **API=0**). |
| Metrics | No invented statistics; cite frozen AUDIT or mark **BLOCKING GAP**. |
| Merge / venue | **Human-only:** no agent merge, no venue upload, no PR close via API. |

---

## P1 — Hygiene and truth docs (**done**, PR #73)

**Unlocks:** Refresh navigation (`START_HERE`, experiment status), publish this roadmap, resolve doc conflict markers if present (tip truth: dual-track FAIL + Track B scoped improvement).

**Deliverables:** `QUALITY_ROADMAP_5PHASE.md`, `STATUS.md`, minimal `START_HERE` pointer.

---

## P2 — D-22 taxonomy decision lock (names only; **done**, PR #73)

**Unlocks:** Lock **six** Confirmatory V2 `family_id` strings aligned to Track A frozen pack `datasets/frozen/vnext_confirm_v1` (see `DECISION_LOCK_D22_CONFIRMATORY_V2_TAXONOMY.md`).

**Still not locked:** Episode text, 151 attack allocation table, SAP, new dataset files, live eval.

**Does not unlock:** Building Confirmatory V2 episodes or changing historical n_attack=61 evidence.

---

## P3 — Manuscript claims polish (**done**, PR #73)

**Unlocks:** Wording pass on workshop/dual-track manuscript docs under `docs/paper/` — allowed/forbidden claims, cross-links, publisher-facing consistency with `CLAIMS_DUAL_TRACK.md`.

**Deliverables:** `docs/paper/CLAIMS_CHECKLIST.md`; tightened `workshop_vnext_fail/MANUSCRIPT.md`, README, `04_results.md` banners; submission packet Track B boundary.

**Locks kept:** All AUDIT numbers and FAIL/SUPPORTED_IMPROVEMENT outcomes unchanged.

---

## P4 — Artifact and reproducibility (**done**, PR #73)

**Unlocks:** Repro checklists, hash citation tables, offline verification steps (no LLM), alignment of `REPRODUCIBILITY_PACKAGE.md` with tip tree.

**Deliverables:** Refreshed [`REPRODUCIBILITY_PACKAGE.md`](REPRODUCIBILITY_PACKAGE.md); `APPENDIX_HASHES.md` dual-track + P1 mechanism rows; workshop README / `SUBMISSION_PACKET` pointers; `START_HERE` repro link.

**Locks kept:** No regeneration of eval outputs; simulation ≠ confirmatory live claims; SHAs cited only from existing freeze/AUDIT docs.

---

## P5 — Workshop submit checklist (no external upload) (**done**, PR #73)

**Unlocks:** Human checklist: merge order (`PR_STACK.md`), packet completeness, citation/hashes, **explicit** “human submits venue” steps — documentation only.

**Deliverables:** [`docs/paper/workshop_vnext_fail/SUBMISSION_CHECKLIST.md`](../paper/workshop_vnext_fail/SUBMISSION_CHECKLIST.md) · links from [`SUBMISSION_PACKET.md`](../paper/workshop_vnext_fail/SUBMISSION_PACKET.md) and workshop README.

**Locks kept:** Agents do not submit to arXiv/workshop; Track A FAIL narrative unchanged. No venue marked DONE.

---

## After P5 (human)

1. Review and **merge PR #73** (docs quality path).  
2. **Choose venue** and compile camera-ready from [`MANUSCRIPT.md`](../paper/workshop_vnext_fail/MANUSCRIPT.md).  
3. **Submit** via venue portal (HUMAN_ONLY).  
4. Optional: merge historical stack [#23–#44](../paper/workshop_vnext_fail/PR_STACK.md) per Matin’s merge strategy.

---

## Read order (publisher)

1. [`docs/START_HERE.md`](../START_HERE.md)  
2. [`STATUS.md`](STATUS.md) (this folder)  
3. [`docs/paper/CLAIMS_CHECKLIST.md`](../paper/CLAIMS_CHECKLIST.md)  
4. [`docs/paper/workshop_vnext_fail/MANUSCRIPT.md`](../paper/workshop_vnext_fail/MANUSCRIPT.md)  
5. [`DECISION_LOCK_D22_CONFIRMATORY_V2_TAXONOMY.md`](DECISION_LOCK_D22_CONFIRMATORY_V2_TAXONOMY.md)  
6. [`docs/paper/workshop_vnext_fail/SUBMISSION_CHECKLIST.md`](../paper/workshop_vnext_fail/SUBMISSION_CHECKLIST.md)  
7. [`docs/paper/dual_track/DUAL_TRACK_STATUS.md`](../paper/dual_track/DUAL_TRACK_STATUS.md)
