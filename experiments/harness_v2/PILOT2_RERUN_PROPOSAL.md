# Pilot 2 re-run proposal (owner review — **not authorized to execute**)

> ## CURRENT (Revision D) — the only authoritative section
>
> **Revision A** (below, through first `STOP`) is **SUPERSEDED** — kept for history only. Revisions B/C are supporting history; **this block governs** any future live pilot 2 attempt.
>
> | Item | Value |
> |------|--------|
> | **Step 1 usage (+$0.000666)** | **AMBIGUOUS / ON HOLD** (owner) — **not** final **PROVIDER_REPORTING_LAG**; pending owner OpenRouter **Activity** dashboard check **14:30–15:15 UTC** |
> | **Obfuscated P4/P5** | **Standard** per Amendment **7b** (not KNOWN_RISK split) |
> | **Code tip** | `76cc234` |
> | **Templates SHA-256** | `33397e91138012e2e2f0f0d058f6d1cd0648e676e27b91d2f925809397784a44` |
> | **Criteria SHA-256** | `716c36024f1e6b33cec060800ae228ff4b32c6fa8f859b515647b2eccc4b8e85` |
> | **Scope** | **160 episodes** (4 models × 10 scenarios × 2 instances × 2 conditions) |
> | **HTTP cap** | **640** — hard-coded `HTTP_CAP` in `scripts/run_harness_v2_pilot.py` **L55** |
> | **USD cap (soft)** | Checked **after each HTTP** completes and is persisted; **at most one request** may push **billed** spend over the cap. Use **`--usd-cap 0.049`** so **billed** totals stay ≤ **$0.05** paper ceiling. |
> | **Process / lock / dir** | Single `run_harness_v2_pilot.py --live`; lock on; **new** out-dir; **`--resume` same dir only** |
> | **Ledger** | Report **`billed_*`** vs **`analysis_*`** (superseded partial rows excluded from analysis) |
> | **Authorization** | **Not authorized to execute** — await explicit owner **go** |
>
> **Live command (not run):**
>
> ```bash
> python3 scripts/run_harness_v2_pilot.py --live --usd-cap 0.049 \
>   --out-dir experiments/harness_v2/HARNESS_V2_PILOT_<UTC-ts>/
> ```
>
> **STOP after pilot completes** — no full eval without separate owner authorization.

**Prerequisites satisfied (owner additions 2026-09-27):**

- ~~Step 1: usage +$0.000666 classified **PROVIDER_REPORTING_LAG** (see `AMENDMENT6_PROOF.md` § Step 1).~~ **[SUPERSEDED: owner verdict AMBIGUOUS, see CURRENT]**
- Step 2: Amendment 6 mock proof PASS (`AMENDMENT6_DEMO_20260927-155900/`, `step2_resume_integrity.json`).
- Step 3: `obfuscated_instruction_v1` **KNOWN_RISK** + `PILOT2_OBFUSCATED_P4P5_LOCKED.md` committed before run. **[SUPERSEDED]**

## Execution plan (single flight)

| Parameter | Value |
|-----------|--------|
| **Processes** | Exactly **one** `python3 scripts/run_harness_v2_pilot.py --live` |
| **Lock** | `experiments/harness_v2/.pilot_live.lock` — must acquire before HTTP |
| **Out dir** | **New** `experiments/harness_v2/HARNESS_V2_PILOT_<UTC-ts>/` (never reuse aborted attempts) |
| **Scope** | 160 episodes (10×2×4×A0/B3), `max_rounds=4` |
| **HTTP cap** | 640 |
| **USD cap** | ~~$0.05 (enforced from `running_ledger.json` after each HTTP)~~ **[SUPERSEDED]** |
| **Resume** | **`--resume` only on the same `out-dir`** after crash/SIGKILL; never start a second out-dir concurrently |
| **Routing** | DeepInfra, `require_parameters`, no fallbacks, temp 0, reasoning off |
| **Criteria** | ~~`PILOT2_CRITERIA_LOCKED.md` + obfuscated P4/P5 split per `PILOT2_OBFUSCATED_P4P5_LOCKED.md`~~ **[SUPERSEDED]** |
| **Templates** | ~~Amendment 5 SHA `dd445b19af36b1784cd40964944e7ff60f2cb248f94408efc1fda8281a5fb43a`~~ **[SUPERSEDED]** |

## Pre-flight checklist

1. `pgrep -af 'python3 scripts/run_harness_v2_pilot'` → empty.
2. Remove stale lock only if PID dead (`PilotRunLock` stale semantics).
3. Record `/auth/key` `usage` + `limit_remaining` before first HTTP.
4. Append row to `experiments/judge_gold/RUN_REGISTRY.md` when dir created.

## Post-run

1. `scripts/analyze_harness_v2_pilot.py` on pack.
2. `PILOT2_FINAL_REPORT` addendum criteria table + obfuscated appendix.
3. `/auth/key` after finalize; compare pack `spent_usd` to ledger.

**STOP — await explicit owner “go” before any `--live` command.**

---

## Revision B (2026-09-27) — post Amendment 7b/7c (mock PASS)

**Code tip at proposal write:** `76cc234` (Amendment 7 owner mock bundle).

| Parameter | Value |
|-----------|--------|
| **Templates SHA-256** | `33397e91138012e2e2f0f0d058f6d1cd0648e676e27b91d2f925809397784a44` |
| **Scope** | 4 models × 10 scenarios × 2 instances × 2 conditions = **160 episodes** |
| **HTTP cap** | 160 × `max_rounds=4` = **640** completions |
| **USD cap (soft)** | Checked **after each HTTP** completes and is persisted; **at most one request** may push **billed** spend over the cap. Use **`--usd-cap 0.049`** so **billed** totals stay ≤ **$0.05** paper ceiling. |
| **Processes** | Exactly **one** `python3 scripts/run_harness_v2_pilot.py --live` |
| **Lock** | `experiments/harness_v2/.pilot_live.lock` — must acquire before HTTP |
| **Out dir** | **New** `experiments/harness_v2/HARNESS_V2_PILOT_<UTC-ts>/` only; never reuse aborted packs |
| **Resume** | **`--resume` on the same `--out-dir` only** (never concurrent out-dirs) |
| **Ledger** | Report **`billed_*`** (all rows, incl. `superseded_by_resume`) vs **`analysis_*`** (excludes superseded partial-attempt rows) |
| **Criteria doc** | `PILOT2_CRITERIA_LOCKED.md` SHA-256: `716c36024f1e6b33cec060800ae228ff4b32c6fa8f859b515647b2eccc4b8e85` |
| **Obfuscated P4/P5** | **Standard** per Amendment **7b** (not KNOWN_RISK split; `PILOT2_OBFUSCATED_P4P5_LOCKED.md` superseded) |

**Example command (not run):**

```bash
python3 scripts/run_harness_v2_pilot.py --live --usd-cap 0.049 \
  --out-dir experiments/harness_v2/HARNESS_V2_PILOT_<UTC-ts>/
```

**STOP after pilot completes** — no full eval without separate owner authorization.

---

## Revision C (2026-09-27) — proposal doc (no code change)

| Field | SHA / value |
|-------|-------------|
| **Code tip** | `76cc234` (Amendment 7 owner mock bundle; unchanged by this revision) |
| **Templates SHA-256** | `33397e91138012e2e2f0f0d058f6d1cd0648e676e27b91d2f925809397784a44` |
| **Criteria SHA-256** | `716c36024f1e6b33cec060800ae228ff4b32c6fa8f859b515647b2eccc4b8e85` |
| **Proposal commit** | `939e648` |

Live example command: Revision **B** block above (no `unset OPENROUTER_API_KEY`; real key required in environment for live OpenRouter).
