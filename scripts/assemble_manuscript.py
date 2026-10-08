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
| The adaptive stack (B3, VNEXT-ADAPT) showed no effect above the frozen 0.20 gate in any run, and B3 never blocked; the Track A executed-call difference (6/0 discordant pairs, δ̂ 0.098) is descriptive | that adaptivity provides a benefit, or that it matches or beats any fixed level |
| On seven partially independent families PHASE1-CORE left the model input unchanged and B3 changed only trailing punctuation; neither blocked anything, and the executed-attack differences (+0.006 and 0.000) are consistent with run-to-run noise | that the defenses were tested as mechanisms on these families, or a general statement about detectors, models or adaptive attackers |
| Five measurement choices and a channel check changed or qualified conclusions on our own traces | SOTA, production-readiness, or that the rules are validated beyond the two datasets used |
| A static tool policy executes no attack on the E2 attack set by construction, and completes 15/45 benign episodes, the weather tasks that need no denied tool | that this measures the cost of tool policies in general, or that any published system-level defense (CaMeL, Progent) was evaluated or compared |
| Delimiters applied to the untrusted context lowered indirect injections from 8 to 1 of 18 in a small re-run | that spotlighting works in general |
| In an exploratory pilot on 120 independently authored InjecAgent cases (Appendix A; earlier open models, not the final panel), undefended susceptibility ranged from 5/120 to 50/120 and tool-channel delimiters lowered it for one model (26/9 discordant pairs) but not for the larger model of the same family (7/13) | that delimiters, or any tested defense, generalize across models; or anything about frontier or closed models |
| On InjecAgent (186 cases, two measurable targets), delimiters on the tool channel lowered the rate of attacker-tool first calls (proposal level, nothing executed) by about ten points (12.4% to 2.7% and 2.2%) | that any defense is effective in general, or anything about adaptive attackers, other benchmarks or the targets at the floor |
"""

S10 = """## 10 Ethics, dual use, AI assistance and reproducibility
**Ethics and dual use.** All attacks run against mock tools and reserved example domains; no live system, account or person was involved. The attack templates, in particular the authority-claim family, are directly reusable. They are not in the tree of any branch, but both template files are retrievable from the public repository by commit SHA (the original set at `bea82347`, the independent set at `e5135a6`; the retrieved files match the SHA-256 values recorded in `REPRODUCIBILITY.md`), so we do not describe them as withheld or their release as staged. The traces, the frozen packs and the offline analysis scripts are public; the live multi-turn harness (`src/adapti_guard/evaluation/harness_v2/`), the run scripts for E2, E3, the calibration and the external test, and the external-test analysis scripts are not in the tree of any public branch or tag. They exist in two commits of the original history (`1ae0fb4d` and the archive commit `dfbea801`) that can be fetched from the public remote by full SHA but are not reachable from any ref and are not guaranteed to persist; we therefore do not claim that the harness is publicly released. The work is defensive: it improves how defenses are measured.
**Use of AI assistance.** An AI assistant was used under the first author's direction in the research-support and writing work: it contributed to analysis code, harness extensions, the independent attack-scenario templates (§8.3) and drafts of this manuscript, and to repository audits and internal review notes. The first author specified the studies; no record of approval of the four multi-turn harness runs of E2 and E3 (2026-09-30) or of their budgets is preserved (§8.5). Numbers were regenerated from the persisted traces by scripts. The assistant is not an author. The same assistant family wrote the independent scenarios (§8.3), drafted this manuscript and produced the internal reviews, so none of these is an independent human check.

**Ledger coverage.** `NUMBERS_LEDGER.md` lists 54 quoted strings with their sources; it does not cover every number (for example the E1 κ values, the Track B string-match counts of §6.1, the E3 audit counts of §6.3, the multi-turn re-run counts, most of Appendix A, and the §6.6 and §6.7 tables). Appendix C states which tables the one-command script regenerates.
**Reproducibility.** The frozen packs carry SHA-256 hashes in `datasets/frozen/*/hashes.sha256`; the run manifests of the multi-turn runs record commit SHAs, not file hashes, and the template files' SHA-256 values are given in `REPRODUCIBILITY.md` (the template files themselves are not in the tree); the E1 to E4 tables and figures are regenerated by a script from committed traces (`scripts/rescore_tracks_ab_deterministic.py`, `scripts/analyze_harness_v2_exploratory.py`, `scripts/analyze_independent_defended.py`, `scripts/apply_rules_second_dataset_mt1.py`, `scripts/analyze_spotlight_ctx_check.py`, `scripts/make_fig{1,2,3}_*.py`); a number ledger (`NUMBERS_LEDGER.md`) lists each quoted number with its source. The external-test numbers of §6.6 and §6.7 are read from committed per-episode and derived records; their runner and analysis scripts are not public, so those numbers cannot be regenerated from this repository, and the archive of the original history (`case-study-v1`) is not published as a tag. Hosted models change and temperature 0 is not deterministic (measured), so traces, model identifiers and dates are released rather than relying on reruns. Live spend is reported per experiment in §5 and §8.5. Checked on 2026-10-07: `scripts/reproduce_negative_result.sh` runs offline without network or key and exits 0; the regenerated manuscript and ledger are identical to the committed ones, and the figure files are rewritten with different bytes (plotting-library version) from unchanged figure data. Test status is given once, in §8.5.
"""

S11 = """## 11 Conclusion
This paper reports an empirical methodological case study on one testbed. On the same traces, the choice of success endpoint (executed call versus judge or proposal), the labeling of blocked payloads and per-model reporting changed the reported verdict or its size (§6.1–§6.3), and an external InjecAgent test on two targets, scored at proposal level, is consistent with the per-model and tool-channel effects (§6.6). Scenario validity, attack-set authorship independence (only partially achieved) and the defense-channel check rest on a single scenario, a partially independent author and 18 episodes respectively, and remain preliminary. The six checks are therefore candidate measurement rules and a reporting checklist, not a validated framework; we evaluated no adaptive attacker and make no claim that any defense is effective. Confirmation requires independent replication on other harnesses, defenses and authors (§8).
"""

REFS = """## References
Reading status: on 2026-10-01 every cited claim and number of the first 23 entries below was checked against the PDF of the cited paper (per-claim table in `docs/paper/negative_result/REFERENCE_VERIFICATION_20261001.md`). The last six entries (1912.05511, 2511.04703, 2411.00640, 2306.05685, 2302.12173, FC1990) were added on 2026-10-07 after checking title, authors, year and abstract on the arXiv or publisher page; their claims were not checked against the full text, and FC1990 was confirmed only from citing sources. Several cited works are preprints or workshop papers that are not peer reviewed (Shaw, Pathade et al., Narisetty et al., Deep et al., Akinrele and Gowda, Sakib et al.).
- [2406.13352] Debenedetti et al. AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents. [arXiv:2406.13352, 2024]
- [2403.02691] Zhan et al. InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated LLM Agents. [arXiv:2403.02691, 2024; ACL 2024 Findings]
- [2503.18813] Debenedetti et al. Defeating Prompt Injections by Design (CaMeL). [arXiv:2503.18813, 2025]
- [2504.11703] Shi et al. Progent: Securing AI Agents with Privilege Control. [arXiv:2504.11703, 2025]
- [2503.00061] Zhan et al. Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents. [arXiv:2503.00061, 2025; NAACL 2025 Findings]
- [2510.09023] Nasr et al. The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections. [arXiv:2510.09023, 2025]
- [2606.15057] Ma et al. AutoDojo: A Generative Benchmark for Evaluating Prompt Injection Defenses in LLM Agents. [arXiv:2606.15057, 2026]
- [2606.26479] Narisetty et al. Adaptive Evaluation of Out-of-Band Defenses Against Prompt Injection in LLM Agents. (not peer-reviewed, per the paper) [arXiv:2606.26479, 2026]
- [2609.32691] Shaw. Silent Failures in Agentic Security Evaluation: A Validated Harness for Tool-Call Mediation Under Indirect Prompt Injection (full text). [arXiv:2609.32691, 2026]
- [2502.05174] Zhu et al. MELON: Provable Defense Against Indirect Prompt Injection Attacks in AI Agents (ICML 2025). [arXiv:2502.05174, 2025]
- [2412.16682] Jia et al. The Task Shield: Enforcing Task Alignment to Defend Against Indirect Prompt Injection in LLM Agents. [arXiv:2412.16682, 2024]
- [2312.14197] Yi et al. Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models (BIPIA; KDD 2025). [arXiv:2312.14197, 2023]
- [2506.09956] Abdelnabi et al. LLMail-Inject: A Dataset from a Realistic Adaptive Prompt Injection Challenge. (dataset license: MIT) [arXiv:2506.09956, 2025]
- [2608.28411] Liu et al. LongPIBench: A Long-Context Benchmark for Prompt Injection. [arXiv:2608.28411, 2026; Findings of EMNLP 2026 (to appear)]
- [2605.30454] Sakib et al. The Surface You Test Is Not the Surface That Breaks. (NeurIPS 2026 workshop paper) [arXiv:2605.30454, 2026]
- [2606.10525] Hofer, Debenedetti and Tramèr. Assessing Automated Prompt Injection Attacks in Agentic Environments. [arXiv:2606.10525, 2026]
- [2605.26999] Akinrele and Gowda. Prompt Injection Detection is Regime-Dependent: A Deployment-Aware Evaluation with Interpretable Structural Signals. [arXiv:2605.26999, 2026]
- [2604.23887] Deep et al. Evaluation of Prompt Injection Defenses in Large Language Models (vendor study). [arXiv:2604.23887, 2026]
- [2609.25173] Pathade, Pawar and Patil. Attack Success Rate Is Not a Number: On Measurement Validity in Agentic AI Security Evaluation. [arXiv:2609.25173, 2026]
- [2603.15714] Dziemian et al. How Vulnerable Are AI Agents to Indirect Prompt Injections? Insights from a Large-Scale Public Competition. [arXiv:2603.15714, 2026]
- [2609.36817] Ying et al. (Tencent Zhuque Lab). pikit: A Composable Toolkit for Indirect Prompt Injection Research and Evaluation. [arXiv:2609.36817, 2026]
- [2604.08499] Geng et al. PIArena: A Platform for Prompt Injection Evaluation. [arXiv:2604.08499, 2026; ACL 2026 (to appear)]
- [2403.14720] Hines et al. Defending Against Indirect Prompt Injection Attacks With Spotlighting. [arXiv:2403.14720, 2024]
- [1912.05511] Jacobs and Wallach. Measurement and Fairness. [FAccT 2021, doi:10.1145/3442188.3445901; arXiv:1912.05511]
- [2511.04703] Bean et al. Measuring what Matters: Construct Validity in Large Language Model Benchmarks. [NeurIPS 2025 Datasets and Benchmarks; arXiv:2511.04703]
- [2411.00640] Miller. Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations. [arXiv:2411.00640, 2024]
- [2306.05685] Zheng et al. Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. [NeurIPS 2023 Datasets and Benchmarks; arXiv:2306.05685]
- [2302.12173] Greshake et al. Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection. [arXiv:2302.12173, 2023]
- [FC1990] Feinstein and Cicchetti. High agreement but low kappa: I. The problems of two paradoxes. [Journal of Clinical Epidemiology 43(6):543-549, 1990, doi:10.1016/0895-4356(90)90158-L; bibliographic data confirmed from citing sources only, full text not read]
"""

HEADER = """# What Reached the Executor? Six Candidate Measurement Checks for Evaluating Runtime Defenses of LLM Agents: A Case Study with a Negative Result

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
