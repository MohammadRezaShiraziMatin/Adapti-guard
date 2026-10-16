# Extended reference-solution audit [EXPLORATORY] (2026-10-16, Tehran)
The procedure was locked in PROCEDURE_EXT_AUDIT.sha256 before any run. Everything ran offline at $0.
Raw outputs: audit_{agentdojo,agentdyn,autodojo,adr}.{txt,json} and injectable_probe_{dyn,agentdojo}.txt.
Note: the first run aborted on a relative-path assert. The rerun used absolute paths, and the script was not changed.

## Code bases
| benchmark | repo @ commit | license | installed offline? |
|---|---|---|---|
| AgentDojo | ethz-spylab/agentdojo @ 089ed468 (local clone ad/) | MIT [verify on repo] | yes |
| AgentDyn | SaFo-Lab/AgentDyn @ 5353cf76 (leolee99/AgentDyn redirects here with 301) | MIT | yes |
| AutoDojo | xhOwenMa/AutoDojo @ aa458794 | MIT | yes |
| ADR (uber) | uber/ADR @ a6076aa3 | Apache-2.0 | NO: top-level imports (`from base_tasks import`) are not a package. By diff it is AgentDojo v1/v1_1 with only import paths and a `TASK_TYPE` attribute changed, with no ground_truth/security changes. It inherits the AgentDojo v1/v1.1 results (all pass). Not executed. |

## Per-task results: injection tasks failing security() after their own ground_truth()
| benchmark | suite (version) | failing / total | class |
|---|---|---|---|
| AgentDojo | workspace (v1.2, v1.2.1, v1.2.2) | 8/14 (inj6–13) | stub: ground_truth() returns [] |
| AgentDojo | workspace v1 user_task_7 (utility) | 1 user task | other (not root-caused) |
| AgentDyn | shopping v1 | 9/9 | stub: send_money(recipient="") placeholder |
| AgentDyn | github v1 | 9/9 | tool absent: send_money is not in the github toolset (ToolNotFoundError) |
| AgentDyn | dailylife v1 | 2/10 | inj2 missing step (OTP verify); inj6 wrong args (create_calendar_event lacks start/end_time) |
| AgentDyn | inherited workspace v1.2.x | 8/14 | same as AgentDojo |
| AutoDojo | shopping v1 | 3/9 (inj2, 5, 8) | other: OTP-gated; a static call list cannot name a random OTP. AutoDojo replaced the 9 stubs; 6 now pass. |
| AutoDojo | github v1 / dailylife v1 | 9/9 / 2/10 | unchanged from AgentDyn |
| AutoDojo | banking_v2_0–4, travel_v2_0–4 (new) | 0 | none |
| AutoDojo | inherited workspace v1.2.x | 8/14 | same as AgentDojo |

## Benchmark × defect class × count (unique injection tasks; inherited copies are not double-counted)
| benchmark | stub | wrong args | missing step | tool absent | other |
|---|---|---|---|---|---|
| AgentDojo (original) | 8 (workspace inj6–13, empty GT) | 0 | 0 | 0 | 0 (+1 user task) |
| AgentDyn (new suites) | 9 | 1 | 1 | 9 | 0 |
| AutoDojo (beyond AgentDyn) | 0 (fixed 9 → 3 remaining) | 0 | 0 | 0 | 3 (OTP-gated) |
| ADR | 0 (by diff; not executed) | 0 | 0 | 0 | 0 |

Caveat: whether workspace inj6–13 with an empty GT is an intentional upstream design (security-only tasks) or a defect is UNVERIFIED. Here it is classed as "stub" only in the sense that check() fails.

## The "all user tasks not injectable" observation: root-caused
In this code version, tool messages carry `content` as a list of content blocks, not a str. `is_task_injectable()` only scans str contents, so it returns False even though the canary is present (probe: canary present = True, injectable() = False, in every suite). It is called only in check()'s user-task section, never in the injection-task loop, so it cannot affect injection-task security checks.

## PRIOR ART FOUND (important for priority claims)
AutoDojo's shopping/injection_tasks.py carries a NOTE dated 2026-06-14. It states that the original `send_money(recipient="")` stubs "matched no security() check". It also says inj2/5/8 cannot pass check() because of OTP gating. So the AgentDyn shopping-stub defect was already noticed and fixed in public code by AutoDojo (xhOwenMa). The github and dailylife defects are not mentioned there.
