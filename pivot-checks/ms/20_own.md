
## 6 Own-harness evidence (E1–E5) [OWN-HARNESS EVIDENCE]

*These results come from our own testbed. They are shortened from [v1 §5–§6]; all numbers are unchanged from v1, and v1 cites the trace files and scripts for each. They are not external validation. Labels follow v1: none of E2–E4 was preregistered, and E5 followed a locally drafted, not externally registered, protocol [v1 §5.5, §6.6].*

**E1: frozen judge-scored tracks, re-scored by the tool layer's execution record [v1 §5.2, §6.1].** Two hash-locked packs of 61 attack and 61 benign episodes; one target (qwen/qwen-2.5-7b-instruct); an LLM judge (qwen/qwen-2.5-72b-instruct). The judge and the executed outcome agree only weakly (κ 0.18, 0.36 and 0.16 in the three informative arms). Every disagreement has the judge saying success while the call did not execute. On Track B the frozen "supported improvement" has a judge-scored paired effect of δ̂ = 0.4426 (27/0, p = 1.49e-8, utility 59/61 = 0.967). With executed calls the effect is 0.9016 (55/0), and utility for tool-required tasks is 49/61 = 0.80, below the 0.95 floor. The frozen classification therefore rests on two judge errors that offset each other.

**E2: exploratory four-arm run on the original scenarios [v1 §5.3, §6.2].** Multi-turn mock-tool harness, three open targets, 468 episodes, 72 attack episodes per arm. A static tool policy (TOOLDENY) has 65/72 attack episodes with a matching proposed call but 0/72 executed (M1). PHASE1-CORE executed 36/72 when blocks count as failed attacks, but 36/36 when blocks are dropped as "not delivered" (M2). Restricted to the one valid attack scenario it executed 0/36: the second scenario requests the effect in the trusted user turn and is excluded under M3. Benign utility under TOOLDENY is 15/45, against 45/45 for the other arms. The episode-inclusion rule was adopted post hoc [DEVIATION; v1 §4.2].

**E3: independently authored attack families [v1 §5.4, §6.3].** Seven families, frozen before any run; 168 undefended episodes (56 instances × 3 models). Susceptibility is model-specific: deepseek 41/56, qwen3 8/56, gemma 8/56 (M5). Paired with the undefended baseline:
- B3: 56 vs 57 executed of 167 pairs, b10/b01 = 3/4.
- PHASE1-CORE: 57 vs 57 of 168 pairs, b10/b01 = 4/4. PHASE1-CORE removed the payload from 0 of 168 instances, although it had blocked 36/36 on the original pack (M4).
- Noise floor: 8 of 168 paired outcomes differ at temperature 0 even with identical model input.

Authorship independence is only partial and is disclosed (the author had read the detector's pattern lists earlier in the same session).

**E4: held-out application and channel re-run [v1 §5.4b, §6.5].**
- Applied unchanged to an earlier run (MT1 r1), the rules exposed M6: a delimiter defense wrapped the user prompt and left the untrusted context unmarked. Indirect injections went from 21 to 21 of 36.
- A follow-up run ($0.0669, 180 episodes) that marks the context instead lowered indirect injections from 8 to 1 of 18 (7 wins, 0 losses). Direct injections were unchanged (22 to 22 of 30).
- With a verifiable canary token, judge and deterministic emission agree well (κ 0.81 to 0.91).

**E5: external InjecAgent test, proposal-level endpoint [v1 §5.6, §6.6–§6.7].** The protocol was drafted locally and not externally registered. On the fixed 186-case sample, delimiters on the tool channel (SPOT_TOOL) lowered attacker-tool first calls:
- llama-4-maverick: 23/186 → 5/186, difference −0.097 [−0.145, −0.048];
- qwen3.8-flash: 23/186 → 4/186, difference −0.102 [−0.156, −0.054];
- undefended replicates differed by 0.005 and −0.005 (noise floor).

Three of five 2026 targets were at the floor in calibration, so a defense effect there would have been unmeasurable. The endpoint is tool identity at proposal level, so E5 does not test M1.

Live spend for E2–E4 is reported in [v1 §5, §8.5] (E2 and E3 about $0.23; E4 follow-up $0.0669). It is separate from the $0.3787 for the re-analysis (§8).

