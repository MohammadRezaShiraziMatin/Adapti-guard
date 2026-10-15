# Layer A v4 Candidate — Upgrade Specification

**Status:** specification only; candidate data not yet authored or evaluated  
**Parent assets:** `datasets/frozen/layer_a_v3/`, `datasets/candidates/p1_mechanism_v1/`  
**Non-negotiable:** do not modify frozen datasets, confirmatory manifests, experiment logs, or paper results.

## Acceptance criteria

A new candidate pack should not be promoted to frozen until all of the following are satisfied:

- [ ] Every row has a stable unique ID, label, split, provenance, and explicit success/failure condition.
- [ ] Attack and benign controls are paired by legitimate task and interaction length where practical.
- [ ] Multi-turn cases have explicit ordered turns, role labels, and state dependencies; a static transcript is labeled `serialized_history_proxy`, not live multi-turn.
- [ ] Tool-abuse cases specify the exact structured tool proposal and the unauthorized side effect that defines success.
- [ ] Data-exfiltration cases define the protected asset, authorized destination, and observable leakage event.
- [ ] Benign controls include quoted or attack-like text that must be treated as data, not instructions.
- [ ] Exact duplicate IDs/bodies are absent; near-duplicate/scaffold review is recorded.
- [ ] Train/dev/test split assignment is deterministic and leakage-aware; test rows are not used for tuning.
- [ ] Canary-based scorers have tests for direct emission, quoted mention, refusal, and legitimate-task completion.
- [ ] At least two reviewers adjudicate ambiguous labels and success conditions; disagreements are recorded.
- [ ] Machine-readable manifest and SHA-256 hashes match the built artifacts.
- [ ] The pack card states synthetic/external provenance, known limitations, and that no model has been evaluated unless a gated run actually occurs.

## Proposed coverage

1. Direct instruction override.
2. Indirect injection in email/document/web/tool output.
3. Obfuscated instruction, with transformation and decoding expectations recorded.
4. Unauthorized structured tool proposal and attempted execution.
5. Private-data exfiltration with explicit source and destination.
6. Stateful multi-turn escalation and delayed triggers.
7. Context/memory poisoning, only where the runtime actually retains state.
8. Matched benign tasks and hard negatives.
9. Utility regression controls: successful legitimate task completion under defense.

## Evaluation boundary

The current confirmatory InjecAgent campaign remains untouched. The candidate pack is a separate exploratory evaluation, with its own predeclared estimands, sampling plan, model/arm matrix, cost cap, and failure handling. No API/model calls are authorized by this specification.
