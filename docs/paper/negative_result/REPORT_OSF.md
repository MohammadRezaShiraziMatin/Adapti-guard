# OSF preregistration fix: freeze flag, OSF final text, PENDING-RUN, mismatch table (2026-10-11)

Branch: case-study/osf-preregistration-fix (from origin/phase3/confirmatory-protocol, 5f94372). Split from PR #130 so the OSF fix and the AgentDojo work review and merge separately. No model or API calls, no spend, no OSF registration, no merge.

## 1. Freeze result
- Protocol: docs/protocols/CONFIRMATORY_PROTOCOL_DRAFT_v0.1.md, SHA-256 3f935384dcd48aeaf69e96f9614a477d6ec91bbcf2f7f5604bcd75181bb09cb2. Matches docs/protocols/CONFIRMATORY_PROTOCOL_FROZEN.sha256.
- configs/models_panel_external_v2.yaml: `frozen: false` changed to `frozen: true`, with the protocol hash and date (2026-10-11) in the comment. No other line changed. YAML parses.
- Cells P2-QWEN-A0-RETRY, P2-QWEN-NOINJ-RETRY, P2-GPT-A0-EXTRA20: **MISSING.** They appear neither in the repo (git grep) nor in /home/claude/adaptiguard_private. Nothing was created. Their PENDING_APPROVAL status cannot be confirmed.

## 2. OSF mismatches (base PREREGISTRATION_OSF_DRAFT.md vs protocol)
| # | topic | OSF draft (line) | protocol (line) |
|---|---|---|---|
| 1 | study | title "external tests" (6) | confirmatory S-A protocol (1, 3) |
| 2 | H1 | B3/CORE equivalence null, 5 pp (7) | floor test: A0 below 5% per target (19) |
| 3 | H2 | delimiter effect model-specific, no pooled effect (7) | SPOT reduces executed calls, llama and qwen, n = 150, Holm over two (20) |
| 4 | H3 | susceptibility differs more than 3x (7) | A0 minus A0_REP noise floor (21) |
| 5 | endpoint | first tool call, proposal-level, state-based (8) | executed call primary (103); proposal secondary (104) |
| 6 | conditions | A0, NOINJ, SPOT, B3, CORE; NOINJ must be at most 3% (9) | A0, A0_REP, SPOT_TOOL, NOINJ (33-34); no B3/CORE; no 3% rule anywhere |
| 7 | panel | 4 open, 2 closed, 2 judges, "section 3" (10) | 3 models (33-35); deepseek and glm not in plan (39); panel is section 2 |
| 8 | data | InjecAgent 62x17; Hard set 238; AgentDojo pairs (11) | S-A 186 cases, 62x3 (43); Hard set not chosen (45); no AgentDojo |
| 9 | sample | Hard set test 170; closed about 60 (12) | n = 150 retained; gpt 72 (61-62) |
| 10 | analysis | 4000 resamples, seed 7; Holm over four open models (13) | exact binomial H1 (112); 10,000 resamples, seed 20261001; McNemar confirmatory, Holm over two H2 targets (114, 115); Holm over three H1 (120) |
| 11 | floor rule | A0 below 5% with n at least 40 "at the floor"; n below 40 undetermined (14) | H1 outcomes (222-223); degenerate bootstrap (201) |
| 12 | exclusions | no exclusions after freezing; smoke-test exclusion (15) | invalid if error above 5% (106); R-0 (107); transport errors count to 5% (130) |
| 13 | deviations | first deviation = panel replacement, closed target swap (16) | policy: date, reason, effect, author approval (220); no such deviation recorded |
| 14 | disclosure | closed target or judge in assistant's vendor family (17) | not in protocol |
| 15 | attachment | PROTOCOL_EXTERNAL_TEST_DRAFT_v1.md (3-4) | CONFIRMATORY_PROTOCOL_DRAFT_v0.1.md, 3f93... |
| 16 | omitted | — | freeze status (3); S-A sample and hashes (43-73); budget, caps and `/auth/key` (194-198); run order (202-207); NOINJ subset (208); partial independence (68); contamination (70); deviations and interpretation (215-229) |

Resolution: docs/paper/negative_result/PREREGISTRATION_OSF_FINAL.md, which uses only protocol content. The registry URL, date and `/auth/key` snapshot value are owner placeholders. The base draft is left unchanged.

## 3. Manuscript
§6.5 and §8.8 in the section sources now read "PENDING-RUN, registry URL to be inserted by owner." Headings name PENDING-RUN. §8.8 keeps the protocol-fixed limitation bullets, which are limits, not results. MANUSCRIPT_DRAFT_v1.md reassembled. Offline pytest: 769 passed.

