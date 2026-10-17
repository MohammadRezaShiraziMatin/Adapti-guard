
# Round 10 sync scan (2026-10-16)
Additional exclusions: papers/ (not updated in this commit), ext/ADR, ext/AutoDojo (see UPSTREAM_MANIFEST.md), human_packet/KEY_SEPARATE/* (blind key held separately; only human_packet/KEY_SEPARATE.sha256 kept), release_zenodo_round10.zip.
Included on purpose: attarg/validation/KEY_DO_NOT_OPEN/key.json and bitems/scorer_validation/KEY_DO_NOT_OPEN/key.json (AI-validation answer keys, comparison already done).
Accepted false positive: release_zenodo/round10/SECRET_SCAN.txt line 1 lists the scan patterns (no values).
Result: CLEAN.


## Erratum (2026-10-17)
- OLD: "Additional exclusions: papers/ (not updated in this commit)" (Round 10 section; also the 986387e commit message: "papers/ excluded").
- NEW: papers/ was **not** excluded from the commits: its 17 files were tracked and committed in 2eb0b80 and are present in 986387e; they were only left out of this scan. The folder was removed from the branch on 2026-10-17 (copyright); see docs/PAPERS_REFERENCES.md. The files remain in history at 2eb0b80/986387e.
- Evidence: `audit/VERIFY_ROUND10.md` (round-10 verification note; that file is not part of this branch).
