# Part 1 — Llama 4 Maverick probe (STOP)

**Branch:** PR #80 · **Live smoke:** **NOT RUN** (probe gate failed)

## 1) Provider metadata (GET only)

**Artifact:** `PROVIDER_PROBE_MAVERICK.json`

| Field | Value |
|-------|--------|
| OpenRouter slug | `meta-llama/llama-4-maverick` |
| DeepInfra endpoint | `DeepInfra \| meta-llama/llama-4-maverick-17b-128e-instruct` |
| Quantization | **fp8** |
| Pricing (DeepInfra JSON) | prompt **`0.0000002`**, completion **`0.0000008`** USD/token |
| `tools` in supported_parameters | **false** |
| `tool_choice` in supported_parameters | **false** |

**Decision:** **STOP** — harness v2 requires native tools + `tool_choice` on DeepInfra with `require_parameters: true`.

## 2) Smoke criteria lock

**File:** `MAVERICK_SMOKE_CRITERIA_LOCKED.md` (SHA recorded in commit message).

## 3) Live smoke

**Skipped.** Spend **$0.000**.

## 4) Amendment / budget recompute

**Not applied** (smoke gate failed). Pilot **`1af54c1`** and locked thresholds unchanged. Full-run maverick budget recompute deferred until a tools-capable DeepInfra row exists.

## PASS/FAIL table

| Step | Result |
|------|--------|
| Probe tools+tool_choice | **FAIL** |
| Smoke S1–S5 | **NOT RUN** |
| Amendment 5 | **NOT APPLIED** |
