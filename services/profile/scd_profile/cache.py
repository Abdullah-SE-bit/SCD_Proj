"""Verdict cache in Redis (M02-003, M02-004, CMN-002, AMB-11).

The key covers the user, the idea version, the profile version and the rubric, engine and knowledge-base snapshot
versions, so changing any of them misses. Entries expire (DBS-003). A broken or missing Redis only means a miss:
the cache never makes a request fail. Speaks the few RESP commands it needs with the standard library.
"""

import hashlib
import json
import socket
import threading
from typing import Any
from urllib.parse import urlsplit

TTL_SECONDS = 24 * 3600
KEY_PARTS = ("user_id", "version_id", "profile_version", "rubrics", "engine", "snapshot")


class RedisError(Exception):
    pass


class Redis:
    def __init__(self, url: str, timeout: float = 1.0) -> None:
        parts = urlsplit(url)
        if parts.scheme != "redis" or not parts.hostname:
            raise ValueError("a cache address looks like redis://host:port")
        self.address, self.timeout = (parts.hostname, parts.port or 6379), timeout

    def command(self, *words: str) -> str | None:
        encoded = [word.encode() for word in words]
        message = b"*%d\r\n" % len(encoded) + b"".join(b"$%d\r\n%s\r\n" % (len(w), w) for w in encoded)
        try:
            with socket.create_connection(self.address, self.timeout) as connection:
                connection.sendall(message)
                with connection.makefile("rb") as reply:
                    return self._read(reply)
        except (OSError, ValueError) as error:
            raise RedisError(type(error).__name__) from None

    def _read(self, reply: Any) -> str | None:
        line = reply.readline()
        if not line.endswith(b"\r\n"):
            raise RedisError("incomplete answer")
        kind, rest = line[:1], line[1:-2]
        if kind == b"+":
            return rest.decode()
        if kind == b"$":
            size = int(rest)
            if size < 0:
                return None
            data = reply.read(size + 2)
            if len(data) != size + 2:
                raise RedisError("incomplete answer")
            return data[:size].decode()
        raise RedisError(rest.decode(errors="replace")[:100] if kind == b"-" else "unexpected answer")


def key_of(parts: dict[str, Any]) -> str:
    return "verdict:" + hashlib.sha256(json.dumps([parts[name] for name in KEY_PARTS]).encode()).hexdigest()


class VerdictCache:
    """Counts what happens so hits are visible (M02-004)."""

    def __init__(self, store: Redis | None, ttl: int = TTL_SECONDS) -> None:
        self.store, self.ttl = store, ttl
        self.counts = {"cache_hits": 0, "cache_misses": 0, "cache_errors": 0}
        self.lock = threading.Lock()

    def count(self, name: str) -> None:
        with self.lock:
            self.counts[name] += 1

    def get(self, parts: dict[str, Any]) -> dict[str, Any] | None:
        value = None
        if self.store:
            try:
                found = self.store.command("GET", key_of(parts))
                value = json.loads(found) if found is not None else None
            except (RedisError, ValueError):
                self.count("cache_errors")
        self.count("cache_hits" if value is not None else "cache_misses")
        return value

    def put(self, parts: dict[str, Any], document: dict[str, Any]) -> bool:
        if not self.store:
            return False
        try:
            return self.store.command("SET", key_of(parts), json.dumps(document), "EX", str(self.ttl)) == "OK"
        except RedisError:
            self.count("cache_errors")
            return False

    def metrics(self) -> dict[str, Any]:
        with self.lock:
            return {**self.counts, "cache": "redis" if self.store else "off"}
