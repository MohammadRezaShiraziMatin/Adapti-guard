# Claim-to-evidence checklist and open items

## Claims
| # | Claim (manuscript §) | Evidence file |
|---|---|---|
| 1 | Primary F3: adaptive_dev − L1 = −0.0118, CI [−0.0258, +0.0024], inconclusive (§6.2) | `results/f3_confirmatory/RESULTS.md`; `docs/F3_CONFIRMATORY_CONTRACT.md` |
| 2 | adaptive_exp worse than L1 (+0.0663, [+0.0550, +0.0771]) (§6.2, §6.4) | `results/f3_confirmatory/RESULTS.md` |
| 3 | Arm means (loss, ASR, utility, cost) (Table 1) | `results/f3_confirmatory/RESULTS.md` |
| 4 | Burst-only CI excludes 0 but is secondary/uncorrected (Table 2) | `results/f3_confirmatory/RESULTS.md` |
| 5 | Frozen design: model, seeds 1000–1019, pool v3 54 attacks / 32 benign, equivalence ±0.02, bootstrap 5000 (§5) | `docs/F3_CONFIRMATORY_CONTRACT.md`; `results/f3_confirmatory/pool_v3.json` (not re-counted here) |
| 6 | 200 runs, 0 API errors, spend $0.507 (§5.6, §10) | `docs/F3_CONFIRMATORY_CONTRACT.md`; `results/f3_confirmatory/cost_v3.json` |
| 7 | Regex recall 0.94 (design pool) vs 0.21–0.26 (fresh); guard 0.75, 0/20 benign (§6.1) | `results/q1_f3_real_llm_v2/FINDINGS.md`; `results/q1_f3_real_llm_v2_sem/FINDINGS.md` |
| 8 | Pool v3 layered recall 0.82, benign flagged 0.028 (§6.1, §7) | `results/f3_confirmatory/RESULTS.md` |
| 9 | Offline dev replay table (§6.3) | `docs/F3_CONFIRMATORY_CONTRACT.md` |
| 10 | Live v2 / guard-check qualitative statements (§6.3) | `results/q1_f3_real_llm_v2/FINDINGS.md`, `…_v2_sem/FINDINGS.md` |
| 11 | Controller behaviour and limits (§3) | `docs/ADAPTIVE_CONTROLLER_SPEC.md`; `docs/DEFENSE_LEVELS.md` |
| 12 | Headroom explanation is a hypothesis (§7) | `docs/ADAPTIVE_CONTROLLER_CASE_STUDY.md` finding 3 (not tested directly) |
| 13 | Review scores 34→52→70 (§6.5, App. C) | project `audit/` files (not in repo); numbers from project notes and PR #93 |

## Open TODOs
- Author block, venue, anonymization (title page).
- Release policy confirmation (§9).
- Verify stream definitions and pool counts (`pool_v3.json`) by a second reader; manuscript quotes the contract.
- Attach or summarise `audit/` reviews (Appendix C); confirm the 34/52/70 scores against the reports.
- Optionally render and visually check the two SVG figures; convert to the venue's format.
- Confirm that the "mostly cost" decomposition (§6.2) matches per-seed data if a reviewer asks.

## [CITATION NEEDED] items
- Perez & Ribeiro 2022; Greshake et al. 2023; Debenedetti et al. 2024 (AgentDojo); Liu et al. 2024: named from memory, verify details.
- Spotlighting / delimiting defences; StruQ; SecAlign.
- Prompt-injection detector/guard classifiers.
- Defence in depth / adaptive risk-based escalation for LLM agents.
- Pre-registration in ML; negative-result reporting; held-out evaluation of defences tuned on known attacks.
