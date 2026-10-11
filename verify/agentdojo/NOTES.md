# AgentDojo error concentration: reproduction notes (2026-10-11)

Scope: only the numbers below were re-derived from committed or public files. No model or API calls, no spend, no merge.

Pin: AgentDojo `089ed468cf3ed0322acc66b0211f26d9d90dbf60`; see `verify/agentdojo/PIN.md`.
Script: `scripts/agentdojo_error_count.py`. Per-episode extracts: `verify/agentdojo/episodes_*.csv`.

## Counting rules

- Published rule: `security = True` means the injection succeeded. An errored episode has `security = True`, so AgentDojo counts it as an attack success.
- Unresolved rule: an errored episode is `None`. It is removed from the numerator and the denominator.

## Reproduction of published numbers

| source | model | attack | published | reproduced, published rule | reproduced, unresolved rule |
|---|---|---|---|---|---|
| `verify/agentdojo/results-table.html:320` | Llama-3-70B | important_instructions | 25.60% | 161/629 = 25.60% (exact) | 126/594 = 21.21% |
| `verify/agentdojo/results-table.html:177` | GPT-4o-2024-05-13 | important_instructions | 47.69% | 300/629 = 47.69% (exact) | 300/629 = 47.69% (no errored episodes) |

Llama-3-70B has 35 errored episodes out of 629. Under the unresolved rule its rate is 21.21%, which is 4.39 points lower than the published 25.60%. The unresolved rule does not change GPT-4o.

This is a single-model finding. It does not establish that other published numbers change.

## Not in this document

Earlier drafts listed error counts for other models and a shortlist of related papers. Those figures relied on files outside this repository and were not reproduced, so they are removed.
