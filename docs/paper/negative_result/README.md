# Negative-result manuscript: index

Title: *What Reached the Executor? Six Measurement Checks for Evaluating Runtime Defenses of LLM Agents, with a Negative Result* (see `MANUSCRIPT_DRAFT_v1.md`).

## Layout
| file | role |
|---|---|
| `MANUSCRIPT_DRAFT_v1.md` | assembled manuscript (generated; do not edit by hand) |
| `SECTIONS_*.md`, `SECTION4_*.md`, `SECTION8_*.md` | source sections that `scripts/assemble_manuscript.py` joins |
| `NUMBERS_LEDGER.md` | every key number, recomputed from committed artifacts (generated) |
| `PROTOCOL_EXTERNAL_TEST_DRAFT_v1.md` | pre-registration draft for the external tests (not frozen) |
| `PAPER_STANDARDS_CHECKLIST.md` | reporting checklists with honest status |
| `INTERNAL_REVIEW_20260930.md`, `RELATED_WORK_NOTES.md` | hostile review and literature notes |
| `figures/` | Fig. 1 to 3 as csv, png, svg (svg is byte-reproducible) |

## Reproduce everything offline
```bash
STRICT=1 bash scripts/reproduce_negative_result.sh   # no network, no key, no spend
```
It regenerates the re-scoring, analyses and figures of E1 to E3, the MT1 held-out application and the M6 channel check, then the manuscript and number ledger, and runs the consistency test that checks each ledger number appears in the manuscript (`STRICT=1` also fails if a regenerated file differs from the committed copy). Sections 6.6, 6.7 and Appendix A use committed derived artifacts; the scripts that produced them, the multi-turn harness and runner, and the attack-template files are not in this repository (staged release, §10 of the manuscript).

## Claim to evidence map
| claim (section) | evidence artifact | script |
|---|---|---|
| Judge and tool layer disagree (6.1) | `docs/research/artifacts/tracks_ab_deterministic_rescoring_20260930.json` | `rescore_tracks_ab_deterministic.py` |
| Four scoring rules flip the verdict (6.2, Fig. 1) | `figures/fig1_scoring_flip.csv` | `make_fig1_scoring_flip.py` |
| Defended stack changes nothing on independent families (6.3, Figs. 2 and 3) | `experiments/harness_v2/HARNESS_V2_INDEPENDENT_*` | `analyze_independent_defended.py` |
| Held-out check and channel finding (6.5) | `mt1_second_dataset_rules_20260930.json`, `spotlight_ctx_check_20260930.json` | `apply_rules_second_dataset_mt1.py`, `analyze_spotlight_ctx_check.py` |
| External test, model-specific delimiter effect (6.6) | `experiments/external/injecagent_registered_20261001/`, `experiments/external/injecagent_live_*`, `docs/research/artifacts/injecagent_live_analysis_*.json` (committed derived artifacts) | none in this repository (analysis and run scripts not published) |
| Dataset limits (8) | none committed (the audit artifact is not in this repository) | none in this repository |
