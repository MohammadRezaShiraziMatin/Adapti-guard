# Configs snapshot (eval contract at FAIL)

Snapshot of committed YAML used by Layer A intervention and the official VNEXT confirmation. **Do not treat this as a live-eval authorization.** Secrets never live in these files.

Recompute:

```bash
sha256sum configs/models.yaml configs/datasets.yaml configs/models_local.yaml \
  configs/experiments/ablation_study.yaml configs/experiments/long_term_adaptation.yaml
```

---

## Binding eval-contract keys (`configs/models.yaml`)

SHA-256 `3e7b33d8b1001f0f86abf74b4d8c1558751275835c10a69152f1f7b386cc58b4`

| Key | Required value | Observed on this tree |
| --- | --- | --- |
| `models.target_2.model` | `qwen/qwen-2.5-7b-instruct` | yes |
| `models.target_2.provider` | `openrouter` | yes |
| `models.target_2.temperature` | `0.0` | yes |
| `models.judge_fallback.model` | `qwen/qwen-2.5-72b-instruct` | yes |
| `models.judge_fallback.provider` | `openrouter` | yes |
| Target ≠ Judge | required | yes |
| `cache.enabled` | `false` | yes |
| `cache.directory` | `.llm_cache` | yes |

Official VNEXT run (`experiments/real_llm_eval/VNEXT_CONFIRM/20260914-133147/manifest.json`): `target_config_key=target_2`, `judge_config_key=judge_fallback`, `cache_enabled=false`, `seed=42`.

API keys come from `OPENROUTER_API_KEY` in the environment. They are not in git. Offline checks must not call OpenRouter.

---

## Other committed configs (not the confirmatory contract)

These files exist in the repo. They did **not** select the VNEXT Target/Judge pair.

| Path | SHA-256 | Role |
| --- | --- | --- |
| `configs/datasets.yaml` | `fd005720c44f7786a93202536bea4d5eb336d6c25ad313d156df402f7b5acaca` | Dataset path registry |
| `configs/models_local.yaml` | `cfcd748388a7ae771cf9c951d74211364c673262f06f633a0ace1a0de0ba5126` | Local/dev model aliases |
| `configs/experiments/ablation_study.yaml` | `80791f5122bdfa8ae6b7b177d1f2de043255de8a261a75941e3f0ee418eaf0c5` | Historical ablation YAML |
| `configs/experiments/long_term_adaptation.yaml` | `96c36db643192e6261ccfe702b4d5c2d610463be8063ffb9f370aa8e91080da5` | Historical long-run YAML |
| `configs/evaluation/README.md` | (markdown pointer) | Points at `docs/STATISTICAL_PROTOCOL.md` |

---

## What a reader should not do with this snapshot

- Do not enable `cache.enabled` and re-score the locked pack.
- Do not swap Target/Judge to “improve” ASR.
- Do not copy `judge_primary` (Groq) over `judge_fallback` for a new unofficial confirmation.
- Do not treat `configs/experiments/*.yaml` as the VNEXT protocol.
