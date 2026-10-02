# Prompt for an independent reviewer (for example Cursor), clean-clone reproduction

Task: verify, without trusting the authors' claims, that the negative-result manuscript reproduces from the repository.
1. Clone `MohammadRezaShiraziMatin/adapti-guard`, branch `claude/analysis-5vlrfi`, into an empty directory. Do not reuse any local state.
2. Create a Python 3.12 virtual environment and install the package (`pip install -e ".[dev]"`, plus `matplotlib`).
3. Run `PYTHON=python scripts/reproduce_negative_result.sh` (it needs no network or API key; the InjecAgent steps are skipped if the external checkout is absent, which is expected).
4. Report: which steps pass, any error or missing file, whether `git status` is clean afterwards (generated files should be byte-identical), and whether every number in `docs/paper/negative_result/NUMBERS_LEDGER.md`
   matches the artifact it cites.
5. Independently re-derive three numbers by hand from the committed traces (suggested: Track A b10/b01 = 5/0; InjecAgent llama-3.1-8b A0 50/120; the cluster-bootstrap interval for the same model) and say whether they agree.
6. Adversarial pass: list claims in `MANUSCRIPT_DRAFT_v1.md` sections 6.6 and 9 that the data do not support, and any place where per-model results are pooled.
Deliver a written report; do not edit the repository.
