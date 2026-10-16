# Leave-one-defense-out (LODO) sensitivity — [EXPLORATORY, not preregistered]

Written 2026-10-16 (Tehran) BEFORE running; hash-locked in docs/SENSITIVITY_LODO.sha256. Separate from the frozen ranking-flip preregistration (docs/DESIGN_VARIANCE_STUDY.PREREG_2026-10-15_2240.md), which is not modified.

**Purpose.** Check how much the EXEC→ATTEMPTED flip result depends on any single defense.

**Data sets (analysed separately).**
1. Confirmatory subset: as review/run.py `conf` (AgentDyn shopping and github excluded).
2. Full data: as rankflip/analyze.py (post-hoc target map included).

**Procedure.** For each defense d in the union of defenses present in the (≥3-defense) cells, excluding `none`: remove all episodes of d, then run the unchanged rankflip/analyze.py logic:
- cell eligibility: (benchmark, model, attack) with ≥3 defenses incl. no-defense (preregistered rule, line "Primary");
- bootstrap: resample episodes within each (cell, defense), 2000 reps, seed 20261015 (preregistered settings; no Holm, no task-level resampling — those are not in the ranking-flip prereg);
- significant flip: pair whose 95% CIs of ASR difference exclude 0 with opposite sign (EXEC vs ATT; EXEC vs CA reported separately, CA not used for any claim).

**Outputs per (data set, dropped defense):** eligible cells; cells with ≥1 ATT flip; ATT flips; pairs tested; whether ≥25% of eligible cells have ≥1 flip; same counts for CA. The without-progent row is highlighted. Baseline (nothing dropped) included for reference.

**Files.** lodo/lodo.py, lodo/lodo_results.json. No API/LLM/network calls.
