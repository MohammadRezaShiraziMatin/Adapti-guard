# Downstream exposure of AgentDyn reference-solution defects [EXPLORATORY]
Procedure locked first: PROCEDURE_EXPOSURE.md / .sha256. Sources: full-text arXiv HTML in papers/<id>.txt, fetched 2026-10-16.
Search: WebSearch and DDG "AgentDyn" (2026). Semantic Scholar citations: HTTP 429 (s2_cites.json). The arXiv API query hung and was killed.
This is an **incomplete** census (no citation index was available). It reports exposure only and makes no claim that any result is wrong.
Defective GT on AgentDyn (our audit): shopping 9/9, github 9/9, dailylife inj2 and inj6.

| Paper | AgentDyn suites | Attacks | tool_knowledge / ground_truth()-based use | Exposure | Refs |
|---|---|---|---|---|---|
| AgentDyn, Li et al. 2602.03117v3 | shopping, github, dailylife | important_instructions (default); ignore-previous, completion and manual adaptive attacks | None stated. Metrics are utility / utility under attack / ASR (security()). tool_knowledge is not mentioned. | NOT EXPOSED (reported metrics) | §4.1 Attacks; App. F Table 8; Table 3 |
| Agent-Sentry 2603.22868 | github, dailylife, shopping (Native-Trace Bench) | AgentDojo/AgentDyn injection tasks [attack template UNVERIFIED] | YES: "label each action by matching it against the injection task's ground-truth signature (the specific tool and argument values the attacker aimed for)", used to label training/eval traces | EXPOSED (labels on shopping/github derive from stub GT; on github the target tool does not exist) | §4.1.4 Trace labeling; §5.2.2; §6.6, §6.7.2 |
| AuthGraph 2605.26497 | "AgentDyn" (suites not itemised) | "diverse attack types" [not specified] | None found. Metrics ASR / UR / A.UR. | UNKNOWN (attacks not specified) | §4 setup (Benchmarks, Baselines); results table |
| ActGov 2609.24446 | AgentDyn test split (60 user / 28 injection tasks; 560 cases) | "multiple attack configurations" [not specified in text] | None found. Uses "the native benchmark scorer" | UNKNOWN (attacks not specified) | Experimental Setup; Table 2; Evaluation Integrity |
| AutoDojo 2606.15057 | github, shopping, dailylife | important_instructions (static) plus the AutoDojo adaptive optimizer | Code (aa458794): the optimizer prompt includes `$ground_truth_calls` from ground_truth() (variant_generation/suite_gen_utils.py L71, L93). AutoDojo rewrote the shopping GTs (code note 2026-06-14). github/dailylife GTs are unchanged. The paper text does not state this use. | EXPOSED (code-level; github and dailylife inj2/6). Whether the App. D runs used this prompt field is UNVERIFIED. | §4.1; App. D, Tables 3–4, Fig. 11 |

Excluded / not found: no other 2026 paper evaluating on AgentDyn was located with the tools available. Results from GitHub dependents and Google Scholar were not obtained.


## Erratum (2026-10-17)
- OLD (Agent-Sentry row, Exposure column): "EXPOSED (labels on shopping/github derive from stub GT; ...)".
- NEW: "PLAUSIBLY EXPOSED (inference; paper does not state use of ground_truth())". The paper labels traces against "the injection task's ground-truth signature"; that this signature is taken from AgentDyn's ground_truth() is our inference.
- Source note: `papers/<id>.txt` cited in line 2 was removed from the branch on 2026-10-17 (copyright); identifiers in docs/PAPERS_REFERENCES.md, texts in history at 2eb0b80/986387e.
- Evidence: `audit/VERIFY_ROUND10.md` (round-10 verification note; that file is not part of this branch).
