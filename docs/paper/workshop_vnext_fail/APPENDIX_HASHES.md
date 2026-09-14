# Appendix: artifact hashes and AUDIT paths

Verify these digests on a clean checkout. **Do not rewrite** the frozen JSONL files.
A live or manuscript claim that cites a different confirmation hash is invalid (protocol S3).

Recompute:

```bash
sha256sum \
  datasets/frozen/vnext_confirm_v1/dataset.jsonl \
  datasets/frozen/vnext_confirm_v1/confirmation.jsonl \
  datasets/frozen/layer_a_v3/test_split.jsonl \
  datasets/frozen/layer_a_v3/dataset.jsonl \
  datasets/frozen/layer_a_v2/dataset.jsonl
```

---

## 1. Frozen packs (do not modify)

| Artifact | SHA-256 |
| --- | --- |
| VNEXT confirmation `datasets/frozen/vnext_confirm_v1/dataset.jsonl` | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` |
| Byte-identical `datasets/frozen/vnext_confirm_v1/confirmation.jsonl` | `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` |
| Layer A v3 TEST `datasets/frozen/layer_a_v3/test_split.jsonl` | `47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8` |
| Layer A v3 full pack `datasets/frozen/layer_a_v3/dataset.jsonl` | `abbc87134dc6563231aa422cb923226a5158d512c260a0ec17fd6997877632dd` |
| Layer A v2 `datasets/frozen/layer_a_v2/dataset.jsonl` | `76c60433d07258d06c5df451bfdd5be4d8ff08988b26c3ecea32ebc32d09ac33` |

Pack identity: `vnext_confirm_v1.0`, 122 rows (61 attack + 61 benign), split field `confirmation`.
Card: `datasets/frozen/vnext_confirm_v1/DATASET_CARD.md`.
Sidecar listing: `datasets/frozen/vnext_confirm_v1/hashes.sha256`.

Layer A TEST `47b975f7…` is **CLOSED**. It is not the VNEXT confirmation set and must not be retuned.

---

## 2. VNEXT confirmation AUDIT path (binding FAIL record)

| Path | Role |
| --- | --- |
| `experiments/real_llm_eval/VNEXT_CONFIRM/README.md` | Suite index; STATUS=FAIL |
| `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/AUDIT.md` | **Canonical confirmatory record** |
| `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/verdict.json` | Machine-readable FAIL (`qualified_win: false`) |
| `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/comparison.json` | McNemar cells, taxonomy, Wilson CIs, spend |
| `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/manifest.json` | Run identity |
| `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/preflight.json` | Hash gate before live calls |
| `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/B0/B0_metrics.json` | B0 arm |
| `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/VNEXT-ADAPT/VNEXT-ADAPT_metrics.json` | Treatment arm |
| `results/summaries/VNEXT_CONFIRM_20260914-133147.md` | One-page summary |

Official scoring git recorded in AUDIT: `dc6dbd37ea75104390c91f338709a4a8c64bfcd6` (same-ID repair; not extra N).
FAIL recording commit on parent branch: `ebd4fc6836e92153dca14688ff900cb8bd4451e2`.

---

## 3. Layer A diagnostic folders (CLOSED; cite, do not rerun to “improve”)

| Folder | Contents |
| --- | --- |
| `experiments/real_llm_eval/LAYER_A_V3_DETECTOR/20260913-200341/` | v3 detector-only (TEST recall 2/40, AUROC ≈ 0.368) |
| `experiments/real_llm_eval/LAYER_A_V3_INTERVENTION/20260913-200544/` | B0, B3 (v3), L3, ORACLE_BLOCK |
| `experiments/real_llm_eval/LAYER_A_V4_DETECTOR/dev_gate/` | TRAIN/DEV gate (no TEST in this gate) |
| `experiments/real_llm_eval/LAYER_A_V4_DETECTOR/20260914-frozen-test/` | One-shot v4 TEST detector eval |
| `experiments/real_llm_eval/LAYER_A_V4_INTERVENTION/20260914-101700/` | B3_V4, B2_L3_V4, McNemar, taxonomy |
| `docs/paper/04_results_layer_a_diagnostic.md` | Paper-facing Layer A tables |
| `docs/paper/CLAIMS_CHECKLIST_LAYER_A.md` | Allowed / forbidden Layer A wording |
| `docs/experiments/LAYER_A_V4_PUBLICATION_NOTE.md` | Folder pointer |

Detector freeze: `evidence_v4.0` at git `46bffe142be334260f767a98c2201ca273c24f71`.
Intervention wiring: git `3ca86a7a876c3de01c208eea62e736bce33ee422`.

---

## 4. Protocol and power lock (not results)

| Path | Role |
| --- | --- |
| `docs/experiments/VNEXT_PROTOCOL.md` | `VNEXT-PROTOCOL-0.1` |
| `docs/experiments/VNEXT_PROTOCOL_ADDENDUM.md` | `VNEXT-PROTOCOL-ADDENDUM-0.3` (hash + MSID) |
| `docs/experiments/VNEXT_POWER_MEMO.md` | `VNEXT-POWER-MEMO-0.1` (n=61 exact 80% power) |
| `docs/experiments/VNEXT_CONFIRM_EXPERIMENT_REQUEST.md` | Live-eval contract + FAIL table |

---

## 5. Historical simulation (not judge ASR)

`docs/paper/04_results.md` simulation tables are **LEGACY_SIMULATION_ONLY**.
This package does not rewrite that body. A pointer at the top of that file directs readers here.

---

## 6. Eval contract (both Layer A intervention and VNEXT)

| Item | Value |
| --- | --- |
| Target | `target_2` / `qwen/qwen-2.5-7b-instruct` |
| Judge | `judge_fallback` / `qwen/qwen-2.5-72b-instruct` |
| Target ≠ Judge | required and observed |
| Cache | `enabled=false` (0 hits on the official VNEXT run) |
| Backend | OpenRouter |
| VNEXT estimated USD (list-rate aid) | 0.059016 (~$0.059); not a billing invoice |
