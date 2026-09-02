# EXP-004 — BLOCKED

## Status: EXP-004 NOT COMPLETE

Full EXP-004 was **not launched** because Phase 2.7 pilot failed the go/no-go gate.

## Blocker

OpenRouter **HTTP 402** — insufficient in-flight credit budget for judge API calls (`anthropic/claude-sonnet-4`).

Estimated full run requires **~6,000 API calls** (500 episodes × 2 baselines × 3 models × target+judge). Current account cannot sustain even the 30-call pilot without judge failures.

## Infrastructure prepared (ready when API budget available)

| Component | Path |
|-----------|------|
| Frozen eval loader | `src/adapti_guard/evaluation/attack_success.py` |
| Phase 2.7 pilot | `experiments/PHASE2_7_PILOT/run.py` |
| EXP-004 runner | `experiments/EXP-004/run.py` |
| Analysis | `experiments/EXP-004/analyze.py` |
| API budget doc | `experiments/EXP-004/README.md` |

## Command to run when unblocked

```bash
python experiments/PHASE2_7_PILOT/run.py          # must PASS first
python experiments/EXP-004/run.py --skip-existing  # n=500, 3 models, B0/B6
python experiments/EXP-004/analyze.py
```

## Dataset integrity

- SHA-256: `27b1733cb6678e6144687b60387b564bd248c89871042eef0ffb0e2ce4c54c24` — verified unchanged
- benchmark_q1: UNCHANGED

## No fabricated data

No EXP-004 metrics, ASR tables, or statistical significance claims are reported.
