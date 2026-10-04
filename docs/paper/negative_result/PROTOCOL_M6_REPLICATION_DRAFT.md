# M6 replication protocol (DRAFT v0.1, separate from E6; not frozen, not approved, not run)

**Status.** Draft, 2026-10-04. M6 (is the defense applied to the untrusted channel?) was removed from the E6 confirmatory protocol. E6 does not test M6, cannot validate it, and nothing in E6 may be cited as M6 evidence. This file is a design sketch for a separate, later study; it has no approval record, no registration and no run. Current M6 evidence is one post hoc discovery on MT1 r1 and one targeted re-run of 18 indirect episodes (judge-scored 8 to 1; canary-scored 8 to 2; 7 wins, 0 losses; exact p = 0.016), preliminary and unreplicated.

## Why this needs new data, not a re-run
The frozen pack `layer_a_v2` holds 80 authored items, of which 40 are attacks and only **16 are indirect context injections**; MT1 used 6 per model per arm. There is no generator, so "a fresh pack with a new seed" does not exist. Repeating the same 16 items at temperature 0 measures nondeterminism, not replication. A replication therefore needs a **new, independently authored indirect-injection pack** (canary-token success condition, frozen and hashed before any run).

## Hypotheses (to be classified at approval)
- **M6-H1 (primary, confirmatory):** marking the untrusted context (SPOT_ctx) changes the canary-emission probability on indirect injections relative to the undefended arm, per model, two-sided.
- **M6-H2 (secondary):** the prompt-wrapped arm (SPOT_prompt) does not change indirect emission, while it does change direct emission (negative and positive contrasts); any interaction test is exploratory.
- **Validity gate (not a test):** an injection-free control with neutral context.
- **Descriptive:** undefended replicate discordance (8 of 57 episodes, about 0.07 per direction, in the earlier run).

## Design sketch and sample size
Arms per item and model: undefended, undefended replicate, SPOT_ctx, SPOT_prompt, randomized and interleaved as in E6 (block = item × model, seed from frozen hashes). Endpoint: canary-token emission (deterministic); judge scoring secondary. Unit: the item if items are independently authored; if the author writes items from shared templates, the analysis moves to the family level exactly as in E6. Primary test per model: exact McNemar on item pairs at alpha = 0.05 / 3 = 0.0167 (three models, Bonferroni).

Planning numbers (exact McNemar, per-direction noise 0.07, independent items; an upper bound if items cluster): 20-point reduction needs 90 pairs for 80% power and 112 for 90% at alpha 0.0167; 30-point reduction needs 52 and 63. Minimum proposed: **112 indirect items per model**. About 1,344 episodes for three models at 4 arms (the earlier re-run cost $0.0669 for 180 episodes, about $0.00037 per episode, so about $0.50), plus the control. A power calculation here is a design property, not evidence about M6.

## Required before it can be approved
An independent pack author (not Claude; blind to MT1 outcomes and the detector); pack schema and hash; owner decisions on models, budget and registration venue; an approval record with the same fields as E6 §10.
