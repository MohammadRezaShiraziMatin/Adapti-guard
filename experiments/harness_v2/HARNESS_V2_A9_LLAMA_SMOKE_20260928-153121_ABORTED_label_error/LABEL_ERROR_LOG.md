# Aborted smoke launch attempt 1 (label error) — 2026-09-28T15:31:21Z

- Command: `scripts/run_harness_v2_pilot.py --live --pilot-label harness_v2_amendment9_llama_smoke_20260928-153121 --amendment9-llama-smoke --usd-cap 0.01` at `4fe1cb7454d1117fbead388017813d672eaba1db`.
- Runner exited rc=1 after 0.2s: `ValueError: pilot_label must start with 'harness_v2_pilot_'` (`pilot_number_from_label`), before the runner's own `/auth/key` preflight.
- **0 model (chat/completions) requests.** Only external calls: snapshot B (15:31:20Z) and postflight (15:31:21Z) `GET /auth/key`, both HTTP 200, usage 0.
- Relaunched with label `harness_v2_pilot_20260928153204` → pack `HARNESS_V2_A9_LLAMA_SMOKE_20260928-153204/`.
