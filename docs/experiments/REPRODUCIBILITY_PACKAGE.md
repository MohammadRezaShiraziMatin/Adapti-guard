# Reproducibility package (offline verification hub)

**Tip baseline:** `main` @ `30ddc75` (2026-09-23). **API=0** for checks in this file.

**Scientific status (unchanged).** Layer A = **CLOSED diagnostic**. Track A VNEXT = **FAIL** (qualified win = NO). Track B Phase-1 LIVE = **SUPPORTED_IMPROVEMENT** on a **different** pack — does **not** reverse Track A.

This file does not authorize live eval, retune, N increase, frozen-pack edits, merge, or venue submit.

**Related docs:** hash tables [`docs/paper/workshop_vnext_fail/APPENDIX_HASHES.md`](../paper/workshop_vnext_fail/APPENDIX_HASHES.md) · configs [`CONFIGS_SNAPSHOT.md`](../paper/workshop_vnext_fail/CONFIGS_SNAPSHOT.md) · claims [`docs/paper/CLAIMS_CHECKLIST.md`](../paper/CLAIMS_CHECKLIST.md) · workshop hub [`workshop_vnext_fail/README.md`](../paper/workshop_vnext_fail/README.md) · diary [`RESEARCH_LOG.md`](RESEARCH_LOG.md) · PR index [`PR_STACK.md`](../paper/workshop_vnext_fail/PR_STACK.md) (**human merge only**).

---

## Frozen confirmatory packs (pin only; do not edit bytes)

| Pack ID | Path | SHA-256 (`dataset.jsonl`) | Live eval / claim role |
| --- | --- | --- | --- |
| `vnext_confirm_v1.0` | `datasets/frozen/vnext_confirm_v1/` | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` | Track A confirmatory **FAIL** |
| `phase1_confirm_v1` | `datasets/frozen/phase1_confirm_v1/` | `c789811a07d3ed06e1c77d8a45eda6172f480226e006d84fa28386a982536d01` | Track B **SUPPORTED_IMPROVEMENT** (scoped) |
| `p1_mechanism_v1.0.0` | `datasets/frozen/p1_mechanism_v1.0.0/` | `1a0b0053c392e7b3e0727b92b4f088790abda001fd852ec1703c5ee0a67dd235` | Mechanism benchmark; **`live_evaluated=false`** ([freeze record](../research/P1_MECHANISM_V1_0_0_FREEZE.md)) |

Sidecars: each pack’s `hashes.sha256` / `DATASET_CARD.md` when present. **Do not** recompute or “fix” digests in docs without a new freeze PR.

### Canonical AUDIT folders (read-only)

| Track | AUDIT path | Verdict |
| --- | --- | --- |
| A — VNEXT | `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md` | FAIL |
| B — Phase-1 | `experiments/real_llm_eval/PHASE1_CONFIRM/phase1_confirm_20260914T213022Z_a2681e92/AUDIT.md` | SUPPORTED_IMPROVEMENT |

Machine-readable: sibling `verdict.json`, `comparison.json` (Track A), arm metrics under the same run folder.

### Eval contract (protocol; not new numbers)

| Item | Binding value |
| --- | --- |
| Target | `target_2` → `qwen/qwen-2.5-7b-instruct` |
| Judge | `judge_fallback` → `qwen/qwen-2.5-72b-instruct` |
| Target ≠ Judge | Required on confirmatory live runs |
| Cache | `configs/models.yaml` → `cache.enabled = false` |
| YAML hash | `configs/models.yaml` SHA-256 `37174858710a087b3fe58c40e65c796418d1791ff4280bca08d96486b35d7ec3` |

Full YAML table: [`CONFIGS_SNAPSHOT.md`](../paper/workshop_vnext_fail/CONFIGS_SNAPSHOT.md).

---

## Identities

- Repo: ADAPTI-GUARD
- Detector v4 freeze: git `46bffe142be334260f767a98c2201ca273c24f71` (`evidence_v4.0`)
- Intervention wiring: git `3ca86a7a876c3de01c208eea62e736bce33ee422`
- Frozen TEST: `datasets/frozen/layer_a_v3/test_split.jsonl`  
  SHA-256 `47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8`
- Historical v2: SHA-256 `76c60433d07258d06c5df451bfdd5be4d8ff08988b26c3ecea32ebc32d09ac33`

## Models and eval contract

- Target `target_2` = `qwen/qwen-2.5-7b-instruct`
- Judge `judge_fallback` = `qwen/qwen-2.5-72b-instruct`
- `cache.enabled = false` (`configs/models.yaml`)
- seed 42; 40 attack + 40 benign from `datasets/frozen/layer_a_v3_test_split_view`

## Commands

Detector DEV gate (no TEST):

```
python3 scripts/run_layer_a_v4_detector_eval.py --output experiments/real_llm_eval/LAYER_A_V4_DETECTOR/dev_gate
```

One-shot TEST (do not iterate afterward):

```
python3 scripts/run_layer_a_v4_detector_eval.py --include-test --output experiments/real_llm_eval/LAYER_A_V4_DETECTOR/20260914-frozen-test
```

Intervention (v4 policies only):

```
python3 scripts/run_layer_a_v4_eval.py --require-key --baselines B3_V4 B2_L3_V4 --attack-n 40 --benign-n 40 --seed 42 --output experiments/real_llm_eval/LAYER_A_V4_INTERVENTION/20260914-101700 --experiment-id LAYER-A-V4-INTERVENTION
```

Tests:

```
python3 -m pytest tests/test_layer_a_v4_detector.py tests/test_tool_loop.py tests/test_layer_a_v3_pack.py tests/test_statistics.py -q
```

## Artifacts

| Path | Contents |
| --- | --- |
| `docs/archive/layer_a/PROJECT_COMPLETION_AUDIT.md` | Phase 0 |
| `docs/archive/layer_a/LAYER_A_V4_FORENSIC_AUDIT.md` | Phase 1 (TRAIN/DEV) |
| `docs/archive/layer_a/LAYER_A_V4_DEV_GATE.md` | Phase 2–3 gate |
| `docs/archive/layer_a/LAYER_A_V4_RISK_CALIBRATION.md` | Phase 4 |
| `experiments/real_llm_eval/LAYER_A_V4_DETECTOR/` | detector metrics |
| `experiments/real_llm_eval/LAYER_A_V4_INTERVENTION/20260914-101700/` | B3_V4 / B2_L3_V4 |
| `docs/archive/layer_a/FINAL_SCIENTIFIC_AUDIT.md` | Phase 10 |
| `docs/archive/paper_working_notes/RESULTS_RECONCILIATION.md` | Phase 11 (no manuscript overwrite) |
| `docs/archive/layer_a/PROJECT_FINAL_STATUS.md` | CASE B |

Historical v2/v3 folders and `docs/paper/04_results.md` are intentionally untouched.

---

## VNEXT confirmation identities (FAIL)

- Pack: `datasets/frozen/vnext_confirm_v1/dataset.jsonl` (`vnext_confirm_v1.0`)
- SHA-256 `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` (byte-identical `confirmation.jsonl`)
- Protocol `VNEXT-PROTOCOL-0.1` · addendum `VNEXT-PROTOCOL-ADDENDUM-0.3` · MSID `VNEXT-MSID-0.1` (δ = 0.20)
- Canonical AUDIT: `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md`
- Scoring git recorded in AUDIT: `dc6dbd37ea75104390c91f338709a4a8c64bfcd6`
- N = 61 attack + 61 benign; seed: pack mix 61 (file order), pipeline/bootstrap 42
- Same eval contract as Layer A intervention: `target_2` ≠ `judge_fallback`; `cache.enabled = false`

---

## Configs snapshot list

Binding YAML hashes and Target/Judge keys: [`docs/paper/workshop_vnext_fail/CONFIGS_SNAPSHOT.md`](../paper/workshop_vnext_fail/CONFIGS_SNAPSHOT.md).

| Path | SHA-256 | Used for official VNEXT pair? |
| --- | --- | --- |
| `configs/models.yaml` | `37174858710a087b3fe58c40e65c796418d1791ff4280bca08d96486b35d7ec3` | **Yes** (`target_2`, `judge_fallback`, `cache.enabled=false`) |
| `configs/models_mt2.yaml` | (additive MT2 registry) | **No** |
| `configs/mt2_panel.yaml` | (additive MT2 contract) | **No** |
| `configs/mt2_openrouter_catalog_snapshot.json` | (additive OR catalog) | **No** |
| `configs/datasets.yaml` | `fd005720c44f7786a93202536bea4d5eb336d6c25ad313d156df402f7b5acaca` | No (path registry) |
| `configs/models_local.yaml` | `cfcd748388a7ae771cf9c951d74211364c673262f06f633a0ace1a0de0ba5126` | No |
| `configs/experiments/ablation_study.yaml` | `80791f5122bdfa8ae6b7b177d1f2de043255de8a261a75941e3f0ee418eaf0c5` | No |
| `configs/experiments/long_term_adaptation.yaml` | `96c36db643192e6261ccfe702b4d5c2d610463be8063ffb9f370aa8e91080da5` | No |

Do not enable the LLM cache or swap Target/Judge to amend the FAIL.

---

## How to reproduce offline checks (no OpenRouter)

These commands must not call a live LLM. They re-hash frozen packs, re-score committed AUDIT JSON, and run deterministic unit tests.

```bash
# 1. Frozen pack identities (must match APPENDIX_HASHES / freeze records)
sha256sum \
  datasets/frozen/vnext_confirm_v1/dataset.jsonl \
  datasets/frozen/vnext_confirm_v1/confirmation.jsonl \
  datasets/frozen/phase1_confirm_v1/dataset.jsonl \
  datasets/frozen/p1_mechanism_v1.0.0/dataset.jsonl \
  datasets/frozen/layer_a_v3/test_split.jsonl \
  datasets/frozen/layer_a_v3/dataset.jsonl \
  datasets/frozen/layer_a_v2/dataset.jsonl \
  configs/models.yaml

# Expected digests (confirmatory + mechanism; do not amend without new freeze):
# vnext_confirm_v1: 523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518
# phase1_confirm_v1: c789811a07d3ed06e1c77d8a45eda6172f480226e006d84fa28386a982536d01
# p1_mechanism_v1.0.0: 1a0b0053c392e7b3e0727b92b4f088790abda001fd852ec1703c5ee0a67dd235
# layer_a_v3 TEST: 47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8

# 2. Manuscript + dual-track docs vs frozen AUDIT FAIL (no OpenRouter)
python3 docs/paper/workshop_vnext_fail/verify_manuscript_facts.py

# 3. Deterministic pytest (pack gates, harness, workshop facts, Layer A unit tests)
python3 -m pytest \
  tests/test_vnext_confirm_pack.py \
  tests/test_vnext_confirm_runner.py \
  tests/test_vnext_phase2_harness.py \
  tests/test_workshop_vnext_fail_facts.py \
  tests/test_layer_a_v4_detector.py \
  tests/test_tool_loop.py \
  tests/test_layer_a_v3_pack.py \
  tests/test_statistics.py \
  -q
```

**Do not** rerun `scripts/run_vnext_confirm.py --require-key` to change the verdict. That would be a new experiment ID. The official FAIL is the AUDIT folder already in git.

**Citation / software metadata:** root [`CITATION.cff`](../../CITATION.cff) · workshop [`CITATION.md`](../paper/workshop_vnext_fail/CITATION.md) (author: Seyed Mohammadreza Shirazi Matin; repo `https://github.com/MohammadRezaShiraziMatin/adapti-guard`).

---

## PR index

Open stack **PRs #23–#44** (roles, CLOSE/SKIP, Track B path): [`PR_STACK.md`](../paper/workshop_vnext_fail/PR_STACK.md). Agents must not merge. Human cover letter: [`SUBMISSION_PACKET.md`](../paper/workshop_vnext_fail/SUBMISSION_PACKET.md) (**not a venue submit**).

Quality/docs-only tip PR: **#73** (`cursor/docs-quality-phase1-2-1d46`) — does not replace AUDIT numbers.

| PR | Role | Binding for Track A FAIL numbers? |
| ---: | --- | --- |
| 31 | `live` official VNEXT FAIL | **Yes** |
| 29 | `unused` parallel runner | **No** |
| 39 | `live` Track B confirm (draft) | Track B only; does not reverse #31 |

---

## VNEXT FAIL numbers (do not invent)

| Quantity | Value |
| --- | --- |
| B0 ASR | 0.9508 (58/61) |
| VNEXT-ADAPT ASR | 0.8689 (53/61) |
| McNemar | b10 = 5, b01 = 0, p = 0.0625 |
| δ̂ vs MSID | 0.0820 < 0.20 |
| U | 0.9344 < 0.95 (false blocks = 1) |
| Fail reasons | `s5_mcnemar_not_significant`, `msid_not_met`, `s4_utility_ineligible` |
| Qualified win | **NO** |
