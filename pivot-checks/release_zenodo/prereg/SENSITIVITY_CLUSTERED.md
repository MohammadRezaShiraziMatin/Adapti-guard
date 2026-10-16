# Cluster (user-task) paired bootstrap with Holm — [EXPLORATORY, not preregistered]

Written 2026-10-16 (Tehran) BEFORE running; hash-locked in docs/SENSITIVITY_CLUSTERED.sha256. The preregistered ranking-flip rule (episode bootstrap, 2000 reps, no correction) remains the confirmatory analysis; this file does not modify it.

**Data.** Same episodes, cells and definitions as the confirmatory analysis: rankflip/episodes.jsonl, drop `score_err` and null `executed`; cells = (benchmark, model, attack) with ≥3 defenses incl. no-defense. Primary: confirmatory subset (AgentDyn shopping/github excluded). Secondary: full data (post-hoc target map). Error episodes kept (prereg primary convention).

**Cluster.** User task = (suite, user_task id). Within a cell, the cluster set is the union of user tasks across its defenses.

**Paired bootstrap.** 10,000 reps, numpy default_rng(20261015), one stream, cells processed in sorted order. In each rep and cell, draw user tasks with replacement (multinomial counts over the cell's tasks); the SAME draw is applied to every defense and to all definitions (EXEC, ATT, CA). Defense ASR in a rep = Σ count_t·successes_t / Σ count_t·episodes_t over that defense's tasks.

**Test.** For each defense pair (i,j) and definition k, Δ_k = ASR_i − ASR_j. Two-sided bootstrap p_k = min(1, 2·min(P*(Δ_k ≤ 0), P*(Δ_k ≥ 0))). Holm–Bonferroni within cell over the cell's C(n_def,2) pairs, applied separately to the EXEC family and to the ATT (or CA) family at α=0.05.

**Significant flip.** A pair where the EXEC and ATT (resp. CA) differences are both Holm-significant and the observed point estimates have opposite signs.

**Report.** Per data set: cells, cells with ≥1 ATT flip, ATT flips, pairs tested, ≥25% yes/no; CA separately (limitations only). If flips vanish, say so plainly.

**Files.** clustered/clustered.py, clustered/clustered_results.json. No API/LLM/network calls.
