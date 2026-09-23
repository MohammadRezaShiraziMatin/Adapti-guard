# Workshop submission checklist (human review)

**Status:** Documentation complete for the 5-phase quality path (PR [#73](https://github.com/MohammadRezaShiraziMatin/adapti-guard/pull/73)).  
**Agents:** do **not** merge, upload to EasyChair/OpenReview/arXiv, or run live LLM eval.

**Legend:** **DONE** = content exists and matches frozen AUDIT · **READY** = draft in repo; human may adapt to venue template · **HUMAN_ONLY** = Matin must decide/act · **BLOCKED** = known gap; do not invent numbers.

Companion packet (cover letter, camera-ready map, titles): [`SUBMISSION_PACKET.md`](SUBMISSION_PACKET.md).

---

## A. Venue and submission mechanics

| Item | Status | Pointer / note |
| --- | --- | --- |
| Target venue / track | **HUMAN_ONLY** | **TBD.** Fit notes: [`PR_STACK.md`](PR_STACK.md) § venue fit; negative-result / evaluation track preferred. |
| OpenReview / EasyChair / email upload | **HUMAN_ONLY** | Not executed. This repo does not perform external submit. |
| arXiv deposit | **HUMAN_ONLY** | Optional per [`CITATION.md`](CITATION.md); package does not upload by itself. |
| LaTeX/PDF camera-ready from Markdown | **HUMAN_ONLY** | Source: [`MANUSCRIPT.md`](MANUSCRIPT.md). Template (LNCS/ACL/IEEE/CEUR) is venue-specific. |
| Page limits / anonymization / copyright form | **HUMAN_ONLY** | Map sections via [`SUBMISSION_PACKET.md`](SUBMISSION_PACKET.md) §2. |
| Merge docs quality PR **#73** to `main` | **HUMAN_ONLY** | Branch `cursor/docs-quality-phase1-2-1d46`. Agents never merge. |
| Merge historical stack **#23–#44** (optional) | **HUMAN_ONLY** | Order / CLOSE-SKIP: [`PR_STACK.md`](PR_STACK.md). Separate from #73 unless Matin squashes strategy differs. |
| Budget for any **future** live eval | **HUMAN_ONLY** | Default **API=0**; gate: [`docs/research/LIVE_EVALUATION_GATE.md`](../../research/LIVE_EVALUATION_GATE.md). |

---

## B. Manuscript content (workshop / LNCS-style)

| Item | Status | Pointer / note |
| --- | --- | --- |
| Title (FAIL-consistent) | **READY** | Default: [`MANUSCRIPT.md`](MANUSCRIPT.md) H1 · alternates: [`SUBMISSION_PACKET.md`](SUBMISSION_PACKET.md) §3 |
| Abstract (conservative; headline set D) | **READY** | [`MANUSCRIPT.md`](MANUSCRIPT.md) Abstract · map: [`CLAIMS_MAP.md`](CLAIMS_MAP.md) §D |
| Keywords | **READY** | [`CITATION.cff`](../../../CITATION.cff) (LLM security, prompt injection, adaptive defense, negative result, evaluation framework) |
| Author name | **DONE** | **Seyed Mohammadreza Shirazi Matin** — [`MANUSCRIPT.md`](MANUSCRIPT.md) header · [`SUBMISSION_PACKET.md`](SUBMISSION_PACKET.md) §1 |
| Author email | **DONE** | `mrshirazimatin@gmail.com` (same files) |
| Affiliations / institution line | **HUMAN_ONLY** | Not invented in packet (“AI Security · LLM-agent defense” is descriptive only). Add per venue rules. |
| Introduction + confirmatory RQ | **READY** | [`MANUSCRIPT.md`](MANUSCRIPT.md) §1 — official answer **no** |
| Related work | **READY** | §2 — not AgentDojo leaderboard |
| Threat model | **READY** | §3 — label-blind; authored corpus |
| Method + intervention taxonomy | **READY** | §4 — \(\mathcal{W}\) = `correct_block`, `correct_tool_deny` only |
| Protocol (Layer A vs VNEXT separate) | **READY** | §5 — do not pool tracks |
| Results (AUDIT numbers) | **DONE** | §6 — values from `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md` |
| Failure analysis | **READY** | §7 — three independent FAIL reasons |
| Limitations | **READY** | §8 — small-N, heuristic detector, Target≠Judge, simulation, AgentDojo-class, judge API |
| Ethics | **READY** | §9 — dual-use corpus; anti-overclaim |
| Conclusion | **READY** | FAIL restated; no retune-into-win |
| References (non-archival evidence list) | **READY** | §10 + [`APPENDIX_HASHES.md`](APPENDIX_HASHES.md) as primary evidence |

---

## C. Claims, dual-track, and forbidden language

| Item | Status | Pointer / note |
| --- | --- | --- |
| Track A VNEXT = **FAIL** (immutable) | **DONE** | AUDIT + [`DUAL_TRACK_STATUS.md`](../dual_track/DUAL_TRACK_STATUS.md) |
| Track B **SUPPORTED_IMPROVEMENT** (scoped) | **DONE** | Separate pack; **does not reverse** Track A — [`CLAIMS_DUAL_TRACK.md`](../dual_track/CLAIMS_DUAL_TRACK.md) |
| Workshop packet scope (Track A + Layer A only) | **DONE** | Track B excluded from cover letter — [`SUBMISSION_PACKET.md`](SUBMISSION_PACKET.md) §1 |
| Allowed / forbidden one-liners | **DONE** | [`../CLAIMS_CHECKLIST.md`](../CLAIMS_CHECKLIST.md) · workshop detail [`CLAIMS_MAP.md`](CLAIMS_MAP.md) |
| No ASR=0 / L3 / simulation as “solved” | **DONE** | [`MANUSCRIPT.md`](MANUSCRIPT.md) §6.1, §8; [`04_results.md`](../04_results.md) banner |
| Offline fact verifier | **DONE** | `python3 docs/paper/workshop_vnext_fail/verify_manuscript_facts.py` (expect PASS) |

---

## D. Artifacts, reproducibility, citation

| Item | Status | Pointer / note |
| --- | --- | --- |
| Frozen pack SHA-256 (VNEXT) | **DONE** | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` — [`APPENDIX_HASHES.md`](APPENDIX_HASHES.md) |
| Canonical AUDIT path | **DONE** | `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/` |
| Repro hub (offline, API=0) | **DONE** | [`docs/experiments/REPRODUCIBILITY_PACKAGE.md`](../../experiments/REPRODUCIBILITY_PACKAGE.md) |
| Config snapshot (Target≠Judge, cache off) | **DONE** | [`CONFIGS_SNAPSHOT.md`](CONFIGS_SNAPSHOT.md) |
| Software + manuscript citation stubs | **DONE** | [`CITATION.md`](CITATION.md) · [`CITATION.cff`](../../../CITATION.cff) |
| Persian next-step note (human) | **READY** | [`SUBMIT_NEXT_FA.md`](SUBMIT_NEXT_FA.md) |

---

## E. Known blockers (do not fabricate)

| Item | Status | Pointer / note |
| --- | --- | --- |
| Track A δ̂ 95% CI in AUDIT | **BLOCKED** | Not in frozen AUDIT — see [`DUAL_TRACK_STATUS.md`](../dual_track/DUAL_TRACK_STATUS.md); do not invent |
| Venue-specific PDF | **HUMAN_ONLY** | Depends on chosen template |
| External submit confirmation | **HUMAN_ONLY** | No DONE until Matin uploads |

---

## F. Pre-submit smoke (human runs locally)

```bash
python3 docs/paper/workshop_vnext_fail/verify_manuscript_facts.py
sha256sum datasets/frozen/vnext_confirm_v1/dataset.jsonl
# expect 523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518
```

Full pytest list: [`REPRODUCIBILITY_PACKAGE.md`](../../experiments/REPRODUCIBILITY_PACKAGE.md) (**API=0**; requires `scipy` for McNemar unit tests).

---

## G. Explicit HUMAN_ONLY summary

1. **Merge** PR #73 (and optionally stack #23–#44) — not agents.  
2. **Choose venue** and submission portal — TBD.  
3. **Compile/upload** camera-ready — not in repo automation.  
4. **Approve budget** for any future live LLM eval — separate from this FAIL packet.  

No item in this file marks venue upload as **DONE**.
