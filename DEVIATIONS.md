# Deviations log

Each entry records a departure from the frozen protocol or the run plan. Entries are append-only.

## D3: R2 interrupted at 571/980, raw folder lost

- **What happened:** The R2 run stopped at about 571 of 980 episodes after a process kill at roughly 30 minutes. The run folder was not committed incrementally, and it is no longer recoverable: it is not on the owner's computer, not in the run environment, and not on any git ref.
- **Analysis impact:** No episodes from the interrupted R2 run are analyzed. No partial result is reported.
- **Budget impact:** About 0.0607 USD of spend (runner figure 0.061056) counts against the campaign cap.
- **Key-usage reconciliation:** The OpenRouter `/auth/key` usage read moved from 0.068159 to 0.068612 USD after R2 stopped, a difference of 0.000453 USD. This is not yet attributed to a process. No launcher or run process was found in the repository at HEAD that would make calls after R2 stopped. This needs checking against the provider's usage_daily breakdown before the entry is closed.
- **Corrective action:** A full R2 rerun in a fresh folder (option a). Its progress.log and episodes.jsonl are committed incrementally, and the run is launched detached (setsid or nohup) so a session timeout cannot kill it.
- **Status:** Open. The rerun has not been started.
