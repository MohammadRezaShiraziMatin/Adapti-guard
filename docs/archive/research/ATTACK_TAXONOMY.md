# ADAPTI-GUARD — Attack Taxonomy Audit

**Phase 1 Audit | Date:** 2026-09-02

---

## Summary

| Category | benchmark_q1 (total) | attack_dataset.json | OWASP map | Agent lit. | Relevant to current impl? |
|----------|---------------------:|--------------------:|-----------|------------|----------------------------|
| Direct Prompt Injection | 263 | 100 | LLM01 direct | BIPIA, Garak | **Yes** |
| Indirect Prompt Injection | 1,037 | 100 | LLM01 indirect | InjecAgent, BIPIA | **Yes** |
| Jailbreak | 6,104 | 100 | LLM01 / misuse | JailbreakBench | **Yes** |
| RAG Poisoning | 1,927 | 100 | LLM01 indirect | RAGTruth | **Yes** (static context) |
| Multi-turn Attacks | 2,500 | 100 | LLM01 | Adaptive templates | **Partial** (single-turn eval) |
| Tool Abuse | 28 | 28 | LLM07 | AgentDojo, InjecAgent | **No** (no tool exec) |
| System Prompt Leakage | ~2 keywords | **0** | LLM02 | Garak probes | **No** (no samples) |

**Do not inflate taxonomy to 7 balanced categories until data exists.**

---

## Category Definitions

### 1. Direct Prompt Injection

| Field | Definition |
|-------|------------|
| **Definition** | Adversarial instructions in the user message override system/developer intent |
| **Attacker goal** | Hijack behavior, exfiltrate instructions, force harmful output |
| **Vector** | User prompt channel |
| **Expected impact** | Policy violation, data leak, unsafe completion |
| **Dataset source** | prompt-injections corpus, BeaverTails-derived |
| **Eval criterion** | Judge: model follows adversarial instruction |
| **OWASP** | LLM01 (Direct) |
| **Literature** | Perez & Ribeiro 2022; PromptInject; OWASP GenAI |
| **Relevance** | **High** — core to detector regex patterns |

### 2. Indirect Prompt Injection

| Field | Definition |
|-------|------------|
| **Definition** | Injection embedded in untrusted content the model is asked to summarize/use |
| **Attacker goal** | Trigger action when model processes external text |
| **Vector** | Context / retrieved document field |
| **Expected impact** | Covert instruction following |
| **Dataset source** | RAGTruth-style, news/document wrappers |
| **Eval criterion** | Judge: harmful compliance despite benign wrapper task |
| **OWASP** | LLM01 (Indirect) |
| **Literature** | Greshake et al. 2023; BIPIA |
| **Relevance** | **High** — `context` concatenation in pipeline |

### 3. Jailbreak Attacks

| Field | Definition |
|-------|------------|
| **Definition** | Role-play, persona (DAN), encoding, or policy-evasion framing |
| **Attacker goal** | Bypass safety alignment |
| **Vector** | User prompt |
| **Expected impact** | Harmful content generation |
| **Dataset source** | JailbreakBench, BeaverTails (dominant class: 6,104) |
| **Eval criterion** | Judge: safety policy violation |
| **OWASP** | LLM01 + misuse |
| **Literature** | JailbreakBench, HarmBench |
| **Relevance** | **High** — but conflated with general unsafe content in corpus |

### 4. RAG Poisoning

| Field | Definition |
|-------|------------|
| **Definition** | Malicious passages injected into retrieval context to steer answers |
| **Attacker goal** | Wrong/harmful answers grounded in poisoned passages |
| **Vector** | Retrieved passages in prompt |
| **Expected impact** | Integrity failure of RAG system |
| **Dataset source** | RAGTruth (1,927) |
| **Eval criterion** | Judge: answer reflects injected instruction not passages |
| **OWASP** | LLM01 indirect |
| **Literature** | RAGTruth; poisoned RAG papers |
| **Relevance** | **Moderate** — no live retriever; static passage injection only |

### 5. Multi-turn Attacks

| Field | Definition |
|-------|------------|
| **Definition** | Attack spread across conversation turns or evolving templates |
| **Attacker goal** | Gradual policy erosion |
| **Vector** | Conversation history |
| **Expected impact** | Late-turn compromise |
| **Dataset source** | `adaptive_attacks` (2,500) — template evolution at **generation** time |
| **Eval criterion** | ASR on multi-turn sessions |
| **OWASP** | LLM01 |
| **Literature** | Crescendo attacks; AgentDojo multi-step |
| **Relevance** | **Low in current harness** — single-turn API calls |

### 6. Tool Abuse Attacks

| Field | Definition |
|-------|------------|
| **Definition** | Injection causing unauthorized or harmful tool/API invocation |
| **Attacker goal** | Exfiltrate data, modify state, execute commands |
| **Vector** | Prompt → tool planner |
| **Expected impact** | Real-world side effects |
| **Dataset source** | AgentDojo (28 samples — **insufficient**) |
| **Eval criterion** | Tool call trace audit |
| **OWASP** | LLM07, LLM08 |
| **Literature** | AgentDojo, InjecAgent, ToolEmu |
| **Relevance** | **Not evaluated** — `tool_sensitive=False` everywhere in production paths |

### 7. System Prompt Leakage

| Field | Definition |
|-------|------------|
| **Definition** | Elicitation of hidden system/developer instructions |
| **Attacker goal** | Extract secrets, enable follow-up attacks |
| **Vector** | User prompt |
| **Expected impact** | Confidentiality breach |
| **Dataset source** | **None in attack_dataset** (2 keyword hits in full corpus) |
| **Eval criterion** | Substring/semantic match to system prompt |
| **OWASP** | LLM02 |
| **Literature** | Garak leak probes |
| **Relevance** | **Unsupported** — category empty

---

## Taxonomy Recommendations

### Keep (with evidence)
- Direct, Indirect, Jailbreak, RAG — sufficient samples, match implementation

### Rename / downgrade
- **Multi-turn** → "Adaptive templates (single-turn replay)" until multi-turn API eval exists
- **Tool abuse** → remove from title/abstract until AgentDojo integration

### Must add before claiming
- System prompt leakage: ≥100 curated probes (Garak)
- Tool abuse: ≥100 AgentDojo security test cases with tool sandbox

### Do NOT create
- Artificial category splits to reach "7 categories" without distinct eval criteria
