"""The only way a scout reaches a source: through M5 (ARC-007). Waits when M5 says a limit applies."""

import json
import os
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

MAX_WAIT = 90.0
ATTEMPTS = 4
Post = Callable[[str, dict[str, Any]], tuple[int, dict[str, Any]]]


class SourceError(Exception):
    """One request to a source failed; the message is safe to log."""


def http_post(url: str, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=60) as reply:
            return reply.status, json.load(reply)
    except urllib.error.HTTPError as error:
        try:
            return error.code, json.load(error)
        except ValueError:
            return error.code, {}
    except (OSError, ValueError) as error:
        raise SourceError(f"tool layer unreachable: {type(error).__name__}") from None


class Tools:
    def __init__(self, base: str | None = None, post: Post = http_post,
                 sleep: Callable[[float], None] = time.sleep) -> None:
        self.url = (base or os.environ.get("TOOLS_URL") or "http://tools:8000").rstrip("/") + "/fetch"
        self.post, self.sleep = post, sleep

    def get_json(self, url: str, method: str = "GET", payload: Any = None) -> Any:
        body: dict[str, Any] = {"url": url, "method": method}
        if payload is not None:
            body["payload"] = payload
        for _ in range(ATTEMPTS):
            status, answer = self.post(self.url, body)
            if status == 200:
                try:
                    return json.loads(answer["content"])
                except (KeyError, ValueError):
                    raise SourceError("the source did not answer with JSON") from None
            wait = answer.get("retry_after")
            if status != 429 or not isinstance(wait, (int, float)) or wait > MAX_WAIT:
                raise SourceError(f"{status}: {answer.get('error', 'no detail')}")
            self.sleep(wait + 0.05)
        raise SourceError("still rate limited after several attempts")
