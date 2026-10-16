# Preregistration hash recovery (2026-10-16)

**Result.** Recovered. The frozen Ranking-flip pre-registration text matches `review/PREREG_RANKFLIP.sha256`.

**Frozen hash (recorded 2026-10-15 22:40 Tehran):**
`97bdb074ae8911cab5ffbad1ed700b6895efff67c3080432c672c660361e63c1`

**Current working file hash** (`docs/DESIGN_VARIANCE_STUDY.md`, modified 2026-10-15 23:01):
`dc596e83f62cb25719d8a78bcd868f0c71063840f3e07659eb8fe97fd421148c`

**What changed after freeze.** Only the section `### DEVIATIONS — ranking-flip (2026-10-15 23:01, Tehran)` was appended (plus a blank line before it). No edit was found inside the Ranking-flip pre-registration bullets themselves.

**Recovered artifact.** `docs/DESIGN_VARIANCE_STUDY.PREREG_2026-10-15_2240.md`  
Recompute: `sha256sum docs/DESIGN_VARIANCE_STUDY.PREREG_2026-10-15_2240.md` must equal the frozen hash above.

**How recovered.** Truncate current `DESIGN_VARIANCE_STUDY.md` immediately before `### DEVIATIONS — ranking-flip`, rstrip trailing whitespace, end with a single newline. Hash matches exactly.

**Manuscript note.** Open issue 1 in `docs/MANUSCRIPT_M1_M3_EXTERNAL_VALIDATION_DRAFT.md` is resolved by this artifact. Rule text cited in the draft (25% cell threshold, EXECUTED/ATTEMPTED/CA definitions) is present unchanged in the recovered file.
