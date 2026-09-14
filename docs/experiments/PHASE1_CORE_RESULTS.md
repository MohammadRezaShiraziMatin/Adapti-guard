# Phase 1 core results (architectural, offline)

**Quality gate: PASS** (architecture only).  
This is **not** a VNEXT re-score, not an ASR claim, and not a reversal of FAIL.

LLM/API calls = **0**. Frozen packs were read, not written.

---

## What changed

`CoreDefensePipeline` runs ContextBuilder → detector v4 → `RiskEngineCore` → `CorePolicyEngine` → `DefenseActionLayer` → `ToolPermissionGate` → `EpisodeTrace`.

`PHASE1-CORE` / `make_core_defense` is a new factory. `VNEXT-ADAPT` / `make_b3_adaptive_v4` still uses `tool_sensitive=False`.

Causal behavior now tested:

- A0 executes `search`
- A1 sanitizes and still allows tools (honest)
- A2 denies `send_email` / other privileged tools; registry stays empty
- A3 blocks; no tool execution
- LOW privileged tools remain allowed
- Gold `is_attack` / `label` / `category` cannot drive the core path
- `target_refusal` ≠ `correct_block`

---

## Tests

`tests/test_phase1_core_pipeline.py`: **17 passed**.

Related regression (v4 detector, tool loop, Phase 2 harness, workshop FAIL facts, pack, runner, action/policy, core/pipeline): **82 passed**.

Broader `pytest` (ignore pre-existing `test_artifact_standard.py` collection error): **226 passed**. Three failures in `test_gemini_provider.py` / `test_groq_provider.py` (`No module named 'google'` / `'openai'`) are environment gaps, not this change.

---

## Offline frozen-pack diagnostics (not performance)

Command: `python3 scripts/run_phase1_core_offline_eval.py`

Pack SHA-256 still `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` (n=122).

| Action | Count |
| --- | ---: |
| A0 | 112 |
| A1 | 2 |
| A2 | 7 |
| A3 | 1 |

`tool_denied=7`, `tool_executed=75`, traces complete 122/122.

Most rows stay A0 because detector v4 still does not fire on much of this authored pack. That is a remaining detection gap, not a confirmation win. Do not cite these counts as security performance.

---

## Integrity

| Artifact | Unchanged |
| --- | --- |
| `datasets/frozen/vnext_confirm_v1/dataset.jsonl` | YES (`523c8818…`) |
| Layer A TEST `47b975f7…` | YES |
| VNEXT AUDIT `20260914-133147` | YES (not rewritten) |
| `VNEXT-MSID-0.1` δ=0.20 | YES |
| Official FAIL numbers | YES |

---

## Limitations

- Text-only MEDIUM without a privileged tool still maps to A1.
- Core policy is a new table; it is not the historical `DefensePolicyEngine` used for VNEXT-ADAPT.
- Detector v4 scores on this pack remain mostly non-firing; Phase 1 did not retune it.
- `AdaptiGuard.run` (regex v3 MVP) was not rewritten.
- No live Target/Judge evaluation.

---

## Non-claims

Not SOTA. Not production-ready. Does not solve prompt injection. Does not claim statistically significant improvement or a qualified win.
