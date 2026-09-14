# AdaptiGuard — Repository Refactor Audit

**Date:** 2026-09-04  
**Scope:** Pre–GitHub-release structure audit. No methodology changes.

## Current structure (pre-refactor)

| Path | Role |
|------|------|
| `src/adapti_guard/` | Core package (detector, risk, policy, defense, adaptation, evaluation, experiments) |
| `configs/` | `models.yaml`, experiment YAMLs |
| `datasets/` | frozen eval, benchmark_q1/v2, attack_dataset |
| `experiments/` | Flat mix of runs, audits, paper drafts, smoke tests |
| `results/` | phase7/8 simulation, experiment_runs, figures |
| `docs/` | Research protocols, audits, manuscript notes |
| `scripts/` | Harmonized / sensitivity / dataset builders |
| `tests/` | Unit + artifact tests |
| Root stubs | Empty `Agent`, `Defense`, `Policy`, `Risk`, `assert` (0 bytes) |
| Root placeholders | `attacks/`, `defenses/`, `evaluation/`, `models/`, `figures/` (README only) |
| `baselines/` | Top-level baseline stubs (also under `src/adapti_guard/baselines`) |
| `.venv/`, `.venv_phase5/`, `.llm_cache/` | Local only — must stay gitignored |

## Important files that MUST remain

- `datasets/frozen/eval_v1/` (+ hashes)
- `results/common_attack_stream.json` (+ SHA-256)
- `results/phase7/`, `results/phase8/`
- `experiments/PHASE5_CONSTRAINED/raw_results.jsonl`
- `experiments/REAL_LLM_EVAL/` metrics & predictions
- `experiments/FINAL_*` scientific audits, QC, manifests
- `src/adapti_guard/**` algorithms
- `configs/models.yaml` (not `.bak` copies)
- `docs/` research evidence
- `REPRODUCIBILITY.md`, `requirements*.txt`

## Duplicated / confusing items

| Item | Notes |
|------|-------|
| Root `baselines/` vs `src/adapti_guard/baselines/` | Prefer package path; root kept as thin pointer |
| Root `attacks/`/`defenses/` stubs | Point into `src/`; retain README only |
| Multiple `models.yaml.backup_*` | Config backups — archive |
| `.env.save*` | Secret-adjacent local dumps — remove from tree (gitignored) |
| Root audit MD files | Overlap with `docs/` — move to `docs/archive/` |
| `test_core.py` / `test_pipeline.py` at root | Duplicate entry vs `tests/` — move into `tests/` |

## Temporary / cache (safe to remove)

- All `__pycache__/` and `*.pyc` under `src/`
- `.pytest_cache/`
- Editor swap files (`*.swp`)
- Transient completion stdout logs (non-evidence)

## Logs (preserve vs clean)

| Keep (evidence) | Clean / archive |
|-----------------|-----------------|
| `results/experiment_runs/**/stdout.log` | `experiments/FINAL_COMPLETION/stdout.log` |
| Phase5 stderr/stdout (run provenance) | Duplicate tee logs after archival copy |

## Code markers (project source only)

| Pattern | Location | Status |
|---------|----------|--------|
| `NotImplementedError` | `target_model.TargetModel`, `detector/base.py`, `outcome_evaluators.py` | Abstract base / unimplemented detector backends — keep |
| `LEGACY_SIMULATION_ONLY` | evaluation modes, EXP-006 | Scientific label — keep |
| `TODO` in docs tables | Pre-submission review | Documentation debt — keep |
| `normalize_legacy_mode` | `evaluation_modes.py` | Compatibility — keep |

## Broken / weak references

- `python -m src.adapti_guard.experiments.*` modules lack `__main__` (use scripts / `experiments/*/run.py`)
- OpenRouter multi-model track blocked without valid key
- Cerebras judge chat historically HTTP 402
- `.gitignore` previously ignored most of `datasets/` — release needs frozen allowlist

## Outdated experiments

| Artifact | Disposition |
|----------|-------------|
| EXP-002 early failed OpenRouter | Archive under `experiments/archive/` |
| EXP006 simulation-only metrics | Keep labeled `LEGACY_SIMULATION_ONLY` |
| REAL_LLM_EVAL_MIXED partial abort | Keep + status JSON |
| Empty root stubs | Remove |

## Refactor policy (this release)

1. **Do not rename** Python packages (`policy` stays `policy`, not `policies`) — avoids breaking imports.
2. **Organize** top-level `experiments/` into category folders with **compatibility symlinks** at legacy paths where scripts depend on them.
3. **Archive** root audits, config backups, empty stubs — never delete metrics/manifests/frozen data.
4. Map conceptual layout in README to existing package layout.
