"""JSON calls to an internal service by its cluster name."""

import json
import urllib.error
import urllib.request
from typing import Any

TIMEOUT = 5  # seconds


class Unavailable(RuntimeError):
    """The service could not be reached or did not answer with JSON."""


class Client:
    def __init__(self, base: str) -> None:
        if not base.startswith(("http://", "https://")):
            raise ValueError("a service address starts with http:// or https://")
        self.base = base.rstrip("/")

    def __call__(self, method: str, path: str, body: Any = None) -> tuple[int, Any]:
        data = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(self.base + path, data=data, method=method,
                                         headers={"Content-Type": "application/json"})
        try:
            try:
                with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # nosec B310
                    return response.status, json.load(response)
            except urllib.error.HTTPError as error:  # 4xx and 5xx still carry the service's JSON
                return error.code, json.load(error)
        except (OSError, ValueError) as error:
            raise Unavailable(type(error).__name__) from error
