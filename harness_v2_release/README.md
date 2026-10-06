# harness_v2 runner snapshot (E2 / E3)

Verbatim copy of the E2/E3 runner code, execution scripts and scenario templates, taken from git commits that exist on the
public remote (fetchable by full SHA, not reachable from any branch). Nothing here was edited, regenerated or reconstructed;
`MANIFEST.sha256` lists the SHA-256 of every file below it.

| Run | Runner commit (`runner_code_sha` in its `run_manifest.json`) | Where in this snapshot |
|---|---|---|
| E3 defended (B3, CORE) | `44830fa23dce2d38f129a89a149af2f4deefb72c` | base tree (this directory) |
| E3 independent screen (A0) | `7b0e053d9da8ed913257ecb725362d1907d0e6d4` | base tree + `overlays/E3_screen_7b0e053/` (2 files differ) |
| E2 exploratory (A0/B3/CORE/TOOLDENY) | `bea82347460f6dfa9cbac81ab1b14d50e0a39f29` | base tree + `overlays/E2_bea82347/` (9 files differ; 3 base files do not exist at that commit: `argallow_policy.py`, `build_harness_v2_independent_templates.py`, `SCENARIO_INSTANCE_TEMPLATES_INDEPENDENT_V2.json`) |

Template files (SHA-256, same at all three commits): `SCENARIO_INSTANCE_TEMPLATES.json` `b9f9994f…bdb9d`;
`SCENARIO_INSTANCE_TEMPLATES_INDEPENDENT_V2.json` `8ae353ca…9de8`. Both match `REPRODUCIBILITY.md`.

## Why this is a separate, self-contained tree
Repository `main` carries older versions of `target_model.py`, `defense_baselines.py`, `adaptive_attacker.py`, `llm_judge.py` and
lacks 17 modules the harness imports (`b2_*`, `stateful_*`, `live_*`, `openrouter_panel_pricing`, ...). The snapshot therefore
carries the full import closure of the harness at the run commit under `src/`. It is not meant to be mixed with `main`'s `src/`;
use it only with `PYTHONPATH=src:.` from this directory. Root `pytest` (`testpaths = tests`) does not collect it.

## What can be checked offline (no API, no key)
```
cd harness_v2_release
PYTHONPATH=src:. python -m pytest -q --import-mode=importlib -c /dev/null --rootdir=. tests/test_harness_v2_exploratory_arms.py   # 13 pass
PYTHONPATH=src:. python scripts/replay_harness_v2_offline.py --out /tmp/replay_base.json
PYTHONPATH=src:. python scripts/replay_harness_v2_offline.py --templates experiments/harness_v2/SCENARIO_INSTANCE_TEMPLATES_INDEPENDENT_V2.json --out /tmp/replay_indep.json
```
The two replay outputs are byte-identical to `harness_v2_offline_replay_20260930.json` and `harness_v2_independent_replay_20260930.json`
as committed in `dfbea801e01051974f51efcc9b7aea179b32d42a`.

## Not covered
* Live re-execution of E2/E3: needs `OPENROUTER_API_KEY`, paid calls and the same providers; not attempted, not claimed.
* The full pilot/amendment test suite (`tests/test_harness_v2_amendment*`, ~160 tests) and `PREREG_HARNESS_V2_FULL.md`, `AMENDMENT9_DECISIONS.md`: they exist at the run commits but are not needed for the E2/E3 path and are not copied.
* Provider-side behaviour (model versions, routing) cannot be reproduced from code.
