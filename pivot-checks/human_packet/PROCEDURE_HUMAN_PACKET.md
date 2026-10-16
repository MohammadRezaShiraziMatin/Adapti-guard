# [EXPLORATORY] Human blind labelling packet procedure (locked before sampling)
Population: AgentDyn important_instructions episodes with a defined ATT-ARG label, in the flip model cells, defenses progent, drift, tool_filter, repeat_user_prompt;
excluding every episode already in bitems/scorer_validation and attarg/validation keys.
Sample: seed 20261018, 5 per (defense x ATT-ARG label) = 40. Order shuffled; ids H000-H039.
Shown: suite, injection goal, the agent's proposed tool calls (function + args, truncated 300 chars). NOT shown: defense, model, tool outputs (they can reveal the defense), any label.
Key (defense, pipe, episode path, ATT-ARG, name-match ATT, EXEC) is written to KEY_SEPARATE/key.json and sha256-hashed; the key must not be given to the labeller.
