# AgentDojo pin and published reference

- Source: https://github.com/ethz-spylab/agentdojo
- Pinned commit: `089ed468cf3ed0322acc66b0211f26d9d90dbf60` (shallow clone, 2026-10-11)
- Public run files: `runs/<model>/<suite>/user_task_*/<attack>/...json` in that commit (525 MB; not copied here)
- Published table: `docs/results-table.html` at the same commit, copied to `verify/agentdojo/results-table.html`
  - GPT-4o row, important_instructions, Targeted ASR `47.69%`: line 177
  - Llama-3-70B row (`meta-llama/Llama-3-70b-chat-hf`), important_instructions, Targeted ASR `25.60%`: line 320

Reproduce from a checkout at the pin:

    python3 scripts/agentdojo_error_count.py <checkout> meta-llama_Llama-3-70b-chat-hf important_instructions --csv verify/agentdojo/episodes_llama3_70b_important_instructions.csv
    python3 scripts/agentdojo_error_count.py <checkout> gpt-4o-2024-05-13 important_instructions --csv verify/agentdojo/episodes_gpt4o_important_instructions.csv

The CSV files are the per-episode extract (629 pairs per model) written by the script from the pinned run files.
