# Reference verification (2026-10-01)

Method: each cited paper was opened as PDF text through the alphaXiv PDF reader and each claim or number the manuscript attributes to it was looked up on the quoted page. "OK" = confirmed in the PDF. "Edited" = the manuscript wording was changed to match. Nothing was guessed; where a paper could not be found it is listed as not read.

| ref | what the manuscript says | result |
|---|---|---|
| 2406.13352 AgentDojo | stateful, deterministic state-based checks; three metrics; "important message" attack; tool filter lowest ASR (6.84%, text says 7.5%); BERT detector hurts utility (false positives) | OK (Table 5: delimiting 41.65, detector 7.95, repeat prompt 27.82, tool filter 6.84; detector utility 41.49 vs 69.0) |
| 2403.02691 InjecAgent | 1,054 cases = 17 user cases x 62 attacker cases; single-turn; success by tool execution | OK. **Edited:** the claim "type of retrieved content predicts success more than the attacker instruction" was imprecise; the paper reports that the user case (Cramér's V 0.28-0.31) is more strongly associated than the attacker case (0.18-0.20) and that high content freedom raises ASR |
| 2506.09956 LLMail-Inject | 208,095 unique submissions, 839 participants, success = tool call with right arguments, MIT license | OK. **Edited:** "human-written" softened to participant-submitted (one team used an LLM to generate variants); limitation added to section 8 |
| 2312.14197 BIPIA | five scenarios, 250 attacker goals, rules + LLM judge, KDD 2025 | OK |
| 2608.28411 LongPIBench | defenses that look strong on short inputs fail on long context | OK. Also used to qualify the SPOT_TOOL result (delimiters ASR 0.96 vs 0.98 undefended on its synthetic tasks) |
| 2503.18813 CaMeL | privileged/quarantined LLM, interpreter, capabilities, 77% tasks with provable security | OK |
| 2504.11703 Progent | symbolic least-privilege rules at the tool call, deterministic check, LLM-generated policy | OK (AgentDojo 39.9% -> 1.0%) |
| 2503.00061 Zhan et al. | eight defenses, adaptive attacks, ASR above 50% | OK |
| 2510.09023 Nasr et al. | twelve defenses, above 90% for most, spotlighting and sandwiching above 95% on AgentDojo, human red-teaming 100% | OK |
| 2606.15057 AutoDojo | static benchmarks overestimate defenses; black-box; system-level defenses mostly hold | OK. **Edited:** title in the reference list corrected ("AutoDojo: A Generative Benchmark for Evaluating Prompt Injection Defenses in LLM Agents"); the sentence now says one system-level defense (DRIFT) rises above its static rate |
| 2606.26479 Narisetty et al. | protocol for adaptive evaluation of out-of-band defenses | OK; LaunchSafe Research, "not peer-reviewed" per the paper |
| 2606.10525 Hofer et al. | judge recall 100%, precision 52.3% (Qwen3-4B) and 29.4% (GPT-5); TAP beats GCG; no transfer to GPT-5 | OK. **Edited:** model names added |
| 2605.30454 Sakib et al. (first author Syed Nazmus Sakib; Shifat E. Arman is the corresponding author; corrected 2026-10-08) | 13 models, four suites, 44.9% (35/78) pairs reorder, repeat-prompt and spotlighting leave tool-description surface exposed | OK; NeurIPS 2026 workshop paper |
| 2609.32691 Shaw | four defect classes; 21.7% vs 1.2% on identical traces; 62.8% -> 0% | OK; single independent author |
| 2605.26999 Akinrele and Gowda | detection is regime-dependent, sensitive to threshold / low-FPR operating point | OK |
| 2604.23887 Deep et al. | sandwich 0.4% at 25 rounds, 3.8% over 277 rounds; only output filtering held | OK. **Edited:** "output filtering (alone or inside a multi-layer stack)"; Swept AI vendor study |
| 2609.25173 Pathade et al. | six ASR axes A1-A6, 259 papers, 18.2 pp MDD at m=100 (analytical), ten-item checklist, no empirical ranking inversion, no artifact repository | OK; the paper itself says the checklist is proposed, not validated |
| 2603.15714 Dziemian et al. | 464 participants, ~272k attempts, 13 models, ASR 0.5%-8.5%, one-shot evaluation can be unreliable, 95 Qwen attacks released | OK. **Edited:** reworded "unreliable" to what the paper says (a replayed attack does not always succeed again) |
| 2609.36817 pikit | composable toolkit varying attack, channel, defense | OK. **Edited:** described as a composable toolkit, not only "a toolkit for such evaluation" |
| 2604.08499 PIArena | unified platform, adaptive strategy-based attack | OK |
| 2502.05174 MELON | masked re-execution and tool-call comparison | OK (ICML 2025) |
| 2412.16682 Task Shield | task-alignment check of instructions and tool calls | OK |
| 2403.14720 Hines et al. | spotlighting = delimiting, datamarking, encoding; delimiting alone not recommended | OK; identifier found; limitation sentence added to section 6.6 |
| Cui, Wu, Backes, Zhang, "Rethinking assessments of prompt injection attacks", ACL Findings 2026 | not cited for any claim | **Not read.** Title search did not find an arXiv or alphaXiv record. Bibliographic data comes only from the reference list of 2608.28411. Listed in the references with a `[NOT READ]` flag and a TODO for the owner. No content is attributed to it. |

Remaining open items (not resolvable from the PDFs): the registry URL for the pre-registration, a second human rater for the generated Hard-set items, and an independent reproduction.

## Added 2026-10-07 (abstract-level check only)

Six entries were added to the manuscript's reference list after the PDF check above: Jacobs and Wallach (1912.05511, FAccT 2021), Bean et al. (2511.04703), Miller (2411.00640), Zheng et al. (2306.05685), Greshake et al. (2302.12173) and Feinstein and Cicchetti (FC1990). Title, authors, year and abstract were checked on the arXiv, ACM or Elsevier page (record: change table of the revision, item 8). The per-claim comparison against the full text that the table above documents was not done for these six, and FC1990 was confirmed only from citing sources.
