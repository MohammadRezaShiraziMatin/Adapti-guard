# Step 0 harness analysis (zero API; code trace)

## Q1 target: tool declaration?

**Answer:** **No.** The P1 / Step 0 text-only path does **not** send a system prompt that lists tools, argument schemas, or call syntax, and does **not** use the OpenRouter `tools` / `tool_choice` API.

### Evidence (file:line)

| Claim | Location |
|-------|----------|
| Target request uses empty `system_prompt` unless caller sets it | `src/adapti_guard/evaluation/target_model.py:184-187` — system message omitted when `request.system_prompt` is falsy |
| Step 0 / P1 adapter builds **user-only** transcript (`role: content` lines + final `user:` line); no system message | `src/adapti_guard/evaluation/stateful_target_adapter.py:16-18` |
| Step 0 logging explicitly sets `system_prompt=""` | `scripts/run_step0_format_sample.py` (updated runner) `_logging_target_fn` |
| OpenRouter `create_kwargs` has `messages`, `temperature`, `max_tokens`, `extra_body` — **no** `tools` key unless added elsewhere | `src/adapti_guard/evaluation/target_model.py:193-200` |
| Privileged tool **names** exist for **defense** (`send_email`, `create_record`, `retrieve_document`) — not injected into target prompt | `src/adapti_guard/core/episode.py:16-17`, `ContextBuilder.privileged_tools` |
| Dataset `tools` / `tool_call` fields are for eval semantics, not wired into target `generate()` in this harness | `ContextBuilder.build` `src/adapti_guard/core/episode.py:55-88` |

### Exact target system prompt for `vnext_c1_atk_001`

**There is none.** `GenerationRequest.system_prompt` is `""`, so OpenRouter receives a **single user message** whose content is the multi-turn transcript built from the dataset anchor (prompt + context) and adaptive turns.

Example first-call user payload shape (conceptually):

```
user: <attack prompt>
<context lines if any>
user: <defended or raw turn prompt>
```

(Constructed in `stateful_target_adapter.py:17-18`.)

That explains gemma / llama replies such as “I do not have the capability to send emails” — generic assistant self-model, **not** a tool-capable agent system prompt.

## Qwen3 empty `message.content`

**Panel config:** `configs/models_q1_eval_panel.yaml` → `q1_primary_qwen3_30b_a3b` → `openrouter_extra_body.include_reasoning: false`.

**Request body sent (structure):**

```json
{
  "model": "qwen/qwen3-30b-a3b",
  "messages": [{"role": "user", "content": "<transcript>"}],
  "temperature": 0.0,
  "max_tokens": 512,
  "extra_body": {"include_reasoning": false}
}
```

Built in `OpenRouterTargetModel.generate` (`target_model.py:193-200`) with `openrouter_extra_body` from panel (`target_model.py:1137-1146`).

**Why content can still be empty:** Qwen3 on OpenRouter may emit reasoning in a separate field while `content` is empty (`_openrouter_assistant_text`, `target_model.py:83-97`). With `include_reasoning: false`, reasoning may be **stripped from the response**, leaving **both** `content` and visible reasoning empty → Step 0 slots 1/3/4 marked `TECH_ERROR: empty_target_content`. P1 diagnosis D5 same root cause.

**Not a missing “reasoning fix” on targets:** J1 judge has `reasoning.effort: none`; Qwen **target** panel only sets `include_reasoning: false`, not full `reasoning: {effort: none, exclude: true}`.
