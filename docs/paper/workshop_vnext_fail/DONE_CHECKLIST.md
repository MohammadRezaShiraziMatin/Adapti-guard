# Master-prompt DONE checklist (after VNEXT FAIL)

Agent-closable items for the workshop package. **Human-only** actions stay NO.

No live LLM eval. No OpenRouter calls. No retune. No N increase. No frozen dataset edits. No arXiv/external submit.

| # | Item | Agent DONE? | Evidence |
| --- | --- | --- | --- |
| 1 | Verify manuscript facts still match AUDIT FAIL numbers | **YES** | `python3 docs/paper/workshop_vnext_fail/verify_manuscript_facts.py` vs `experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/{AUDIT.md,verdict.json,comparison.json}` |
| 2 | Strengthen reproducibility package (configs snapshot, offline checks, PR index) | **YES** | `docs/experiments/REPRODUCIBILITY_PACKAGE.md`; [`CONFIGS_SNAPSHOT.md`](CONFIGS_SNAPSHOT.md); [`PR_STACK.md`](PR_STACK.md); this file’s offline commands |
| 3 | CLAIMS_MAP / checklist consistency with FAIL (no win language) | **YES** | [`CLAIMS_MAP.md`](CLAIMS_MAP.md); `docs/paper/CLAIMS_CHECKLIST_LAYER_A.md` FAIL/CLOSED banner; verifier forbidden-positive scan |
| 4 | `docs/experiments/RESEARCH_LOG.md` entry for 2026-09-14 | **YES** | Layer A closed; Phase 1–3a; Phase 2 harness; pack freeze; VNEXT FAIL; manuscript PR32 |
| 5 | Short [`PR_STACK.md`](PR_STACK.md) for open PRs 23–32 | **YES** | Roles `docs` / `harness` / `pack` / `live` / `manuscript`; merge **not** executed |
| 6 | Human submission packet (cover letter, camera-ready map, titles, forbidden claims, artifacts, merge reminder) | **YES** (docs only) | [`SUBMISSION_PACKET.md`](SUBMISSION_PACKET.md); Persian note [`SUBMIT_NEXT_FA.md`](SUBMIT_NEXT_FA.md). **Not** a venue submit |

| Human-only (must stay NO for agents) | DONE? |
| --- | --- |
| Merge PRs 23–34 | **NO** |
| Choose venue / submit arXiv or workshop | **NO** |
| New live eval / OpenRouter | **NO** |
| Retune detector or HIGH/MEDIUM bands | **NO** |
| Increase N or edit frozen JSONL | **NO** |

Canonical FAIL facts (must remain): pack SHA-256 `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518`; B0 ASR 0.9508; VNEXT-ADAPT ASR 0.8689; b10=5 b01=0 p=0.0625; δ̂=0.0820 < MSID 0.20; U=0.9344 < 0.95; qualified win **NO**.
