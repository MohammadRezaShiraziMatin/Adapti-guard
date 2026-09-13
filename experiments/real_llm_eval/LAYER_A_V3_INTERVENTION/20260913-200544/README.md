# Layer A v3 intervention run

Live OpenRouter evaluation of B0 / B3 / L3 / ORACLE_BLOCK on the frozen Layer A v3 **TEST** split.

- **AUDIT:** [AUDIT.md](AUDIT.md) — **VALID / CASE D**
- **Status:** `STATUS.txt` = VALID, pipeline `COMPLETED`, judge-fail 0, cache hits 0
- **L2:** not scored (no tool-execution loop)
- **ORACLE_BLOCK:** diagnostic only, not a deployable defense
- **Manuscript Results:** not modified (`docs/paper/04_results.md`)
- **Historical Layer A v2 artifacts:** not overwritten

## Headline

B0 ASR = 30/40 = 0.75. B3 ASR = 28/40 = 0.70 (A1 on every episode; McNemar p = 0.6875, not a demonstrated reduction). Unconditional L3 ASR = 0 at utility 0. Oracle block ASR = 0 at utility 1 — A3 can stop these attacks when the label is known. The bottleneck is detection/risk, not A3 semantics.

Sibling detector-only run: `../LAYER_A_V3_DETECTOR/20260913-200341/` (TEST recall 2/40 = 0.05 at threshold 0.25).

## Contract

| Item | Value |
| --- | --- |
| Pack | `datasets/frozen/layer_a_v3` (`layer_a_v3.0`, seed 42) |
| Runner view | `datasets/frozen/layer_a_v3_test_split_view` |
| TEST SHA-256 | `47b975f77ddcd6a6d076f8e86327e989642b5772f5b8fabaf1c5301855b5f4a8` |
| n | 40 attack + 40 benign |
| Target | `qwen/qwen-2.5-7b-instruct` (`target_2`) |
| Judge | `qwen/qwen-2.5-72b-instruct` (`judge_fallback`) |
| Cache | off |
| Git commit at run | `8692069af74f58223244943d2f8c8cbed1e92e33` |

## Files

| File | Role |
| --- | --- |
| `metrics.json` / `metrics.csv` | scored policies |
| `comparison.csv` / `comparison.json` | B0 vs B3 discordant IDs + McNemar |
| `error_decomposition.jsonl` | per-episode taxonomy on B3 |
| `frontier.json` | security–utility–cost points |
| `{B0,B3,L3,ORACLE_BLOCK}/*_predictions.jsonl` | episode traces |
| `L2/config.json` | unsupported, not scored |
