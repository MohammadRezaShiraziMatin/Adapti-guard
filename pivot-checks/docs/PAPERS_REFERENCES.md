# References for the removed `pivot-checks/papers/` folder (2026-10-17)

The 17 files in `pivot-checks/papers/` (third-party paper PDFs and their text extractions) were removed from branch `audit/pivot-checks` on 2026-10-17 for copyright reasons. **They are still present in git history at commits 2eb0b80 and 986387e.** Docs that cite `papers/<id>.txt` or `papers/<id>.pdf` (exposure/EXPOSURE_TABLE.md, review/RELATED_FULLREAD.md, review/RELATED_WORK_ROUND10.md, LIU_JUDGE_READ.md, manuscript drafts) should be read against those commits or the public arXiv pages.

Method: identifiers come only from the file contents, namely the arXiv stamp line printed in each text extraction (e.g. `arXiv:2609.25173v1 [cs.CR] 21 Sep 2026`). PDFs were not parsed; a PDF's identifier rests on its filename matching the same-ID text file and is marked accordingly. No DOI for any of these papers appears in the files (DOIs in the texts belong to cited works). URLs are the standard arXiv abs form of the stamped ID. Nothing is invented; anything not checkable from the file is marked unverified.

| File | Title (from text) | Identifier | Basis |
|---|---|---|---|
| 2609.00038.pdf | trajectory-judge: What Outcome-Only LLM Judges Miss on Agent Trajectories | arXiv:2609.00038 (unverified from PDF itself) | filename = 2609.00038.txt |
| 2609.00038.txt | trajectory-judge: What Outcome-Only LLM Judges Miss on Agent Trajectories (H. Mohammadi) | arXiv:2609.00038v2, https://arxiv.org/abs/2609.00038v2 | stamp line in text |
| 2609.25173.pdf | Attack Success Rate Is Not a Number: On Measurement Validity in Agentic AI Security Evaluation | arXiv:2609.25173 (unverified from PDF itself) | filename = 2609.25173.txt |
| 2609.25173.txt | Attack Success Rate Is Not a Number: On Measurement Validity in Agentic AI Security Evaluation (Pathade, Pawar, Patil) | arXiv:2609.25173v1, https://arxiv.org/abs/2609.25173v1 | stamp line in text |
| 2609.25173.full.txt | same as 2609.25173.txt (same size, 57,526 bytes) | arXiv:2609.25173v1 | stamp line in text |
| 2609.32691.pdf | Silent Failures in Agentic Security Evaluation: A Validated Harness for Tool-Call Mediation Under Indirect Prompt Injection | arXiv:2609.32691 (unverified from PDF itself) | filename = 2609.32691.txt |
| 2609.32691.txt | Silent Failures in Agentic Security Evaluation: A Validated Harness for Tool-Call Mediation Under Indirect Prompt Injection (A. Shaw) | arXiv:2609.32691v1, https://arxiv.org/abs/2609.32691v1 | stamp line in text |
| 2609.34862.pdf | JEV as a Judge for Agent Trace Security: An Empirical Comparison with Generative LLM Judges | arXiv:2609.34862 (unverified from PDF itself) | filename = 2609.34862.txt |
| 2609.34862.txt | JEV as a Judge for Agent Trace Security: An Empirical Comparison with Generative LLM Judges (Z. Wang, Y. Gao) | arXiv:2609.34862v1, https://arxiv.org/abs/2609.34862v1 | stamp line in text |
| 2610.00651.pdf | Agent Evaluation Reliability: More Tasks Won't (Always) Fix an Agent Leaderboard | arXiv:2610.00651 (unverified from PDF itself) | filename = 2610.00651.txt |
| 2610.00651.txt | Agent Evaluation Reliability: More Tasks Won't (Always) Fix an Agent Leaderboard (M. Hardy et al.) | arXiv:2610.00651v1, https://arxiv.org/abs/2610.00651v1 | stamp line in text |
| 2610.03448.pdf | Passing the Test You Trained On: Re-evaluating Prompt-Injection Detectors for LLM Agents | arXiv:2610.03448 (unverified from PDF itself) | filename = 2610.03448.txt |
| 2610.03448.txt | Passing the Test You Trained On: Re-evaluating Prompt-Injection Detectors for LLM Agents (Z. Liu) | arXiv:2610.03448v1, https://arxiv.org/abs/2610.03448v1 | stamp line in text |
| 2610.04504.pdf | The Same Zero: Why Identical ASR Can Imply Different Guarantees in LLM-Agent Security | arXiv:2610.04504 (unverified from PDF itself) | filename = 2610.04504.txt |
| 2610.04504.txt | The Same Zero: Why Identical ASR Can Imply Different Guarantees in LLM-Agent Security (Y. Yin) | arXiv:2610.04504v1, https://arxiv.org/abs/2610.04504v1 | stamp line in text |
| L.txt | Passing the Test You Trained On: Re-evaluating Prompt-Injection Detectors for LLM Agents (Z. Liu) | arXiv:2610.03448v1 | stamp line in text (first line) |
| P.txt | Attack Success Rate Is Not a Number: On Measurement Validity in Agentic AI Security Evaluation (Pathade, Pawar, Patil) | arXiv:2609.25173v1 | stamp line in text (first line) |
