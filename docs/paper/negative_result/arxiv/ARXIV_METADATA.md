# arXiv metadata, ready to paste (ASCII only; owner to confirm)

arXiv metadata fields accept ASCII only, so the kappa and section signs of the manuscript are spelled out below.

**Title** (119 characters):
```
What Reached the Executor? Six Measurement Checks for Evaluating Runtime Defenses of LLM Agents, with a Negative Result
```

**Authors** (Firstname Lastname, comma separated):
```
Matin Shirazi, Reza Manzour
```
Confirm the spelling of the second name. Affiliations are optional in this field; add them in parentheses if wanted, e.g. `Matin Shirazi (Your University)`. The owner stated both authors are independent (no institution), so the paper's author block says "Independent Researchers"; leave this field without a parenthetical or add `(Independent Researcher)`.

Author emails (given by the owner; they appear in the paper's author block, not in this arXiv field): Matin Shirazi: Shirazimatin@gmail.com; Reza Manzour: Rezamanzourolajdad@gmail.com. The corresponding author is set to Matin Shirazi as a default.

**Abstract** (1529 characters; arXiv limit is 1920; do not type the word "Abstract"):
```
This paper is an empirical case study of six candidate measurement validity checks (M1 to M6) for evaluating runtime defenses of tool-using LLM agents: executed call versus proposed call, labeling of blocked payloads, attacker-controlled effect, authorship of attack scenarios, per-model reporting, and defense applied to the untrusted channel. The first and fifth have the most support; the other four are preliminary (Table 3). All six were derived and demonstrated on one testbed by one team and have not been independently replicated.

Two frozen judge-scored confirmatory runs reached opposite verdicts. Re-scoring the same episodes by the tool layer's execution record moves the 0.44 paired effect to 0.90 while benign utility falls from 0.97 to 0.80; the judge agrees with the executed outcome only weakly (kappa 0.16 to 0.36). On seven partially independent attack families, neither detector-style defense changes executed attacks beyond run-to-run noise (56 undefended vs 57 defended, and 57 vs 57, of 167 and 168 pairs). In the earlier E2 run, a static tool policy stops every executed attack but lowers benign utility from 1.00 to 0.33. We release the committed traces and offline scripts that regenerate the E1 to E4 tables and figures; the live harness, run scripts and external-test runner are not public (Section 10). An external InjecAgent test (protocol drafted locally, not externally registered) and a calibration on five 2026 targets are reported descriptively. We do not claim that any defense is effective.
```

**Comments** (use the page count of the file you actually upload):
```
29 pages, 3 figures, 15 tables. Negative-result case study on one testbed; preprint, not peer reviewed.
```
(If you upload the 15-page two-column variant instead: `15 pages main text plus 7 pages supplement ...`; but arXiv takes one source, so the 29-page single-column file is the one packaged for arXiv.)

**Primary category:** cs.CR (Cryptography and Security). **Cross-list:** cs.LG, optionally cs.AI. Moderators may change categories.

**License:** your choice at submission, permanent. See the checklist for tradeoffs.

**Fields to leave empty:** Report-no, MSC-class, ACM-class, Journal-ref, DOI (no published version, no institutional report number; nothing was invented).
