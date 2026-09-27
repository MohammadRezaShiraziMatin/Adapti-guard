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
| **Branch tip for pilot 3** | **`de1e4e6`** on `cursor/q1-p1-diagnosis-1282` (merge to owner default before live) |
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

## HTTP cap (hard — **160-episode** pilot scope)

**Scope:** **160 episodes**, `max_rounds=4` (same as pilot 2 / locked criteria).

**Logical completion ceiling (no harness 429 retries):**

\[
160 \times 4 = \mathbf{640}
\]

**Accounting:** **`HttpCompletionBudget.acquire()` once per billed HTTP attempt** (each harness **429** retry consumes an acquire). **HTTP cap overshoot = 0** (commit `2941692`).

**Retry-inclusive worst (planning only):** with **`rate_limit_max_retries=2`**, each tool round may bill up to **3** attempts (initial + 2 harness retries):

\[
160 \times 4 \times 3 = \mathbf{1920}
\]

| Option | `HTTP_CAP` | Behavior if cap hit mid-run |
|--------|------------|-----------------------------|
| **A** | **640** | Stop at logical ceiling; remaining episodes **`NOT_RUN`** / incomplete semantics; no retry headroom beyond one attempt per round |
| **B** | **1920** | Allows retry-worst billed rows within cap; still stops cleanly at cap |

**Owner decision (Matin):** choose **A** or **B** before live pilot 3 — this proposal does **not** select either.

*(Full-primary **K=24** scope — **not** pilot 3 — uses **~16848** logical / **~17568** retry-worst rows; see Amendment 8 Option C and `PREREG_HARNESS_V2_FULL.md` primary table.)*

---

## USD caps (160-episode scope)

| Cap | Value | Rationale |
|-----|------:|-----------|
| Pilot 2 paper ceiling (historical) | **$0.05** | Locked pilot 2 registry row — **not** pilot 3 target |
| **Pilot 3 hard cap (`usd_cap_hard`)** | **$0.80** | **Below** post–pilot-2 remaining credit **~$0.847** (`limit_remaining`); intentional incomplete-run brake (Amendment 8 §2.4 Option C) |
| Soft check | After **each** persisted HTTP row | At most **one** row may push **billed** spend over cap (placeholder semantics for `cancelled_timeout`) |

**Credit arithmetic (planning):**

- Remaining credit ≈ **$0.847**
- Proposed hard cap **$0.80** ⇒ margin ≈ **$0.047** under remaining credit

**Expected spend (160 episodes, reasoning-off $/HTTP, E[rounds]=2.43):**

\[
E[\text{HTTP}] \approx 160 \times 2.43 = 388.8
\]

Using locked pilot-2 planning rates (`PILOT_CRITERIA_LOCKED.md` / prereg pilot-2 row **~$0.0335** expected on 160 episodes) — informational; **not** the hard cap.

**Worst-case USD (160 episodes, rate-table scaling from PREREG primary worst ~$0.48 at 5376 HTTP rows):**

- At **640** billed rows (cap **A**): \(640/5376 \times 0.48 \approx\) **$0.057**
- At **1920** billed rows (cap **B**, retry-worst): \(1920/5376 \times 0.48 \approx\) **$0.171**

*(Amendment 8 **~$1.4518** retry-worst USD is for **full primary K=24** (~17568 HTTP rows), not this 160-episode pilot.)*

---

## Wall-clock estimates (160 episodes — planning only)

Method: `PREREG_HARNESS_V2_FULL.md` / Amendment 8 (pilot-2 latency × E[HTTP]; ceiling sum uses **40 episodes per model** = 160/4).

| Metric | Order of magnitude |
|--------|-------------------|
| **Expected aggregate** | ≈ **8.99 h** sequential (median latency × E[HTTP] per model — PREREG pilot-2 row) |
| **p90 aggregate** | ≈ **37.5 h** (same PREREG pilot-2 row) |
| **Ceiling-bound worst (160 episodes)** | **40** episodes/model × \(\sum_f T^{\text{worst}}_f\) / 3600 with PREREG X table (442.9 + 457.2 + 474.8 + 763.3 s) ≈ **23.8 h** |

*(PREREG **217.4 h** ceiling is **K=24 primary** with **366** episodes/model — not pilot 3 scope.)*

Per-episode before-round **X** enforced in code (`EpisodeWallClock`); upstream attempt wall **180s** + 429 backoff reserve **40s** per planning row.

---

## Pass / fail (criteria unchanged)

Evaluate **`PILOT2_CRITERIA_LOCKED.md`** P1–P6 **verbatim** on **`analysis_*`** ledger totals (exclude `superseded_by_resume`, `retried_after_rate_limit`, and **`retry_blocked_by_http_cap`** rows from analysis aggregates per Amendment 7c/8).

Report per-model breakdown; obfuscated scenarios per Amendment 7b standard (not split KNOWN_RISK for pilot 3 proposal).

---

## Abort and incomplete-run rules

1. **`usd_cap_hard` ($0.80)** reached mid-schedule → **`PilotBudgetExceeded`**, stop cleanly; remaining episodes **`NOT_RUN`** / **`INVALID_INCOMPLETE`** as applicable.
2. **`http_cap`** exhausted → stop cleanly; same incomplete semantics.
3. **`INVALID_PROVIDER_ERROR`**, **`INVALID_TIMEOUT`**, **`INVALID_INCOMPLETE`** episodes: **no C2 / P1–P6 efficacy claims** on those rows; pack retained append-only.
4. **SIGKILL / crash:** `--resume` on **same** `out-dir` only; supersede partial episode rows (Amendment 7c).
5. **Duplicate process / lock held:** exit **2** without HTTP.
6. **No live call** without explicit owner authorization after this proposal is approved.

---

## Pre-flight (owner)

1. Confirm OpenRouter **`limit_remaining` ≥ **$0.80** (+ margin).
2. Set **`HTTP_CAP`** to **640 (option A)** or **1920 (option B)** per owner decision above.
3. Record new row in `experiments/judge_gold/RUN_REGISTRY.md` when dir is created.
4. Verify templates + criteria SHA match table above.

---

## Post-run (when authorized)

1. `scripts/analyze_harness_v2_pilot.py` on pack.
2. Compare **`billed_*`** vs **`analysis_*`** in `running_ledger.json`.
3. Reconcile cancelled_timeout placeholders if generation IDs available (Amendment 8 item 5).

**STOP — proposal only; pilot 3 not executed.**
