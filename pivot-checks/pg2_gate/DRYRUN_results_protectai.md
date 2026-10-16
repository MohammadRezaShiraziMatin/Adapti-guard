# DRY-RUN — NOT RESULTS (substitute model protectai/deberta-v3-base-prompt-injection-v2)

Threshold 0.50. Flip = flag(A) != flag(C). Wilson 95% CI.

| label | stratum | n | flips A vs C(s512) | rate [95% CI] | flips A vs C(s256) | rate [95% CI] | A flag rate | B flag rate | C512 flag rate |
|---|---|---|---|---|---|---|---|---|---|
| benign | ALL | 434 | 0 | 0.000% [0.000%, 0.877%] | 0 | 0.000% [0.000%, 0.877%] | 0.576 | 0.576 | 0.576 |
| benign | len 512-2k | 27 | 0 | 0.000% [0.000%, 12.456%] | 0 | 0.000% [0.000%, 12.456%] | 0.963 | 0.963 | 0.963 |
| benign | len <=512 | 407 | 0 | 0.000% [0.000%, 0.935%] | 0 | 0.000% [0.000%, 0.935%] | 0.550 | 0.550 | 0.550 |
| injected | ALL | 1549 | 0 | 0.000% [0.000%, 0.247%] | 0 | 0.000% [0.000%, 0.247%] | 0.947 | 0.947 | 0.947 |
| injected | len 512-2k | 270 | 0 | 0.000% [0.000%, 1.403%] | 0 | 0.000% [0.000%, 1.403%] | 1.000 | 1.000 | 1.000 |
| injected | len <=512 | 1279 | 0 | 0.000% [0.000%, 0.299%] | 0 | 0.000% [0.000%, 0.299%] | 0.936 | 0.936 | 0.936 |
| injected | start<510 | 1459 | 0 | 0.000% [0.000%, 0.263%] | 0 | 0.000% [0.000%, 0.263%] | 0.944 | 0.944 | 0.944 |
| injected | start>=510 | 90 | 0 | 0.000% [0.000%, 4.094%] | 0 | 0.000% [0.000%, 4.094%] | 1.000 | 1.000 | 1.000 |

Task-level 'blocked' proxy (any injected output flagged; NOT ASR/utility): 0/560 (user,injection) pairs differ A vs C512.

Pre-registered decision (PREREG.md §5): injected flip rate 0.000%, upper 95% CI 0.247% -> **APPENDIX PARAGRAPH** (DRY-RUN: decision NOT valid)
