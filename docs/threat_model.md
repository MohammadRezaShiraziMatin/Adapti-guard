# Threat Model

## Assets

- System / developer instructions for an LLM agent
- Confidential context (system prompts, private data)
- Tool-calling capabilities that can cause side effects

## Adversary

An attacker who can insert or influence **untrusted text** consumed by the agent:

- Direct user prompts
- Indirect content (documents, RAG passages)
- Tool outputs framed as trusted

Goals include instruction override, jailbreak, secret leakage, and unauthorized tool use.

## Defenses in scope

Runtime, policy-level interventions **after** content arrives:

- Sanitize suspicious phrasing
- Restrict tools
- Block the interaction
- Adapt intervention level across a sequence of episodes

## Out of scope (current codebase)

- Training-time hardening (e.g., SecAlign)
- Full interactive multi-turn red-team mutation (PAIR/Crescendo-class) as the primary protocol
- Live AgentDojo-style tool sandboxes in the primary harness

See also: `docs/research/THREAT_MODEL.md`, `docs/research/ATTACK_TAXONOMY.md`.
