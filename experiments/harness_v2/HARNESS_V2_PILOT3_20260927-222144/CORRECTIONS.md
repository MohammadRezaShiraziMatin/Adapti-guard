# Pilot 3 pack metadata corrections (Amendment 9 §5)

**Approved by:** Matin, 2026-09-28  
**Scope:** post-run metadata only; raw HTTP/ledger/auth bodies unchanged.

| File | Old | New | Reason |
|------|-----|-----|--------|
| `.gitignore` | (no exception) | `!experiments/harness_v2/HARNESS_V2_PILOT*/progress.log` | Allow committed pilot `progress.log` while keeping `*.log` elsewhere |
| `PILOT3_OWNER_REPORT.md` P2 row | "12 calls" | "44 calls in 40/40 gemma episodes" | Truncated sample list was mistaken for total (Amendment 9 §5.1) |
| `PILOT3_OWNER_REPORT.md` postflight bullet | "saved at run end" | `postflight_at_utc` 2026-09-28T00:21:43Z; ~87 min after last HTTP | Auth snapshot timing vs last billed row (Amendment 9 §5.3) |
| `PILOT_REPORT.md` P1 notes | 3 of 17 length rows | all 17 llama length rows listed | Analyzer note truncation (Amendment 9 §5.2) |
| `PILOT_REPORT.md` per-model | incorrect bullet PASS/FAIL | table from raw pack totals | Wrong per-model rollup (Amendment 9 §5.2) |
| `run_manifest.json` | `pilot`: harness_v2_pilot_2; no SHAs | `pilot_3`, `pilot_number`: 3, runner/docs SHA | Runner label hardcode at launch (Amendment 9 §5.5) |
| `pilot_summary.json` | `pilot` / `pilot_number` 2 | `harness_v2_pilot_3` / 3 | Same as manifest (Amendment 9 §5.5) |
