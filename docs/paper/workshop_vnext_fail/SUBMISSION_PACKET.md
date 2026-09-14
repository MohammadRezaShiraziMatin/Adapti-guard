# Submission packet — VNEXT FAIL (workshop / evaluation track)

**Not a merge. Not an arXiv or venue submit. Not a live eval. Not a retune.**

This file is a **human** camera-ready / cover packet for a workshop or evaluation track. Agents do not merge PRs, do not pick a venue, and do not upload the manuscript. LLM API for eval = **0**.

| Field | Binding value |
| --- | --- |
| Framing | **HONEST NEGATIVE RESULT** |
| Scientific outcome | VNEXT confirmation **STATUS = FAIL**. Qualified win (H1) = **NO** |
| Headline claim | Adaptive cost-aware intervention is **not confirmed** under pre-registered MSID `VNEXT-MSID-0.1` (δ = 0.20) |
| Canonical text | [`MANUSCRIPT.md`](MANUSCRIPT.md) |
| Claims boundary | [`CLAIMS_MAP.md`](CLAIMS_MAP.md) (headline set D only) |
| Pack SHA-256 | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` |
| Canonical AUDIT | `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md` |
| Parent closeout | PR [#33](https://github.com/Mohammadreza583/adapti-guard/pull/33) on `cursor/vnext-fail-workshop-closeout-ef12` |

Fail reasons (all three independently sufficient): `s5_mcnemar_not_significant`, `msid_not_met`, `s4_utility_ineligible`.

---

## 1. One-page cover letter (English; copy-paste)

Use this letter as-is for a **workshop / evaluation** track. Do not retitle it as a defense-product submission.

```
To: Workshop chairs / Evaluation-track program committee
From: Seyed Mohammadreza Shirazi Matin (shirazimatin@gmail.com)
Re: Honest negative result — adaptive cost-aware intervention not confirmed
Date: 2026-09-14

Dear Chairs and Reviewers,

Please consider this manuscript for a workshop or evaluation track as an
HONEST NEGATIVE RESULT. It is not a main-track defense paper, not a product
announcement, and not a claim that AdaptiGuard, B3_V4, or VNEXT-ADAPT is a
working runtime guard.

Question. Does a label-blind, cost-aware adaptive policy reduce
defense-attributed attack success versus no defense (B0) on a new,
hash-locked confirmation pack, while keeping benign utility U ≥ 0.95?

Official answer. No. On frozen pack vnext_confirm_v1.0 (61 attack + 61
benign; SHA-256
523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518),
B0 ASR is 0.9508 (58/61) and VNEXT-ADAPT ASR is 0.8689 (53/61).
Intervention-mediated McNemar is b10 = 5, b01 = 0, exact two-sided
p = 0.0625 (α = 0.05) — not statistically significant. The paired effect
δ̂ = 0.0820 is below the pre-registered MSID of 0.20. Treatment utility
U = 0.9344 fails the co-primary gate U ≥ 0.95 (false blocks = 1).
Qualified win (H1) is NO. Fail reasons: s5_mcnemar_not_significant,
msid_not_met, s4_utility_ineligible.

Attribution. All five b10 events are taxonomy correct_block (A3).
insufficient_intervention = 53. Target refusals are not counted as
defense wins. We do not describe p = 0.0625 as “marginally significant
therefore confirmed,” as PARTIAL, or as a trend toward a win.

Layer A (CLOSED diagnostic, different pack). Detector v4 lifts TEST
recall/AUROC without TEST retuning; adaptive B3_V4 remains a
non-significant ASR change (McNemar p = 0.125). Those numbers must not
be pooled with VNEXT judge ASR.

What we ask you to review. Honesty of the FAIL; a hash-locked protocol
with intervention taxonomy, pre-registered MSID, and a utility gate;
inspectable artifacts (frozen JSONL + AUDIT). The reusable contribution
is the evaluation protocol, not a confirmed defense.

What we do not ask. Credit for a useful runtime intervention; SOTA;
production-ready status; or a camera-ready “AdaptiGuard works” narrative.

We have not retuned thresholds, increased N, edited frozen packs, or
changed the MSID after unblinding. This cover letter does not itself
submit the paper; venue choice and upload remain human actions.

Sincerely,
Seyed Mohammadreza Shirazi Matin
Canonical manuscript: docs/paper/workshop_vnext_fail/MANUSCRIPT.md
Canonical AUDIT: experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md
Repository: https://github.com/Mohammadreza583/adapti-guard
```

---

## 2. Camera-ready checklist (maps to `MANUSCRIPT.md`)

Venue page limits, template (ACL/IEEE/CEUR), anonymization, and copyright forms are **human / venue** items. This table only maps package sections so a camera-ready compile does not invent a new claim set.

| Camera-ready item | Source in [`MANUSCRIPT.md`](MANUSCRIPT.md) | Must keep |
| --- | --- | --- |
| Title | H1 (line 1). Pick one option from §3 of this packet if the venue wants a shorter title. | FAIL / “not confirmed” / negative-result stance |
| Authors / email | Header: Seyed Mohammadreza Shirazi Matin · `shirazimatin@gmail.com` | No extra affiliations invented here |
| Status banner | Lines under the header: STATUS = FAIL; qualified win = NO; Layer A CLOSED diagnostic | Do not delete |
| Protocol / pack / AUDIT identities | Header bullets + §5.4 + §10 | SHA-256 `523c8818…`; MSID 0.20; AUDIT path |
| Abstract | **Abstract** | Headline set D from [`CLAIMS_MAP.md`](CLAIMS_MAP.md) §D (five sentences). No win paraphrase |
| Introduction / RQ | **§1 Introduction** | Confirmatory question; official answer **no**; no extra N / no retune |
| Related work | **§2 Related Work** | Not AgentDojo leaderboard; complementary to Llama Guard / StruQ / SecAlign |
| Threat model | **§3 Threat Model** | Label-blind defender; authored frozen corpus, not live adaptive red team |
| Method / arms / taxonomy | **§4 Method** (§4.1 stack, §4.2 arms, §4.3 \(\mathcal{W}\)) | `correct_block` / `correct_tool_deny` only; A1 refusals are not wins |
| Protocol (two tracks) | **§5 Experimental Protocol** | Layer A vs VNEXT stay unlabeled-separate; H0/H1/MSID/stop rules |
| Layer A results | **§6.1** | Diagnostic only; claims A1–A12 wording |
| VNEXT results | **§6.2** | Claims V1–V10; tables from AUDIT; p = 0.0625 not significant |
| Failure analysis | **§7** | Three independently sufficient FAIL reasons |
| Limitations | **§8** | Single Target/Judge; synthetic packs; n=61 powered for MSID 0.20 not small effects |
| Ethics | **§9** | Dual-use note; overstating FAIL as “promising defense” is itself unethical |
| Reproducibility | **§10** | Offline commands; **do not rerun live eval to change the verdict** |
| Conclusion | **Conclusion** | Repeat FAIL; “report the negative result; do not retune it into a win” |
| References | **References (workshop, non-archival)** | Evidence is AUDIT/packs, not the bibliography |
| Artifact appendix | [`APPENDIX_HASHES.md`](APPENDIX_HASHES.md), [`CONFIGS_SNAPSHOT.md`](CONFIGS_SNAPSHOT.md) | Hashes in §5 of this packet |
| Claims / forbidden language | [`CLAIMS_MAP.md`](CLAIMS_MAP.md) | See §4 of this packet |
| Citation stubs | [`CITATION.md`](CITATION.md) | Software vs unpublished negative-result; not arXiv-by-this-package |
| Persian human note | [`SUBMIT_NEXT_FA.md`](SUBMIT_NEXT_FA.md) | Merge / venue / approve-submit; not reviewer-facing |

**Compile hygiene (human).** If the venue template truncates the abstract, cut examples—not the FAIL numbers, not the MSID comparison, not “qualified win: NO.” Do not add Layer A and VNEXT ASR to one unlabeled table. Do not restyle p = 0.0625 as a win.

**Not in this packet.** PDF/LaTeX restyling, page-number tweaks, camera-ready copyright, OpenReview/HotCRP upload.

---

## 3. Suggested title options (FAIL-consistent)

All three are equivalent in scientific stance. Option A is the current [`MANUSCRIPT.md`](MANUSCRIPT.md) H1.

| # | Title | Use when |
| --- | --- | --- |
| A | Adaptive Cost-Aware Runtime Intervention for LLM Prompt Injection Is Not Confirmed under a Pre-Registered MSID | Default / current manuscript |
| B | Honest Negative Result: Adaptive Cost-Aware LLM-Agent Intervention Fails a Pre-Registered MSID Confirmation | Evaluation / negative-result track that wants the word FAIL in the title |
| C | A Hash-Locked Confirmation Protocol for Adaptive Runtime Intervention: Pre-Registered MSID Not Met | Track that wants the protocol artifact first; still a FAIL, not a defense product |

**Do not use** titles that imply a working guard, a qualified win, SOTA, “almost confirmed,” or “toward production.”

---

## 4. What NOT to claim (from [`CLAIMS_MAP.md`](CLAIMS_MAP.md))

Do not paraphrase a **FORBIDDEN** row into an **ALLOWED** row. Headline public claims are only set **D** in the claims map.

### VNEXT FORBIDDEN (claims map §B)

- “VNEXT-ADAPT works / beats B0 / is a useful runtime defense”
- SOTA; production-ready
- Changing MSID after unblinding
- Topping up N
- Counting `target_refusal` as b10
- Labeling this FAIL as PARTIAL or as a trend toward a win
- Treating p = 0.0625 as “marginally significant therefore confirmed”

### Layer A FORBIDDEN (claims map §A)

- Production-ready / SOTA defense
- “B3_V4 beats B0”
- Treating B2_L3_V4 as adaptive
- ORACLE as deployable; L3 as practical
- L2 tool-deny numbers as the confirmatory result
- A1 refusals as defense successes
- TRAIN/DEV saturation as generalization
- Calibrated probabilities
- Mixing simulation ASR with judge ASR
- Retuning TEST bands
- Pareto dominance of B3_V4
- Relabeling FAIL as PARTIAL / “trend toward a win” / “marginally significant therefore confirmed”
- Mixing VNEXT ASR with Layer A TEST ASR

### Conditional claims that are forbidden without the qualifier (claims map §C)

| If someone writes… | It is forbidden unless they also say… |
| --- | --- |
| “v4 improves detection.” | Detector-only; frozen TEST; threshold 0.25 not tuned on TEST; recall 0.675 vs 0.05 and AUROC 0.705 vs 0.368; TRAIN/DEV overfitting risk |
| “HIGH is reachable.” | v4 mapping; TEST 2 attack HIGH vs 6 benign HIGH (inverted); not well calibrated |
| “Risk-gated level 3 can cut ASR.” | Name **B2_L3_V4**, ASR 0.20, utility 0.825; **fixed / diagnostic, not adaptive** |
| “A3 can stop attacks without harming benign utility.” | **ORACLE_BLOCK only** (labels) |
| “Unconditional blocking stops all attacks.” | **L3**, utility 0; `blocked ⇒ fail` |
| Cost / USD | `api_cost_estimate` only (~$0.059 list-rate aid); not a systems benchmark |

### Cover-letter / camera-ready extras that are also forbidden

- Conference main-track framing as a confirmed defense while H1 = NO
- Product or blog “we built a guard”
- Citing historical simulation `docs/paper/04_results.md` as judge ASR (`LEGACY_SIMULATION_ONLY`)
- Treating PR #29 as a second official confirmation (no `20260914-133147` AUDIT)

Allowed headline sentences remain CLAIMS_MAP §D (Layer A detector lift diagnostic; Layer A adaptive non-result; VNEXT confirmatory FAIL; attribution not mixed ASR; evaluation contribution, not a defense product).

---

## 5. Artifact URLs / paths for reviewers

Repository: https://github.com/Mohammadreza583/adapti-guard  
Open PRs: https://github.com/Mohammadreza583/adapti-guard/pulls  

Reviewers should inspect **paths on this stack** (PR #33 closeout plus this packet). Blob URLs follow `https://github.com/Mohammadreza583/adapti-guard/blob/<branch>/<path>`. Binding identities are hashes and the AUDIT folder, not a branch nickname.

### Frozen packs (do not rewrite)

| Artifact | Path | SHA-256 |
| --- | --- | --- |
| VNEXT confirmation | `datasets/frozen/vnext_confirm_v1/dataset.jsonl` | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` |
| Byte-identical copy | `datasets/frozen/vnext_confirm_v1/confirmation.jsonl` | same digest |
| Pack card | `datasets/frozen/vnext_confirm_v1/DATASET_CARD.md` | — |
| Sidecar listing | `datasets/frozen/vnext_confirm_v1/hashes.sha256` | — |
| Layer A v3 TEST (CLOSED; not VNEXT) | `datasets/frozen/layer_a_v3/test_split.jsonl` | `47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8` |
| Layer A v3 full pack | `datasets/frozen/layer_a_v3/dataset.jsonl` | `abbc87134dc6563231aa422cb923226a5158d512c260a0ec17fd6997877632dd` |
| Layer A v2 | `datasets/frozen/layer_a_v2/dataset.jsonl` | `76c60433d07258d06c5df451bfdd5be4d8ff08988b26c3ecea32ebc32d09ac33` |

### Canonical VNEXT AUDIT path (binding FAIL record)

| Path | Role |
| --- | --- |
| `experiments/real_llm_eval/VNEXT_CONFIRM/README.md` | Suite index; STATUS=FAIL |
| `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md` | **Canonical confirmatory record** |
| `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/verdict.json` | `qualified_win: false`; fail reasons |
| `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/comparison.json` | McNemar, taxonomy, Wilson CIs, spend |
| `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/manifest.json` | Run identity |
| `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/preflight.json` | Hash gate before live calls |
| `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/B0/B0_metrics.json` | B0 arm |
| `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/VNEXT-ADAPT/VNEXT-ADAPT_metrics.json` | Treatment arm |
| `results/summaries/VNEXT_CONFIRM_20260914-133147.md` | One-page summary |

Official scoring git recorded in AUDIT: `dc6dbd37ea75104390c91f338709a4a8c64bfcd6` (same-ID repair; not extra N).

### Protocol lock (not results)

| Path | Role |
| --- | --- |
| `docs/experiments/VNEXT_PROTOCOL.md` | `VNEXT-PROTOCOL-0.1` |
| `docs/experiments/VNEXT_PROTOCOL_ADDENDUM.md` | `VNEXT-PROTOCOL-ADDENDUM-0.3` |
| `docs/experiments/VNEXT_POWER_MEMO.md` | n = 61 exact 80% McNemar power |
| `docs/experiments/VNEXT_CONFIRM_EXPERIMENT_REQUEST.md` | Live-eval contract + FAIL table |

### Eval contract YAML

| Path | SHA-256 |
| --- | --- |
| `configs/models.yaml` | `3e7b33d8b1001f0f86abf74b4d8c1558751275835c10a69152f1f7b386cc58b4` |

Target `qwen/qwen-2.5-7b-instruct` ≠ Judge `qwen/qwen-2.5-72b-instruct`. `cache.enabled` = false. Estimated spend 0.059016 (~$0.059) list-rate aid, not an invoice.

### Offline integrity (no OpenRouter)

```bash
sha256sum datasets/frozen/vnext_confirm_v1/dataset.jsonl
# expected 523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518

python3 docs/paper/workshop_vnext_fail/verify_manuscript_facts.py

python3 -m pytest tests/test_workshop_vnext_fail_facts.py \
  tests/test_vnext_confirm_pack.py tests/test_vnext_confirm_runner.py \
  tests/test_vnext_phase2_harness.py -q
```

Full hash tables: [`APPENDIX_HASHES.md`](APPENDIX_HASHES.md). Config snapshot: [`CONFIGS_SNAPSHOT.md`](CONFIGS_SNAPSHOT.md).

---

## 6. Merge-order reminder from [`PR_STACK.md`](PR_STACK.md) (human executes)

**Do not merge from this file.** Merge order and venue choice are **human-only**. This packet does not land PRs 23–33 on `main`.

Suggested stack merge, **if** a human chooses to land this work on the default branch (copied from [`PR_STACK.md`](PR_STACK.md), then extended by closeout #33 and this packet):

1. #22 (Layer A v4 CASE B) if not already in the target default branch.
2. #23 `docs` (Layer A diagnostic manuscript).
3. #24 `docs` (protocol).
4. #25 `harness`.
5. #26 `docs` (power memo).
6. #27 `docs` (MSID lock).
7. #28 `pack` (hash-locked JSONL; do not rewrite).
8. #30 `docs` (pre-live). Prefer this over merging #29 first.
9. **Close or skip #29** unless a human explicitly wants the unused `run_vnext_confirm_eval.py` path. Do not merge #29 as the official FAIL.
10. #31 `live` (FAIL artifacts). Binding numbers live here.
11. #32 `manuscript`.
12. #33 closeout (`cursor/vnext-fail-workshop-closeout-ef12`): reproducibility / claims-map / PR index. Still not a venue submit.
13. #34 `packet` (this file): cover letter, camera-ready map, title options, forbidden claims, reviewer artifact index. Still not a venue submit.

#29 and #30 are siblings on #28. Official scoring walked #30 → #31, not #29. Conflicts: #29 vs #31 both touch `src/adapti_guard/experiments/vnext_confirm.py`.

**Human-only venue choice (not executed here).** Fit after FAIL: security / ML workshop (negative-result or evaluation track), or optional arXiv preprint of the FAIL. Poor fit: conference main track as a defense paper while H1 = NO. Forbidden: product/blog “we built a guard.” Do not change MSID, N, or frozen packs to chase a venue.

Persian short note for the same human actions: [`SUBMIT_NEXT_FA.md`](SUBMIT_NEXT_FA.md).

---

## Integrity

Pack SHA-256 `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518`.  
B0 ASR 0.9508; VNEXT-ADAPT ASR 0.8689; b10 = 5; b01 = 0; p = 0.0625; δ̂ = 0.0820 < MSID 0.20; U = 0.9344 < 0.95.  
FAIL reasons: `s5_mcnemar_not_significant`, `msid_not_met`, `s4_utility_ineligible`.  
Qualified win: **NO**. Adaptive cost-aware intervention is **not confirmed**.
