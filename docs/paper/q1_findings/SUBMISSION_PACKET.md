# Submission packet — Q1 dual-track findings manuscript

**Not a merge. Not a venue upload. Not arXiv deposit by agents. Not live eval.**

Human camera-ready / cover packet for a **findings-length** paper. **Venue strategy LOCKED:** Findings / workshop-style (not ICLR 2027 main) — [`DECISION_LOCK_FINDINGS_VENUE.md`](DECISION_LOCK_FINDINGS_VENUE.md). Agents do not merge PRs or upload PDFs. **API=0** for eval. **Upload NOT DONE.**

**Checklist:** [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md) · **Human review:** [`HUMAN_REVIEW_PASS.md`](HUMAN_REVIEW_PASS.md) · **Figures:** [`FIGURES.md`](FIGURES.md) · **BibTeX:** [`references.bib`](references.bib) · **Venue planning:** [`VENUE_SHORTLIST.md`](VENUE_SHORTLIST.md) · **arXiv (HUMAN_ONLY):** [`ARXIV_PACKET.md`](ARXIV_PACKET.md) · **PDF build:** [`BUILD_PDF.md`](BUILD_PDF.md)

| Field | Binding value |
| --- | --- |
| Framing | **HONEST DUAL-TRACK FINDINGS** (FAIL-first narrative) |
| Track A | VNEXT **FAIL** · H1 qualified win = **NO** · pack `523c8818…` |
| Track B | **SUPPORTED_IMPROVEMENT** (scoped) · **does not reverse** Track A · pack `c789811a…` |
| Canonical text | [`MANUSCRIPT.md`](MANUSCRIPT.md) |
| Claims boundary | [`CLAIMS_MAP.md`](CLAIMS_MAP.md) + [`../CLAIMS_CHECKLIST.md`](../CLAIMS_CHECKLIST.md) |
| Q1 scope lock | [`../../experiments/DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md`](../../experiments/DECISION_LOCK_Q1_P2_EVIDENCE_DESIGN.md) |
| Workshop sibling (Track A only, shorter) | [`../workshop_vnext_fail/SUBMISSION_PACKET.md`](../workshop_vnext_fail/SUBMISSION_PACKET.md) |

---

## 1. Cover letter bullets (English; expand for venue portal)

Copy and adapt; **lead with Track A FAIL**, then Track B scoped result, then methodology.

- **Subject:** Dual-track evaluation of cost-aware runtime intervention — confirmed negative (VNEXT) plus scoped Phase-1 improvement on a separate pack; not a defense product paper.
- **Track A (primary negative):** On `vnext_confirm_v1.0` (61+61), VNEXT-ADAPT vs B0 **FAILS** pre-registered criteria: McNemar p=0.0625 (not significant); δ̂=0.0820 &lt; MSID 0.20; U=0.9344 &lt; 0.95. Qualified win = **NO**.
- **Attribution (Track A):** Five b10 = `correct_block`; 53 `insufficient_intervention`; no “marginally significant therefore confirmed.”
- **Track B (separate scoped result):** On `phase1_confirm_v1`, PHASE1-CORE vs B0 meets Phase-1 MSID with utility eligible per AUDIT (δ̂=0.4426, CI in AUDIT)—**different treatment and pack**; **not** a VNEXT pass and **not** a reversal of Track A FAIL.
- **Layer A:** Closed diagnostic (detector lift; adaptive not significant)—**third pack**; do not pool ASR with confirmatory tracks.
- **Methodology contribution:** Hash-locked dual-track protocol, intervention taxonomy, utility gates, Target ≠ Judge, frozen AUDIT artifacts.
- **Explicit non-claims:** Does not solve prompt injection; not SOTA; not production-ready; not AgentDojo leaderboard; Confirmatory V2 / baselines / mechanism live = **Future Work** (Q1-P2).
- **Reproducibility:** Offline `verify_manuscript_facts.py`; hashes in [`../workshop_vnext_fail/APPENDIX_HASHES.md`](../workshop_vnext_fail/APPENDIX_HASHES.md).
- **Submit:** **HUMAN_ONLY** — this packet does not upload the paper.

**Author:** Seyed Mohammadreza Shirazi Matin · `mrshirazimatin@gmail.com`  
**Repository:** https://github.com/MohammadRezaShiraziMatin/adapti-guard

---

## 2. Suggested title options (FAIL-first; dual-track honest)

| # | Title | Use when |
| --- | --- | --- |
| A | Dual-Track Evaluation of Cost-Aware Runtime Intervention for LLM Prompt Injection: A Confirmed Negative and a Scoped Phase-1 Improvement | Default ([`MANUSCRIPT.md`](MANUSCRIPT.md) H1) |
| B | Hash-Locked Dual-Track Confirmation for Adaptive Runtime LLM Defense: VNEXT Fails MSID; Phase-1 Improvement Is Scoped and Non-Reversing | Venue wants explicit FAIL + dual-track in title |
| C | When Not to Merge Tracks: A Confirmed VNEXT Negative and Separate Phase-1 Evidence under Pre-Registered Gates | Evaluation / methodology emphasis |

**Do not use** titles implying solve-PI, SOTA, production deployment, or “VNEXT confirmed.”

---

## 3. Section → camera-ready map

| Camera-ready item | Source | Must keep |
| --- | --- | --- |
| Title | §2 options or MANUSCRIPT H1 | FAIL-first; dual-track honesty |
| Abstract | MANUSCRIPT **Abstract** | Track A FAIL before Track B scoped paragraph |
| Introduction | §1 | Track A answer **NO** first in RQ list |
| Related work | §2 | Not AgentDojo leaderboard; cite [`references.bib`](references.bib) |
| Threat model | §3 | Authored frozen corpus |
| Method / dual-track table | §4 | Separate packs/SHAs/AUDIT paths |
| Protocol | §5 | Target ≠ Judge; δ̂ CI gap labeled |
| Results Track A | §6.1 | FAIL numbers from AUDIT only |
| Results Track B | §6.2 | Scoped; non-reversal sentence |
| Layer A | §6.3 | Diagnostic only |
| Failure analysis | §7 | Track A primary |
| Limitations | §8 | Q1 blocker matrix dispositions |
| Ethics | §9 | No oversell |
| Reproducibility | §10 | Do not rerun to amend verdict |
| Conclusion | §11 | FAIL-first, then scoped B, then methodology |
| References | §References + `references.bib` | Evidence = AUDIT, not bib alone |
| Figure 1 | [`FIGURES.md`](FIGURES.md) mermaid | Separate tracks |
| Claims | [`CLAIMS_MAP.md`](CLAIMS_MAP.md) | No forbidden paraphrase |

**Compile hygiene:** If abstract length is limited, shorten Layer A sentence—not Track A FAIL numbers, not “does not reverse Track A.”

---

## 4. HUMAN_ONLY submit steps (not executed in-repo)

1. Pick venue / CFP — see [`VENUE_SHORTLIST.md`](VENUE_SHORTLIST.md) (verify deadlines on official sites; **do not** rush ICLR 2027 main).
2. Matin review: [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md) + [`CLAIMS_MAP.md`](CLAIMS_MAP.md).
3. Convert markdown → venue LaTeX/Word; include Figure 1 from mermaid export.
4. `\bibliography{references}` or paste from [`references.bib`](references.bib); verify OWASP release note if needed.
5. Run offline: `python3 docs/paper/workshop_vnext_fail/verify_manuscript_facts.py`.
6. Upload via venue portal (**human**). **Do not** mark upload DONE in git unless Matin confirms.
7. Optional: arXiv preprint only with explicit Matin approval (separate from this packet).

**Phase 3:** Optional live supplements require **new** AUDIT folders after budget—**not** claimed in current draft.

---

## 5. Artifact paths for reviewers

| Artifact | Path |
| --- | --- |
| Track A AUDIT | `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md` |
| Track B AUDIT | `experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/AUDIT.md` |
| Dual-track status | `docs/paper/dual_track/DUAL_TRACK_STATUS.md` |
| Q1 roadmap / blockers | `docs/experiments/Q1_ROADMAP_4PHASE.md`, `Q1_BLOCKER_MATRIX.md` |

**Do not merge from this file.** Draft on tip `main` @ `0469fbc` (PR #74 + #75 merged; venue lock). Human review [`HUMAN_REVIEW_PASS.md`](HUMAN_REVIEW_PASS.md) and venue submit remain **HUMAN_ONLY** / **NOT DONE**.
