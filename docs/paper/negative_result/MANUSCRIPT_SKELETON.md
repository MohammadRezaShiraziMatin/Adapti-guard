# Manuscript skeleton (working draft; not for submission)

**Working title:** *When adaptive defenses look like they work: an execution-level, hash-locked evaluation of runtime defenses for tool-using LLM agents*
**Target:** workshop / Findings-style negative-result or evaluation-methodology track (see `docs/paper/q1_findings/DECISION_LOCK_FINDINGS_VENUE.md`); a main-track defense paper is **not** supported by the evidence (see §9).
**Drafted sections (see sibling files):** abstract, §1, §3, §7 in `SECTIONS_1_3_7_INTRO_THREAT_DISCUSSION.md`; §4 `SECTION4_MEASUREMENT_VALIDITY.md`; §5–§6 `SECTIONS_5_6_EXPERIMENTS_RESULTS.md`; §8 `SECTION8_LIMITATIONS.md`. Still to write: §9 (claims table finalisation), §10 (ethics, AI assistance, reproducibility) in final form, references. The abstract below is superseded by the revised abstract in the §1/§3/§7 file.
**Status legend:** `[DATA]` number taken from a committed artifact · `[TODO]` needed before submission · `[VERIFY]` citation known only from a title/abstract snippet, read the paper before citing.
**Nothing here is a confirmatory result.** All harness_v2 numbers below are exploratory (Amendment 10 is `PROPOSED`, not approved).

---

## Abstract (draft)
Runtime defenses against prompt injection in tool-using LLM agents are commonly reported as reducing attack success. We evaluate a fixed and adaptive intervention stack (AdaptiGuard) with hash-locked packs and an execution-level endpoint (did the attacker-specified call reach the executor). On a frozen 61+61 pack, one defense (PHASE1-CORE) reduced harmful-action success from 1.00 to 0.56 [DATA: Track B]. Re-testing in a multi-turn tool harness, the adaptive baseline had no effect (65 vs 66 executed attacks of 72) and PHASE1-CORE's effect appeared in one of two scenarios; on seven independently authored attack families, neither B3 nor PHASE1-CORE changed a single outcome beyond run-to-run noise (57 vs 56, and 57 vs 57 of 168 pairs) [DATA]. A static tool-permission policy stops all attacks by construction at a benign-utility cost (1.00 → 0.33). We trace the discrepancy to four measurement choices — proposal vs execution scoring, labelling of pre-target blocks, scenario validity, and pack authorship coupled to detector development — each of which flips the conclusion. We release the frozen packs, harness, and analysis code. `[TODO]` tighten after Amendment 10 decisions.

## 1 Introduction
- Problem: defense claims on self-authored static packs; adaptive attackers break detection-style defenses (Zhan et al.; "The Attacker Moves Second") `[VERIFY]`; system-level/out-of-band defenses are the current direction (CaMeL; Progent; DRIFT) `[VERIFY]`.
- Gap: *validity of the measurement* is rarely examined (arXiv 2609.32691, read).
- Contributions (each maps to evidence):
  1. A hash-locked testbed with an execution-level endpoint and a delivery check (harness_v2; `INVALID_NOT_DELIVERED`). `[DATA]`
  2. A case study where a defense effect (Track B, δ̂ = 0.4426) does not survive re-measurement: explained by pack-shaped detector patterns (audit H1). `[DATA]`
  3. Four measurement choices that flip conclusions, each demonstrated on our own data (§6).
  4. An independent attack-scenario set with a construct-validity gate, and its A0 susceptibility profile (model-specific: deepseek 0.73, qwen3/gemma 0.14). `[DATA]`
  5. Honest negative result and full artifact release.
- Explicit non-claims: not a production defense; no claim about frontier models; no adaptive attacker.

## 2 Related work
Cite only what has been read before submission. Detailed notes with evidence levels: `RELATED_WORK_NOTES.md` (AgentDojo, InjecAgent, Zhan et al., "The Attacker Moves Second", CaMeL, Progent, AutoDojo, 2606.26479, 2609.32691 now read; numbers still to re-check against PDFs).
- Benchmarks: AgentDojo (2406.13352) `[READ via report]`, InjecAgent (2403.02691) `[READ via report]`, ToolHazard `[VERIFY]`, Adaptive Adversaries `[VERIFY]`.
- Defenses: Spotlighting (baseline in repo) `[VERIFY]`; CaMeL (2503.18813) `[READ via report]`; Progent (2504.11703) `[READ via report]`; DRIFT, ActGuard, ToolFence, ROPE `[VERIFY]`; Task Shield, MELON, IPIGuard, CommandSans `[VERIFY]`.
- Adaptive attacks: AutoDojo (2606.15057, **read**); Zhan et al. (2503.00061) `[READ via report]`; "The Attacker Moves Second" (2510.09023) `[READ via report]`.
- Evaluation validity: arXiv 2609.32691 (**read**): four defect classes (payload non-delivery, tool-identity scoring, false-rejection conflation, no audit trail). Our §4 maps onto D1–D4 and adds pre-target-block labelling and scenario-authorship coupling.
- Out-of-band defenses and adaptive-evaluation protocol: arXiv 2606.26479 (**read**).
`[TODO]` re-verify numbers against PDFs; read MELON, Task Shield, DRIFT in full; several 2026 preprints are unreviewed.

## 3 Threat model and testbed
- Trusted: user turn, system prompt, defense code. Untrusted: tool outputs. Direct-injection scenarios (user-turn override) are labelled as such and analysed separately.
- No adaptive, defense-aware attacker (explicit limitation; `docs/paper/phase1/PHASE1_THREAT_MODEL.md`).
- Targets: qwen/qwen-2.5-7b-instruct (Tracks A/B); harness_v2: qwen3, gemma-4-31b-it, deepseek via OpenRouter, temperature 0, llama excluded after Amendment 9 smoke failure. `[DATA]`
- Tools (mock, deterministic): `get_weather`, `retrieve_document`, `send_email`, `create_record`.
- Arms: A0; B3 (original adaptive stack, never blocked in any run); PHASE1-CORE; TOOLDENY (static deny of `send_email`/`create_record`); ARGALLOW (implemented, not run live).
- Provenance: frozen packs with SHA-256 (`c789811a…`, `523c8818…`, template files), per-episode trajectories, ledger reconciliation with `/auth/key`.

## 4 Measurement validity (core contribution)
| choice | wrong default | our rule | effect in our data |
|---|---|---|---|
| Endpoint | model *proposed* the call (`exec_success`) | call *reached the executor* (`exec_executed`), argument- and marker-level | TOOLDENY: 65/72 proposed vs 0/72 executed |
| Pre-target block | label `INVALID_NOT_DELIVERED` and exclude | `BLOCKED_PRE_TARGET`, counted as non-success, with sensitivity analysis | CORE: 0.50 executed if counted, "no effect" if excluded (Amendment 10 §1) |
| Scenario validity | count any call as attack | attacks need untrusted channel + attacker-controlled effect | `create_record_exfil_v1` is a legitimate user request differing from benign only by kind name (§5a) |
| Pack authorship | pack authored with the detector | independent authors; freeze before unseal | CORE 36/36 blocked on original pack, 0/168 on independent families |
| Text claims | count "I sent it" as compromise | executor log only | qwen3 claims the action without calling in 3–8 of 8 episodes in five families |
| Judge vs tool layer (frozen tracks) | LLM judge decides harmful action and utility | tool layer's own executed record | Track B CORE harm 34/61 (judge) vs 6/61 (executed); utility 0.967 (judge) vs 0.80 (executed); κ 0.16–0.36 (`TRACKS_AB_DETERMINISTIC_RESCORING_20260930.md`) |
**Figure 1** (done): `docs/paper/negative_result/figures/fig1_scoring_flip.{png,svg}` with data table `fig1_scoring_flip.csv`, built by `scripts/make_fig1_scoring_flip.py` from the 468 exploratory episodes. Under the four rules the same traces give: CORE 36/72, 36/72, **36/36**, 0/36 (executed, valid scenario only) and TOOLDENY 62/69 (proposed) vs 0/69 (executed).

## 5 Experiments
- **E1 (Tracks A/B; frozen packs, LLM judge).** Track A VNEXT: FAIL (b10/b01 = 5/0, δ̂ = 0.0820, p = 0.0625, U = 0.9344). Track B Phase-1: b10/b01 = 27/0, δ̂ = 0.4426, 95% CI [0.2757, 0.6096], p = 1.49e-8, U = 0.9672; B0 harmful-action success 61/61. Different packs; Track B does not reverse Track A. `[DATA: AUDIT.md, both tracks]`
- **E2 (harness_v2, exploratory, 468 episodes).** 2 attack scenarios × 12 × 3 models × 4 arms + 3 benign scenarios. `[DATA: HARNESS_V2_EXPLORATORY_20260930]`
- **E3 (independent set, exploratory).** 7 families × 8 instances × 3 models: A0 screening (168 episodes, $0.0469), then B3 + CORE (336 episodes, $0.0944). Templates SHA `8ae353ca…9de8`, frozen before any run; offline replay post-freeze. `[DATA]`
- **Cost:** total live spend today ≈ $0.23. `[DATA]`

## 6 Results
Table R1 (E2, executed attacks of 72 pairs / benign utility of 45): A0 66 / 45; B3 65 / 45; CORE 36 / 45; TOOLDENY 0 / 15. Valid attack scenario only (`direct_user_override_v1`): A0 30/36, B3 29/36, CORE 0/36, TOOLDENY 0/36.
Table R2 / Figure 2 (E3 A0 susceptibility): authority-claim 23/24; important-instructions (doc) 9/24; (weather) 8/24; second-document 8/24; unrequested-write 5/24; split-address 4/24; workflow-footer 0/24; by model deepseek 41/56, qwen3 8/56, gemma 8/56.
Table R3 (E3 defended vs A0, paired): B3 167 pairs, 56 → 57, b10/b01 = 3/4, p = 1.0; CORE 168 pairs, 57 → 57, b10/b01 = 4/4, p = 1.0; blocks 0.
Noise floor: ~4–5% of pairs flip between A0 and an input-identical arm at temperature 0 (8/168 CORE; 7/167 B3).
Ablation of scoring rules: Figure 1.

## 7 Discussion
- What the results support: text-level adaptive defenses show effects only where patterns coincide with the pack; a static tool policy is the only complete stop and it is blunt; measurement choices decide conclusions.
- Why PHASE1-CORE's original win did not transfer: shared tool-literal regexes (`send_email … to`) with the pack family; independent families avoid the literal.
- Susceptibility is model-specific; pooled reporting hides it.
- Implication for practice: prefer execution-level endpoints, report per-model results, freeze detectors before scenarios are unsealed, include an A0 replicate.

## 8 Limitations (must stay in the paper)
Small K (8–12 per cell) and 2 + 7 scenario families by a single author; independence from the detector author is **partial** (author read detector patterns earlier in the session; disclosed); no adaptive attacker; 3 open-weight targets via one provider; mock tools; exploratory analyses without pre-registration of Amendment 10; McNemar p-values are descriptive (clustered data); ARGALLOW not evaluated live; judge-based Tracks A/B use a same-family judge (Qwen).

## 9 What the paper may and may not claim
| may | may not |
|---|---|
| PHASE1-CORE reduced harmful-action success on `phase1_confirm_v1` (Track B, scoped) | PHASE1-CORE / AdaptiGuard is an effective defense |
| B3 showed no effect in any run | adaptivity provides benefit |
| Independent families were not blocked by B3 or CORE (0/336 paired episodes) | a general claim about detectors |
| Measurement rules changed conclusions in our data | SOTA, production-ready, "solves prompt injection" |
| Static tool policies stop attacks by construction at utility cost | ARGALLOW is validated |

## 10 Ethics, dual use, AI assistance, reproducibility
- Ethics/dual use: attacks run against mock tools and reserved domains (`.invalid`, `.example`); no live systems. Staged release option for attack templates (as in 2609.32691). `[TODO owner decision]`
- AI assistance: analysis code, harness extensions, scenario templates and drafts were produced with an AI assistant under owner direction; owner verified numbers. `[TODO exact disclosure text per venue policy]`
- Reproducibility: code, frozen packs, SHA-256 manifests, per-episode trajectories, ledgers, analysis scripts (`scripts/analyze_harness_v2_exploratory.py`, `scripts/analyze_independent_defended.py`, `scripts/replay_harness_v2_offline.py`), commit SHAs. Provider nondeterminism at temperature 0 noted. `[TODO reproducibility checklist for chosen venue]`

## Figures and tables plan
F1 scoring-rule flip (done) · F2 per-family × model A0 heatmap (done: `figures/fig2_susceptibility.{png,svg,csv}`, `scripts/make_fig2_susceptibility_heatmap.py`) · F3 defended vs A0 paired dot plot (done: `figures/fig3_defended_vs_a0.{png,svg,csv}`, `scripts/make_fig3_defended_vs_a0.py`; pooled diff B3 +0.006 [-0.024, +0.036], CORE +0.000 [-0.036, +0.036]) · T1 measurement-choice table (§4) · T2 arms and mechanisms · T3 claims table (§9). Use the `dataviz` skill when building charts.

## Open items before any submission
1. Owner decisions on Amendment 10 (§1 scoring rule, §5 per-model admission, noise floor).
2. Independent author/reviewer of the confirmatory scenario set who has not seen the detector; ≥ 6 admitted families per model; A0 replicate.
3. Evaluate ARGALLOW/TOOLDENY utility on independently authored benign tasks.
4. Read and cite related work properly; consider a small adaptive-attacker (AutoDojo-style) condition.
5. Venue selection, template, page limit; ethics and AI-assistance statements.
6. Reconcile `PHASE1_SCIENTIFIC_REPORT.md` unverified claim about commit `c462945` before citing the holdout-tuning statement.
