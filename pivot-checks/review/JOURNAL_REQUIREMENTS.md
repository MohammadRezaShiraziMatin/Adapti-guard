# Journal requirements check (read 2026-10-16, Tehran)

## Target: Computers & Security (Elsevier, ISSN 0167-4048)
Official page read: https://www.sciencedirect.com/journal/computers-and-security/publish/guide-for-authors

| Requirement | What the official page says | Status for our manuscript |
|---|---|---|
| **Scope** | "As of early 2024, we have instituted a moratorium on consideration of submissions that feature AI or ML as significant components … items directed to the security of AI/ML systems themselves (such as LLM and federated learning) are out of scope of the journal and should be submitted to a venue primarily about AI/ML." | **BLOCKER — not met.** The paper is about measuring prompt-injection defenses for LLM agents, i.e. the security of LLM systems. As written, it falls under the moratorium. Do not submit without written confirmation from the editors that the moratorium has been lifted or does not apply. |
| Article type | Not stated on the guide page. | unverified |
| Length | "no longer than 12k words … includes Abstract, Main text, References and any Appendices" | Met (submission copy is below 12k words; see below). |
| Abstract | "does not exceed 250 words"; stand-alone; avoid references (cite author and year if essential); define abbreviations | Met in MANUSCRIPT_SUBMISSION.md (word count reported there). |
| Keywords | "5 to 10 keywords"; English; avoid multi-word with "and"/"of" | Met (7). |
| Highlights | Encouraged; separate editable file with "highlights" in the file name; 3–5 bullets, each ≤85 characters incl. spaces | Prepared as `HIGHLIGHTS.md` (4 bullets, all ≤85 characters); must be uploaded as a separate .docx. |
| File format | .doc/.docx or .tex; PDF not accepted as source; single column for Word | **Not met yet:** files are Markdown. Conversion (e.g. pandoc to .docx) is needed. |
| Title page | names, affiliations with postal address and country, corresponding author's e-mail | **Not met:** [PLACEHOLDER author/affiliation/e-mail]. |
| Sections | numbered sections 1, 1.1, …; abstract not numbered; appendices A, B with Table A.1 etc. | Met in structure; appendix table numbering to be applied at formatting. |
| Reference style | No strict format at submission ("any style … as long as consistent"); author–year in text recommended; preprints marked as preprint with DOI | **Partly met:** in-text uses arXiv ids, not author–year; the reference list carries arXiv ids, but DOIs and full author lists are not yet added. |
| Data | Option C: deposit data in a repository, cite and link it, or explain why not; a data statement is required | Data statement drafted; **repository deposit and DOI [PLACEHOLDER]** (release.zip is prepared, not deposited). |
| Generative AI | Declare at submission in a section before the references titled "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process"; AI must not be an author; authors are responsible for verification | Drafted. Note: the policy says AI tools must "never be used as a substitute for human critical thinking". Our AI did the analysis and labelling, so the human-verification statement must be true before submission (owner review [PLACEHOLDER]). |
| Competing interests | The declarations tool is required (.docx upload) | Statement drafted; tool form [PLACEHOLDER]. |
| Funding | Standard sentence if none | Drafted ("did not receive any specific grant…"); owner to confirm. |
| CRediT | Required from the corresponding author | Drafted with [PLACEHOLDER] for author names. |
| Vitae | max 100 words per author plus photo | [PLACEHOLDER] |
| Preprint | Allowed ("will not count as prior publication"); optional SSRN posting | OK; the project rule (issue to maintainers before any preprint) still applies. |
| Review model | single anonymized | No anonymisation needed. |

## Fallback: Transactions on Machine Learning Research (TMLR)
Official pages read: https://jmlr.org/tmlr/author-guide.html; https://jmlr.org/tmlr/editorial-policies.html

| Requirement | Official text (summary) | Status |
|---|---|---|
| Scope | includes "formalization of new learning tasks … and of methods for assessing performance on those tasks" and "reproducibility studies of previously published results or claims" | Plausible fit (evaluation-methodology re-analysis of released benchmark runs). Editor judgement applies. |
| Review | open, **double-blind**; anonymised submission on OpenReview; all authors need OpenReview profiles | **Not met:** the manuscript names the owner, the repo paths and the assistant; an anonymised copy is needed. |
| Format | "any length"; PDF from the TMLR LaTeX template; supplementary ≤100 MB PDF/ZIP, anonymised | **Not met:** LaTeX conversion needed; release.zip must be anonymised (it contains no names after the scan, see release report, but paths and commit links must be checked). |
| Broader impact | required if significant risk of harm | Optional here; an Ethics section exists. |
| LLM policy | LLMs allowed as assistive tools; authors fully responsible; LLMs not authors | Compatible with the disclosure; heavy AI-generated content will be "closely examined". |
| Originality | no reuse of text or results from archival venues; arXiv is OK | OK (nothing published). |
| Fees | none | — |
| Abstract and keyword limits | not stated on the pages read | unverified |
| Quota | Generalized Harmonic Quota Rule per author | check at submission |

## Recommendation
- Computers & Security's stated AI/ML moratorium makes it an unsuitable target as the guide currently reads.
- The submission files below are formatted to C&S limits as requested, and also fit TMLR apart from anonymisation and LaTeX.
- Decision needed from Matin: confirm C&S scope with the editor (no message has been sent), or switch to the fallback.
