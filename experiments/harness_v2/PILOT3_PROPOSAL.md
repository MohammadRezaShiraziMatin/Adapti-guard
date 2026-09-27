# Pilot 3 proposal — full primary (Amendment 8 code path)

**Status:** **PROPOSED** — **not authorized to execute**. No live OpenRouter calls in this document.

---

## Scope (unchanged vs pilot 2)

| Parameter | Value |
|-----------|--------|
| Episodes | **160** = 10 scenarios × 2 instances × 4 models × 2 conditions (A0/B3) |
| `max_rounds` | **4** per episode |
| Scenarios | 7 attack + 3 benign (`PREREG_HARNESS_V2_FULL.md`) |
| Routing | DeepInfra, native tools, reasoning off, temp 0, `require_parameters`, no fallbacks |
| Criteria | **`experiments/harness_v2/PILOT2_CRITERIA_LOCKED.md`** — **unchanged** (P1–P6 table locked) |
| Criteria SHA-256 | `716c36024f1e6b33cec060800ae228ff4b32c6fa8f859b515647b2eccc4b8e85` |
| Templates SHA-256 | `b9f9994fcbae9af42810d2d9e3ff31bd64825cc5005a8fa2523abec91d7bdb9d` (`SCENARIO_INSTANCE_TEMPLATES.json` @ Amendment 8 Pass A i0/i1) |

---

## Code tip (Amendment 8 coding phase complete)

| Item | SHA (short) |
|------|-------------|
| **Branch tip for pilot 3** | see `AMENDMENT8_CODE_CHECKLIST.md` on `cursor/q1-p1-diagnosis-1282` |
| Combined mock regression | `tests/test_harness_v2_amendment8_combined_integration.py` |
| Checklist | `experiments/harness_v2/AMENDMENT8_CODE_CHECKLIST.md` |

**Runner:** `scripts/run_harness_v2_pilot.py` — async path, per-attempt HTTP client, incremental ledger (Amendment 6–8).

---

## Live command (**do not run** until owner **go**)

```bash
python3 scripts/run_harness_v2_pilot.py --live \
  --usd-cap 0.80 \
  --out-dir experiments/harness_v2/HARNESS_V2_PILOT3_<UTC-ts>/
```

- **Process:** exactly one pilot process; `PilotRunLock` on `experiments/harness_v2/.pilot_live.lock`.
- **Out dir:** new timestamped pack only (append-only persistence; `--resume` same dir only after crash).
- **Manifest:** `run_manifest.json` (`python_version`) + `pip_freeze.txt` at pilot start (Amendment 8 item 3).
- **Not run:** this proposal does not execute the command above.

---

## HTTP cap (Matin decision — **640**, 160-episode scope)

**Hard cap:** **`HTTP_CAP = 640`**

\[
160\ \text{episodes} \times 4\ \text{max\_rounds} = 640
\]

**Accounting:** **`HttpCompletionBudget.acquire()` once per billed HTTP attempt** (each harness **429** retry consumes an acquire). **HTTP cap overshoot = 0**.

**Stop rule:** When **`http_used ≥ 640`**, the pilot stops. **Every remaining scheduled episode** is persisted with status **`INVALID`** and **`reason: http_cap`** (no HTTP). Mock: `tests/test_harness_v2_amendment8_http_cap_remaining_invalid.py`.

*(Harness 429 retries still consume cap budget; at 640 the schedule halts even if retry headroom was not pre-allocated — Matin chose logical ceiling **640**, not a retry-inflated cap.)*

---

## USD (160-episode scope — show arithmetic)

**Expected HTTP** (`PILOT2_CRITERIA_LOCKED.md` / `E[rounds]=2.43`):

\[
160 \times 2.43 = 388.8 \approx 389
\]

**Expected USD** (40 episodes per model × `E[rounds]` × reasoning-off $/HTTP):

| Model | Episodes | × E[rounds] | × $/HTTP | Subtotal |
|-------|---------:|--------------:|---------:|---------:|
| qwen3 | 40 | 2.43 | 0.0000649 | **$0.00631** |
| gemma | 40 | 2.43 | 0.0000528 | **$0.00513** |
| llama | 40 | 2.43 | 0.0000740 | **$0.00719** |
| deepseek | 40 | 2.43 | 0.0001530 | **$0.01487** |
| **Total expected** | | | | **≈ $0.0335** |

**Worst HTTP:** **640** (cap = worst logical rows).

**Worst USD** (each episode bills up to 4 HTTP at model rate):

| Model | 40 ep × 4 × $/HTTP | Subtotal |
|-------|---------------------:|---------:|
| qwen3 | 160 × 0.0000649 | **$0.01038** |
| gemma | 160 × 0.0000528 | **$0.00845** |
| llama | 160 × 0.0000740 | **$0.01184** |
| deepseek | 160 × 0.0001530 | **$0.02448** |
| **Total worst** | | **≈ $0.0552** |

| Cap | Value | Rationale |
|-----|------:|-----------|
| Pilot 2 paper ceiling (historical) | **$0.05** | Locked pilot 2 registry — **not** pilot 3 target |
| **Pilot 3 hard cap (`usd_cap_hard`)** | **$0.80** | Below post–pilot-2 remaining credit **~$0.847**; incomplete-run brake |

---

## Wall-clock (160-episode scope — show arithmetic)

**Expected aggregate** (PREREG pilot-2 planning, median latency × E[HTTP] per model):

\[
\approx \mathbf{8.99\ h}
\]

**p90 aggregate:**

\[
\approx \mathbf{37.5\ h}
\]

**Ceiling-bound worst** (40 episodes/model; PREREG per-family worst bound seconds):

\[
\frac{40 \times (442.944787 + 457.158873 + 474.816364 + 763.263164)}{3600}
\approx \mathbf{23.8\ h}
\]

Per-episode before-round **X** enforced in code (`EpisodeWallClock`); upstream attempt wall **180s** + 429 backoff reserve **40s** per planning row.

---

## Pass / fail (criteria unchanged)

Evaluate **`PILOT2_CRITERIA_LOCKED.md`** P1–P6 **verbatim** on **`analysis_*`** ledger totals (exclude `superseded_by_resume`, `retried_after_rate_limit`, and **`retry_blocked_by_http_cap`** rows).

Report per-model breakdown; obfuscated scenarios per Amendment 7b standard.

---

## Abort and incomplete-run rules

1. **`usd_cap_hard` ($0.80)** → stop; remaining episodes **`NOT_RUN`** (USD path) unless already **`INVALID`** from HTTP cap.
2. **`http_cap` (640)** → stop; remaining episodes **`INVALID`** / `reason: http_cap`.
3. **`INVALID_PROVIDER_ERROR`**, **`INVALID_TIMEOUT`**, **`INVALID_INCOMPLETE`**: no C2 / P1–P6 efficacy claims on those rows.
4. **SIGKILL / crash:** `--resume` same `out-dir` only; supersede partial rows (Amendment 7c).
5. **Duplicate process / lock held:** exit **2** without HTTP.
6. **No live call** without explicit owner authorization.

---

## Pre-flight (owner)

1. Confirm OpenRouter **`limit_remaining` ≥ **$0.80** (+ margin).
2. Confirm runner **`HTTP_CAP == 640`** (Matin decision — locked for pilot 3).
3. Record new row in `experiments/judge_gold/RUN_REGISTRY.md` when dir is created.
4. Verify templates + criteria SHA match table above.

---

## Post-run (when authorized)

1. `scripts/analyze_harness_v2_pilot.py` on pack.
2. Compare **`billed_*`** vs **`analysis_*`** in `running_ledger.json`.
3. Reconcile cancelled_timeout placeholders if generation IDs available (Amendment 8 item 5).

**STOP — proposal only; pilot 3 not executed.**
