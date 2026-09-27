"""Hard counter for OpenRouter chat completion HTTP requests."""
from __future__ import annotations


class HttpCompletionBudget:
    def __init__(self, max_requests: int, *, initial_used: int = 0) -> None:
        self.max_requests = max_requests
        self.used = initial_used

    def acquire(self) -> bool:
        if self.used >= self.max_requests:
            return False
        self.used += 1
        return True

    def can_continue(self) -> bool:
        return self.used < self.max_requests

    @property
    def exhausted(self) -> bool:
        return self.used >= self.max_requests
