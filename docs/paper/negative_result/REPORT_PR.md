# PR separation and OSF verification report (2026-10-11)

No model or API calls, no spend, no OSF registration, no merge. Nothing under `frozen/`, `datasets/attackset_hard_v1/`, or the panel config changed on either branch (see §4).

## 1. Branches and PRs

- **PR #130**, branch `case-study/agentdojo-errors`: AgentDojo error work only. OSF-related changes removed (commit 4eaa214).
- **PR #131**, branch `case-study/osf-preregistration-fix`: OSF corrections and the §6.5 / §8.8 PENDING-RUN change. The panel config change was reverted (§3).
- The brief names `phase3/confirmatory-protocol` as PR #131. That branch is the base of #131 and is not itself a PR; it was not modified.

## 2. Diff stats

Against `main` (as requested; `main` predates the phase3 stack, so these include the shared base):

```
git diff --stat main...case-study/agentdojo-errors       59 files, 16148 insertions(+), 635 deletions(-)
git diff --stat main...phase3/confirmatory-protocol      56 files, 16126 insertions(+), 635 deletions(-)
git diff --stat main...case-study/osf-preregistration-fix (PR #131 branch) — see §5
```

PR-only diffs against the shared base `phase3/confirmatory-protocol` (what each PR actually adds):

- #130: `docs/paper/negative_result/REPORT_AGENT.md` only, +22.
- #131: see the diff stat in §5.

## 3. Hash check

- File: `docs/protocols/CONFIRMATORY_PROTOCOL_DRAFT_v0.1.md`
- SHA-256: `3f935384dcd48aeaf69e96f9614a477d6ec91bbcf2f7f5604bcd75181bb09cb2`
- Matches the `3f935384…bb09cb2` prefix. Also matches `CONFIRMATORY_PROTOCOL_FROZEN.sha256` on the phase3 branch.

## 4. Reverted changes

- `configs/models_panel_external_v2.yaml`: reverted to the phase3 version (`frozen: false`). The brief forbids touching the panel config. This was part of the original OSF fix and is now not on #131. It is still needed later, so the owner should decide when to set `frozen: true`.
- PR #130: `PREREGISTRATION_OSF_FINAL.md`, the config, `MANUSCRIPT_DRAFT_v1.md`, `SECTIONS_5_6_EXPERIMENTS_RESULTS.md` and `SECTION8_LIMITATIONS.md` reverted to phase3 versions; `REPORT_AGENT.md` reduced to the AgentDojo sections.
- No `frozen/`, `datasets/attackset_hard_v1/` or panel-config path differs from the phase3 base on #130. On #131 only the panel config differed, and it is reverted.
- No protocol-section content was reported as UNSUPPORTED. The old draft's item 14 (disclosure) is removed in the final text, not added.

## 5. Mismatch verification table (PR #131)

Old = `PREREGISTRATION_OSF_DRAFT.md` on phase3. New = `PREREGISTRATION_OSF_FINAL.md` on #131. Protocol = `CONFIRMATORY_PROTOCOL_DRAFT_v0.1.md`. Protocol lines are from the earlier mapping table and were spot-checked at lines 19–21, 33–35, 43–47, 61–62, 112–115, 194–208.

| # | Item | Old (file:line) | New (file:line) | Protocol section (line) | Status |
|---|---|---|---|---|---|
| 1 | Title / study | draft:6 | final:1, :3 | title (1, 3) | matches |
| 2 | H1 | draft:7 | final:8 | H1 (19) | matches |
| 3 | H2 | draft:7 | final:9 | H2 (20) | matches |
| 4 | H3 | draft:7 | final:10 | H3 (21) | matches |
| 5 | Endpoint | draft:8 | final:34–35 | §4 (103–104) | matches |
| 6 | Conditions (NOINJ ≤3% rule removed) | draft:9 | final:17–19 | §2 (33–34) | matches |
| 7 | Panel | draft:10 | final:15–21 | §2 (33–39) | matches |
| 8 | Data / sample | draft:11 | final:23–24 | §3 (43, 45) | matches |
| 9 | Sample sizes | draft:12 | final:25–26 | §3 (61–62) | matches |
| 10 | Analysis | draft:13 | final:42–44 | §5 (112, 114, 115, 120) | matches |
| 11 | Floor rule | draft:14 | final:42, 47 | §5 (201, 222–223) | matches |
| 12 | Exclusions / errors | draft:15 | final:36–39 | §4 (106, 107, 130) | matches |
| 13 | Deviations | draft:16 | final:68 | §10 (220) | matches |
| 14 | Disclosure (vendor-family line) | draft:17 | removed | not in protocol | removed, not added |
| 15 | Attachment name | draft:3–4 | final:5 | protocol file name | matches |
| 16 | Omitted protocol content (added) | — | final:5, 24–31, 49–55, 57–62, 64–75 | §3 (43–73), §6 (194–198), run order (202–207), NOINJ subset (208), §10 (215–229) | matches |

Numeric and hash checks on the final text, all found in the protocol:

- Hashes: `3f935384…`, `f19c9f2c…` (release commit), `d8f25d18…` (retained set), `840cc16a…` (release map), `33e349f5…` (pilot).
- Budget: 0.02 / 0.2978 / 0.1822 USD; campaign cap 0.50 USD; 0.2803 USD estimate; HTTP caps 60 / 980 / 72; 1,052 total; 0.01 USD tolerance.
- Counts: 150 retained cases from 50 clusters; gpt set 72 cases from 24 clusters; NOINJ 40 cases; pilot 10 clusters / 30 cases; 69 generated items.
- Statistics: Holm thresholds 0.0167 / 0.025 / 0.05; 10,000 resamples; seed 20261001.
- Commit `d1538af`.

Finding: the final text is consistent with the protocol on every checked item. I did not verify the §8 interpretive bullets line by line; they are restatements of §10.

## 6. §6.5 and §8.8 check

- §6.5 and §8.8 in `MANUSCRIPT_DRAFT_v1.md`, `SECTIONS_5_6_EXPERIMENTS_RESULTS.md` and `SECTION8_LIMITATIONS.md` now read "PENDING-RUN, registry URL to be inserted by owner." No results and no claim of registration are present.
- §8.8 keeps the protocol's limitation bullets. These describe limits, not results.

## 7. Items for the owner (not blocking verification)

- Registry URL, registration date and `/auth/key` snapshot are placeholders.
- Three cells are MISSING from the repo (`P2-QWEN-A0-RETRY`, `P2-QWEN-NOINJ-RETRY`, `P2-GPT-A0-EXTRA20`). They are not invented.
- Merge conflict risk: the OSF edits on #130 were removed in 4eaa214, so the two PRs no longer overlap.
