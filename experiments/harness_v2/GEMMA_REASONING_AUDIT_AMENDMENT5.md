# Gemma reasoning_tokens audit (pilot 1 → Amendment 5)

Pilot 1 `cost_log.jsonl` used `int(usage.reasoning_tokens or 0)`, masking **null** as 0 while P2 analysis reads **both** `usage.reasoning_tokens` and `usage.completion_tokens_details.reasoning_tokens`.

## Finding

- When OpenRouter returns reasoning only under `completion_tokens_details`, P2 correctly flags `reasoning_tokens>0`.
- **Not a threshold relaxation:** reasoning-off request policy unchanged; extraction aligned in pilot 2 `cost_log` via `usage_tokens.reasoning_tokens_from_usage`.
- **Billing:** non-zero reasoning tokens appear in OpenRouter `usage.cost` / per-call `cost_usd` (billed as completion-side tokens when provider reports them).

## Samples (pilot 1)

```json
[
  {
    "episode_id": "indirect_retrieved_doc_v1/i0/gemma/A0",
    "call_index": 2,
    "reasoning_tokens": 2,
    "field_path": "usage.completion_tokens_details.reasoning_tokens",
    "completion_tokens": 26,
    "cost_usd": 6.162e-05,
    "usage_excerpt": {
      "prompt_tokens": 398,
      "completion_tokens": 26
    },
    "completion_tokens_details": {
      "audio_tokens": 0,
      "reasoning_tokens": 2,
      "image_tokens": 0
    }
  },
  {
    "episode_id": "indirect_retrieved_doc_v1/i0/gemma/B3",
    "call_index": 2,
    "reasoning_tokens": 2,
    "field_path": "usage.completion_tokens_details.reasoning_tokens",
    "completion_tokens": 33,
    "cost_usd": 6.35e-05,
    "usage_excerpt": {
      "prompt_tokens": 392,
      "completion_tokens": 33
    },
    "completion_tokens_details": {
      "audio_tokens": 0,
      "reasoning_tokens": 2,
      "image_tokens": 0
    }
  },
  {
    "episode_id": "indirect_retrieved_doc_v1/i1/gemma/A0",
    "call_index": 2,
    "reasoning_tokens": 2,
    "field_path": "usage.completion_tokens_details.reasoning_tokens",
    "completion_tokens": 26,
    "cost_usd": 6.162e-05,
    "usage_excerpt": {
      "prompt_tokens": 398,
      "completion_tokens": 26
    },
    "completion_tokens_details": {
      "audio_tokens": 0,
      "reasoning_tokens": 2,
      "image_tokens": 0
    }
  }
]
```
