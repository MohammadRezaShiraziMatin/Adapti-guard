# Workshop / preprint package — VNEXT confirmation FAIL

**Status:** negative result. Adaptive cost-aware runtime intervention is **not confirmed** under the pre-registered MSID.

This directory is an English workshop-style manuscript package. It does **not** retune detectors, change N, modify frozen packs, run a new eval, or submit to arXiv.

| Field | Binding value |
| --- | --- |
| Scientific outcome | **FAIL** (qualified win: **NO**) |
| Protocol | `VNEXT-PROTOCOL-0.1` |
| Addendum | `VNEXT-PROTOCOL-ADDENDUM-0.3` |
| MSID | `VNEXT-MSID-0.1` (δ = 0.20) |
| Pack | `vnext_confirm_v1.0`, 61 attack + 61 benign |
| Pack SHA-256 | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` |
| Canonical AUDIT | `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md` |
| Layer A | **CLOSED** diagnostic (detector lift; B3_V4 not significant) |

## How to read this package

1. **Claims first.** [`CLAIMS_MAP.md`](CLAIMS_MAP.md) (Track A + Layer A) · dual-track one-liners [`../CLAIMS_CHECKLIST.md`](../CLAIMS_CHECKLIST.md) · Track B allowed/forbidden [`../dual_track/CLAIMS_DUAL_TRACK.md`](../dual_track/CLAIMS_DUAL_TRACK.md). Do not paraphrase forbidden rows into allowed claims. Track B **does not** reverse this FAIL packet.
2. **Manuscript.** [`MANUSCRIPT.md`](MANUSCRIPT.md) is the workshop/preprint text (abstract through reproducibility).
3. **Hashes.** [`APPENDIX_HASHES.md`](APPENDIX_HASHES.md) points at frozen packs and the VNEXT_CONFIRM AUDIT path.
4. **Citation.** [`CITATION.md`](CITATION.md) (software + negative-result preprint). Root [`CITATION.cff`](../../../CITATION.cff) is the GitHub citation file.
5. **Configs snapshot.** [`CONFIGS_SNAPSHOT.md`](CONFIGS_SNAPSHOT.md) lists YAML hashes and the Target/Judge/cache contract.
6. **PR index.** [`PR_STACK.md`](PR_STACK.md) — open PRs 23–41 with roles and **CLOSE / SKIP**. **Do not merge.**
7. **Submission packet (human).** [`SUBMISSION_PACKET.md`](SUBMISSION_PACKET.md) — cover letter, camera-ready map, title options, forbidden claims. **Not a venue submit.**
8. **Submission checklist (Phase 5).** [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md) — DONE / READY / HUMAN_ONLY / BLOCKED per item; venue TBD.
9. **Persian next-step note.** [`SUBMIT_NEXT_FA.md`](SUBMIT_NEXT_FA.md) — for Matin: merge order, pick venue, approve submit.
10. **Reproducibility (offline, API=0).** [`docs/experiments/REPRODUCIBILITY_PACKAGE.md`](../../experiments/REPRODUCIBILITY_PACKAGE.md) — frozen SHAs, AUDIT paths, `verify_manuscript_facts.py`, pytest list. Hashes: [`APPENDIX_HASHES.md`](APPENDIX_HASHES.md).
11. **DONE checklist (legacy closeout).** [`DONE_CHECKLIST.md`](DONE_CHECKLIST.md). Diary: [`docs/experiments/RESEARCH_LOG.md`](../../experiments/RESEARCH_LOG.md).

## Canonical FAIL facts (do not invent or alter)

| Quantity | Value |
| --- | --- |
| Pack SHA-256 | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` |
| N | 61 attack + 61 benign |
| B0 ASR | 0.9508 (58/61) |
| VNEXT-ADAPT ASR | 0.8689 (53/61) |
| McNemar | b10 = 5, b01 = 0, p = 0.0625 |
| Effect vs MSID | δ̂ = 0.0820 < MSID 0.20 |
| Utility | U = 0.9344 < 0.95 |
| False blocks | 1 |
| Fail reasons | `s5_mcnemar_not_significant`, `msid_not_met`, `s4_utility_ineligible` |
| b10 taxonomy | 5 × `correct_block` (A3) |
| Residual attacks | `insufficient_intervention` = 53 |
| Target ≠ Judge | `qwen/qwen-2.5-7b-instruct` ≠ `qwen/qwen-2.5-72b-instruct` |
| Cache | off (0 / 0 hits) |
| Spend (list-rate aid) | ~$0.059 (artifact 0.059016) |

## What this package does not do

- Does not claim a defense win, SOTA detector, or production-ready system.
- Does not treat Layer A `B3_V4` as confirmed.
- Does not mix historical simulation ASR in `docs/paper/04_results.md` with judge ASR or cite simulation ASR=0 as “solved.”
- Does not use Track B Phase-1 LIVE results to reverse or soften VNEXT FAIL in this manuscript.
- Does not rewrite the simulation body of `docs/paper/04_results.md` (pointer only).
- Does not reopen Layer A TEST `47b975f7…` or change `VNEXT-MSID-0.1`.

## Integrity checks (no live LLM)

```bash
sha256sum datasets/frozen/vnext_confirm_v1/dataset.jsonl
# 523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518

python3 docs/paper/workshop_vnext_fail/verify_manuscript_facts.py

python3 -m pytest tests/test_workshop_vnext_fail_facts.py \
  tests/test_vnext_confirm_pack.py tests/test_vnext_confirm_runner.py \
  tests/test_vnext_phase2_harness.py -q
```

Parent confirmation branch: `cursor/vnext-confirm-live-81ad` (PR #31).
Manuscript package: `cursor/vnext-fail-workshop-manuscript-de91` (PR #32).
Closeout: `cursor/vnext-fail-workshop-closeout-ef12` (PR #33).
Submission packet: `cursor/vnext-fail-submission-packet-1411` (PR #34; no venue submit).
