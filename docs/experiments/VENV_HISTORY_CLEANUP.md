# Git history cleanup: remove `.venv_phase5` (STAGE ONLY)

**Do not run these commands from a cloud agent or as an automated PR merge.**
This document stages a **human-local** history rewrite. Rewriting shared git history is irreversible for collaborators and invalidates every existing commit SHA (and open PR tips that point at those SHAs).

## Why

`.venv_phase5/` was committed historically (e.g. commit `022d542` added `.venv_phase5/bin/*` and site-packages). It is gitignored now (`.venv/`, `.venv_*/` in `.gitignore`) and untracked in the working tree, but **blobs remain in git history**. Evidence:

```bash
git log --all --diff-filter=A --summary -- '.venv_phase5' | head
git rev-list --objects --all | grep '\.venv_phase5' | head
```

## Pre-flight checklist (human)

Complete **all** boxes before rewriting:

- [ ] Every open PR that must survive has been **merged or closed**; remaining tips do not need old SHAs (see [`PR_TRIAGE.md`](PR_TRIAGE.md)).
- [ ] Collaborators are notified: after rewrite everyone needs a **fresh clone** (or hard reset to new history) — no `git pull` on old remotes.
- [ ] Confirm `.venv_phase5` is **not** referenced as a required path by active scripts/docs (search below). Historical mentions in `docs/archive/` and run logs are OK.
- [ ] You have a full backup remote or bundle of the pre-rewrite tip.
- [ ] `git filter-repo` (or BFG) is installed locally; you are on a throwaway cleanup branch first if desired.
- [ ] You accept force-push to the default branch / all rewritten refs will be required.

### Active-path reference check (run before rewrite)

```bash
# Should return only archive / historical / gitignore mentions — not runtime requirements
rg -n '\.venv_phase5' -g '!.git/**' -g '!docs/archive/**' -g '!experiments/runs/**'
```

As of the portfolio-hygiene branch, active references are documentation/history notes and `.gitignore` patterns only (no script imports `.venv_phase5`).

## Recommended command (`git filter-repo`)

```bash
# Fresh clone recommended
git clone https://github.com/MohammadRezaShiraziMatin/adapti-guard.git adapti-guard-venv-clean
cd adapti-guard-venv-clean

# Remove path from all history
git filter-repo --path .venv_phase5 --invert-paths

# Verify
git rev-list --objects --all | grep '\.venv_phase5' && echo FAIL || echo CLEAN

# Force-push all rewritten refs (HUMAN ONLY — destructive)
git remote add origin https://github.com/MohammadRezaShiraziMatin/adapti-guard.git
git push --force --all origin
git push --force --tags origin
```

## BFG alternative

```bash
# After installing BFG
java -jar bfg.jar --delete-folders .venv_phase5 adapti-guard.git
cd adapti-guard.git
git reflog expire --expire=now --all && git gc --prune=now --aggressive
# then force-push as above
```

## Aftercare

1. Invalidate old PR branches that pointed at pre-rewrite SHAs; re-open only what still matters.
2. Ask every collaborator to delete local clones and re-clone.
3. Re-run CI on the new tip (`pytest` workflow).
4. Record the rewrite date and pre-rewrite tip SHA in `docs/experiments/RESEARCH_LOG.md`.

## Explicit non-goals for agents

- Agents **must not** run `git filter-repo`, BFG, or `git push --force` as part of this close-out.
- Agents **must not** push to `main`.
