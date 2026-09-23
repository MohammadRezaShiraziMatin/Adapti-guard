# Q1 findings manuscript (dual-track)

**Purpose:** Findings-length English manuscript for the **Q1 / dual-track ladder** — broader than the short [`workshop_vnext_fail`](../workshop_vnext_fail/README.md) negative-result packet, but bound by the same frozen AUDIT numbers and [`DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md`](../../experiments/DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md).

**Author:** Seyed Mohammadreza Shirazi Matin · `mrshirazimatin@gmail.com`

**Mode:** Documentation draft only. **API=0.** Agents do **not** merge, upload to a venue, or run live LLM eval.

---

## Claim ceiling (this cycle)

| Supports | Does not support |
| --- | --- |
| Dual-track evaluation methodology (hash-locked packs, Target ≠ Judge, utility gates) | Solve prompt injection, SOTA, production-ready, FAIL→PASS |
| Track A **FAIL** — confirmed negative for VNEXT-ADAPT under pre-registered MSID | One unlabeled table mixing Track A ASR with Track B harmful-action rates |
| Track B **SUPPORTED_IMPROVEMENT** (scoped) on a **different** pack/treatment | Track B reversing Track A; VNEXT “works” |
| Layer A **CLOSED diagnostic** (detector lift; adaptive not significant) | Simulation / L3 oracle ASR=0 as live confirmatory wins |
| Confirmatory V2, AgentDojo loops, external baselines, mechanism live | **Future Work** per Q1-P2 (optional P3 after budget) |

**No Q1 acceptance guarantee.** Venue **TBD**. Submit = **HUMAN_ONLY**.

---

## Files

| File | Role |
| --- | --- |
| [`MANUSCRIPT.md`](MANUSCRIPT.md) | Findings draft (~8–12 page markdown structure) |
| [`CLAIMS_MAP.md`](CLAIMS_MAP.md) | Allowed / forbidden one-liners for this manuscript |
| [`SUBMISSION_PACKET.md`](SUBMISSION_PACKET.md) | Cover letter bullets, title options, section map, HUMAN_ONLY submit |
| [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md) | Human pre-submit checklist (upload **NOT DONE**) |
| [`FIGURES.md`](FIGURES.md) | Dual-track mermaid + claim-ceiling caption text |
| [`references.bib`](references.bib) | Related-work BibTeX stubs |
| [`VENUE_SHORTLIST.md`](VENUE_SHORTLIST.md) | Planning-only venue fit (no agent submit) |
| [`ARXIV_PACKET.md`](ARXIV_PACKET.md) | arXiv HUMAN_ONLY steps (upload **NOT DONE** in repo) |
| [`ARXIV_ABSTRACT.txt`](ARXIV_ABSTRACT.txt) | Plain-text abstract for arXiv form |
| [`BUILD_PDF.md`](BUILD_PDF.md) | Local pandoc PDF build from `MANUSCRIPT.md` |
| [`QUALITY_GAPS.md`](QUALITY_GAPS.md) | Findings vs main bar; Phase 3 value (honest) |
| [`artifacts/vnext_delta_ci_offline.json`](artifacts/vnext_delta_ci_offline.json) | Offline Track A δ̂ 95% CI (not in AUDIT) |
| [`artifacts/vnext_track_a_power_sensitivity.json`](artifacts/vnext_track_a_power_sensitivity.json) | Offline McNemar power / sensitivity (n=61) |
| [`CONTRIBUTION_CEILING.md`](CONTRIBUTION_CEILING.md) | What the paper is / is not (abstract-safe) |
| [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) | SHAs, AUDIT paths, offline scripts, API budget boundary |
| [`verify_q1_findings_facts.py`](verify_q1_findings_facts.py) | Claim/number gate (exit 0 = PASS) |

---

## Pointers

- Roadmap: [`docs/experiments/Q1_ROADMAP_4PHASE.md`](../../experiments/Q1_ROADMAP_4PHASE.md) · blockers [`Q1_BLOCKER_MATRIX.md`](../../experiments/Q1_BLOCKER_MATRIX.md)
- Dual-track status: [`docs/paper/dual_track/DUAL_TRACK_STATUS.md`](../dual_track/DUAL_TRACK_STATUS.md) · [`CLAIMS_DUAL_TRACK.md`](../dual_track/CLAIMS_DUAL_TRACK.md)
- Global one-liners: [`docs/paper/CLAIMS_CHECKLIST.md`](../CLAIMS_CHECKLIST.md)
- Workshop packet (Track A focus, shorter): [`workshop_vnext_fail/MANUSCRIPT.md`](../workshop_vnext_fail/MANUSCRIPT.md)
- Hashes / repro: [`workshop_vnext_fail/APPENDIX_HASHES.md`](../workshop_vnext_fail/APPENDIX_HASHES.md) · [`docs/experiments/REPRODUCIBILITY_PACKAGE.md`](../../experiments/REPRODUCIBILITY_PACKAGE.md)

**Phase 3 (controlled live evidence):** **Not done** — pending human budget; this folder is Phase 4 **draft** only (PR #74).
