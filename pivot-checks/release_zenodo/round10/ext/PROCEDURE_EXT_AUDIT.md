# Extended reference-solution audit — procedure [EXPLORATORY; CODE FACT outputs]
Written 2026-10-16 (Tehran) before running. Locked by ext/PROCEDURE_EXT_AUDIT.sha256 (this file + ext/audit_suites.py + ext/injectable_probe.py).
For each code base (path to its `src` dir containing package `agentdojo`), with PYTHONPATH pointing ONLY at that src (venv deps reused, no network, no LLM):
1. For each benchmark version and suite returned by get_suites(version): run upstream TaskSuite.check() unchanged; record ok / exception.
2. Per task isolated: same logic as check() (ground-truth pipeline; utility for user tasks with injections={}, security for injection
   tasks with the suite's first user task), each task in try/except; record pass / fail / exception text.
3. Classify each failing injection task, by reading its ground_truth() and security() and the tool result:
   tool-absent (ToolNotFoundError), stub (GT unrelated to GOAL / identical copy across tasks), wrong-args (schema/validation error or
   args not matching security), missing-step (a gate requires an extra call), text-only (empty GT, goal is a text output),
   other/unknown. Classification is by the AI analyst, reported per task with the evidence string.
4. Dedup: suites whose injection_tasks.py is byte-identical to an already audited file are reported as copies, not new defects.
Injectable probe (ext/injectable_probe.py): for one user task per suite, show tool-response content types seen by is_task_injectable()
and whether canaries occur in non-str contents; and show from code that check()'s injection-task loop does not call is_task_injectable.
