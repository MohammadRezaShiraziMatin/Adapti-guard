# Live evaluation human sign-off (template)

**Status:** `PENDING` — **not** an approval. Do not commit as authorized.

**Gate:** [`LIVE_EVALUATION_GATE.md`](LIVE_EVALUATION_GATE.md) · **Budget contract:** [`live_budget_authorization.yaml`](live_budget_authorization.yaml) (template until replaced).

---

## Required approver role

Principal investigator or explicitly delegated budget owner for AdaptiGuard Q1 live evaluation (human only; agents may not sign).

---

## Checklist (copy from LIVE_EVALUATION_GATE.md)

All items must be checked before changing `approval_status` to `LIVE_AUTHORIZED`.

---

## Signature block (fill only at real approval)

```text
Approver name: PENDING_HUMAN_SIGNOFF
Approver role: PENDING_HUMAN_SIGNOFF
Date (UTC): PENDING_HUMAN_SIGNOFF
Explicit sentence (required): "I authorize live API spend under LIVE-EVAL-GATE-0.1 for the conditions listed in live_budget_authorization.yaml"
Repository commit (HEAD at approval): PENDING
```

---

## After approval (human workflow — not performed by agents)

1. Update `live_budget_authorization.yaml` with real values (no `PENDING_*` placeholders).
2. Set `approval_status: LIVE_AUTHORIZED`, `explicit_authorization_for_live_execution: true`, `api_live_execution_confirmed: true`.
3. Run `python3 scripts/validate_phase7_live_authorization.py` — must report `LIVE_AUTHORIZED` only if contract valid.
4. Optional lock file: `configs/p1_mechanism_l1_live_lock.json` per gate doc.

Until then: **NO LIVE CALLS · NO API SPEND**.
