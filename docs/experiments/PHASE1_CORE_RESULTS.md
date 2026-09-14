# Phase 1 core results (architectural, offline)

**Quality gate: PASS** — see [`PHASE1_FINAL_QUALITY_GATE.md`](PHASE1_FINAL_QUALITY_GATE.md).

Not a VNEXT re-score. Not an ASR claim. Official VNEXT confirmation remains **FAIL**.

LLM/API calls = **0**. Frozen packs were read, not written.

---

## Pipeline

`CoreDefensePipeline` → ContextBuilder → **`PromptInjectionDetectorPhase1`** → `RiskEngineCore` → `CorePolicyEngine` → `DefenseActionLayer` → `ToolPermissionGate` → `EpisodeTrace`.

`PHASE1-CORE` uses Phase1 evidence. `VNEXT-ADAPT` still uses frozen `evidence_v4.0` + `tool_sensitive=False`.

Causal behavior:

- A0 executes benign tools (`search`, privileged workflows)
- A1 sanitizes **text-only** MEDIUM (no declared tool)
- A2 denies declared tools under MEDIUM/HIGH tool-mediated risk
- A3 blocks text-only HIGH; no tool execution
- Hard negatives (quoted / analysis / redaction) stay A0
- Gold labels cannot drive the core path
- `target_refusal` ≠ `correct_block`

---

## Tests

- Phase1 core + evidence scenarios + v4 detector + tool loop + Phase2 harness + workshop facts + pack/runner: **95 passed**
- Broader deterministic suite: **241 passed**; 3 pre-existing provider-import failures (`google`/`openai`)
- Frozen v4 identity still `evidence_v4.0`

---

## Offline frozen-pack diagnostics (NOT performance)

Command: `python3 scripts/run_phase1_core_offline_eval.py`

Pack SHA-256 `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518` (n=122).

After Phase1 evidence upgrade (diagnostic):

| Metric | Value |
| --- | ---: |
| Attack detector hits | 56 / 61 |
| Attack residual misses | 5 |
| Attack actions | A2=56, A0=5 |
| Benign false A2/A3 | 0 |
| Benign A0 / A1 | 60 / 1 |

Do not cite as a live-model ASR improvement or a reversal of VNEXT FAIL.

---

## Integrity

| Artifact | Unchanged |
| --- | --- |
| `datasets/frozen/vnext_confirm_v1/dataset.jsonl` | YES (`523c8818…`) |
| Layer A TEST `47b975f7…` | YES |
| VNEXT AUDIT `20260914-133147` | YES |
| `VNEXT-MSID-0.1` δ=0.20 | YES |
| Official FAIL numbers | YES |
| Detector v4 freeze identity `evidence_v4.0` | YES |

---

## Limitations

- Residual obfuscation / social-engineering / subtle multi-turn misses (~5/61 diagnostic).
- Text-only MEDIUM → A1 by design.
- Legacy `AdaptiGuard.run` is regex-v3 compatibility only.
- No live Target/Judge evaluation.

## Non-claims

Not SOTA. Not production-ready. Does not solve prompt injection. Does not claim statistically significant improvement or a qualified win.
