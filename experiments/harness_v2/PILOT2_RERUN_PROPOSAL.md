# Pilot 2 re-run proposal (owner review — **not authorized to execute**)

**Prerequisites satisfied (owner additions 2026-09-27):**

- Step 1: usage +$0.000666 classified **PROVIDER_REPORTING_LAG** (see `AMENDMENT6_PROOF.md` § Step 1).
- Step 2: Amendment 6 mock proof PASS (`AMENDMENT6_DEMO_20260927-155900/`, `step2_resume_integrity.json`).
- Step 3: `obfuscated_instruction_v1` **KNOWN_RISK** + `PILOT2_OBFUSCATED_P4P5_LOCKED.md` committed before run.

## Execution plan (single flight)

| Parameter | Value |
|-----------|--------|
| **Processes** | Exactly **one** `python3 scripts/run_harness_v2_pilot.py --live` |
| **Lock** | `experiments/harness_v2/.pilot_live.lock` — must acquire before HTTP |
| **Out dir** | **New** `experiments/harness_v2/HARNESS_V2_PILOT_<UTC-ts>/` (never reuse aborted attempts) |
| **Scope** | 160 episodes (10×2×4×A0/B3), `max_rounds=4` |
| **HTTP cap** | 640 |
| **USD cap** | $0.05 (enforced from `running_ledger.json` after each HTTP) |
| **Resume** | **`--resume` only on the same `out-dir`** after crash/SIGKILL; never start a second out-dir concurrently |
| **Routing** | DeepInfra, `require_parameters`, no fallbacks, temp 0, reasoning off |
| **Criteria** | `PILOT2_CRITERIA_LOCKED.md` + obfuscated P4/P5 split per `PILOT2_OBFUSCATED_P4P5_LOCKED.md` |
| **Templates** | Amendment 5 SHA `dd445b19af36b1784cd40964944e7ff60f2cb248f94408efc1fda8281a5fb43a` |

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

**Code tip at proposal write:** see repo `git rev-parse HEAD` after Amendment 7 owner bundle (not executed live).

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
unset OPENROUTER_API_KEY  # live run only — real key required
python3 scripts/run_harness_v2_pilot.py --live --usd-cap 0.049 \
  --out-dir experiments/harness_v2/HARNESS_V2_PILOT_<UTC-ts>/
```

**STOP after pilot completes** — no full eval without separate owner authorization.
