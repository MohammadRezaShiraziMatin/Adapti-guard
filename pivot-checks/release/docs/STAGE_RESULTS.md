# Item 3 — Stage-aware EXECUTED vs ATTEMPTED gap (2026-10-16, Tehran). **EXPLORATORY.**
Code `stage/stage_gap.py` → `stage/stage_gap_results.json`. Data: `rankflip/episodes.jsonl` (EXEC = stored `security`; ATT = rankflip scorer), important_instructions, error episodes dropped, `none` excluded. Gap per defense set = ATT ASR − EXEC ASR.
Exploratory because: ATT for shopping/github uses the post-hoc target map (rankflip Dev.1; required by item 2's defects); the stage map below was written after seeing rankflip flips (which involved progent/drift); no pre-registration.

## Stage map (from code in dyn/src/agentdojo/agent_pipeline/agent_pipeline.py and defense READMEs)
- **input** (acts on prompt/tool-output text before the LLM reasons): spotlighting_with_delimiting, repeat_user_prompt, transformers_pi_detector, piguard_detector, prompt_guard_2_detector (detectors scan tool outputs).
- **planning** (constrains what the LLM can propose): tool_filter (`OpenAILLMToolFilter` prunes the tool list before the LLM, L592–604); camel (planner/interpreter; also has capability enforcement → arguably mixed; only gpt-4o-mini, 320 ep).
- **execution-time** (vets a proposed call): progent (policy check; logged as `ValidationError: The tool ... is not allowed`), drift (`DRIFTToolsExecutionLoop` with dynamic_validation=True; also builds constraints and isolates injections → mixed, classified by its main blocking point).

## Test
Statistic: mean over (benchmark, model) cells of the stage-mean gap; contrasts between stages. p = within-model stratified permutation of stage labels across defenses (5,000 perms, seed 20261016); CI = episode bootstrap within set (1,000). 9 cells (8 AgentDyn models + AgentDojo gpt-4o-2024-05-13).
| analysis | input | planning | execution | exec−input [95% CI], p | exec−planning, p | planning−input, p |
|---|---|---|---|---|---|---|
| all suites | 0.081 | 0.040 | 0.154 | +0.073 [0.065, 0.081], p=0.0006 | +0.114 [0.104, 0.123], p=0.0002 | −0.041 [−0.048, −0.034], p=0.089 |
| sensitivity: AgentDyn dailylife only, excluding gt-defective inj 2/6 (8 cells) | 0.099 | 0.012 | 0.206 | +0.107 [0.090, 0.123], p=0.0008 | +0.195, p=0.0006 | −0.088, p=0.060 |
Per-set gaps in the JSON.

## Reading / limits
Execution-time defenses show a larger ATT−EXEC gap (≈+7 to +11 pp vs input), as expected mechanically: they let the agent propose the call and then block it. This largely restates rankflip's "flips are definitional" negative, now quantified by stage. Stage is confounded with defense identity (2 execution defenses, 1–2 planning); bootstrap CIs ignore between-defense variance and are too narrow — the permutation p is the honest test, and with ≤10 defenses per cell its resolution is limited. Planning vs input not significant. ATT scorer validated only on AgentDyn gpt-4o (κ 0.645). No mixed-effects model fitted (no statsmodels in venv; permutation used instead — Dev. #4).
