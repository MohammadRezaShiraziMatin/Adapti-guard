# E1 and B3/E3 manuscript corrections (PROPOSED, not signed off)

- `VERIFICATION.md`, `MANUSCRIPT_CORRECTIONS_DRAFT.md`, `e1_recount.py`: the audit as written against commit e5949bc,
  added unchanged. `manuscript.patch` (against e5949bc) does not apply to the current manuscript and is not included.
- `e1_recount.py` is offline (no API). Run it from the repository root: `python docs/research/corrections/e1_recount.py`.
  At da7621b it reproduces: 488 predictions with 0 parseable calls; Track B CORE A2 55 / A0 6; 10 of 40 tool-required
  benign tasks denied and judged useful; judge utility 59 (49/61 after re-labelling); B0 model named the tool in 28/61
  (33 never named, exact match); 43/61 user_prompt (B); 41/61 direct (A); Track A 40/61 attacks with kind/to.
- E3 checks re-run at da7621b (inline, offline): CORE b3_log 412 checks, all A0 (168 user, 244 tool); B3 413, all A1
  (168 user, 245 tool); 0 blocked; in 158 comparable episodes the first tool message is identical for both arms, the CORE
  user message is identical and the B3 user message equals A0's with the final period removed (158/158).
- The current manuscript no longer uses E1 as evidence (?8.5 "Excluded evidence"), so the E1 edits of the draft have
  no target text. A short correction note was added to ?8.5 instead. The E3 edits were re-applied, with adaptations, to ?6.2,
  ?8.2, ?9 and Appendix D. See the PR description for the mapping.
- Track A provenance (resolved, PROPOSED): 241 of 244 predictions were produced at `7ee4581` (2026-09-14 13:31:54 to 14:10 UTC). The 3 episodes that failed with API errors (`vnext_c1_atk_031`, `vnext_c1_ben_046` in B0; `vnext_c1_atk_045` in VNEXT-ADAPT) were re-run with the same IDs at `dc6dbd37`, its direct child. That commit changes only the runner's resume logic and adds judge retries. `manifest.json` and `AUDIT.md` record the SHA of the last pass (`dc6dbd37`), and each prediction row records the SHA at the time it was written. Tool loop, defense, scoring and prompts are identical at both commits, and all Track A counts are unchanged with or without the 3 repaired rows. See `OPEN_QUESTIONS.md` Q1.
