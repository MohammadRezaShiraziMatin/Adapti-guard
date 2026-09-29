# Owner additions — final report (2026-09-27 UTC)

**No live OpenRouter calls** in this work. Mock demo only on `127.0.0.1`.

---

## Step 1 — Usage +$0.000666 (`1.624137948` → `1.624804008`)

**Classification: PASS — `PROVIDER_REPORTING_LAG`** (not `NEW_REQUEST_AFTER_KILL`).

### Timestamp evidence (quoted)

| Event | UTC timestamp | Source |
|-------|---------------|--------|
| Foreground pilot 2 **last shell end** | **`2026-09-27T15:01:46.506Z`** | `ABORTED_PILOT2_ATTEMPTS_20260927/terminal_947558_foreground_pilot2.txt`: `ended_at: 2026-09-27T15:01:46.506Z` |
| Foreground pilot 2 start | `2026-09-27T14:45:58.942Z` | same file `started_at` |
| Concurrent tmux attempt start | `~2026-09-27T15:01:51Z` | `manifest.json` `pilot2_tmux_harness-v2-pilot2-run` |
| Agent STOP manifest + `/auth/key` **1.624137948** | **`2026-09-27T15:10:00Z`** | `manifest.json` `recorded_at_utc`, `openrouter_auth_key_at_stop.usage` |
| `PILOT2_STOP_REPORT.md` usage | **1.624137948** | same snapshot as manifest |
| Git commit addendum (first post-stop doc with higher usage) | **`2026-09-27 15:10:47 +0000`** | `git log` → `c999ac1` `docs(harness_v2): pilot 2 final report addendum` |
| `/auth/key` reads at **1.624804008** | **≥ 15:10:47 UTC** (addendum turn); stable through **`15:52–15:56`** | `AMENDMENT6_DEMO_20260927-155900/auth_key_snapshot_t0.json`, `auth_key_snapshot_t2min.json` |
| Mock Amendment 6 demo HTTP | **`2026-09-27T15:55:00.xxxZ`** | `http_stream_at_sigkill.jsonl` `recorded_at_utc` — **`127.0.0.1` only** |

### Accounting tie-in

- `usage` Δ = **0.000666060**
- `usage_daily` Δ (stop report **1.610788592** → snapshot **1.611454652**) = **0.000666060** (exact match)
- Implies OpenRouter **backfilled daily usage** for charges already incurred during **14:45–15:02** live window, not a new billed `/chat/completions` call after kill.

### Why not `NEW_REQUEST_AFTER_KILL`

- Last OpenRouter-capable runners stopped by **`15:10:00Z`** manifest (PIDs **47822**, **48642** killed earlier in STOP turn).
- Post-**15:10:00Z** agent activity on real API: **`GET /auth/key`** and **`/activity`** (403) only — **no** `chat/completions`.
- No `run_harness_v2_pilot.py` on OpenRouter after STOP (`process_check_owner_commands.txt`).

**Kill mechanism:** not incomplete for post-15:10 billing (no evidence of new live inference after kill).

Detail: `AMENDMENT6_PROOF.md` § Step 1 (updated).

---

## Step 2 — Mock-server proof

**Classification: PASS**

| Check | Result | Raw / artifact |
|-------|--------|----------------|
| SIGKILL at **N=7**; three counts equal | **7 = 7 = 7** | `wc -l` on `http_stream_at_sigkill.jsonl`, `mock_server_requests_at_sigkill.jsonl`; `running_ledger_at_sigkill.json` `"http_used": 7` |
| Ledger = sum stream costs | **0.00028** | `post_sigkill_report.json` |
| `--resume` no duplicate episode ids | **33 unique** | `step2_resume_integrity.json` `"episode_ids_unique": true` |
| First episode not re-started | **`episode_begin_first_episode_count": 1`** | same file |
| No duplicate mock tool call ids | **`duplicate_mock_tool_call_ids": []`** | same file |
| Concurrent second `--live` | **exit 2** | `AMENDMENT6_LOCK_DEMO_RAW.txt`: `pilot_run_lock_held: pid=53601 ...` |
| Stale lock dead PID | **does not block** | `acquired_pid 53610`, `lock_after_release_exists False` |

Demo pack: `AMENDMENT6_DEMO_20260927-155900/`. Proof bundle commit **`ab803fc48d3af264038ac3574f72ed392e9c44aa`**.

---

## Step 3 — `obfuscated_instruction_v1` KNOWN_RISK

**Classification: PASS** (documented; detector unchanged)

- Template payloads quoted in `DEVIATIONS_AMENDMENTS.md` § KNOWN_RISK.
- Pre-run lock: **`PILOT2_OBFUSCATED_P4P5_LOCKED.md`** (obfuscated P4/P5 reported separately; does not alone FAIL pilot).
- **Not Amendment 7** — channel/template tension is preregistered; not treated as a plain implementation bug in `marker in content`.

---

## Step 4 — Re-run proposal

**Classification: PASS** (document only)

- **`PILOT2_RERUN_PROPOSAL.md`** written; **not executed**.

---

## Commit SHAs (this additions bundle)

| Artifact | SHA |
|----------|-----|
| Owner additions + Step 1–4 docs | `196ae8bb7c5f2b0ba1d4d207cc9218d3a14cddbb` |
| Prior Amendment 6 proof bundle | `ab803fc48d3af264038ac3574f72ed392e9c44aa` |
| Pilot 2 addendum | `c999ac1dda0a125b028d78d88209e2971322a6d0` |
| Pilot 2 STOP + Amendment 6 code | `836085a12343c45da4654eab63ffb547a327b9cc` |

**STOP.** Awaiting owner **go** for live pilot 2.
