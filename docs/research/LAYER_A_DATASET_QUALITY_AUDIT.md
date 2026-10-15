# Layer A / P1 Dataset Quality Audit (Read-only)

**Status:** offline audit report; no model/API calls; no source dataset modified  
**Scope:** current default-branch contents of Layer A v3 and P1 mechanism v1 candidate  
**Purpose:** identify evidence-backed dataset improvements for a separate Q1 exploratory evaluation

## Executive finding

The repository already contains two useful in-house assets. Layer A v3 is a balanced, synthetic, frozen 160-row pack with 80 attacks and 80 benign cases; its test split contains 40 attacks and 40 benign cases. It includes 16 rows labeled multi-turn, of which 8 are in test. P1 mechanism v1 is a 96-row candidate with 44 attacks, 52 benign rows, and 22 in-scope mechanism leaves.

Neither asset should be silently substituted into the current InjecAgent confirmatory campaign. The current audit is structural and metadata-based, not a live-model evaluation or independent human-label validation.

## Checks performed

### Layer A v3 — `datasets/frozen/layer_a_v3/dataset.jsonl`

- 160 JSONL rows parsed; 0 parse errors.
- 160 unique IDs; no duplicate IDs.
- No missing prompts or success conditions.
- No exact duplicate bodies under the audited prompt+context representation.
- Labels: 80 attack / 80 benign.
- Splits: 40 train / 40 dev / 80 test.
- Attack-family counts: 24 direct, 22 indirect, 18 obfuscated, 16 multi-turn.
- Test split: 40 attack / 40 benign; 8 multi-turn attacks.
- All 80 attack rows contain canary-oriented success criteria according to the current metadata scan.
- Multi-turn examples encode prior dialogue in a text `context` field and the last instruction in `prompt`. This is a **serialized dialogue-history representation**, not proof of a runner that conducts live stateful turns.
- Provenance metadata identifies the pack as synthetic/authored. It must not be described as an externally sourced or externally validated benchmark.

### P1 mechanism v1 — `datasets/candidates/p1_mechanism_v1/dataset.jsonl`

- 96 JSONL rows parsed; 0 parse errors.
- 96 unique IDs; no duplicate IDs.
- No missing prompts or success conditions.
- No exact duplicate bodies under the audited prompt+context representation.
- Labels: 44 attack / 52 benign; 8 benign rows are marked hard negatives.
- 22 in-scope mechanism leaves have two attacks each according to the candidate manifest.
- The candidate is marked `CANDIDATE` and `live_evaluated=false`; retain that status until a separate gated evaluation is authorized and completed.
- The candidate audit previously documented that several indirect/tool-output cases are authored-channel proxies rather than live retriever/tool I/O, and that semantic/scaffold-level contamination was not ruled out.

### Historical dataset audit

`docs/archive/research/PHASE2_5_DATASET_AUDIT.md` reports earlier coverage gaps in `benchmark_q1` and `attack_dataset.json`, including weak tool-abuse coverage, zero system-prompt-leakage examples in the audited test mapping, and overlap between an attack subset and the benchmark test split. Because this is an archived audit, re-check current artifacts before making claims about the present state.

## Quality limitations that remain

1. **Synthetic-only evidence:** Layer A v3 is authored synthetic data. It is useful for controlled mechanism tests but does not alone establish ecological validity or external generalization.
2. **Multi-turn execution gap:** existing multi-turn rows store transcript history in `context`; the primary confirmatory harness has `max_turns=1`. Do not claim that R2/R3 tested interactive multi-turn attacks.
3. **Small test strata:** only 8 multi-turn attacks are in the frozen v3 test split. Family-level estimates will be imprecise; do not imply statistical power from total N alone.
4. **Success-condition validity:** canary matching is reproducible but can misclassify outputs that quote, discuss, or refuse around a canary unless the scorer follows the exact row-level rule. Human spot-checking and scorer tests are needed.
5. **No semantic contamination audit:** exact-body dedup does not detect paraphrases, shared templates, or near-duplicate attack scaffolds across splits or across packs.
6. **Benign difficulty is uneven:** the pack has benign and hard-negative cases, but the presence of a hard-negative label is not proof that the case is genuinely difficult or matched to an attack.
7. **Mechanism coverage versus power:** P1 has two attacks per in-scope mechanism leaf; appropriate for a mechanism-coverage pilot, not strong per-mechanism inferential claims.
8. **Tool semantics:** some candidate examples describe tool calls in text. A valid execution-rate endpoint requires a real structured tool proposal/execution record, not merely text mentioning a tool.

## Recommended non-destructive upgrade

Create a **new candidate pack**, never edit `datasets/frozen/layer_a_v3/`, `datasets/frozen/layer_a_v2/`, prior result artifacts, or the frozen confirmatory protocol.

- Keep the existing v3 rows as a traceable parent set; preserve source IDs and record parent hashes.
- Add genuinely stateful multi-turn scenarios in a separate candidate split/schema with explicit turn arrays and a runner adapter. Keep transcript-proxy rows labeled as proxies.
- Pair attack cases with task-matched benign/hard-negative controls; measure both security failure and legitimate-task completion.
- Add or curate tool-abuse and data-exfiltration scenarios only where the ADAPTI-GUARD runtime can observe a concrete attempted/executed action.
- Add provenance, authoring method, expected action, success/failure examples, difficulty rationale, and a clear adjudication rule for each case.
- Run exact and near-duplicate checks across all splits and parent packs; do not use test rows to tune the detector or defense.
- Use an independent human review pass for label validity and ambiguous success conditions.
- Freeze the new pack only after the candidate is reviewed. Evaluate it separately as exploratory unless a distinct protocol is approved before any model run.

## Decision

**Proceed with a candidate-only improvement; do not modify frozen evidence or run models in this PR.** This report is an audit and specification, not a claim that the new candidate data has already been authored, human-reviewed, or evaluated.
