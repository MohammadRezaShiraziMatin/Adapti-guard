# Proposed manuscript corrections (draft, not applied)

Target: `docs/paper/negative_result/MANUSCRIPT_DRAFT_v1.md` at repo HEAD `e5949bc`. Unified diff: `manuscript.patch` (checked with `git apply --check` on a scratch clone; not applied to any repo). Full corrected file: `MANUSCRIPT_DRAFT_v1.corrected.md`. Evidence IDs refer to `VERIFICATION.md`.

## Errata / Correction statement (proposed text)

> **Correction.** A previous version of this manuscript said that re-scoring the frozen E1 confirmatory tracks with the tool layer's execution record moved the paired effect from 0.44 to 0.90 and benign utility from 0.97 to 0.80, and presented these as executed-call outcomes of the agent. That was wrong. In E1 the target model never emitted a parseable tool call (0 of 488 predictions). When there was no such call, the harness executed the call scripted in the dataset unless the defense denied it (`tool_loop.py:96`), and appended a `[TOOL_RESULT]` line that the LLM judge then read. The "executed" record is therefore the defense's deny log. 0.90 is PHASE1-CORE's deny rate on attack items (55/61), and 0.80 (49/61) reflects 10 of 40 tool-required benign tasks wrongly denied. Most E1 attack items (43/61 and 41/61) put the instruction in the user turn, which our threat model (§3.1) does not count as an attack. We also clarify that, in the E3 negative result, one defense never triggered (412/412 checks with no action) and the other's only change to model input was removing the trailing period of the user message; the injected tool content was byte-identical in all 158 comparable episodes. E3 is therefore reported as a no-op result and as an identical-input repeat study (8 of 168 pairs differ at temperature 0), not as evidence about detector-style defenses. No raw data or other numbers changed.

## Changes (OLD -> NEW -> evidence)

### 1. Abstract ¶2 (E1)

**OLD:**

> Re-scoring the same episodes by the tool layer's execution record moves the 0.44 paired effect to 0.90 while benign utility falls from 0.97 to 0.80; the judge agrees with the executed outcome only weakly (κ 0.16 to 0.36).

**NEW:**

> In those runs the model never emitted a parseable tool call; the harness executed the dataset's scripted call unless the defense denied it, so the tool layer's "executed" record measures the defense's allow/deny decision, not agent behaviour. Against that decision log the judge agrees only weakly (κ 0.16 to 0.36): on one track it scored 28 of 55 denied attack calls as successful and all 10 denied benign tool tasks as useful.

**Evidence:** E1 #1,#2 (VERIFICATION.md)

### 2. Abstract ¶2 (E3)

**OLD:**

> On seven partially independent attack families, neither detector-style defense changes executed attacks beyond run-to-run noise (56 undefended vs 57 defended, and 57 vs 57, of 167 and 168 pairs).

**NEW:**

> On seven partially independent attack families, neither of two detector-style defenses changed executed attacks (56 undefended vs 57 defended, and 57 vs 57, of 167 and 168 pairs), but neither acted on the injected content: one never triggered (no action on 412 of 412 checks), and the other's only change to model input was removing the user message's final period, leaving the tool output identical. Because the model input was effectively unchanged, these runs serve as a repeat study: 8 of 168 pairs differed at temperature 0.

**Evidence:** E3 #11-14

### 3. New: Correction notice after Keywords

**OLD:**

> **Keywords:** prompt injection; LLM agents; evaluation validity; tool calling; reproducibility; negative results.

**NEW:**

> **Keywords:** prompt injection; LLM agents; evaluation validity; tool calling; reproducibility; negative results.

**Correction notice (this revision).** An earlier draft said that re-scoring the frozen E1 tracks by the tool layer's execution record moves the paired effect from 0.44 to 0.90 and benign utility from 0.97 to 0.80, and presented these as executed-call outcomes of the agent. That was wrong. When the model output contains no parseable tool call, the E1 harness falls back to the attacker call scripted in the dataset (`src/adapti_guard/defense/tool_loop.py`, line 96) and executes it unless the defense chooses A2 or A3. None of the 488 E1 predictions contains a parseable call. The "executed" record is therefore the defense's deny log: 0.90 is PHASE1-CORE's deny rate on attack items (55/61), and the utility drop comes from denying 10 of 40 tool-required benign tasks. The harness also appends `[TOOL_RESULT] <observation>` to the model response before the judge reads it. Most E1 attack items (43/61 in Track B, 41/61 in Track A) place the instruction in the user turn, which §3.1 does not count as an attack. Separately, the E3 negative result involves defenses that did not act on the untrusted channel (§6.3). §3.2, §5.2, §6.1, §6.3, §9 and Table 1 are corrected. No raw data changed.

**Evidence:** Correction notice: E1 #1-3,#7,#9; E3 #11-13

### 4. §1 Findings

**OLD:**

> **Findings.** The judge-scored favorable result understates the tool-layer effect (0.44 vs 0.90) and overstates benign utility (0.97 vs 0.80).

**NEW:**

> **Findings.** The judge-scored favorable result in E1 does not match the harness's own defense-decision log: the judge scored 28 of 55 denied attack calls as successful and 10 of 10 denied benign tool tasks as useful. The "executed" record in E1 comes from the harness, not the model, so it is not an agent outcome (§6.1).

**Evidence:** E1 #3,#4,#7

### 5. Table 1 rows 1-2

**OLD:**

> | success endpoint (M1) | judge-scored paired effect 0.4426 | executed-call effect 0.9016 | §6.1 |
| benign utility behind the gate (M1) | judge 0.97 | executed 0.80 (49/61) | §6.1 |

**NEW:**

> | judge vs defense-decision log (E1; not an agent endpoint) | judge-scored paired effect 0.4426 | defense deny rate on attack items 55/61 (0.9016); the scripted call was executed whenever it was not denied | §6.1 |
| benign utility behind the gate (E1) | judge 0.97 (59/61) | 10/40 tool-required benign tasks denied by the defense, all judged useful; 49/61 = 0.80 if those 10 count as failures | §6.1 |

**Evidence:** E1 #3,#4 (0.80=49/61)

### 6. Table 1 last row

**OLD:**

> | do the frozen judge-scored tracks measure executed harm? No | κ 0.16 to 0.36 | the Track B classification depends on two offsetting judge errors | §6.1 |

**NEW:**

> | do the frozen judge-scored tracks measure executed harm? No, and E1 has no model-driven executed endpoint | κ 0.16 to 0.36 against the defense-decision log | the model emitted no parseable call in 0/488 predictions; the harness executed the scripted call; most attack items are direct (user-turn) injections | §6.1 |

**Evidence:** E1 #2,#9

### 7. §1 Contribution 2

**OLD:**

> 2. A quantified judge–executor disagreement on two frozen confirmatory runs, including a case where a headline improvement rests on two offsetting judge errors (§6.1).

**NEW:**

> 2. A quantified disagreement between the judge and the harness's defense-decision log on two frozen confirmatory runs, including a case where a headline improvement rests on judge errors in both directions (§6.1). The E1 "executed" record is scripted by the harness and is not an agent outcome.

**Evidence:** E1 #1-3

### 8. §3.2 Testbed, frozen tracks

**OLD:**

> run once in a single-turn text interface with simulated tools; the tool layer records for each episode whether the requested call was permitted and executed.

**NEW:**

> run once in a single-turn text interface with simulated tools. The target received no tool schema (prompt and system prompt only). If the model output contained no parseable tool call (a structured call or `TOOL_REQUEST: {...}` text), the harness used the attacker or benign call scripted in the dataset (`record.tool_call`, `src/adapti_guard/defense/tool_loop.py:96`) and executed it unless the defense action was A2 or A3. This happened in all 488 E1 predictions. The tool layer's "executed" flag is therefore the defense's allow/deny decision, not a model-driven outcome. The harness then appended `[TOOL_RESULT] <observation>` to the model response, and the judge read that text (`src/adapti_guard/evaluation/attack_success.py:331-346`).

**Evidence:** E1 #1,#2,#7

### 9. §5.2

**OLD:**

> The stored predictions also contain the tool layer's own record per episode (tool, `executed`, observation). We re-score the same episodes with that record (attacker-specified call executed, key argument present in the observation) and compare it with the judge (`scripts/rescore_tracks_ab_deterministic.py`). This is a sensitivity analysis; it does not replace the frozen verdicts.

**NEW:**

> The stored predictions also contain the tool layer's own record per episode (tool, `executed`, observation). Because no prediction contains a model-emitted call, the recorded call is always the dataset's scripted call (§3.2), and `executed` equals "not denied by the defense". We compare the judge with this defense-decision log (`scripts/rescore_tracks_ab_deterministic.py`). This is a judge-consistency check, not an executed-call endpoint, and it does not replace the frozen verdicts. In Track A the re-scoring rule looks for a `kind` or `to` argument, so the 21 attacks on `retrieve_document`/`search` cannot score as success; the undefended 40/61 equals the number of attacks with such an argument. Threat-model validity: 43 of 61 Track B attack items (`threat_surface = user_prompt`) and 41 of 61 Track A items (`direct`) carry the instruction in the user turn, which §3.1 does not treat as an attack.

**Evidence:** E1 #1,#2,#8,#9

### 10. §6.1 heading + preamble

**OLD:**

> ### 6.1 E1: the judge and the tool layer disagree, on attack success and on benign utility
| track / arm | judge-scored success | executed (tool layer) |

**NEW:**

> ### 6.1 E1: the judge disagrees with the defense-decision log, on attack success and on benign utility
The "executed" column is the harness's record that the scripted call was not denied (§3.2). It is not a model-driven executed call. In B0 it is 61/61 by construction, even though in 33 of 61 Track B B0 episodes the model's text never contains the attacker tool's name (31 case-insensitive).
| track / arm | judge-scored success | not denied (scripted call executed) |

**Evidence:** E1 #5,#6 (exact-match count 33)

### 11. §6.1 Track B

**OLD:**

> With executed calls: 55/0, δ̂ = 0.9016. PHASE1-CORE denied the attacker call in 55 of 61 attack episodes;

**NEW:**

> Against the decision log: 55/0, δ̂ = 0.9016, which is PHASE1-CORE's deny rate on the attack items (action A2 in 55/61, A0 in 6/61), not an executed-harm effect. PHASE1-CORE denied the attacker call in 55 of 61 attack episodes;

**Evidence:** E1 #3

### 12. §6.1 closing sentence

**OLD:**

> The frozen classification therefore rests on two judge-versus-tool-layer mismatches that offset each other: it understated harm reduction (0.44 vs 0.90) and overstated benign utility (0.967 vs 0.80).

**NEW:**

> The frozen classification therefore rests on judge verdicts that disagree with the defense-decision log in both directions. The judge counted 28 denied attack calls as successful and 10 denied benign tasks as useful. The 0.90 and 0.80 figures are detector statistics (deny rate on attack items, and the utility cost of a 10/40 false-deny rate on tool-required benign tasks). They are not agent outcomes and should not be read as the defense's effect on executed harm. The judge also read harness-appended `[TOOL_RESULT]` text in every attack episode.

**Evidence:** E1 #3,#4,#7

### 13. §6.3 paired paragraph (E3 negative result)

**OLD:**

> Neither defense produced a block in any of the 336 episodes and per-family intervals include zero.

**NEW:**

> Neither defense produced a block in any of the 336 episodes and per-family intervals include zero. Neither defense acted on the untrusted channel. PHASE1-CORE returned A0 (no action) on all 412 checks (168 user, 244 tool). B3 returned A1 on all 413 checks (168 user, 245 tool), but its only observable change to model input was removing the trailing period of the user message. In all 158 episodes where both arms called the carrier tool, the injected tool message was byte-identical to the undefended arm. This result therefore shows that these two defenses, as wired, did nothing to the injected content. It is not evidence about detector-style defenses in general.

**Evidence:** E3 #11,#12,#13

### 14. §6.3 Nondeterminism floor (repeat study)

**OLD:**

> *Nondeterminism floor.* PHASE1-CORE with zero blocks presents essentially the same model input as the baseline, yet 8 of 168 paired outcomes differ at temperature 0 (B3: 7 of 167); differences of that order cannot be attributed to a defense.

**NEW:**

> *Nondeterminism floor (repeat study).* Since PHASE1-CORE took no action, its arm received the same input as the baseline (system, user and carrier tool messages identical in 158/158 comparable episodes). E3 is therefore in effect a repeat of the undefended run. 8 of 168 pairs still differ at temperature 0 (4 each way). B3 changed only one character of the user turn, and 7 of its 167 pairs differ (3/4). About 5% of paired outcomes can flip between identical-input runs, so differences of that order cannot be attributed to a defense.

**Evidence:** E3 #12,#14

### 15. §9 row 1

**OLD:**

> | On the frozen Phase-1 pack, judge-scored harmful-action success fell from 1.00 to 0.56; with the tool layer's record it is 6/61 against 61/61, and judge-scored utility 0.967 becomes 0.80 | that the defense (or adaptive intervention in general) is effective |

**NEW:**

> | On the frozen Phase-1 pack, judge-scored harmful-action success fell from 1.00 to 0.56, and the judge disagreed with the defense's own deny log (28 of 55 denied attack calls scored as success; 10 of 10 denied benign tool tasks scored useful) | that the defense (or adaptive intervention in general) is effective; that E1 measures executed calls produced by the model; any 0.90 executed-harm effect or 0.80 executed utility as an agent outcome |

**Evidence:** E1 #3,#4

### 16. §9 row 3

**OLD:**

> | On seven partially independent families neither detector-style defense changed executed attacks beyond run-to-run noise (paired differences +0.006 and 0.000, intervals include zero) | a general statement about detectors, models or adaptive attackers |

**NEW:**

> | On seven partially independent families, two defenses that never acted on the injected tool content (one never triggered; the other only removed a trailing period from the user turn) left executed attacks unchanged (paired differences +0.006 and 0.000, intervals include zero); identical-input pairs differed in 8 of 168 cases at temperature 0 | a general statement about detectors, models or adaptive attackers; that a defense acting on the tool channel would fail |

**Evidence:** E3 #11-14

## Rewritten E3 negative result (consolidated, for §6.3 / §7)

> **Defenses that effectively did nothing.** On seven partially independent families, executed attacks were 56 vs 57 (B3, 167 pairs, b10/b01 3/4) and 57 vs 57 (PHASE1-CORE, 168 pairs, 4/4). Neither defense acted on the injected content. PHASE1-CORE returned "no action" on all 412 checks. B3 returned A1 on all 413 checks, but A1's only observable effect was removing the user message's final period, and the carrier tool message was byte-identical to the undefended arm in 158/158 comparable episodes. The null therefore says that defenses that did not touch the untrusted channel did not change outcomes. It says nothing about detector-style defenses in general, and it is itself an instance of the defense-fidelity failure (M6).
>
> **Repeat study.** Because the defended arms received (essentially) the same input as the baseline, E3 doubles as a temperature-0 repeat study: 8 of 168 PHASE1-CORE pairs (4 each way) and 7 of 167 B3 pairs had different outcomes. About 5% of paired outcomes flip between identical-input runs, so per-arm differences of that size cannot be attributed to a defense. (Identical input holds at the first request; later turns depend on the model's own outputs, and 11-12 of 158 episodes diverge in later tool calls in either arm.)

## Legacy-claim register (`docs/baseline/LEGACY_CLAIMS.md`): proposed status updates (not in the patch)

- **L5** (Track B δ̂ = 0.4426, p ≈ 1.5e-8): numbers reproduce. Add: "the judge-to-executor check showed that E1's 'executor' is the harness-scripted call (tool_loop.py:96); 43/61 items are user-turn instructions. Do not cite as a defense effect."
- **L6** (CORE 36/72 vs 36/36): **not re-derived in this verification**. The independent review reports that it reproduces. It stays legacy until re-derived.
- **L7** (0 of 336 paired episodes blocked): **VERIFIED** (0 blocked entries in all 825 E3 defense checks). Add: "CORE took no action at all; B3 changed only the user turn's trailing period."
- **L8** (CORE harm 34/61 vs 6/61): numbers **VERIFIED** against the JSON artifact. Relabel "6/61" as "6/61 not denied by the defense (scripted call)", not "executor harm".

## Flagged: not verified or partly verified (keep out of the text, or reword)

- "32 B0 episodes where the model never named the tool": I get 33 (exact name) or 31 (case-insensitive). The patch uses "33 of 61 (31 case-insensitive)".
- "0.80 = 10/40": 0.80 is 49/61. The 10/40 false-deny rate is the driver. The patch states both.
- Temperature 0 for E3 is taken from the manuscript; the run manifests do not record it.
- Not checked here: L6, E2 numbers, InjecAgent, MT1, calibration, spend.

## Optional title (suggestion only)

*Same Traces, Different Verdicts: Re-scoring Released Prompt-Injection Defense Evaluations Under Explicit Estimands*. This fits only if the paper is re-scoped to path B (offline re-scoring of public traces, e.g. AgentDojo). It is not applied in the patch.
