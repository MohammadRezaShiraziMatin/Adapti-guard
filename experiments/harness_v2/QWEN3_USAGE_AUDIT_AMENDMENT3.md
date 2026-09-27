# Qwen3 token accounting audit (Amendment 3, zero API)

Source run: `experiments/harness_v2/HARNESS_V2_SMOKE3_20260927-131707/trajectories.json` (family `qwen3`).

## Conclusion (read first)

**Not a local parsing bug.** OpenRouter returns `usage.completion_tokens` and `usage.completion_tokens_details.reasoning_tokens` as separate fields; for Qwen3, **`reasoning_tokens` can exceed `completion_tokens`** because `total_tokens` (= prompt + completion_tokens) **does not include** reasoning tokens in the billed total shown (e.g. prompt 436 + completion 522 = total 958 while reasoning_tokens=605).

Our parser (`_openrouter_usage_dict`, `target_model.py:100-121`) copies `reasoning_tokens` from `completion_tokens_details` without altering counts.

**`include_reasoning: false` is not sent** on harness v2 requests. `openrouter_tools_session.py` sets `extra_body` to DeepInfra provider pin only (no `include_reasoning`). The API **still returns** a populated `message.reasoning` field on responses — so exclusion is **not effective** on this path.

---

## HTTP 5 (episode round 1) — verbatim `usage` from `raw_response`

```json
{
  "completion_tokens": 522,
  "prompt_tokens": 436,
  "total_tokens": 958,
  "completion_tokens_details": {
    "audio_tokens": 0,
    "reasoning_tokens": 605,
    "image_tokens": 0
  },
  "prompt_tokens_details": {
    "audio_tokens": 0,
    "cache_write_tokens": 0,
    "cached_tokens": 0,
    "video_tokens": 0
  },
  "cost": 0.00031332,
  "is_byok": false,
  "cost_details": {
    "upstream_inference_cost": 0.00031332,
    "upstream_inference_prompt_cost": 5.232e-05,
    "upstream_inference_completions_cost": 0.000261
  }
}
```

## HTTP 6 — verbatim `usage`

```json
{
  "completion_tokens": 693,
  "prompt_tokens": 544,
  "total_tokens": 1237,
  "completion_tokens_details": {
    "audio_tokens": 0,
    "reasoning_tokens": 743,
    "image_tokens": 0
  },
  "prompt_tokens_details": {
    "audio_tokens": 0,
    "cache_write_tokens": 0,
    "cached_tokens": 0,
    "video_tokens": 0
  },
  "cost": 0.00041178,
  "is_byok": false,
  "cost_details": {
    "upstream_inference_cost": 0.00041178,
    "upstream_inference_prompt_cost": 6.528e-05,
    "upstream_inference_completions_cost": 0.0003465
  }
}
```

## HTTP 7 — verbatim `usage`

```json
{
  "completion_tokens": 357,
  "prompt_tokens": 658,
  "total_tokens": 1015,
  "completion_tokens_details": {
    "audio_tokens": 0,
    "reasoning_tokens": 412,
    "image_tokens": 0
  },
  "prompt_tokens_details": {
    "audio_tokens": 0,
    "cache_write_tokens": 0,
    "cached_tokens": 0,
    "video_tokens": 0
  },
  "cost": 0.00025746,
  "is_byok": false,
  "cost_details": {
    "upstream_inference_cost": 0.00025746,
    "upstream_inference_prompt_cost": 7.896e-05,
    "upstream_inference_completions_cost": 0.0001785
  }
}
```

---

## Request body shape (harness v2 — all models)

Built in `openrouter_tools_session.py` (`req_body`):

```python
{
  "model": "qwen/qwen3-30b-a3b",
  "messages": [...],
  "tools": HARNESS_V2_TOOLS,
  "tool_choice": "auto",
  "temperature": 0.0,
  "max_tokens": 2048,
  "extra_body": {
    "provider": {
      "order": ["DeepInfra"],
      "allow_fallbacks": False,
      "require_parameters": True
    }
  }
}
```

**No** `include_reasoning`, **no** `reasoning: {effort, exclude}` in harness v2 (contrast: `configs/models_q1_eval_panel.yaml` `q1_primary_qwen3_30b_a3b` sets `include_reasoning: false` for Step 0 target path only).

---

## Response `message.reasoning` present

Example: HTTP 5 `choices[0].message` includes key **`reasoning`** with long chain-of-thought text (truncated in logs); **`content`** holds visible/tool-call text. Same pattern on HTTP 6–7.

---

## Parsing code (local)

```100:121:src/adapti_guard/evaluation/target_model.py
def _openrouter_usage_dict(usage_obj: Any) -> dict[str, Any]:
    ...
    details = getattr(usage_obj, "completion_tokens_details", None)
    if details is not None:
        rt = getattr(details, "reasoning_tokens", None)
        if rt is not None:
            out["reasoning_tokens"] = int(rt)
```

No arithmetic combines reasoning into completion; values are passed through from provider JSON.
