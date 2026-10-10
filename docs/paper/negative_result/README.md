# Negative-result manuscript: index

Title: *What Reached the Executor? Six Measurement Checks for Evaluating Runtime Defenses of LLM Agents, with a Negative Result* (see `MANUSCRIPT_DRAFT_v1.md`).

## Layout
| file | role |
|---|---|
| `MANUSCRIPT_DRAFT_v1.md` | assembled manuscript (generated; do not edit by hand) |
| `SECTIONS_*.md`, `SECTION4_*.md`, `SECTION8_*.md` | source sections that `scripts/assemble_manuscript.py` joins |
| `NUMBERS_LEDGER.md` | every key number, recomputed from committed artifacts (generated) |
| `PROTOCOL_EXTERNAL_TEST_DRAFT_v1.md` | locally drafted protocol for the external tests (not frozen, not externally registered) |
| `PAPER_STANDARDS_CHECKLIST.md` | reporting checklists with honest status |
| `INTERNAL_REVIEW_20260930.md`, `RELATED_WORK_NOTES.md` | hostile review and literature notes |
| `figures/` | Fig. 1 to 3 as csv, png, svg (svg is byte-reproducible) |

## Reproduce everything offline
```bash
PYTHON=python3.12 ./scripts/reproduce_negative_result.sh   # no network, no key, no spend
```
It regenerates the re-scoring, analyses, figures, manuscript and number ledger, then runs the consistency test that
checks each ledger number appears in the manuscript. The external-data steps (InjecAgent, §6.6 and §6.7) are skipped: their scripts and the external
checkout are not part of this repository, so those numbers are read from committed records and are not regenerated (see `REPRODUCIBILITY.md`).

## Claim to evidence map
| claim (section) | evidence artifact | script |
|---|---|---|
| Judge and tool layer disagree (6.1) | `docs/research/artifacts/tracks_ab_deterministic_rescoring_20260930.json` | `rescore_tracks_ab_deterministic.py` |
| Four scoring rules flip the verdict (6.2, Fig. 1) | `figures/fig1_scoring_flip.csv` | `make_fig1_scoring_flip.py` |
| Defended stack changes nothing on independent families (6.3, Figs. 2 and 3) | `experiments/harness_v2/HARNESS_V2_INDEPENDENT_*` | `analyze_independent_defended.py` |
| E3 non-delivered episodes and delivery-restricted pairs (6.3, 8.5, App. D) | `docs/research/artifacts/e3_delivery_audit_20261003.json` | `audit_e3_delivery.py` |
| Held-out check and channel finding (6.5) | `mt1_second_dataset_rules_20260930.json`, `spotlight_ctx_check_20260930.json` | `apply_rules_second_dataset_mt1.py`, `analyze_spotlight_ctx_check.py` |
| External test, model-specific delimiter effect (6.6, 6.7) | `experiments/external/injecagent_*`, `injecagent_live_analysis_*.json` | `recompute_external_test.py` (counts, rates, paired means, §6.7 cells; checked by `test_external_ledger_raw.py`); bootstrap CIs read from `ANALYSIS.json`. Restored from `96b33e4e`: `run_injecagent_panel.py`, `run_phase2_calibration.py`, `injecagent_offline_check.py`, `analyze_injecagent_live.py` (the two run scripts call a provider and are not run). Absent from the tree: `run_injecagent_registered.py`, `run_injecagent_live.py`, the producer of `ANALYSIS.json` |
| Dataset limits (8) | `dataset_audit_20260930.json` | not in the public tree (`audit_datasets.py`) |
