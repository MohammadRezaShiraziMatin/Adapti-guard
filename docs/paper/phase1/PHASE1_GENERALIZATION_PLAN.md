# Phase 1 Generalization Plan

**ID:** `PHASE1-GEN-0.1`  
**Date (UTC):** 2026-09-14  
**Live runs:** Not executed in this hardening pass.

---

## What is claimed vs not

Phase-1 confirmatory TEST (`phase1_confirm_v1`) estimates effect on **one** locked single-turn distribution with mock tools.  
It does **not** demonstrate broad robustness across models, attack sources, or environments.

---

## Pre-registered secondary generalization axes (≥1 required)

| Axis | Design | Status |
| --- | --- | --- |
| **G1 Attack-source / wording** | Secondary offline detector+pipeline dry metrics on Layer A TEST text split (`47b975f7…`) without tool claims | Protocol ready; offline-only allowed pre-approval |
| **G2 Tool-environment** | Same confirm IDs with alternate mock tool-name aliases (pre-registered rename map) | Design only; not run |
| **G3 Model** | Same confirm protocol on a second target model after human live approval | Design only; not run |

Primary TEST is **not** weakened to manufacture G1–G3.

---

## Reporting language

Allowed: “evaluated on locked confirm pack; secondary axis G1 offline …”.  
Forbidden: “robust,” “general,” “cross-model proven” from a single extra check.
