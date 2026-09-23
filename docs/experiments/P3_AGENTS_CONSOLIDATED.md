# Phase 3 — consolidated agent audit (parallel runs)

**Purpose:** Single source of truth merging parallel cloud-agent readouts. **API=0.** **No live authorized.**

**Canonical next work:** Continue on **PR #74** branch only (`cursor/q1-roadmap-phase1-c4b6`); do not relaunch parallel P3 agents for status.

| Tip | SHA | Role |
| --- | --- | --- |
| **This branch (PR #74)** | `4f4f0ffc3b567d0631e83fdbf5a3dcf8817f58ce` | Design locks, P3-1 offline runner smoke, docs |
| **`main`** | `e4870b9cc03a344835f341bfd61aa83d2bdf2bff` | Workshop P1–P5 done; Q1 P3 bundle not merged until Matin |

---

## Merged P3 arm status

| Arm | ID | Authorization | Engineering / design | Live evidence |
| --- | --- | --- | --- | --- |
| External baseline | **P3-1** | **NOT AUTHORIZED TO RUN** | Design lock + candidates + `run_q1_p3_1_confirm.py` (`--preflight-only`, `--defense-smoke`); default **STATIC-A3** on `phase1_confirm_v1` (design only) | None |
| Mechanism live | **P3-5** | **NOT AUTHORIZED TO RUN** | [`DECISION_LOCK_Q1_P3_5_MECHANISM.md`](DECISION_LOCK_Q1_P3_5_MECHANISM.md); pack SHA `1a0b0053…`; `live_evaluated=false` | None |
| Multi-model robustness | **P3-3/4** | **NOT AUTHORIZED TO RUN** | Scaffold only; default Target/Judge qwen 7b ≠ 72b until human model-ID lock | None |
| Confirmatory V2 + larger n | **P3-2** | **NOT EXECUTED** (Q1-P2 Future Work) | D-22 names locked; no V2 pack bytes/SAP/live in this cycle | None |

**Historical confirmatory (not P3 optional arms):** Track A VNEXT **`FAIL`** immutable @ `VNEXT_CONFIRM/20260914-133147/` (qwen 7b target / 72b judge). Track B scoped **SUPPORTED_IMPROVEMENT** on separate pack. P3 arms **add** new AUDIT folders only; they do **not** amend Track A FAIL.

---

## What each source agent proved

### Agent A (`bc-2a83beab`) — P3 audit on `main` tip `e4870b9`

- Read-only Phase 3 scope audit; **no code changes**; **API=0**.
- Confirmed: P3-1 / P3-5 / P3-3/4 **NOT AUTHORIZED**; P3-2 **NOT EXECUTED**; VNEXT confirm remains historical **FAIL** baseline pair.
- No contradiction with science locks on `main`.

### Agent B (`bc-98b4440d`) — Environment + branch `4f4f0ff`

- `python3 scripts/run_q1_p3_1_confirm.py --preflight-only` → **PREFLIGHT_OK** (pack/detector/live-lock checks; no API).
- **`OPENROUTER_API_KEY` missing** → live path correctly blocked; `authorized_to_run_live=false`.
- **pytest 282 passed** (full suite on branch at audit time).
- **STATIC-A3** wired via `get_defense_fn` + P3-1 runner; `--defense-smoke` **DEFENSE_SMOKE_OK** (no network).
- **No live** execution performed.

---

## Matin-blocked (all arms)

| Gate | Status |
| --- | --- |
| USD budget cap | **TBD — Matin** |
| Signed pre-run / authorization sentence | **Required per arm lock** |
| `OPENROUTER_API_KEY` (live only) | **MISSING** at agent B audit — live must not start |
| PR #74 merge to `main` | **Human-only** |
| P3-3/4 alternate model matrix | **HUMAN LOCK REQUIRED** (no model-ID guesses in repo) |

Until all required gates pass: **`LIVE_EVALUATION_GATE = CLOSED`**, **`API=0`**.

---

## Priority order (unchanged)

1. P3-1 → 2. P3-5 → 3. P3-3/4 → 4. P3-2 — see [`Q1_P3_PRIORITY.md`](Q1_P3_PRIORITY.md).

---

## Validation snapshot (this consolidation)

Run on branch tip when updating this file:

```bash
python3 docs/paper/q1_findings/verify_q1_findings_facts.py
python3 scripts/run_q1_p3_1_confirm.py --defense-smoke
python3 -m pytest tests/test_q1_p3_1_baseline_smoke.py tests/test_q1_findings_facts.py -q
```

**Navigation:** [`DECISION_LOCK_Q1_P3_ARMS.md`](DECISION_LOCK_Q1_P3_ARMS.md) · [`STATUS.md`](STATUS.md)
