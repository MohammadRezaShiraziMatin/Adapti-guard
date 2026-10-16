# Flag resolutions (verify_numbers.py Part 2), 2026-10-16
Implemented as the ALLOW dict in review/verify_numbers.py.
- `12` (§ prereg hash para): clock time "12:2x Tehran" of the re-run, not a data value.
- `28` (§5.1 Finding, x2) / `28`,`27` (§5.1 "Across all 55"): suite counts from get_suites('v1') and gt_audit_agentdyn_v1.json: dailylife 10+shopping 9+github 9 = 28; workspace 6+travel 7+banking 9+slack 5 = 27. HARD-checked in Part 1 (28,20) and (27,0 defects; travel inj6 has empty ground_truth and a text-only goal).
- `40` (clustered para): shopping 20 + github 20 user tasks (get_suites v1); diag_results.json ntasks 60 (all) vs 20 (conf).
- `0.3787` (§6 spend line): cross-ref to judge pilot spend, judge_pilot/RESULTS.md line 2; the line's only [src] is v1, so the search looked in the wrong file.
