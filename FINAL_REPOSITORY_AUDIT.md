# Final Repository Audit — AdaptiGuard

Date: 2026-09-04  
Scope: GitHub-ready packaging and publication artifact structure (methodology unchanged).

## Repository status

| Check | Result | Evidence |
|-------|--------|----------|
| Structure | **PASS** | Standard tree: `src/adapti_guard/`, `configs/{models,experiments,evaluation}/`, `datasets/{frozen,benchmark*}`, `experiments/{real_llm_eval,simulation,ablations,statistics,reports,archive}/`, `results/{paper_results,figures,raw,archive}/`, `docs/`, `docs/paper/`, `tests/`, `scripts/` |
| Imports | **PASS** | `python -m compileall src` exit 0; core packages import under `PYTHONPATH=.` |
| Tests | **PASS** | `pytest`: **123 passed** (2026-09-04). Fixed Gemini retry `time.sleep(delay)` that had been disabled (`pass # disabled retry sleep`) |
| Experiments reproducible | **PASS** (with caveats) | Frozen eval + attack stream hashes retained; legacy experiment paths kept as **symlinks**; runners importable via `experiments/REAL_LLM_EVAL/run.py`. Full real-LLM re-run needs live API keys and is rate-limit sensitive. Judge ASR for PHASE5 constrained set remains **NOT COMPUTABLE** without a working independent judge (documented; not fabricated). |
| Documentation | **PASS** | `README.md`, `docs/{methodology,threat_model,reproducibility,limitations,final_results}.md`, `docs/paper/01–05_*.md`, audit/move/remove logs |

## Files moved

See `docs/MOVED_FILES_LOG.md`. Summary:

- Experiment suites → `experiments/{real_llm_eval,simulation,ablations,statistics,reports,archive}/` with compatibility symlinks at legacy names
- Root audit reports → `docs/archive/`
- Root stub dirs (`attacks/`, `defenses/`, `evaluation/`, `figures/`, `models/`) → `results/archive/legacy_root_stubs/`
- `paper_notes/` → `docs/archive/paper_notes_dup/paper_notes` (canonical: `docs/paper/`)
- `REPRODUCIBILITY.md` → `docs/archive/REPRODUCIBILITY_ROOT.md` (canonical: `docs/reproducibility.md`)
- Paper-facing result copies under `results/paper_results/`

## Files removed

See `docs/REMOVED_FILES_LOG.md`. Only caches, empty stubs, duplicate config backups, and transient logs. **No** metrics, manifests, frozen datasets, or paper evidence deleted.

## Files created (packaging)

- `LICENSE` (MIT), `CITATION.cff`, updated `.gitignore`, rewritten `README.md`
- `docs/REFACTOR_AUDIT.md`, `docs/REMOVED_FILES_LOG.md`, `docs/MOVED_FILES_LOG.md`
- `docs/methodology.md`, `threat_model.md`, `reproducibility.md`, `limitations.md`, `final_results.md`
- `docs/paper/01_abstract.md` … `05_limitations.md`
- Compatibility aliases: `src/adapti_guard/{models,policies,utils}/`
- Per-experiment packaging stubs where missing: `config.json`, `metrics.json` (or honest `METRICS_NOT_STANDARDIZED` wrapper), `run_metadata.json`, `README.md`, `logs/`, optional `results.json` mirrors of real metrics only
- This file: `FINAL_REPOSITORY_AUDIT.md`

## Important files that must remain

- `datasets/frozen/eval_v1/` (+ hashes)
- `results/common_attack_stream.json` (+ hash references in manifests)
- `experiments/real_llm_eval/PHASE5_CONSTRAINED/raw_results.jsonl` and metrics
- `experiments/real_llm_eval/REAL_LLM_EVAL/` (B0–B3 artifacts)
- `results/phase7/`, `results/phase8/`
- `experiments/reports/FINAL_RESEARCH_MANIFEST.json` and paper section drafts
- `baselines/` (root) — still imported by `EXP003_BASELINES`
- `inspect-test/` — Inspect adapter sample (kept)

## Remaining issues / warnings

1. **Judge availability:** Cerebras judge previously returned HTTP 402; PHASE5 ASR not recomputed as success. Do not treat missing judge as ASR=0.
2. **Mixed real-LLM eval:** `REAL_LLM_EVAL_MIXED` status `ABORTED_PARTIAL` (rate limits); partial metrics only.
3. **Root layout leftovers:** `baselines/`, `inspect-test/`, `garak_adapter.py`, `run_mvp.py`, `experiments/runs/` retained for compatibility — not all under the idealized tree.
4. **`.env` / `.env.backup*`** present locally; gitignored — do not commit.
5. **`.llm_cache/`, `.venv/`, `.venv_phase5/`** local only; gitignored / should stay untracked.
6. Some normalized `metrics.json` files are **packaging stubs** (`status: METRICS_NOT_STANDARDIZED`) pointing at evidence files — they are not scientific results.
7. Full multi-model Target matrix incomplete (documented in limitations).
8. Git working tree has large staged/unstaged packaging delta; **not committed** unless explicitly requested.

## Quality commands executed

```bash
python -m compileall -q src          # exit 0
PYTHONPATH=. pytest -q               # 123 passed
find (project) __pycache__ / *.pyc   # cleaned outside venv
```

## Verdict for publication packaging

Ready for a **public GitHub release commit** after review of staged secrets (ensure `.env` excluded) and optional squash of packaging commits. Scientific claims must continue to cite real artifacts only; incomplete judge/multi-model coverage remains an explicit limitation.
