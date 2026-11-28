"""The fetch pipeline: check the address, then ask, following redirects only to addresses that pass the same checks."""

import datetime
import json
import os
from collections.abc import Callable
from typing import Any
from urllib.parse import SplitResult, urljoin

from scd_tools import policy, transport

TEXT_TYPES = ("application/json", "text/", "application/xml", "application/rss+xml", "application/atom+xml")
Send = Callable[..., transport.Response]


class Upstream(Exception):
    """The source failed or answered with something unusable."""


class Fetcher:
    def __init__(self, sources: dict[str, Any] | None = None, send: Send = transport.send,
                 resolver: policy.Resolver = policy.resolve, env: dict[str, str] | None = None) -> None:
        self.sources = sources or policy.load_sources()
        self.send = send
        self.resolver = resolver
        self.env = os.environ if env is None else env

    def fetch(self, url: Any, method: str = "GET", payload: Any = None) -> dict[str, Any]:
        if method not in ("GET", "POST"):
            raise policy.Refused("only GET and POST are allowed")
        body = None
        for _ in range(self.sources["max_redirects"] + 1):
            parts, rules = policy.check_url(url, self.sources)
            if method == "POST":
                if not rules.get("post"):
                    raise policy.Refused("POST is not allowed for this domain")
                body = json.dumps(payload).encode()
            reply = self._exchange(method, parts, rules, body)
            if reply.status in (301, 302, 303, 307, 308):
                if method == "POST" or "location" not in reply.headers:
                    raise Upstream(f"unusable redirect from {parts.hostname}")
                url = urljoin(url, reply.headers["location"])
                continue
            return self._result(url, parts, reply)
        raise Upstream("too many redirects")

    def _exchange(self, method: str, parts: SplitResult, rules: dict[str, Any],
                  body: bytes | None) -> transport.Response:
        host = str(parts.hostname).rstrip(".")
        address = policy.public_address(host, self.resolver)
        headers = {"User-Agent": self.sources["user_agent"], "Accept": "application/json, text/*;q=0.8",
                   "Accept-Encoding": "identity"}
        token = self.env.get(rules.get("token_env", ""), "")
        if token:
            headers["Authorization"] = f"Bearer {token}"  # added per domain, so a redirect never carries it elsewhere
        if body is not None:
            headers["Content-Type"] = "application/json"
        target = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
        try:
            return self.send(method, host, address, target, headers, body, self.sources["timeout_seconds"],
                             self.sources["max_bytes"])
        except ConnectionError as error:
            raise Upstream(str(error)) from None

    def _result(self, url: str, parts: SplitResult, reply: transport.Response) -> dict[str, Any]:
        if reply.status >= 400:
            raise Upstream(f"{parts.hostname} answered {reply.status}")
        if len(reply.body) > self.sources["max_bytes"]:
            raise Upstream("the response is too large")
        content_type = reply.headers.get("content-type", "").split(";")[0].strip().lower()
        if not content_type.startswith(TEXT_TYPES):
            raise Upstream(f"unsupported content type: {content_type or 'none'}")
        return {"url": url, "status": reply.status, "content_type": content_type,
                "content": reply.body.decode("utf-8", errors="replace"),
                "retrieved_at": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")}
