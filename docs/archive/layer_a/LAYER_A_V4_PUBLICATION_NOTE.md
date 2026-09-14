# Layer A v4 publication pointer

Manuscript diagnostics live in new files. Historical `docs/paper/04_results.md` is **not** overwritten.

| Paper-facing file | Role |
| --- | --- |
| `docs/paper/04_results_layer_a_diagnostic.md` | Setup, detector table, intervention table, McNemar, error decomposition, Pareto, limitations |
| `docs/paper/CLAIMS_CHECKLIST_LAYER_A.md` | ALLOWED / FORBIDDEN / CONDITIONAL wording |
| `docs/paper/RESULTS_RECONCILIATION.md` | Phase 11 claim-to-folder map (unchanged) |
| `docs/experiments/FINAL_SCIENTIFIC_AUDIT.md` | CASE B close-out |

## Frozen artifacts (cite these folders)

| Folder | Contents |
| --- | --- |
| `datasets/frozen/layer_a_v2/` | Historical v2 pack (SHA-256 `76c60433d07258d06c5df451bfdd5be4d8ff08988b26c3ecea32ebc32d09ac33`) |
| `datasets/frozen/layer_a_v3/` | v3 pack + frozen TEST (`test_split.jsonl` SHA-256 `47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8`; `dataset.jsonl` SHA-256 `abbc87134dc6563231aa422cb923226a5158d512c260a0ec17fd6997877632dd`) |
| `experiments/real_llm_eval/LAYER_A_V3_DETECTOR/20260913-200341/` | v3 detector-only (TEST recall 2/40, AUROC ≈ 0.368) |
| `experiments/real_llm_eval/LAYER_A_V3_INTERVENTION/20260913-200544/` | B0, B3 (v3), L3, ORACLE_BLOCK |
| `experiments/real_llm_eval/LAYER_A_V4_DETECTOR/dev_gate/` | TRAIN/DEV gate (no TEST in this gate) |
| `experiments/real_llm_eval/LAYER_A_V4_DETECTOR/20260914-frozen-test/` | One-shot v4 TEST detector eval |
| `experiments/real_llm_eval/LAYER_A_V4_INTERVENTION/20260914-101700/` | B3_V4, B2_L3_V4, McNemar `comparison.json`, `frontier.json`, `error_decomposition_summary.json` |

Do not run new LLM experiments or retune TEST to fill manuscript cells. Missing cells stay empty.
