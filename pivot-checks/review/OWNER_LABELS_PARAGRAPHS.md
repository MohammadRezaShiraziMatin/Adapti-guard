# Owner-label paragraphs (choose one before submission)

## (a) Default: owner labels arrive
Run `python3 review/owner_agreement.py` after `review/owner_labels.jsonl` is filled. Do not fill the brackets by hand; copy them from `review/owner_agreement.json`.

> **Human check of the AI reviewer.** The owner, blind to the AI reviewer's labels and the key, independently labelled a 16-item subset of the disagreement and control items (`review/owner_subset_ids.json`). Owner and AI reviewer agreed on [PLACEHOLDER: agree]/16 items ([PLACEHOLDER: raw_pct]%; Wilson 95% CI [PLACEHOLDER: wilson95]), Cohen's κ = [PLACEHOLDER: cohen_kappa]. Disagreements: [PLACEHOLDER: list from disagreements]. With 16 items this is a coarse check and does not replace an independent second rater on the full set.

## (b) Alternative: no human check
> **No human check of the manual labels.** All manual labels in this paper (53 disagreement and control items, 60 recall items, 113 scorer-validation items) were produced by a single AI reviewer, the same AI agent that designed the analyses. No human labelled any item, and no inter-rater agreement is available. The checker-precision, recall and scorer-validation figures should be read with this in mind. An independent human re-labelling of the blind packets (`review/BLIND_PACKET_ALL.md`, `review/RECALL_PACKET.md`) is the most important missing check.
