"""Assemble docs/paper/negative_result/MANUSCRIPT_DRAFT_v1.md from the section drafts plus new sections (2, 9, 10, refs).

Deterministic; run after editing any section file. Keeps the section files as the single source of prose.
"""
from __future__ import annotations

import re
from pathlib import Path

N = Path(__file__).resolve().parents[1] / "docs/paper/negative_result"


def sections(path: str) -> dict[str, str]:
    parts = re.split(r"(?m)^(?=## )", (N / path).read_text())
    out: dict[str, str] = {}
    for p in parts:
        m = re.match(r"## (.+)", p)
        if m:
            out[m.group(1).strip()] = p.strip() + "\n"
    return out


S2 = (N / "RELATED_WORK.md").read_text()

S9 = """## 9 What the paper may and may not claim
| may claim | may not claim |
|---|---|
| On the frozen Phase-1 pack, judge-scored harmful-action success fell from 1.00 to 0.56; with the tool layer's record it is 6/61 against 61/61, and judge-scored utility 0.967 becomes 0.80 | that the defense (or adaptive intervention in general) is effective |
| The adaptive stack showed no effect in any run | that adaptivity provides a benefit |
| On seven partially independently authored families neither detector-style defense changed executed attacks beyond run-to-run noise (paired differences +0.006 and 0.000, intervals include zero) | a general statement about detectors, models or adaptive attackers |
| Five measurement choices and a channel check changed or qualified conclusions on our own traces (one denominator rule was adopted post hoc; the channel check is a preliminary, unreplicated held-out discovery) | SOTA, production-readiness, that the rules are validated, or that they generalize beyond the datasets used |
| A static tool policy stops the tested attacks by construction and removes most benign tool utility | that any published system-level defense (CaMeL, Progent) was evaluated or compared |
| Delimiters applied to the untrusted context lowered indirect injections from 8 to 1 of 18 in a small, unreplicated re-run (M6, preliminary) | that spotlighting works in general |
| In an exploratory pilot on 120 independently authored InjecAgent cases (Appendix A; earlier open models, not the final panel), undefended susceptibility ranged from 5/120 to 50/120 and tool-channel delimiters lowered it for one model (26/9 discordant pairs) but not for the larger model of the same family (7/13) | that delimiters, or any tested defense, generalize across models; or anything about frontier or closed models |
| On InjecAgent (186 cases, two measurable targets), delimiters on the tool channel lowered emitted attacker tool calls (a proposal-level endpoint) by about ten points (12.4% to 2.7% and 2.2%); a reduced test on two of five planned targets | that any defense is effective in general, comprehensive external validation, or anything about adaptive attackers, other benchmarks or the targets at the floor |
"""

S10 = """## 10 Ethics, dual use, AI assistance and reproducibility
**Ethics and dual use.** All attacks run against mock tools and reserved example domains; no live system, account or person was involved. The attack templates, in particular the authority-claim family, are directly reusable, so release is staged: the committed traces, analysis code and regeneration scripts are in the public repository; the attack-template files are withheld and staged for release (with the camera-ready version or on request to the authors); the multi-turn harness and runner are not in the public repository and no release of them is claimed here. The work is defensive: it improves how defenses are measured.
**Use of AI assistance.** An AI assistant was used under the owner's direction in the research-support and writing work: it contributed to analysis code, harness extensions, the independent attack-scenario templates (§8.3) and drafts of this manuscript, and to repository audits and internal review notes. The owner specified the studies and approved each live run and its budget; numbers were regenerated from the persisted traces by scripts. The assistant is not an author.
**Reproducibility.** Two levels must be kept apart. (A) *Offline analysis reproduction.* From the committed episode traces and derived artifacts, `STRICT=1 bash scripts/reproduce_negative_result.sh` regenerates the E1–E3, MT1 and M6 analyses, Figs. 1–3, the number ledger and this manuscript without network access or API keys (the InjecAgent analyses also need an external benchmark checkout; without it their committed derived files are read). This shows that the reported numbers follow from the committed traces; it does not show that the traces were produced as described. (B) *Re-running the original live experiments* (E2, E3 and the live runs of E4 and §6.6) is not possible from the public repository: the multi-turn harness, the runner and the attack-template files are not published, hosted models change, and temperature 0 is not deterministic (two arms with identical model input differed in 8 of 168 paired outcomes in E3). Provenance of the live runs rests on run manifests (runner and repository commit SHAs, worktree-clean flag), cost summaries, progress logs and the git history of an unpublished checkout; the E3 template SHA-256 is attested only there (§3.2). Each table and figure is produced by a script (`scripts/rescore_tracks_ab_deterministic.py`, `scripts/analyze_harness_v2_exploratory.py`, `scripts/analyze_independent_defended.py`, `scripts/audit_e3_delivery_sensitivity.py`, `scripts/apply_rules_second_dataset_mt1.py`, `scripts/analyze_spotlight_ctx_check.py`, `scripts/make_fig{1,2,3}_*.py`), and a number ledger (`NUMBERS_LEDGER.md`) lists each quoted number with its source. Live spend is reported per experiment in §5 and §8.5.
"""

S11 = """## 11 Conclusion
This paper reports an empirical methodological case study on one testbed built on hash-locked packs, with small samples. On the same traces, the choice of success endpoint (executed call versus judge or proposal), the labeling of blocked payloads and per-model reporting changed the reported verdict or its size (§6.1–§6.3), and the headline of §6.1 rests on execution-record counts rather than on the weak, descriptive judge–executor κ (0.16 to 0.36). The labeling rule for blocked payloads was adopted post hoc, and one defense's E2 headline depends on it (§4.2). A reduced external InjecAgent run (two of five planned targets, a proposal-level first-call endpoint, protocol drafted locally and not externally registered) is consistent with the per-model and tool-channel findings; it is corroboration, not validation (§6.6). Scenario validity, attack-set authorship independence (partial; the same assistant also wrote the scoring predicates) and the defense-channel check (a post hoc held-out discovery supported by 18 episodes, not replicated) rest on a single scenario, a partially independent author and 18 episodes respectively, and remain preliminary. The six checks are therefore candidate measurement rules and a reporting checklist, not a validated framework; we evaluated no adaptive attacker and make no claim that any defense is effective. Confirmation requires independent replication on other harnesses, defenses and authors (§8).
"""

REFS = """## References
Reading status: on 2026-10-01 every cited claim and number below was checked against the PDF of the cited paper (per-claim table in `docs/paper/negative_result/REFERENCE_VERIFICATION_20261001.md`). Several cited works are preprints or workshop papers that are not peer reviewed (Shaw, Pathade et al., Narisetty et al., Deep et al., Akinrele and Gowda, Sakib et al.).
- [2406.13352] Debenedetti et al. AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents.
- [2403.02691] Zhan et al. InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated LLM Agents.
- [2503.18813] Debenedetti et al. Defeating Prompt Injections by Design (CaMeL).
- [2504.11703] Shi et al. Progent: Securing AI Agents with Privilege Control.
- [2503.00061] Zhan et al. Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents.
- [2510.09023] Nasr et al. The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections.
- [2606.15057] Ma et al. AutoDojo: A Generative Benchmark for Evaluating Prompt Injection Defenses in LLM Agents.
- [2606.26479] Narisetty et al. Adaptive Evaluation of Out-of-Band Defenses Against Prompt Injection in LLM Agents.
- [2609.32691] Shaw. Silent Failures in Agentic Security Evaluation: A Validated Harness for Tool-Call Mediation Under Indirect Prompt Injection (full text).
- [2502.05174] Zhu et al. MELON: Provable Defense Against Indirect Prompt Injection Attacks in AI Agents (ICML 2025).
- [2412.16682] Jia et al. The Task Shield: Enforcing Task Alignment to Defend Against Indirect Prompt Injection in LLM Agents.
- [2312.14197] Yi et al. Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models (BIPIA; KDD 2025). (read)
- [2506.09956] Abdelnabi et al. LLMail-Inject: A Dataset from a Realistic Adaptive Prompt Injection Challenge. (read; MIT license)
- [2608.28411] Liu et al. LongPIBench: A Long-Context Benchmark for Prompt Injection. (read)
- [2605.30454] Sakib et al. The Surface You Test Is Not the Surface That Breaks. (read)
- [2606.10525] Hofer, Debenedetti and Tramèr. Assessing Automated Prompt Injection Attacks in Agentic Environments. (read)
- [2605.26999] Akinrele and Gowda. Prompt Injection Detection is Regime-Dependent: A Deployment-Aware Evaluation with Interpretable Structural Signals. (read)
- [2604.23887] Deep et al. Evaluation of Prompt Injection Defenses in Large Language Models (vendor study; read).
- [2609.25173] Pathade, Pawar and Patil. Attack Success Rate Is Not a Number: On Measurement Validity in Agentic AI Security Evaluation.
- [2603.15714] Dziemian et al. How Vulnerable Are AI Agents to Indirect Prompt Injections? Insights from a Large-Scale Public Competition.
- [2609.36817] Ying et al. (Tencent Zhuque Lab). pikit: A Composable Toolkit for Indirect Prompt Injection Research and Evaluation.
- [2604.08499] Geng et al. PIArena: A Platform for Prompt Injection Evaluation.
- [2403.14720] Hines et al. Defending Against Indirect Prompt Injection Attacks With Spotlighting.
"""

HEADER = """# What Reached the Executor? Six Measurement Checks for Evaluating Runtime Defenses of LLM Agents, with a Negative Result

---

"""


def main() -> None:
    a = sections("SECTIONS_1_3_7_INTRO_THREAT_DISCUSSION.md")
    s4 = sections("SECTION4_MEASUREMENT_VALIDITY.md")
    s56 = sections("SECTIONS_5_6_EXPERIMENTS_RESULTS.md")
    s8 = sections("SECTION8_LIMITATIONS.md")
    abstract = a["Abstract (revised draft)"].replace("## Abstract (revised draft)", "## Abstract")
    abstract = abstract.replace(
        "We identify five measurement choices",
        "We identify five measurement choices (and, on held-out data, a sixth check: whether a defense is applied to the untrusted channel)",
    )
    body = [
        abstract, a["1 Introduction"], S2, a["3 Threat model and testbed"], s4["4 Candidate measurement rules for defense evaluation"],
        s56["5 Experiments"], s56["6 Results"], a["7 Discussion"], s8["8 Limitations"], S9, S10, S11, REFS,
        (N / "APPENDIX_A_EXPLORATORY_PILOT.md").read_text(),
        (N / "APPENDIX_B_CHECKLIST.md").read_text(), (N / "APPENDIX_C_ARTIFACTS.md").read_text(),
        (N / "APPENDIX_D_E3_DETAILED_RESULTS.md").read_text(),
    ]
    (N / "MANUSCRIPT_DRAFT_v1.md").write_text(HEADER + "\n".join(body))
    print("wrote MANUSCRIPT_DRAFT_v1.md", sum(len(b.split()) for b in body), "words")


if __name__ == "__main__":
    main()
