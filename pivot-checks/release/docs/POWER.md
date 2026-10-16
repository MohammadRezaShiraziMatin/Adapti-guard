# Power check: TOST, ±3pp equivalence margin (2026-10-15, Tehran)
**Test:** per defense, paired difference Δ = ASR_judge − ASR_checker on the same attack episodes; equivalence if both one-sided tests reject at α=0.05 (90% CI within ±0.03). Paired: Var(d_i) = π_disc − Δ², where π_disc = P(judge ≠ checker). Normal approx; design effect from IP weights (Kish deff 1.06/1.19/1.13 → n_eff ≈ 189/169/178 for tool_filter/PG2/repeat, of n=200 attack each). Disagreement rate π_disc is **unknown** (no judge calls had been made when this was written); values below are assumptions.

| assumed π_disc | power, n_eff 155 / 180 / 200 (true Δ=0) | n_eff needed, 80% power, Δ=0 | n_eff needed, 80%, Δ=0.01 |
|---|---|---|---|
| 2% | 0.68 / 0.77 / 0.83 | 190 | 309 |
| 5% | 0.02 / 0.12 / 0.20 | 476 | 773 |
| 10% | ~0 | 952 | 1,546 |
| 20% | ~0 | 1,903 | 3,091 |

Formulae: n = (z₀.₉₅+z₀.₉₀)²·π_disc/M² (Δ=0); n = (z₀.₉₅+z₀.₈₀)²·π_disc/(M−|Δ|)² (Δ≠0). M=0.03.

**Verdict:** ±3pp equivalence is testable at this sample size **only if judge–checker disagreement is ≤ ~2%**. At ≥5% disagreement it is not testable; required n exceeds the 560-episode population per set when π_disc ≳ 6%, i.e. even a census could not establish superpopulation equivalence (a census gives the finite-population Δ exactly, with no sampling error). Recommendation: treat the pilot's ±3pp test as descriptive; size the main study from the observed π_disc (RESULTS.md).
Caveat: oversampling att_pos changes the disagreement mix; the deff approximation is rough (unverified against simulation).
