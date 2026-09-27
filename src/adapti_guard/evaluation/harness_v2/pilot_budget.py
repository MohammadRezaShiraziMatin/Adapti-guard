"""Pilot run control exceptions (shared by runner and tools session)."""


class PilotBudgetExceeded(Exception):
    """Persisted ledger crossed USD or HTTP cap mid-episode."""
