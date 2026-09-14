# Phase 1 core defense audit (offline)

**Scope.** Architectural quality of Detection → Risk → Policy → Enforcement.  
**Not in scope.** Multi-turn, multi-agent, new benchmarks, live LLM, VNEXT re-score, MSID/pack edits.

**API.** LLM/API calls = **0**. Frozen packs and official VNEXT FAIL numbers are not modified.

Canonical FAIL (unchanged, not re-interpreted here): pack SHA-256 `523c881820710783b5290c76ea5fe5fc01a6341fb427defcba1119fc3e721518`; qualified win **NO**.

---

## 1. Current architecture

Two runtimes exist.

| Path | Entry | Detector | Risk | Policy | Enforcement |
| --- | --- | --- | --- | --- | --- |
| Legacy MVP | `AdaptiGuard.run` (`runtime.py`) | regex v3 `PromptInjectionDetector` | `RiskEngine` (can use `attack_type` metadata) | `DefensePolicyEngine` | `DefenseActionLayer` only (no tool loop) |
| Eval / VNEXT | `evaluate_episode` + `AdaptiveDefenseState` | v4 `detect_episode(prompt, context)` for B3_V4 | `RiskEngineV4` (p → LOW/MED/HIGH) | `DefensePolicyEngine` | Action layer **then** `tool_loop.run_tool_turn` |

Traced eval path:

```
record.prompt/context
  → defense_fn (detect → risk → policy.decide(tool_sensitive=False) → action_layer)
  → (action, blocked, defended_prompt)
  → Target generate unless A3
  → extract_tool_request (model JSON, TOOL_REQUEST text, or record.tool_call)
  → run_tool_turn (A2/A3 deny; A0/A1 execute)
  → Judge / taxonomy (refusals ≠ defense wins)
```

Components (keep unless a causal break is shown):

- Detector v4: `src/adapti_guard/detector/prompt_injection_detector_v4.py`
- Risk v4: `src/adapti_guard/risk/risk_engine_v4.py`
- Policy: `src/adapti_guard/policy/policy_engine.py`
- Action semantics: `src/adapti_guard/defense/action_layer.py`
- Tool permission: `src/adapti_guard/defense/tool_loop.py`
- Scoring/taxonomy: `src/adapti_guard/evaluation/attack_success.py`
- Adaptive state: `src/adapti_guard/experiments/defense_baselines.py` (`AdaptiveDefenseState`)

---

## 2. Strengths

- Policy is already a separate module from the detector.
- A0–A3 have distinct `DefenseActionLayer` semantics (allow / sanitize / `tool_access=False` / block).
- `tool_loop` already denies tools **outside prompt text** for A2 and skips execution for A3.
- Adaptive B3/B3_V4 strips gold `is_attack` / `label` / `category` kwargs (`_LEAKED_GOLD_KWARGS`).
- `classify_episode` already separates `target_refusal` from `correct_block` / `correct_tool_deny`.
- A3 in `evaluate_episode` skips the Target (`blocked_by_defense`).

---

## 3. Weaknesses (evidence)

1. **A1 bottleneck (known).** `DefensePolicyEngine` maps MEDIUM + `defense_level` ∈ {0,1} → A1. A1 sanitizes text, keeps `tool_access=True`, and still calls the Target. A1 is **not** in \(\mathcal{W}\). Official VNEXT action mix was A1 × 114 vs A3 × 6 / A2 × 2 (`AUDIT.md`). This Phase 1 audit does not treat that mix as a new result.

2. **`tool_sensitive=False` is hardcoded** on every eval factory (`AdaptiveDefenseState.evaluate`, `make_b2_fixed_defense`, `make_b2_fixed_defense_v4`). Policy already maps MEDIUM+`tool_sensitive` → A2, but that input never arrives. Declared `tool_call` on episodes (observable) is unused at decision time.

3. **LOW + `tool_sensitive` → A2** in historical policy. Wiring privilege blindly would deny benign `send_email` / `create_record`. That is why the eval path froze `tool_sensitive=False` (utility), which then stranded tool attacks on A1.

4. **Thin `DefenseFn`.** Return is `(action, blocked, prompt)` only. Risk level, policy reason, and tool permission are not a first-class trace on the defense object.

5. **No context builder.** Prompt and context are concatenated ad hoc. Tool name / tool output are not first-class detector/risk inputs.

6. **Risk v4 ignores action sensitivity.** Intentional for Layer A freeze; it is still a causal gap for a tool-aware pipeline.

7. **Legacy `AdaptiGuard.run` infers `attack_present` from the detector** and has no `tool_loop`. Circular outcome, not label-blind scoring.

8. **A1 cannot change tool outcome.** By design: sanitization ≠ permission. Fixing the bottleneck requires **policy to select A2 when privilege evidence exists**, not pretending A1 is a tool deny.

---

## 4. Causal breaks

| Break | Where | Effect |
| --- | --- | --- |
| Privilege never reaches policy | `tool_sensitive=False` | MEDIUM tool attacks stay on A1 |
| Decision vs enforcement split undocumented | `DefenseResult.tool_access` vs `run_tool_turn(action)` | Works if action string matches; no shared gate object |
| Detector does not see tool output as a channel | `detect_episode(prompt, context)` only | Tool-output injection evidence unused unless concatenated into context |
| Outcome uses detector as gold (MVP) | `runtime.py` `is_injection` | Not a valid confirmatory score |
| Trace incomplete | `defense_fn` has only `last_detector_hit` | Cannot audit risk/policy/tool fields per episode |

Do **not** rewrite `DefensePolicyEngine` defaults: Layer A / VNEXT-ADAPT must keep historical mapping. Do **not** change `RiskEngineV4` bands (0.25 / 0.60).

---

## 5. Recommended changes (Phase 1 only)

1. Add a **ContextBuilder** + `EpisodeInput` (prompt, context, optional tool name/args/output). No gold labels.
2. Add **`CoreDefensePipeline`**: detector v4 → `RiskEngineCore` (p bands + observable privilege features) → **new inspectable core policy table** → action layer → **ToolPermissionGate** (`run_tool_turn`).
3. Core policy (new table, not a silent edit of historical `decide`):
   - LOW + privileged tool → **A0** (benign workflow)
   - MEDIUM + privileged tool → **A2** (closes Detection→A1→tools-still-run)
   - HIGH, no privileged tool → **A3**
   - HIGH + privileged tool → **A2** (action-level deny)
   - MEDIUM, no tool → A1 at level 0–1 (remaining text-only limitation; do not retune to chase VNEXT)
4. Optional detector kwargs `tool_name` / `tool_output` that **do not change** prompt-only v4 scores.
5. Persist `last_trace` into `evaluate_episode` metadata when present.
6. Keep `make_b3_adaptive_v4` / VNEXT-ADAPT **byte-behavior** (still `tool_sensitive=False`). New factory `PHASE1-CORE` only.
7. Deterministic tests for label blindness, A0–A3 causal effects, traces. Offline architectural counts on frozen JSONL **read-only**; not a security-performance claim.

---

## 6. Files affected (planned)

| File | Role |
| --- | --- |
| `src/adapti_guard/core/episode.py` | `EpisodeInput`, `ContextBuilder`, `EpisodeTrace` |
| `src/adapti_guard/core/core_pipeline.py` | Phase 1 pipeline |
| `src/adapti_guard/policy/core_policy.py` | Inspectable A0–A3 table |
| `src/adapti_guard/risk/risk_engine_core.py` | Label-blind risk + privilege features |
| `src/adapti_guard/defense/tool_permission.py` | Explicit gate over `tool_loop` |
| `src/adapti_guard/detector/prompt_injection_detector_v4.py` | Optional tool channels; default path unchanged |
| `src/adapti_guard/experiments/defense_baselines.py` | `make_core_defense` only |
| `src/adapti_guard/evaluation/attack_success.py` | Attach `last_trace` |
| `tests/test_phase1_core_pipeline.py` | Causal tests |
| `scripts/run_phase1_core_offline_eval.py` | Read-only architectural checks |

Unchanged on purpose: frozen JSONL, VNEXT protocol/MSID, AUDIT folders, `RiskEngineV4` thresholds, historical `DefensePolicyEngine.decide`, `make_b3_adaptive_v4`.

---

## 7. Tests required

- Label-blind: gold kwargs do not change core decisions
- Detector prompt-only scores unchanged when tool kwargs omitted
- Risk never reads `is_attack` / `label` / `category`
- Policy table: A0 / A1 / A2 / A3 as specified
- A2: `send_email` not executed; registry empty
- A3: no tool execution; blocked
- A1: tools still execute (honest A1 semantics)
- Benign `search` / LOW privileged tool: allowed
- Trace fields complete
- Scorer: `target_refusal` ≠ `correct_block`
- Frozen SHA-256 still matches lock

---

## 8. Non-claims

This audit does not claim a defense win, SOTA, production-ready system, or that Phase 1 would reverse VNEXT FAIL. It identifies a missing causal input (`privilege` → policy) and incomplete traces.

---

## Continuation failure matrix (diagnostic)

See [`PHASE1_FINAL_QUALITY_GATE.md`](PHASE1_FINAL_QUALITY_GATE.md). Summary: primary blind spot was evidence without primary_control (forced markers / weak tool patterns). Phase1 evidence detector addresses this without retuning VNEXT-ADAPT/`evidence_v4.0`. Residual: l33t/Morse/reverse/subtle social-engineering.
