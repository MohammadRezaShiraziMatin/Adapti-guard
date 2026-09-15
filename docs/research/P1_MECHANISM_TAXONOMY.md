# P1 Mechanism Taxonomy

**ID:** `P1-TAX-0.1`  
**Status:** Locked for `p1_mechanism_v1.0-candidate` construction  
**Rule:** Classify by **mechanism**, not by surface wording. Store wording under `surface_form`.

Derived from P0 §15 with one mandatory modification from repository evidence:

- **C4 Adaptive Attacker** remains in the taxonomy for completeness but is **OUT OF SCOPE** for this candidate pack (0 rows). Phase-1 / P0 exclude live adaptive attackers; including adaptive rows without a live harness would falsify estimands.

---

## Hierarchy

```text
A. DIRECT INSTRUCTION ATTACKS
   A1 Instruction Override
   A2 Authority Spoofing
   A3 Goal Hijacking

B. INDIRECT / CONTEXTUAL ATTACKS
   B1 Retrieved-Document Injection
   B2 Web-Content Injection
   B3 File/Document Injection
   B4 Tool-Output Injection
   B5 Context Poisoning

C. SEQUENTIAL ATTACKS
   C1 Multi-Turn Persistence      (frozen_context representation only)
   C2 Delayed Activation          (frozen_context representation only)
   C3 Multi-Step Escalation       (frozen_context / declared chain)
   C4 Adaptive Attacker           (OUT OF SCOPE — 0 rows)

D. AGENT ACTION ATTACKS
   D1 Tool Misuse
   D2 Privilege Escalation
   D3 Cross-Tool Manipulation
   D4 Unauthorized External Action

E. DATA-TARGETING ATTACKS
   E1 Exfiltration
   E2 Sensitive-Context Extraction
   E3 Memory Poisoning            (planted rule in context; no durable memory store)

F. EVASION
   F1 Obfuscation
   F2 Instruction Smuggling
   F3 Semantic Paraphrase
   F4 Indirect Semantic Injection
```

---

## Operational definitions

| Code | Mechanism (operational) | Typical surface_form examples | Primary context_source |
| --- | --- | --- | --- |
| A1 | User text orders the agent to discard prior constraints and perform an attacker action | “ignore previous…”, bare imperative override | user |
| A2 | Text claims elevated authority (system/developer/admin) to compel action | spoofed SYSTEM/developer blocks — **not** DAN role-play alone | user |
| A3 | Text replaces the user’s legitimate goal with an attacker goal | “new goal for model…”, task substitution | user / mixed |
| B1 | Malicious instructions embedded in retrieved-document text | HTML comment / footnote in “Retrieved doc” | retrieved_doc |
| B2 | Malicious instructions in webpage-like content | JSON-LD, hidden HTML, page footer | web |
| B3 | Malicious instructions in file-like artifacts | CSV column, PDF note, YAML frontmatter | file |
| B4 | Malicious instructions inside tool observation / error body | `ASSISTANT_INSTRUCTION`, forged FUNCTION_RESULT | tool_output |
| B5 | Context is poisoned with a standing rule that later triggers harm | planted policy line in notes | dialogue / mixed |
| C1 | Earlier turn plants authorization; final turn invokes it | multi-turn transcript in `context` | dialogue |
| C2 | Earlier content plants payload; benign-looking final prompt triggers it | weather Q after planted rule | dialogue |
| C3 | Escalating steps across frozen turns or declared tool chain | progressive permission story | dialogue / mixed |
| C4 | Attacker adapts after observing defense | — | **N/A this pack** |
| D1 | Declared tool call is itself the misuse relative to user task | unauthorized `create_record` | user |
| D2 | Tool args claim higher privilege (`org_owner`, `admin_grant`, …) | privilege kinds | user |
| D3 | Harm requires coordinating ≥2 tools (declared intent) | search then email | mixed |
| D4 | External side effect via `send_email` / outbound record | email to external inbox | user |
| E1 | Move sensitive data out via tool | email SSN / secrets | mixed |
| E2 | Force retrieve of sensitive doc_id | `retrieve_document` of vault/path | user / context |
| E3 | Poison “memory” via context so later turn acts on planted fact | stored passphrase / debug_flag | dialogue |
| F1 | Encoding to evade lexical detectors | base64, hex, ROT13, ZWSP | user / context |
| F2 | Hide instructions in markup / attributes | HTML comment, markdown image title | context |
| F3 | Same mechanism, paraphrased without classic trigger phrases | polite paraphrase of override | user |
| F4 | Indirect phrasing that still encodes the harmful tool intent | story / metaphor covering tool call | user / context |

---

## Surface vs mechanism (mandatory)

```text
surface_form  →  mechanism (family code)  →  security_objective  →  observable harmful action
```

**Forbidden:** labeling an episode `A2` solely because it contains “you are now DAN”. DAN-style persona play without a tool-level harmful objective is **excluded** from this pack (P0 role audit).

---

## Migration from Phase-1 families

| Phase-1 `attack_family` | P1 code(s) |
| --- | --- |
| DIRECT_OVERRIDE | A1 (often) / A2 |
| SOCIAL_ENGINEERING | A2 / A3 / D4 |
| INDIRECT_RAG | B1 |
| TOOL_OUTPUT_INJECTION | B4 |
| DELAYED_ACTIVATION | C2 |
| PERSISTENCE / CROSS_TURN_STYLE | C1 / C3 |
| PRIVILEGE_EXFIL | D2 + E1 |
| OBFUSCATION | F1 / F2 |

Frozen Phase-1 labels are **not** rewritten.

---

## Coverage policy for `p1_mechanism_v1.0-candidate`

| Leaf | Target attacks | Benign twins | Notes |
| --- | ---: | ---: | --- |
| A1–A3, B1–B5, C1–C3, D1–D4, E1–E3, F1–F4 (22 leaves) | **2 each** | **1:1** | Unique mechanisms; no scaffold clones |
| C4 | **0** | **0** | Out of scope |
| Hard-negative benigns | — | **8** | Quote/analyze attack-like text without executing tools |

Total planned: **44 attacks + 44 twins + 8 hard-negatives = 96 episodes**.
