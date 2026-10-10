"""Assemble docs/paper/negative_result/MANUSCRIPT_DRAFT_v1.md from the section drafts plus new sections (9, 10, 11, refs).

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
| On the E2 traces the success endpoint changes the verdict: a static tool policy executes 0/72 attacks and is invisible to proposal-level scoring (65/72 proposed), and it lowers benign utility from 45/45 to 15/45 | that the static policy is a defense, or that the effect generalizes beyond these scenarios |
| Under the stated M3 rule (an untrusted channel and an attacker-controlled effect), E2 contains no valid attack, so the complete stop of PHASE1-CORE on its direct-override scenario is not evidence of a defense effect | that PHASE1-CORE stops attacks |
| On the partially independent E3 set, which passes the M3 rule, neither detector-style defense changes executed attacks beyond the replicate noise (56/167 undefended vs 57/167 with B3; 57/168 vs 57/168 with CORE) | that any defense is ineffective in general, or on other attacks, adaptive or system-level defenses |
| Undefended susceptibility is model-specific (41/56 for one target, 8/56 for two others) | that results transfer to other targets or to frontier or closed models |
| On the two assessable 2026 targets, a tool-channel delimiter lowers proposal-level attacker tool calls by about ten points (23/186 to 5/186 and 4/186) | that delimiters defend against executed attacks, adaptive attackers or long contexts |
| Most of the five 2026 calibration targets are below 5% or undetermined on InjecAgent and on the Hard set (the closed target gpt-5.6-sol is 0/40, undetermined) | that these targets are robust, or that a floor was demonstrated for any of them |
| Three candidate checks (M3 to M5) are demonstrated on these traces, at exploratory strength; M1 and M2 are illustrated on E2 scenarios that fail the validity rule; M6 is proposed and not demonstrated | that the checks are a validated measurement framework, or that M1 and M2 are demonstrated |
"""

S10 = """## 10 Ethics, dual use, AI assistance and reproducibility
**Ethics and dual use.** All attacks run against mock tools and reserved example domains; no live system, account or person was involved. The attack templates of the partially independent set are directly reusable. They are not in the tree of any branch; the file is retrievable from the public repository by commit SHA (`e5135a6`), and the SHA-256 values in `REPRODUCIBILITY.md` match it, so we do not describe the templates as withheld. The traces, the offline analysis scripts and the number ledger are public. The live multi-turn harness (`src/adapti_guard/evaluation/harness_v2/`), the E2 and E3 run scripts and the registered external-test runner are not in the tree. The work is defensive: it improves how defenses are measured.

**Use of AI assistance.** An AI assistant was used under the first author's direction in the research-support and writing work. It contributed to analysis code, harness extensions, the partially independent attack-scenario templates (§8.3), drafts of this manuscript, and internal review notes. The first author specified the studies. No record of approval of the E2 and E3 runs or of their budgets is preserved (§8.5). Numbers were regenerated from the persisted traces by scripts. The assistant is not an author, and the same assistant family wrote the scenarios, drafted this manuscript and produced the internal reviews, so none of these is an independent human check.

**Number ledger.** `NUMBERS_LEDGER.md` lists the quoted counts, rates and intervals of §5 and §6, the figures' tabulated values, and the external-test and calibration cells, each with its file and key. Two classes of number are not ledgered. The per-family and per-target cells of Appendix D are read from one committed file, `paired_vs_a0_analysis.json`. Design constants (sample sizes, caps, resample counts, seeds, dates, commit and file hashes) are cited to the file that fixes them in the text. A consistency test checks that every ledgered string appears in this manuscript.

**Reproducibility.** The E2 and E3 numbers, the figures, the number ledger and the manuscript regenerate from the committed traces with `scripts/reproduce_negative_result.sh`. The counts, rates and calibration cells of §6.3 and §6.4 are recomputed from the committed external-test and calibration records by `scripts/recompute_external_test.py`, and `tests/test_external_ledger_raw.py` recomputes them again from the raw files without importing that script. The cluster-bootstrap intervals of §6.3 are read from `ANALYSIS.json`, because the script that produced them is not in the tree. The InjecAgent calibration and panel run scripts are restored unchanged (`docs/RESTORED_FROM_96b33e4e.md`). They call a provider and are not run by the reproduction script. Hosted models change, and temperature 0 is not deterministic (measured, §6.2), so traces, model identifiers and dates are released rather than relying on reruns. Live spend is reported as runner summaries in §8.5.
"""

S11 = """## 11 Conclusion
This paper reports a case study of how valid measurements of runtime defenses are, on one testbed. On the same traces, the success endpoint, the labeling of pre-target blocks and the validity of the attack scenarios each changed or qualified the reported verdict (§6.1). On a partially independent set that passes the scenario rule, two detector-style defenses leave executed attacks unchanged within noise (§6.2), and undefended susceptibility differs by model. Most 2026 targets are below 5% or undetermined on public attack sets, so defense comparisons on them would not be informative (§6.4). The external test on two assessable targets corroborates a tool-channel effect at proposal level (§6.3). The checks are candidate rules: three are demonstrated here at exploratory strength, two (M1 and M2) are illustrated on E2 scenarios that fail the validity rule, and the sixth is only proposed. Confirmation requires independent replication on other harnesses, defenses and authors (§8).
"""

REFS = """## References
Reading status: the axes of Pathade et al. and the author order of Sakib et al. were re-checked on 2026-10-10 against the arXiv pages and the full text of 2609.25173. Several cited works are preprints or workshop papers that are not peer reviewed (Shaw, Pathade et al., Sakib et al., Akinrele and Gowda, Deep et al.).
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
"""

HEADER = """# What Reached the Executor? Measurement Validity for Runtime Defenses of LLM Agents, and a Floor Effect on Strong Models

---

"""


def main() -> None:
    a = sections("SECTIONS_1_3_7_INTRO_THREAT_DISCUSSION.md")
    s4 = sections("SECTION4_MEASUREMENT_VALIDITY.md")
    s56 = sections("SECTIONS_5_6_EXPERIMENTS_RESULTS.md")
    s8 = sections("SECTION8_LIMITATIONS.md")
    abstract = a["Abstract (revised draft)"].replace("## Abstract (revised draft)", "## Abstract")
    body = [
        abstract, a["1 Introduction"], S2, a["3 Threat model and testbed"], s4["4 Candidate measurement checks for defense evaluation"],
        s56["5 Experiments"], s56["6 Results"], a["7 Discussion"], s8["8 Limitations"], S9, S10, S11, REFS,
        (N / "APPENDIX_A_EXPLORATORY_PILOT.md").read_text(),
        (N / "APPENDIX_B_CHECKLIST.md").read_text(), (N / "APPENDIX_C_ARTIFACTS.md").read_text(),
        (N / "APPENDIX_D_E3_DETAILED_RESULTS.md").read_text(),
    ]
    (N / "MANUSCRIPT_DRAFT_v1.md").write_text(HEADER + "\n".join(body))
    print("wrote MANUSCRIPT_DRAFT_v1.md", sum(len(b.split()) for b in body), "words")


if __name__ == "__main__":
    main()
