# Agent handoff — Q1 P1_rq1_primary_j1_j2 (2026-09-27)

**Audience:** next Cloud Agent / owner. **Default:** API=0 until explicit owner LIVE + authorization.

## P1 completion verdict

| Item | Status |
|------|--------|
| P1 confirmatory live (488 episodes) | **NOT COMPLETE** |
| Owner STOP (2026-09-25) | partial run killed |
| Episodes completed | **177 / 488** |
| Evidence pack | `experiments/real_llm_eval/Q1_P1_RQ1_ABORTED_20260925/` — **`NOT_RQ1_EVIDENCE`** |
| Authorization | **BLOCKED** (`live_budget_authorization.yaml`, `PHASE7_LIVE_AUTHORIZATION.json`) |

Do **not** analyze aborted episodes for RQ1, McNemar, or manuscript results.

## Code / branch (ready for re-run when authorized)

- **Branch:** `cursor/live-eval-canonical-runner-c775`
- **Head (infra):** `f7527bd` — panel-priced `BudgetLedger`, RR target interleave, A0/B3 back-to-back, stop at pair boundaries
- **Runner:** `scripts/run_q1_p1_live.py`, `src/adapti_guard/evaluation/q1_p1_live_runner.py`
- **Contract SHA:** `eebe84f3b13f69ca48d57f4f968e3945447766d538603ebea4b57002eb73d0c9`
- **J2 manifest SHA:** `1ccf9fe1c632909adc131c7d776749361d13bbcb3ec8e4c0806abfbd887863b0`
- **Dry P1 worst-case preflight:** ~**1.598 USD** (cap $2.00)

## Owner LIVE checklist (not done)

1. Commit authorization scoped to `P1_rq1_primary_j1_j2` only, cap **$2.00**, contract + manifest + `code_git_commit`.
2. Assert: validator, target≠judge, cache off, J2=manifest, B3 reset per episode.
3. Run `run_q1_p1_live.py` → new evidence pack (not ABORTED dir).
4. Post-run: authorization **BLOCKED** + commit artifacts.

## OpenRouter key (operator)

- Valid key in **`.env`**: mask `...2d11`, `limit=2`, `usage=0` when read from file.
- Cloud VM **shell Secret** may still shadow `.env` (`load_dotenv` without override); remove/update Cursor Secret + **new agent run** before live.
- **No new live run** unless owner re-authorizes.

## Tests (last known)

`tests/test_live_budget_gate.py`, `tests/test_q1_p1_ledger_order.py`, `tests/test_b2_budget_accounting.py` — panel pricing / schedule.
