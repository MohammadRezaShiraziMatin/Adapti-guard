"""E6 offline defense replay: a DIAGNOSTIC, never a gate (offline; no API; reads traces or pack text only).

B3 and PHASE1-CORE are pre-target filters: the harness calls `defense_fn(text, None) -> (action, blocked, content)` once for
every user and tool message it appends and never shows the defense a model output. The model-visible text is therefore a
deterministic function of the scripted messages, so replay can say whether a defended arm presents the model with
byte-identical input to A0. It cannot say whether a changed input changes behavior, and it decides nothing about the run.

Reported per defense, family and instance: byte difference of every user/tool message from the A0 text, the block flag and
the action level of every message. The ambiguous "intervened" metric of the 2026-09-30 replay script (detector hit OR block
OR change) is deliberately not used. `consistency` compares replay predictions with the live defended traces.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from typing import Callable

DefenseFn = Callable[[str, "str | None"], tuple]
Factory = Callable[[], DefenseFn]


def model_visible(ep: dict) -> list[dict]:
    """User and tool messages in delivery order, as the model saw them (post-defense for defended arms)."""
    return [m for m in ep.get("final_messages") or [] if m.get("role") in ("user", "tool")]


def replay_texts(make_defense: Factory, texts: list[tuple]) -> list[dict]:
    """Run (role, text[, carries_attack]) units through a fresh defense in delivery order.

    `carrier` marks the attacker-controlled message (the one that carries the injection); everything else is non-carrier.
    """
    fn = make_defense()
    out = []
    for ordinal, unit in enumerate(texts, start=1):
        role, text = unit[0], unit[1]
        carries = bool(unit[2]) if len(unit) > 2 else False
        action, blocked, content = fn(text, None)
        shown = "" if blocked else content
        out.append({"ordinal": ordinal, "role": role, "carrier": carries, "action": str(action), "blocked": bool(blocked),
                    "byte_changed": shown != text, "predicted": shown})
    return out


def diagnostic_rows(units_by_instance: dict, factories: dict[str, Factory]) -> list[dict]:
    """units_by_instance: {(family, instance): [(role, text), ...]} from the frozen pack; one row per message."""
    rows = []
    for defense, factory in sorted(factories.items()):
        for key, units in sorted(units_by_instance.items()):
            family, instance = key[0], key[1]
            for r in replay_texts(factory, units):
                rows.append({"defense": defense, "family": family, "instance": instance, "ordinal": r["ordinal"],
                             "role": r["role"], "carrier": r["carrier"], "action": r["action"], "blocked": r["blocked"],
                             "byte_changed": r["byte_changed"]})
    return rows


def units_from_rendered(rendered: dict, executor_factory, control: bool = False) -> dict:
    """Replay units {(family_id, instance): [(role, text, carries_attack)]} from the rendered artifact.

    The tool message is what the harness's own mock executor returns for the *expected* carrier call (`executor_factory(scenario_id,
    record)` is supplied by the launcher and wraps the harness's `ScenarioMockToolExecutor`; no executor format is duplicated here).
    Whether a live model actually made that call is checked after the run by `carrier_call_consistency`.
    """
    arg = {"retrieve_document": "doc_id", "get_weather": "city"}
    out = {}
    for sid, b in sorted(rendered["scenarios"].items()):
        if (b["kind"] == "control") != control:
            continue
        for rec in b["instances"]:
            tool = executor_factory(sid, rec).execute(name=rec["prerequisite_tool"], arguments={arg[rec["prerequisite_tool"]]: rec["prerequisite_arg"]})
            out[(b["family_id"], rec["instance_index"])] = [("user", rec["user_prompt"], False), ("tool", tool, not control)]
    return out


def carrier_call_consistency(rows: list[dict], rendered: dict) -> dict:
    """Post-run diagnostic: did each live episode make the carrier call the replay assumed, and how many carrier messages did it get?"""
    arg = {"retrieve_document": "doc_id", "get_weather": "city"}
    rec = {(sid, r["instance_index"]): (b, r) for sid, b in rendered["scenarios"].items() for r in b["instances"]}
    n = Counter()
    carriers = Counter()
    odd: list[str] = []
    for ep in rows:
        hit = rec.get((ep.get("scenario_id"), ep.get("instance_index")))
        if hit is None or not isinstance(ep.get("mock_tool_log"), list):
            n["unmatched_or_no_log"] += 1
            continue
        _, r = hit
        tool, key = r["prerequisite_tool"], arg[r["prerequisite_tool"]]
        calls = [c for c in ep["mock_tool_log"] if c.get("name") == tool]
        expected = any((c.get("arguments") or {}).get(key) == r["prerequisite_arg"] for c in calls)
        shown = sum(1 for m in ep.get("final_messages") or [] if m.get("role") == "tool" and r["marker"] in (m.get("content") or ""))
        n["episodes"] += 1
        n["called_carrier_tool"] += bool(calls)
        n["called_with_expected_arg"] += expected
        carriers[shown] += 1
        if not expected and len(odd) < 5:
            odd.append(ep.get("episode_id", ""))
    return {**dict(n), "carrier_messages_per_episode": dict(sorted(carriers.items())), "episodes_without_expected_call": odd}


def replay_sha256(rows: list[dict]) -> str:
    return hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def summarize(rows: list[dict]) -> dict:
    out: dict = {}
    for defense in sorted({r["defense"] for r in rows}):
        sub = [r for r in rows if r["defense"] == defense]
        car = [r for r in sub if r["carrier"]]
        non = [r for r in sub if not r["carrier"]]
        fam_car: dict = defaultdict(int)
        for r in car:
            fam_car[r["family"]] += bool(r["byte_changed"] or r["blocked"])
        out[defense] = {"messages": len(sub), "blocked": sum(r["blocked"] for r in sub),
                        "actions": dict(Counter(r["action"] for r in sub)),
                        "carrier_messages": len(car), "carrier_byte_changed": sum(r["byte_changed"] for r in car),
                        "carrier_blocked": sum(r["blocked"] for r in car),
                        "non_carrier_messages": len(non), "non_carrier_byte_changed": sum(r["byte_changed"] for r in non),
                        "families": len({r["family"] for r in sub}),
                        "families_with_carrier_change_or_block": sum(v > 0 for v in fam_car.values())}
    return out


def consistency(a0_rows: list[dict], defended_rows: list[dict], make_defense: Factory,
                key=lambda r: (r["scenario_id"], r["instance_index"], r["model_id"])) -> dict:
    """Compare replay of the A0 messages with the live defended trace, message by message (aligned by user/tool ordinal).

    A message is comparable only if the live defended episode has a user/tool message at that ordinal; texts that the live
    arm received can differ from A0's when the model chose different calls, which shows up as `unaligned`.
    """
    A = {key(r): r for r in a0_rows}
    n = Counter()
    mism: list[dict] = []
    for d in defended_rows:
        a = A.get(key(d))
        if a is None:
            n["no_a0_pair"] += 1
            continue
        a_msgs, d_msgs = model_visible(a), model_visible(d)
        log = {e.get("message_index"): e for e in (d.get("b3_log") or [])}
        dmsgs_all = d.get("final_messages") or []
        pred = replay_texts(make_defense, [(m["role"], m.get("content") or "") for m in a_msgs])
        for k, p in enumerate(pred):
            if k >= len(d_msgs):
                n["unaligned"] += 1
                continue
            live = d_msgs[k]
            if live["role"] != p["role"]:
                n["unaligned"] += 1
                continue
            a_text = a_msgs[k].get("content") or ""
            live_text = live.get("content") or ""
            predicted_pass_through = p["predicted"] == a_text and not p["blocked"]
            if live_text != a_text and predicted_pass_through:
                n["input_diverged"] += 1  # the live arm received different input than A0 (e.g. another document); replay cannot judge it
                continue
            idx = next((i for i, m in enumerate(dmsgs_all) if m is live), None)
            e = log.get(idx)
            n["comparable"] += 1
            same_text = live_text == p["predicted"]
            same_block = e is not None and bool(e.get("blocked")) == p["blocked"]
            same_action = e is not None and str(e.get("defense_action")) == p["action"]
            n["text_equal"] += same_text
            n["block_equal"] += same_block
            n["action_equal"] += same_action
            if not (same_text and same_block and same_action) and len(mism) < 5:
                mism.append({"episode_id": d.get("episode_id"), "ordinal": k + 1, "role": p["role"], "predicted_action": p["action"],
                             "live_action": None if e is None else e.get("defense_action"), "text_equal": same_text})
    n["episodes"] = len(defended_rows)
    return {**dict(n), "mismatch_examples": mism}
