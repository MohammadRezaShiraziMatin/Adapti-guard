from src.adapti_guard.runtime import AdaptiGuard


class AdaptiGuardPipeline:
    """Thin wrapper around AdaptiGuard for single-text pipeline calls."""

    def __init__(self):
        self.guard = AdaptiGuard()

    def run(self, text: str, **kwargs):
        # kwargs accepted for backward compatibility (garak / inspect adapters)
        return self.guard.run(text)


# Backward-compatible alias used by garak_adapter.py and inspect-test/
DefensePipeline = AdaptiGuardPipeline
