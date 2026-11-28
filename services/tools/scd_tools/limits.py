"""Politeness towards sources (ETH-002, API-007): minimum interval per domain, back-off after errors and a cache.

ponytail: state is in memory, so it holds for one replica; use Redis if M5 is ever scaled out.
"""

import threading
import time
from collections import OrderedDict
from collections.abc import Callable
from typing import Any

MAX_BACKOFF = 600.0


class RateLimited(Exception):
    def __init__(self, host: str, retry_after: float) -> None:
        super().__init__(f"rate limit for {host}: retry in {retry_after:.1f} s")
        self.retry_after = round(retry_after, 1)


class Pacer:
    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self.clock = clock
        self.free_at: dict[str, float] = {}
        self.failures: dict[str, int] = {}
        self.lock = threading.Lock()

    def take(self, host: str, interval: float) -> None:
        """Reserve the next slot for a host, or say how long to wait."""
        with self.lock:
            now = self.clock()
            wait = self.free_at.get(host, 0.0) - now
            if wait > 0:
                raise RateLimited(host, wait)
            self.free_at[host] = now + interval

    def failed(self, host: str, retry_after: str | None = None) -> None:
        """Back off exponentially; a numeric Retry-After from the source wins when it is longer."""
        with self.lock:
            count = self.failures.get(host, 0) + 1
            self.failures[host] = count
            delay = min(MAX_BACKOFF, 2.0 ** count)
            if retry_after and retry_after.strip().isdigit():
                delay = max(delay, min(float(retry_after), 3600.0))
            self.free_at[host] = max(self.free_at.get(host, 0.0), self.clock() + delay)

    def succeeded(self, host: str) -> None:
        with self.lock:
            self.failures.pop(host, None)


class Cache:
    """Least recently used entries that expire."""

    def __init__(self, seconds: float, size: int, clock: Callable[[], float] = time.monotonic) -> None:
        self.seconds, self.size, self.clock = seconds, size, clock
        self.items: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key: str) -> Any:
        with self.lock:
            found = self.items.get(key)
            if found is None or found[0] <= self.clock():
                self.items.pop(key, None)
                return None
            self.items.move_to_end(key)
            return found[1]

    def put(self, key: str, value: Any) -> None:
        with self.lock:
            self.items[key] = (self.clock() + self.seconds, value)
            self.items.move_to_end(key)
            while len(self.items) > self.size:
                self.items.popitem(last=False)
