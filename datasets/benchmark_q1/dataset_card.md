# benchmark_q1 Dataset Card

## Overview
Publication-grade benchmark for ADAPTI-GUARD Q1 experiments.

- **Version:** q1.0
- **Created:** 2026-09-01T15:31:32.700769+00:00
- **Total samples:** 15053
- **Splits:** train 10537 / validation 2257 / test 2259

## Categories
1. direct_prompt_injection
2. indirect_prompt_injection
3. rag_injection
4. agent_tool_injection
5. jailbreak
6. benign_tasks
7. adaptive_attacks

## Label Balance
- attack: 11859
- benign: 3194

## Provenance
Built from benchmark_v2 remapping + adaptive attack generation.
Unavailable sources (NotInject, BIPIA, InjecAgent, TensorTrust, PIArena) have adapter stubs in configs/datasets.yaml.

## Deduplication
Method: exact normalized prompt SHA256 grouping.
Removed: 0 duplicates.

## Contamination
Group-level split assignment prevents duplicate prompts across splits.
Contamination detected: False

## License
Follow upstream dataset licenses (BeaverTails, RAGTruth, JailbreakBench, AgentDojo, prompt-injections).
