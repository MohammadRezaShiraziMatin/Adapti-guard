### 6.6 External case: AgentDojo error accounting

We re-derived the published AgentDojo `important_instructions` counts for one model, Llama-3-70B, from its per-episode records at the pinned commit (`verify/agentdojo/PIN.md`, `verify/agentdojo/NOTES.md`). Under the published rule, an errored episode has `security = True` and counts as an attack success. That rule reproduces 161/629 = 25.60%. Of the 629 episodes, 35 errored. If those 35 are left unresolved and removed from numerator and denominator, the rate is 126/594 = 21.21%.

GPT-4o-2024-05-13 has no errored episodes in the same extract, so its published rate is unchanged: 300/629 = 47.69%. We use it only as a control for the accounting rule.

This is an observation about one published table. We do not claim that other AgentDojo numbers change, and the difference is not a result about either model's robustness to injection. The unresolved rate is a re-accounting of the same episodes, not a new measurement.

This is also an instance of the outcome-labeling concern in M2 (§4.2): an errored episode is not an outcome, so how a published rule labels it is a labeling choice. M2's status in §4 is unchanged by this subsection.
