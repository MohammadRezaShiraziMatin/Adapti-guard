# Decisions the owner must make before posting to arXiv

arXiv postings are public and permanent: a withdrawn version stays visible and cannot be deleted.

1. **Author block.** Name, affiliation and email are placeholders in `main.tex` (set in `scripts/build_arxiv_latex.py`, then regenerate). Decide whether an AI assistant is acknowledged; the manuscript (§10) states it is not an author. arXiv policy also requires that authors take responsibility for the content.
2. **Endorsement and category.** Confirm the category (suggestion: cs.CR, cross-list cs.LG/cs.AI). New submitters may need an endorser.
3. **License.** Choose at submission time: arXiv perpetual non-exclusive license, CC BY 4.0, or CC BY-NC-SA etc. This is hard to change later for posted versions. The repository code license (`LICENSE`) is separate.
4. **Attack-template release policy.** §10 says the attack templates (notably the authority-claim family) are retrievable by commit SHA and that the live harness is only in unreachable commits. The paper cites the SHAs (`bea82347`, `e5135a6`, `1ae0fb4d`, `dfbea801`), so posting makes them easier to find. Decide whether to keep as is, rewrite the history, or publish the templates deliberately with a responsible-disclosure note. The manuscript must stay consistent with whatever is chosen.
5. **Venue conflicts.** Check the target venue's preprint policy and anonymity rules before posting (arXiv is not blind). Open earlier decisions: venue and an anonymized version are still undecided.
6. **Pre-registration wording.** The paper states the external protocol was drafted locally and not externally registered. Confirm you are comfortable with the exact wording being public.
7. **Supplement scope.** Confirm which repository files accompany the preprint; the four internal audit/roadmap/skeleton files are excluded.
8. **Final read of the PDF** (figures, tables, the author block) and a decision on whether to do the optional table/landscape polish first.
