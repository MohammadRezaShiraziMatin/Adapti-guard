# Agent report: AgentDojo error concentration (2026-10-11)

Branch: case-study/agentdojo-errors (from origin/phase3/confirmatory-protocol, 5f94372). OSF-related changes were moved to case-study/osf-preregistration-fix (PR #131). No model or API calls, no spend, no merge.
## 4. Error concentration (AgentDojo, pinned clone, no spend)
Errored = top-level `error` present; all errored attack episodes have security = True.
| model | attack episodes | errored | share |
|---|---|---|---|
| Llama-3-70b | 629 | 35 | 5.56% |
| command-r-plus | 629 | 22 | 3.50% |
| gemini-1.5-pro-001 | 629 | 19 | 3.02% |
| gpt-3.5-turbo-0125 | 629 | 12 | 1.91% |
| command-r | 629 | 3 | 0.48% |
Zero errored: 23 of 28 model directories, including gpt-4o (6,775 episodes), claude-3-opus, claude-3-5-sonnet, Meta-SecAlign-70B. Total 91 of 33,119 (0.27%). Full table: verify/error_concentration.md (outside repo).

## 5. Shortlist (at most 3; see verify/shortlist.md)
1. AgentDojo, arXiv 2406.13352: its runs include the high-error models above. Models in the paper itself UNVERIFIED.
2. SecOPD, arXiv 2608.21500: different context-length settings, which is the mechanism behind the 47 context-length episodes. Models UNVERIFIED.
3. Indirect Prompt Injections: Are Firewalls All You Need, arXiv 2510.05244: flags AgentDojo flaws. Models UNVERIFIED.
Only item 1 passes the model-overlap criterion. The others are included for mechanism.

## 6. Open items
- Shortlisted papers need full-text checks before any claim.
