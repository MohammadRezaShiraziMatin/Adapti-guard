# Human review pass — Q1 findings manuscript (Matin)

**Author / reviewer:** Seyed Mohammadreza Shirazi Matin  
**Venue path:** **LOCKED** — Findings / workshop-style; see [`DECISION_LOCK_FINDINGS_VENUE.md`](DECISION_LOCK_FINDINGS_VENUE.md)  
**Canonical draft:** [`MANUSCRIPT.md`](MANUSCRIPT.md) · **Claims:** [`CLAIMS_MAP.md`](CLAIMS_MAP.md)  
**Automated gate:** `python3 docs/paper/q1_findings/verify_q1_findings_facts.py` (exit 0 = number/hygiene PASS; **not** a substitute for this pass)

**Upload / submit:** **NOT DONE** — no portal or arXiv deposit by agents.

**Review status:** **READY** for Matin review (checklist below). Matin sign-off on this file is **HUMAN_ONLY** (optional checkbox edits in git after review).

---

## FAIL-first (abstract + conclusion)

- [ ] **Abstract** opens with methodology / dual-track framing, then states Track A **FAIL** (McNemar p=0.0625, δ̂ &lt; MSID, utility gate) **before** any Track B improvement language.
- [ ] **Abstract** does **not** say VNEXT “works,” solves prompt injection, SOTA, production-ready, or FAIL→PASS.
- [ ] **Conclusion** restates Track A **FAIL** first; contribution = protocol + confirmed negative + **scoped** Track B — **not** a fielded guard.
- [ ] **Conclusion** does **not** overturn Track A or merge tracks into one “win” narrative.

---

## Track A ≠ Track B (no reversal)

- [ ] Track A (VNEXT-ADAPT, `vnext_confirm_v1.0`) and Track B (PHASE1-CORE, `phase1_confirm_v1`) stay in **separate labeled** sections/tables.
- [ ] Explicit sentence (or equivalent): Track B **SUPPORTED_IMPROVEMENT** **does not reverse** Track A **FAIL** and is **not** a VNEXT pass.
- [ ] No single unlabeled table mixing Track A ASR with Track B rates.
- [ ] Layer A diagnostic treated as **third pack** — not pooled with confirmatory ASR.

---

## Offline δ̂ CI (Track A) — labeled, not-in-AUDIT

- [ ] Track A point δ̂=**0.0820** matches frozen AUDIT; **95% CI [0.0164, 0.1639]** cited only as **offline / recomputed** ([`artifacts/vnext_delta_ci_offline.json`](artifacts/vnext_delta_ci_offline.json)).
- [ ] Prose does **not** imply the Track A δ̂ CI was in original AUDIT.
- [ ] High power (~99% at MSID under b01=0 scaffold) in [`artifacts/vnext_track_a_power_sensitivity.json`](artifacts/vnext_track_a_power_sensitivity.json) is labeled **offline**; **FAIL unchanged** — not “underpowered for MSID” as primary excuse.

---

## Future Work (Q1-P2 scope)

- [ ] Confirmatory **V2**, **AgentDojo-class** loops, **external SOTA baselines**, and mechanism-pack **live** eval appear only as **Future Work** (optional Phase 3 after budget) — **not** as done evidence.
- [ ] Phase 3 **not** claimed complete; **API=0** / live **NOT AUTHORIZED** unless separate locks signed.

---

## Author + claim ceiling

- [ ] Author name: **Seyed Mohammadreza Shirazi Matin**; contact `mrshirazimatin@gmail.com` where the packet requires it.
- [ ] Every abstract/conclusion sentence maps to **Allowed** IDs in [`CLAIMS_MAP.md`](CLAIMS_MAP.md) (especially Q1-A1–A3, Q1-B1, Q1-B3, Q1-M2); none from **Forbidden** (Q1-F1–F9).
- [ ] [`CONTRIBUTION_CEILING.md`](CONTRIBUTION_CEILING.md) linked or reflected in intro/limitations — no ceiling breach.

---

## Packet hygiene (non-science)

- [ ] [`SUBMISSION_PACKET.md`](SUBMISSION_PACKET.md) cover bullets remain FAIL-first; venue strategy matches [`DECISION_LOCK_FINDINGS_VENUE.md`](DECISION_LOCK_FINDINGS_VENUE.md).
- [ ] Run verifier: `python3 docs/paper/q1_findings/verify_q1_findings_facts.py` → **PASS** on tip `main`.

---

## After this pass (human only)

1. Optional **arXiv** timestamp — [`ARXIV_PACKET.md`](ARXIV_PACKET.md) (**HUMAN_ONLY**; still **NOT DONE** until Matin uploads).
2. Watch **ICLR 2027 workshop** CFPs (~Feb 2027 papers) and/or **next ARR → Findings 2027** when the cycle opens.
3. Camera-ready conversion to venue template — **HUMAN_ONLY** / **NOT DONE**.

**No acceptance guarantee** at any venue.
