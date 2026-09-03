# benchmark_q1 Distribution Report

**Total samples:** 15053
**Target met (≥10000):** True

## Category Distribution

| Category | Count | % |
|---|---:|---:|
| jailbreak | 6104 | 40.6% |
| benign_tasks | 3194 | 21.2% |
| adaptive_attacks | 2500 | 16.6% |
| rag_injection | 1927 | 12.8% |
| indirect_prompt_injection | 1037 | 6.9% |
| direct_prompt_injection | 263 | 1.7% |
| agent_tool_injection | 28 | 0.2% |

## Label Distribution

- **attack:** 11859 (78.8%)
- **benign:** 3194 (21.2%)

## Split Distribution

- **validation:** 2257 (15.0%)
- **train:** 10537 (70.0%)
- **test:** 2259 (15.0%)

## Source Attribution

- beavertails: 7575
- ragtruth: 2964
- adaptive_from_beavertails: 1200
- do_not_answer: 938
- adaptive_from_ragtruth: 792
- prompt_injection: 662
- adaptive_from_do_not_answer: 356
- jailbreakbench: 200
- jailbreak_judge: 186
- adaptive_from_prompt_injection: 80
- adaptive_from_jailbreakbench: 40
- adaptive_from_jailbreak_judge: 32
- agentdojo: 28

## Unavailable Sources

- **notinject:** UNAVAILABLE
- **bipia:** UNAVAILABLE
- **injecagent:** UNAVAILABLE
- **tensortrust:** UNAVAILABLE
- **piarena:** UNAVAILABLE

## Contamination Check

- train∩val: 0
- train∩test: 0
- val∩test: 0
- **Contamination detected:** False
