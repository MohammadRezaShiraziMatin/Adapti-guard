# Amendment 8 — code checklist (implementation vs `AMENDMENT8_PROPOSAL.md`)

**Amendment document status:** **PROPOSED** (lock only on Matin’s explicit order).  
**Branch tip (this checklist):** **`364e6ed`** on `cursor/q1-p1-diagnosis-1282` (pilot 3 **docs/tests** tip; runner **`src/` + `scripts/`** unchanged vs **`e69802b`**).  
**Runner code SHA (pilot):** **`e69802b`** (V1 USD cap + V2 smoke wiring; no further runner edits through **`364e6ed`**).  
**Pilot 3 / live full run:** **not prepared, not run.**

Legend: **DONE** = merged code + named mock test; **NOT DONE** = doc-only, owner gate, or out of scope.

---

## Non-bisectable commits (do not `git bisect` alone)

These commits **fail** `pytest` in isolation; later commits add required fields/tests (`retry_blocked_by_http_cap` lands in **`9313c8e`**, not in **`7edba84`** / **`2f86a8f`** / **`5dfa004`**):

| Commit | Topic |
|--------|--------|
| **`7edba84`** | T1 cancelled_timeout (needs store flag from T3) |
| **`2f86a8f`** | T2 incomplete matrix (same async/store stack) |
| **`5dfa004`** | T4 asyncio smokes (needs `family` from **U1** `3b365aa`) |
| **`7561024`..`dea6c18`** | V1 USD-cap rows + renamed 7c test expectation mismatch (**1 failed** / 80 passed on `test_harness_v2_*.py` until **`be1d59d`**) |

**Smoke scripts broken range:** commits **`5dfa004..4e68fc5`** (inclusive) call `run_tools_episode_async` **without** required `family=` until **U1** `3b365aa`; bisect green smoke stack at **`3b365aa`** or later.

Bisect to **`364e6ed`** (green **`test_harness_v2_*.py`**, 82 passed) or minimum **`be1d59d`** (81 passed; V1–V5 docs/tests only through **`dea6c18`**; 7c test **rename** at **`9d54137`**, not `be1d59d`).

---

## Owner coding-phase lock (`f1f1384`)

| Section | Commit SHA | Test(s) | Status |
|---------|------------|---------|--------|
| Single event loop (`run_harness_event_loop`) | `c6dd461` | `test_harness_v2_amendment8_event_loop.py` | **DONE** |

---

## Amendment 8 item checklist (proposal § end)

| # | Topic | Commit SHA | Test(s) | Status |
|---|--------|------------|---------|--------|
| **C** | Full run plan Option C (`usd_cap=$0.80` soft, checked after each billed HTTP; primary K=24; runner **`4f3e981`**) | — | — | **NOT DONE** (planning doc only; not pilot 3 160-ep run) |
| **1** | `delayed_second_turn_v1` §1.5 config + §1.2 Pass A i0/i1 | `d549338` | `test_harness_v2_amendment8_delayed_inject.py` | **DONE** (code + mock i0/i1; §1.3 four-model mock battery **NOT DONE**) |
| **2** | 429 retry + SDK `max_retries=0` | `19e4d77`, `2941692`, `2cf717d`, `64dbe07` | `test_harness_v2_amendment8_provider_error.py`, `test_harness_v2_amendment8_http_budget_per_attempt.py`, `test_harness_v2_amendment8_429_billing.py`, `test_harness_v2_amendment7c.py` | **DONE** (mock) |
| **3** | NoneType / 504 error body | `19e4d77` | `test_harness_v2_amendment8_provider_error.py` | **DONE** |
| **4** | llama `max_tokens` 512→1024 | `6c4fc27` | `test_harness_v2_amendment8_llama_max_tokens.py` | **DONE** (+ `AMENDMENT8_LLAMA1024_RECOMPUTE_NOTE.md`) |
| **5** | gemma P2 intrinsic 2-token residue | — | — | **NOT DONE** (proposal §5 only) |

---

## §2 HTTP 429 / ledger / caps

| Section | Commit SHA | Test(s) | Status |
|---------|------------|---------|--------|
| §2.0–2.1 SDK pin `openai==3.19.2` | `64dbe07` | (requirements pin) | **DONE** |
| §2.2 harness retry backoff / INVALID | `19e4d77`, pilot status in `19e4d77` | `test_harness_v2_amendment8_provider_error.py` | **DONE** |
| §2.3 ledger `retried_after_rate_limit` / analysis totals | `2cf717d`, store in `19e4d77` | `test_harness_v2_amendment8_429_billing.py` | **DONE** |
| §2.4 USD/HTTP cap planning | `92cdab3` | `test_harness_v2_amendment8_cancelled_timeout.py::test_placeholder_pushes_usd_cap_via_pilot_async` | **DONE** (mock cap) |
| §2.5.2 AsyncOpenAI per attempt + `wait_for` | `35c4ed4`, `f855702` | `test_harness_v2_amendment8_per_attempt_client.py`, `test_harness_v2_amendment8_cancelled_timeout.py` | **DONE** |
| §2.5.3 episode wall X | `a5ea7d5` | `test_harness_v2_amendment8_episode_wall.py` | **DONE** |
| HTTP `acquire` per attempt | `2941692` | `test_harness_v2_amendment8_http_budget_per_attempt.py` | **DONE** |
| HTTP cap overshoot = 0 (mid-429 blocked) | `0b59c4a`, **`9313c8e`**, **`6ba29c3` (U2)** | `test_harness_v2_amendment8_http_cap_mid_429.py`, `test_harness_v2_amendment8_http_cap_tool_round_cut.py` | **DONE** |
| HTTP cap stop remaining **`INVALID`** | **`4e68fc5`**, **`6ba29c3` (U2)** | `test_harness_v2_amendment8_http_cap_remaining_invalid.py` | **DONE** |
| USD cap mid-episode cut **`INVALID`** + remainder **`NOT_RUN`** | **`7561024` (V1)** | `test_harness_v2_amendment8_usd_cap_mid_episode.py` | **DONE** |

---

## §3 Error-before-choices

| Section | Commit SHA | Test(s) | Status |
|---------|------------|---------|--------|
| Guard + ledger row | `19e4d77` | `test_harness_v2_amendment8_provider_error.py` | **DONE** |
| §3.1 incomplete matrix (504/empty/JSON/503) | `ff51a8b`, **`758cf4c` (T2)** | `test_harness_v2_amendment8_incomplete_response_matrix.py` | **DONE** |

---

## §4 llama max_tokens

| Section | Commit SHA | Test(s) | Status |
|---------|------------|---------|--------|
| §4.3 `LLAMA_HARNESS_MAX_TOKENS=1024` | `6c4fc27` | `test_harness_v2_amendment8_llama_max_tokens.py` | **DONE** |
| §4.4 cost table in proposal | — | `AMENDMENT8_LLAMA1024_RECOMPUTE_NOTE.md` | **NOT DONE** to edit locked table; recomputed note only |

---

## §5 gemma P2

| Section | Commit SHA | Test(s) | Status |
|---------|------------|---------|--------|
| Threshold / residue policy | — | — | **NOT DONE** |

---

## Wired pilot / persistence (blockers A–D, items 1–5)

| Item | Commit SHA | Test(s) | Status |
|------|------------|---------|--------|
| A — async pilot path | `8217ff2` | `test_harness_v2_amendment8_wired_integration.py` | **DONE** |
| B — reconcile attempt keys | `954e3c9` | `test_harness_v2_amendment8_reconcile.py` | **DONE** |
| C — USD cap via pilot | `92cdab3` | `test_harness_v2_amendment8_cancelled_timeout.py` | **DONE** |
| D — openai pin | `64dbe07` | — | **DONE** |
| Item 2 cancelled_timeout ledger | `f855702` | `test_harness_v2_amendment8_cancelled_timeout.py` | **DONE** |
| Item 3 manifest / timeout | `c08fae7` | `test_harness_v2_amendment8_python_manifest.py` | **DONE** |
| Item 5 post-run reconcile | `5ac3948` | `test_harness_v2_amendment8_reconcile.py` | **DONE** |
| E–I (review @ `64dbe07`) | `19e4d77` … `2cf717d` | see E–I tests in `tests/test_harness_v2_*.py` | **DONE** |
| I — legacy wrapper guard | `7d179a4` | `test_harness_v2_amendment8_legacy_wrapper.py` | **DONE** (superseded by **P** — `NotImplementedError`) |
| J — delayed inject | `d549338` | `test_harness_v2_amendment8_delayed_inject.py` | **DONE** |
| K — llama 1024 | `6c4fc27` | `test_harness_v2_amendment8_llama_max_tokens.py` | **DONE** |
| M — incomplete response matrix | `ff51a8b`, **`758cf4c`** | `test_harness_v2_amendment8_incomplete_response_matrix.py` | **DONE** |
| N — HTTP cap mid-429 | `0b59c4a`, **`9313c8e`**, **`6ba29c3` (U2)** | `test_harness_v2_amendment8_http_cap_mid_429.py` | **DONE** |
| O — 429 billing assumption verbatim | `06dafc7` | (grep `ASSUMPTION_429_UNBILLED_VERBATIM`) | **DONE** |
| P — asyncio smokes + no blocking helper | **`5dfa004`**, **`3b365aa` (U1)**, **`e69802b` (V2)** | `test_harness_v2_smoke_scripts_family_kw.py` (real `run_smoke*` / amendment7b `run_episode`) | **DONE** |
| Q — client lifecycle coding note | `4b84691`, **`758cf4c`** | (AMENDMENT8 §2.5.2 note; SHAs **8217ff2** / **19e4d77**) | **DONE** |
| R — combined mock integration | `b073139`, **`538fdb1` (T1)** | `test_harness_v2_amendment8_combined_integration.py` | **DONE** |
| S — PILOT3 proposal (160-ep scope) | **`93bb541` (U3)** | (doc only) | **DONE** |
| K note — llama recompute | `6c4fc27`, **`62d2fd8` (U4)** | `AMENDMENT8_LLAMA1024_RECOMPUTE_NOTE.md` | **DONE** |

---

## Full regression (item L)

| Scope | Command | Result |
|-------|---------|--------|
| All `tests/test_harness_v2_*.py` | `python3 -m pytest tests/test_harness_v2_*.py -q` | **82 passed** @ **`364e6ed`** |

---

## Registry & criteria (unchanged by design)

| Artifact | Status |
|----------|--------|
| `PILOT2_CRITERIA_LOCKED.md` | **not edited** |
| Historical run packs / `models.yaml` / B3 historical | **not touched** |
