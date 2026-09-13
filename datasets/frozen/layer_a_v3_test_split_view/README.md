# Layer A v3 frozen TEST split — runner view

This directory is a **read-only evaluation view** of
`datasets/frozen/layer_a_v3/test_split.jsonl`.

`test.jsonl` and `dataset.jsonl` are byte-identical to `test_split.jsonl`.

Use this path as `--benchmark-dir` for REAL_LLM_EVAL so `attack_n=40` /
`benign_n=40` loads the frozen TEST split exactly (no resample from train/dev).

Do not treat this as a new pack version. Pack identity remains `layer_a_v3.0`.
