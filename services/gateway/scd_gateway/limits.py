"""Request limits per key in a sliding window."""

import math
import threading
import time
from collections import deque
from collections.abc import Callable

WINDOW = 60.0  # seconds
MAX_KEYS = 10_000


class RateLimiter:
    """ponytail: counts live in this process, so each replica has its own; move them to Redis when scaled out."""

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self.clock = clock
        self.hits: dict[str, deque[float]] = {}
        self.lock = threading.Lock()

    def wait(self, key: str, limit: int) -> int:
        """Count one request. 0 when allowed, otherwise the seconds until the next one is."""
        with self.lock:
            now = self.clock()
            if len(self.hits) >= MAX_KEYS:  # drop idle keys so many different emails cannot fill memory
                self.hits = {k: v for k, v in self.hits.items() if v and v[-1] > now - WINDOW}
            times = self.hits.setdefault(key, deque())
            while times and times[0] <= now - WINDOW:
                times.popleft()
            if len(times) >= limit:
                return max(1, math.ceil(times[0] + WINDOW - now))
            times.append(now)
            return 0
