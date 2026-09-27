# Matin request — Part 1 + Part 2 final report (PR #80)

**Branch:** `cursor/q1-p1-diagnosis-1282` · **Commit SHAs:** see git log after push.

---

## Part 1 — Maverick smoke (live cap 4 HTTP / $0.005)

| Step | Result |
|------|--------|
| Provider probe (`tools` + `tool_choice` on DeepInfra) | **FAIL** |
| Smoke criteria locked (`MAVERICK_SMOKE_CRITERIA_LOCKED.md`) | **DONE** (SHA in file) |
| Live smoke S1–S5 | **NOT RUN** |
| Attack C2 | **NOT RUN** |
| Amendment 5 / maverick swap in prereg | **NOT APPLIED** |
| Full-run budget recompute (168 pairs) | **DEFERRED** (probe gate) |

**Spend:** $0.000

**Probe facts:** `PROVIDER_PROBE_MAVERICK.json` — slug `meta-llama/llama-4-maverick`, DeepInfra FP8, pricing prompt `2e-7` / completion `8e-7` USD/token; `supported_parameters` lacks `tools` and `tool_choice`.

---

## Part 2 — J3 code-only

### (a) Gold v3 / locked 40-item set

| Question | Answer |
|----------|--------|
| GOLD_SET_v3 exists? | **No** (`experiments/judge_gold/GOLD_SET_v3.jsonl` absent) |
| Locked 40-item set | `experiments/judge_gold/GOLD_SET_v2.jsonl` |
| Manifest `content_sha256` | `67f1fe227f7b4d580dc0fa7d7cc6c5bf640365eaca853d9236ad8385bdb6f939` |

### (b) J1 / J2 labels on all 40

| Judge | All 40? | Path |
|-------|---------|------|
| J1 (glm-4.7 P0) | **40 rows**; **39/40 parse-ok** (`GOLD_v2_017` parse error) | `experiments/judge_gold/J1_V2_ABLATION_20260927-070101/per_item.jsonl` |
| J2 (grok-4.7) | **No** | No `j2_*` pack on GOLD_SET_v2 in repo |

**Fleiss κ(J1,J2,J3):** not computable until J2 live on v2 (~**$0.05–0.06** estimated at panel Grok rates and ~900/120 tokens per item — see `run_j3_gold_eval.py` `estimate_j2_cost_usd`).

### (c) `ANTHROPIC_API_KEY`

**Not present** in environment at report time (presence check only).

### J3 implementation

- Module: `src/adapti_guard/evaluation/anthropic_j3_judge.py`
- Script: `scripts/run_j3_gold_eval.py` (default prepare-only; **not run**)
- Criteria lock: `experiments/judge_gold/J3_EVAL_CRITERIA_LOCKED.md`
- Schema diff: `experiments/judge_gold/J3_SCHEMA_FIELD_DIFF.md`

**J3 cost estimate (40 calls):** ~**$0.06** USD at script placeholders ($1/M input, $5/M output tokens, 900+120 tokens/item).

---

## PASS/FAIL summary

| Part | Overall |
|------|---------|
| Part 1 probe gate | **FAIL → STOP** |
| Part 2 deliverables | **COMPLETE** (no live J3) |
