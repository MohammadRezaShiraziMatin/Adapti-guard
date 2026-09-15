# AUDIT_SMOKE — Layer A OpenRouter path

**AUDIT=INVALID**
**STATUS=INVALID_MISSING_KEYS**

Date (UTC): `2026-09-13T18:19:32Z`
Git parent at audit write: `5a7684835fe57303f7786c51719973ea168c1210`
Experiment id: `LAYER-A-OPENROUTER-SMOKE`
Folder: `experiments/real_llm_eval/LAYER_A_OPENROUTER_SMOKE/20260913-181851/`

Layer A (B0 vs B3, 20+20) was **not started**. Hard rule: stop if `OPENROUTER_API_KEY` is missing. No metrics were invented.

## Verdict

| Check | Result | Evidence |
|---|---|---|
| `OPENROUTER_API_KEY` in env / `.env` | **FAIL** — not set | `preflight.txt`, `metrics.json` |
| Target YAML id `target_2` | PASS (config only) | `qwen/qwen-2.5-7b-instruct` |
| Judge YAML id `judge_fallback` | PASS (config only) | `qwen/qwen-2.5-72b-instruct` |
| Target id ≠ Judge id (YAML) | PASS (config only) | 7B vs 72B Qwen 2.5 |
| `cache.enabled=false` | PASS | `configs/models.yaml` |
| `multi_model.judge=judge_fallback` | PASS | OpenRouter path ignores CLI `--judge` |
| Live Target non-empty | **NOT RUN** | key missing |
| Live Judge non-empty / parse OK ≥1 | **NOT RUN** | key missing |
| Live Target id ≠ Judge id in artifacts | **NOT RUN** | no live calls |
| Latencies not all 0 | **NOT RUN** | no live calls |
| Judge-fail counted as ASR=0 | N/A | no episodes |

## Exact commands

```bash
python3 scripts/preflight_api.py --provider openrouter
# stdout: BLOCKED: OPENROUTER_API_KEY not set
# exit: 1

python3 scripts/run_real_eval.py \
  --backend openrouter \
  --target target_2 \
  --judge judge_fallback \
  --baselines B0 \
  --attack-n 2 \
  --benign-n 2 \
  --seed 42 \
  --output /workspace/experiments/real_llm_eval/LAYER_A_OPENROUTER_SMOKE/20260913-181851 \
  --experiment-id LAYER-A-OPENROUTER-SMOKE
# stdout status: BLOCKED
# reason: OPENROUTER_API_KEY not set
# exit: 1
```

No `--no-cache` flag was used. Cache off is `cache.enabled: false` in `configs/models.yaml`.

## Config diffs (this run)

`configs/models.yaml`:

1. `cache.enabled`: `true` → `false`
2. `multi_model.judge`: `judge_primary` → `judge_fallback`

Unchanged model ids (already matched the required pair):

- `models.target_2.model` = `qwen/qwen-2.5-7b-instruct` (provider `openrouter`)
- `models.judge_fallback.model` = `qwen/qwen-2.5-72b-instruct` (provider `openrouter`)

YAML **description** strings do not match those ids (documented, not rewritten):

- `judge_fallback.description` still says `Fallback judge — GPT-4o`
- `target_2.description` still says `Legacy — Qwen2.5-7B`

Claude Sonnet keys remain in yaml (`models.judge`, `models.model_d` = `anthropic/claude-sonnet-4`) but were **not** selected for this path.

## Why `--judge` is not sufficient

`experiments/REAL_LLM_EVAL/run.py` stores `--judge` on `PipelineConfig.judge_config_key`, but `build_models()` for `--backend openrouter` calls `build_judge()`, which reads `multi_model.judge` / `multi_model.judge_fallback` from yaml. That is why `multi_model.judge` was set to `judge_fallback`.

## Pipeline output (verbatim)

From `metrics.json` (written by `run_real_llm_pipeline`; not fabricated):

```json
{
  "status": "BLOCKED",
  "reason": "OPENROUTER_API_KEY not set",
  "experiment_id": "LAYER-A-OPENROUTER-SMOKE",
  "backend": "openrouter"
}
```

From `preflight.txt`:

```text
BLOCKED: OPENROUTER_API_KEY not set
```

Env scan: `OPENROUTER_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY` all absent. No `.env` file in the workspace (only `.env.example`).

## Metrics

**None.** Smoke did not reach Target or Judge. No ASR, utility, FPR, latency, cost, or judge-fail rate exists for this attempt. Do not treat historical `experiments/REAL_LLM_EVAL/` numbers as this run.

## CLI / path notes (blockers, not metrics)

- `python` is not on PATH; use `python3`.
- `experiments/REAL_LLM_EVAL` is a symlink to `experiments/real_llm_eval/REAL_LLM_EVAL`. `run.py` sets `ROOT = Path(__file__).resolve().parents[2]`, which resolves to `experiments/` rather than the repo root. Relative `--output` therefore landed under `experiments/experiments/...` on the first try. Absolute `--output` was used for the recorded attempt. Accidental nested directory was removed.

## Layer A

**NOT STARTED.** Smoke is INVALID (`INVALID_MISSING_KEYS`).

To unblock: set `OPENROUTER_API_KEY` (format `sk-or-…`) in the environment or a local `.env` (gitignored), then re-run smoke before Layer A.
