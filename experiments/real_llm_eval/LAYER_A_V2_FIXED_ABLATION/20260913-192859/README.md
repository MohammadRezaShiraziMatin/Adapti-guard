# Layer A v2 fixed-intervention ablation

Run ID: `20260913-192859`  
Status: **VALID**  
Interpretation: **CASE D**

This folder is an immutable record of a diagnostic ablation on the frozen Layer A v2 pack. It does **not** overwrite `experiments/real_llm_eval/LAYER_A_V2_OPENROUTER/20260913-191217/`.

## What was run

| Policy | Code key | What it is | Scored? |
| --- | --- | --- | --- |
| B0 | `B0` | Historical A0 control | Yes (copied, not rerun) |
| B3 | `B3` | Historical adaptive control (observed A1) | Yes (copied, not rerun) |
| B2 / L2 | `L2` (`B2` alias) | Unconditional A2 | **No** — tool restriction is not enforceable here |
| B2_L3 | `B2_L3` | Existing risk-gated defense **level** 3 | Yes (new live run) |
| L3 | `L3` | Unconditional A3 | Yes (new live run; no target/judge calls) |

`B2_L3` is **not** the same policy as `L3`. `B2_L3` still consults the detector. `L3` always blocks.

## Contract

- Pack: `datasets/frozen/layer_a_v2/` SHA-256 `76c60433d07258d06c5df451bfdd5be4d8ff08988b26c3ecea32ebc32d09ac33`
- Seed 42, n=40 (20 attack + 20 benign), cache off
- Target `qwen/qwen-2.5-7b-instruct` ≠ judge `qwen/qwen-2.5-72b-instruct`
- Git commit at execution: `01d2350d8af1d4924e7af56cb9194766b4a2f37e`

See `AUDIT.md` and `docs/experiments/LAYER_A_V2_FIXED_ABLATION.md`.
