# Files restored from unreachable commit 96b33e4e

Source commit (full SHA, resolved with `gh api` from the short form `96b33e4e` and fetched from origin by full SHA):
`96b33e4eec1f2b32afcbe697a1d3d26add2bbd38`
Commit subject: "Registered InjecAgent test runner (llama-4-maverick, qwen3.8-flash)". The commit itself adds only `scripts/run_injecagent_registered.py`, which is **not** restored here.

The five files below were copied with `git show 96b33e4eec1f2b32afcbe697a1d3d26add2bbd38:<path>`. The git blob of each restored file equals the blob in the source commit (verified with `git hash-object`), so the content is unchanged. SHA-256 is of the file as committed on this branch.

| path | source git blob | sha256 |
|---|---|---|
| `scripts/run_injecagent_panel.py` | `28a36ecd3c0c61e7f60b6f8146fbc770e4deb992` | `6078488d015f9beeb89e2174959510a8ae99b8633c0c0e71218dcea82c0e5193` |
| `scripts/run_phase2_calibration.py` | `1a7c3d0719d86e32e324fff5ac4c70d3a808d6de` | `bbdb9c0ea1876109a23179340541e017f84f731d41672a49e2d60010ee48c428` |
| `scripts/injecagent_offline_check.py` | `409b555f6ce924b7e3e652628a7e85ed887891c4` | `d787b0dddf3d2ce95add49c9d057d3803c487455e5662087a805541ffdd881ba` |
| `scripts/analyze_injecagent_live.py` | `cd36b4c7de39033e898f141bdb4817490b32c883` | `866970cc17236aa7fba7d8c0ecc2ce755056af68ea076ec0f433392a5a67b5cb` |
| `datasets/attackset_hard_v1/MANIFEST.json` | `dced500145bff419e95ce771654d6ddf63db54b1` | `786505ecaa77c6c8619495a23661eb364dd0c857c368a7c1cb9c383b8b7ba1d4` |

## Notes

- **Live calls.** `scripts/run_injecagent_panel.py` and `scripts/run_phase2_calibration.py` call the OpenRouter chat endpoint and need `OPENROUTER_API_KEY`. They were **not run** while preparing this branch and `scripts/reproduce_negative_result.sh` does not run them.
- **Hard-set MANIFEST.** Its SHA-256 equals `manifest_sha256` for `datasets/attackset_hard_v1/MANIFEST.json` in `datasets/attackset_hard_v1/FREEZE_RECORD.json`.
- **Not restored (outside the agreed list):** the registered runner `scripts/run_injecagent_registered.py` (commit `96b33e4e`), `docs/research/artifacts/injecagent_offline_check_20260930.json`, and the other Hard-set manifests.
- **Not changed:** no restored file was edited. Reproducibility uses the committed records, not these scripts.
