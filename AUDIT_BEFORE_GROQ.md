# AUDIT_BEFORE_GROQ.md — PHASE 0

**Date:** 2026-09-03  
**Repo:** `/home/mohammadreza/01_BASE_Q1/adapti_guard`  
**Git HEAD:** `35833a6` (working tree has prior Gemini/EXP005 uncommitted changes)  
**Mode:** Read-only audit — no production logic changed in Phase 0.

---

## 1. Current architecture

```text
Dataset loaders
  (benchmark_q1 | frozen eval_v1 | unified_security_dataset.jsonl)
        ↓
Defense baselines (B0 / B1 / B2_L1–L3 / B3)
  OR Harmonized PolicyMode (fixed_l0–l3, full_adaptive, ablations)
        ↓
TargetModel.generate()   ← provider adapters
        ↓
LLMJudge.judge()         ← separate TargetModel call (blind payload)
        ↓
EvalEpisode / prediction_provenance
        ↓
compute_real_metrics + statistics (bootstrap / McNemar / Holm)
        ↓
results/experiment_runs/...  OR  results/real_llm/...
```

**Core abstractions**

| Piece | Location |
|-------|----------|
| `TargetModel` / `GenerationRequest` / `GenerationResult` | `src/adapti_guard/evaluation/target_model.py` |
| Factory `build_target_model()` | same — dispatches on `provider` in `configs/models.yaml` |
| Blind judge | `src/adapti_guard/evaluation/llm_judge.py` |
| Episode loop | `attack_success.evaluate_episode` |
| Publication pipeline | `experiments/real_llm_pipeline.py` |
| Legacy runner (OpenRouter-hardcoded gate) | `experiments/real_llm_runner.py` |
| Env / keys | `experiments/env_loader.py` + project `.env` |
| Provenance | `experiment_logging.py`, `prediction_provenance.py` |
| Stats | `evaluation/statistics.py` |

**Existing providers (do not break)**

| Provider | Class | Key env | Config keys |
|----------|-------|---------|-------------|
| OpenRouter | `OpenRouterTargetModel` | `OPENROUTER_API_KEY` | `model_*`, `judge_*`, `target_*` |
| Ollama | `OllamaTargetModel` | n/a (local) | `ollama_target` |
| Google Gemini | `GeminiTargetModel` | `GEMINI_API_KEY` | `gemini_target`, `gemini_judge` |

**Groq:** **NOT IMPLEMENTED** (no class, no yaml block, no `validate_groq_key`, no `EvaluationBackend.GROQ`).

---

## 2. Current provider flow

1. Experiment sets `PipelineConfig.backend` (`AUTO` | `openrouter` | `ollama` | `gemini`).
2. `resolve_backend()` validates the corresponding key / Ollama availability.
3. `build_models(config, backend)`:
   - Builds **target** via `build_target_model(target_config_key)` (with Gemini/Ollama remapping).
   - Builds **judge**:
     - Ollama → same local model
     - Gemini → `gemini_judge` (same family; documented fallback)
     - else → `build_judge()` → OpenRouter Claude primary + GPT-4o fallback
4. `run_baseline_evaluation` / `run_real_llm_pipeline` loops baselines and writes predictions + metrics.

**AUTO preference today:** Gemini if key valid → else OpenRouter → else Ollama.  
**Scientific rule for Groq primary:** do **not** make Groq the silent AUTO default; primary runs must set `backend=groq` explicitly.

---

## 3. Current CLI / backend entry points

| Entry | Path | Notes |
|-------|------|-------|
| Canonical multi-baseline pipeline | `experiments/REAL_LLM_EVAL/run.py` → `real_llm_pipeline` | Prefer for B0–B3 |
| Multi-model | `experiments/EXP004_MULTI_MODEL/run.py` | OpenRouter-oriented; currently BLOCKED 401 |
| Gemini EXP005 | `experiments/EXP005_GEMINI_FLASH/run.py` | Smoke VALID; full BLOCKED 429 |
| Legacy single-defense | `real_llm_runner.run_real_llm_evaluation` | **Hard-gated on OpenRouter only** |
| Preflight | `scripts/preflight_api.py` | Needs Groq awareness later |
| Harmonic sim | `scripts/run_q1_harmonized_v1.py` | Simulation — not Real-LLM |

---

## 4. Dataset / frozen artifacts (prefer existing)

| Artifact | Path | Hash (SHA-256) | Role |
|----------|------|----------------|------|
| Unified v2 | `~/datasets/q1_llm_security/ADAPTI_GUARD_Benchmark_v2/processed/unified_security_dataset.jsonl` | `3d3ae9e4863c0288c308bd736878f61c80c28fe288a6935927fe1b058edc9b24` | 12,799 lines — **do not rebuild** |
| Frozen eval_v1 | `datasets/frozen/eval_v1/dataset.jsonl` | `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24` | Attack-only n=770 |
| benchmark_q1 test | `datasets/benchmark_q1/test.jsonl` | `fa35c657dae473e21f6b89d389e3b85b4daa445eccd4aedeb415b344ab3cf74e` | Mixed attack+benign |
| Attack stream | `results/common_attack_stream.json` | `d101f94d97e0a29e8b9f9cc4dacb92472e29cd9af403114cb09b8f1d50a06c47` | Harmonized sim |

Loader already supports unified path via `PipelineConfig.use_unified_dataset` + `UNIFIED_DATASET_DEFAULT`.

---

## 5. Blockers (current)

| ID | Blocker | Impact | Severity |
|----|---------|--------|----------|
| B1 | **`GROQ_API_KEY` not present** in environment after `load_dotenv()` | Cannot run live Groq smoke / primary | **P0** |
| B2 | OpenRouter HTTP **401** (historical) | Preferred independent judge (Claude) unavailable | **P0 for full paper** |
| B3 | Gemini free-tier HTTP **429** (historical) | Gemini target/judge quota | **P1** |
| B4 | Ollama **not available** (`localhost:11434`) | No local independent judge fallback right now | **P1** |
| B5 | Judge independence rule | User requires: **do not silently use Groq target as judge**; if no independent judge → mark experiment **BLOCKED** | **P0 design** |
| B6 | `real_llm_runner.py` OpenRouter-only gate | Legacy path cannot select Groq | **P1** (fix during Phase 1) |
| B7 | No `paper/` dir | Manuscript is `docs/MANUSCRIPT_DRAFT.md` | P2 |
| B8 | Primary VALID real-LLM matrix still absent | Paper Results cannot be written yet | P0 science |

---

## 6. Files requiring modification (Phase 1+)

| File | Change |
|------|--------|
| `src/adapti_guard/evaluation/target_model.py` | Add `GroqTargetModel`; wire factory `provider == "groq"`; optional `reasoning_effort` |
| `configs/models.yaml` | Add `groq_target` + `groq:` block; keep all existing providers |
| `.env.example` | Add `GROQ_API_KEY=` (empty) |
| `src/adapti_guard/experiments/env_loader.py` | Add `validate_groq_key()` |
| `src/adapti_guard/experiments/real_llm_pipeline.py` | `EvaluationBackend.GROQ`; resolve + `build_models` for `groq_target`; **do not** AUTO-prefer Groq |
| `src/adapti_guard/experiments/real_llm_runner.py` | Provider-aware key validation (OpenRouter/Gemini/Groq/Ollama) |
| `src/adapti_guard/evaluation/experiment_logging.py` | `redact_env()`: `groq_key_present` / REDACTED; richer provider metadata in configs |
| `tests/test_groq_provider.py` | New mocked unit tests |
| `experiments/GROQ_SMOKE/` or `scripts/run_groq_smoke.py` | Exactly **one** real request |
| Later: `experiments/EXP006_GROQ_*` / extend REAL_LLM_EVAL | Explicit `backend=groq`, independent judge or BLOCKED |

---

## 7. Files that must NOT be modified (unless versioned necessity)

- `~/datasets/q1_llm_security/ADAPTI_GUARD_Benchmark_v2/processed/unified_security_dataset.jsonl` (and hashes)
- `datasets/frozen/eval_v1/*` frozen contents
- `results/common_attack_stream.json` (unless regenerating under new experiment ID)
- Existing OpenRouter / Gemini / Ollama adapter behavior (additive only)
- Simulation result JSONs used as historical artifacts (do not relabel as Real-LLM)
- Do not large-refactor `harmonized_runner.py` for Groq (orthogonal path)

---

## 8. Judge design (binding)

| Role | Preferred | Fallback policy |
|------|-----------|-----------------|
| Target | Groq `openai/gpt-oss-120b` | — |
| Judge | Independent (`judge_primary` OpenRouter Claude, or other non-target) | If OpenRouter & Gemini blocked and Ollama down → **BLOCKED**; never silent Groq=target=judge |

Smoke test (Phase 3) is **target-only** (one generation) — no judge required.

Primary experiment (Phase 5) requires an independent judge or explicit BLOCKED status with reason.

---

## 9. Recommended implementation order

1. **Phase 1 — Groq adapter**  
   `GroqTargetModel` (OpenAI-compatible, `base_url=https://api.groq.com/openai/v1`), yaml, `validate_groq_key`, `EvaluationBackend.GROQ`, factory, provenance redact, `real_llm_runner` provider-aware gate.  
   AUTO unchanged (no Groq default).

2. **Phase 2 — Unit tests**  
   Mock OpenAI client; no live quota.

3. **Phase 3 — One-request smoke**  
   Stop on failure. Requires `GROQ_API_KEY` in `.env`.

4. **Phase 4 — Small pilot**  
   Tiny n (e.g. 3–5) only if independent judge available; else document BLOCKED for judged metrics.

5. **Phase 5+ — VALID primary**  
   Frozen/unified protocol, baselines B0–B3 (+ L2/L3), stats, seeds, ablations — only after smoke + judge resolution.

---

## 10. Tests to run after Phase 1–2

```bash
.venv/bin/python -m py_compile src/adapti_guard/evaluation/target_model.py \
  src/adapti_guard/experiments/env_loader.py \
  src/adapti_guard/experiments/real_llm_pipeline.py \
  src/adapti_guard/experiments/real_llm_runner.py

.venv/bin/python -m pytest -q tests/test_groq_provider.py tests/test_target_model.py tests/test_real_llm_pipeline.py
.venv/bin/python -m pytest -q   # full suite regression
```

Live smoke (Phase 3 only): dedicated script with **max 1** API call.

---

## 11. Readiness to proceed to Groq integration

| Check | Status |
|-------|--------|
| TargetModel abstraction reusable | **YES** |
| OpenAI SDK in venv (`openai 2.54.0`) | **YES** |
| Patterns from OpenRouter adapter | **YES** |
| Unified + frozen datasets present | **YES** |
| `GROQ_API_KEY` configured | **NO — P0 before live smoke** |
| Independent judge ready | **NO — BLOCKED for judged primary until resolved** |
| Safe to implement Phase 1 code | **YES** (additive) |

**Verdict:** Ready to implement **Phase 1 (code + config + tests)**.  
**Not ready** for Phase 3 live smoke until `GROQ_API_KEY` is set in `.env`.  
**Not ready** for Phase 5 VALID primary until an **independent judge** path works or the run is honestly marked BLOCKED.

---

## 13. Phase 1–3 progress (post-audit)

| Phase | Status | Notes |
|-------|--------|-------|
| 0 Audit | **DONE** | This file |
| 1 Groq integration | **DONE** | `GroqTargetModel`, yaml, `validate_groq_key`, `EvaluationBackend.GROQ`, runner provider-aware, provenance redaction |
| 2 Unit tests | **DONE** | `tests/test_groq_provider.py`; full suite **122 passed, 2 skipped** |
| 3 Live smoke | **BLOCKED** | `GROQ_API_KEY not set` after `load_dotenv()` — see `experiments/GROQ_SMOKE/smoke_*.json` |

**AUTO policy:** Groq is **not** selected by AUTO; primary runs must set `backend=groq`.

**Next required human action:** add `GROQ_API_KEY=...` to project `.env` (never commit), then:

```bash
.venv/bin/python experiments/GROQ_SMOKE/run_smoke.py
```

Only if smoke status is `VALID`, continue to Phase 4 pilot.

---

*End of Phase 0 audit (+ Phase 1–3 status).*
