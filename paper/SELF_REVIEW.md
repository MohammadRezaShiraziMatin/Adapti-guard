# Self-review: what a Q1 reviewer would still criticise

- **Abstract/Intro:** a negative result on one cheap model; reviewers will ask why it is publishable. Answer rests on the reliability contribution and the pre-specified protocol; the novelty is modest.
- **Related work:** placeholders; no real positioning against existing adaptive guards yet.
- **System (§3):** nominal action costs are not measured; level semantics collapse (L0≈L1 for MEDIUM; L1=L2 content), so only three distinct behaviours are compared.
- **Method (§5):** the freeze is only evidenced by commit hashes; selection of fixed L1 and adaptive_dev on the same family of data as the contract; equivalence margin ±0.02 is unmotivated and the design could not reach it (CI width ≈ 0.028).
- **Results (§6):** primary CI is wide; secondary rows could be over-read; one model; utility metric noisy (0.63 flat). The ablation bundles several parameters.
- **Discussion (§7):** headroom is untested; no run with a leaky fixed level.
- **Limitations (§8):** long list; reviewers will say the evidence base is too thin for any positive or strong negative claim.
- **Ethics (§9):** release policy undecided.
- **Reproducibility (§10):** live steps need a paid key and give non-deterministic outputs; five known environmental test failures.
- **Overall:** guard cost excluded from the loss, no adaptive attacker, and synthetic text-only prompts.
