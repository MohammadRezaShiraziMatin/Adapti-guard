# Layer A v2 attack pack — how to run

Frozen mixed eval of **real prompt-injection** episodes (not BeaverTails / jailbreak
relabeled as PI). Pack card: `datasets/frozen/layer_a_v2/DATASET_CARD.md`.

This document is wiring + procedure only. It does **not** claim a defense win.

## Paths

| Artifact | Path |
|---|---|
| Pack root | `datasets/frozen/layer_a_v2/` |
| Runner split | `datasets/frozen/layer_a_v2/test.jsonl` |
| Canonical copy | `datasets/frozen/layer_a_v2/dataset.jsonl` |
| SHA-256 | `datasets/frozen/layer_a_v2/hashes.sha256` |
| Builder | `scripts/build_layer_a_v2_pack.py` |
| CLI wrapper | `scripts/run_layer_a_v2_eval.py` |

`eval_v1` is unchanged and remains attack-only.

## Scientific contract (same as Layer A OpenRouter)

- Target key: `target_2` → `qwen/qwen-2.5-7b-instruct`
- Judge key: `judge_fallback` → `qwen/qwen-2.5-72b-instruct`
- Target ≠ Judge
- `cache.enabled=false` in `configs/models.yaml`
- `multi_model.judge=judge_fallback` (OpenRouter `build_judge()` reads yaml, not `--judge` alone)
- ASR from the independent judge only (no regex ASR)

Each attack row has `success_condition`. The runner copies it to `JudgeInput`
and **does not** send it to the target.

## Rebuild the pack (optional)

```bash
python3 scripts/build_layer_a_v2_pack.py
```

Overwrites JSONL + hashes + card. Commit the frozen outputs if they change.

## B0 probe (required before full B0+B3)

Check the key:

```bash
python3 -c "import os; print('SET' if os.environ.get('OPENROUTER_API_KEY') else 'MISSING')"
```

If **MISSING**: ship the pack only. Do not fake probe metrics.

If **SET**:

```bash
python3 scripts/preflight_api.py --provider openrouter

TS=$(date -u +%Y%m%d-%H%M%S)
python3 scripts/run_layer_a_v2_eval.py \
  --require-key \
  --backend openrouter --target target_2 --judge judge_fallback \
  --baselines B0 --attack-n 20 --benign-n 20 --seed 42 \
  --output "experiments/real_llm_eval/LAYER_A_V2_B0_PROBE/${TS}" \
  --experiment-id LAYER-A-V2-B0-PROBE
```

Equivalent without the wrapper:

```bash
python3 scripts/run_real_eval.py \
  --backend openrouter --target target_2 --judge judge_fallback \
  --benchmark-dir datasets/frozen/layer_a_v2 --split test \
  --baselines B0 --attack-n 20 --benign-n 20 --seed 42 \
  --output /absolute/path/to/experiments/real_llm_eval/LAYER_A_V2_B0_PROBE/${TS} \
  --experiment-id LAYER-A-V2-B0-PROBE
```

Use an **absolute** `--output` if you invoke `experiments/REAL_LLM_EVAL/run.py`
directly: that script sets `ROOT` to `experiments/`, so a relative output path
nests under `experiments/experiments/`.

Write `AUDIT.md` in the probe folder from `metrics.json` only. Do not invent numbers.

Recorded probe (this branch): `experiments/real_llm_eval/LAYER_A_V2_B0_PROBE/20260913-190706/`
(`AUDIT=VALID`, B0 ASR from `B0/B0_metrics.json`). Pack-quality only — not a defense result.

### Probe decision rule

- B0 ASR **≥ 0.15**: pack is strong enough to consider a later full B0+B3 Layer A run.
- B0 ASR **< 0.15**: pack is still **too weak** — strengthen once (harder / clearer canaries) and re-probe once.
- Informal next-eval band on Target 7B / B0: **~0.3–0.6**. That band is a pack-quality goal, not a defense claim.

Do **not** run full B0+B3 Layer A until the probe clears 0.15 or you report a blocker.

Recorded full Layer A on pack v2 (this branch):
`experiments/real_llm_eval/LAYER_A_V2_OPENROUTER/20260913-191217/` (`AUDIT=VALID`).
B3 does not beat B0 on that draw (see that folder's `AUDIT.md`). Not a manuscript Results rewrite.

## Offline checks (no API)

```bash
python3 scripts/build_layer_a_v2_pack.py
python3 -m pytest tests/test_layer_a_v2_pack.py tests/test_blind_judge.py tests/test_real_llm_pipeline.py -q
```
