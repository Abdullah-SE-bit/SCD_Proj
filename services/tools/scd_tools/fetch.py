"""The fetch pipeline: check the address, then ask, following redirects only to addresses that pass the same checks."""

import datetime
import json
import os
from collections.abc import Callable
from typing import Any
from urllib.parse import SplitResult, urljoin
from urllib.robotparser import RobotFileParser

from scd_tools import limits, policy, sanitise, transport

TEXT_TYPES = ("application/json", "text/", "application/xml", "application/rss+xml", "application/atom+xml")
Send = Callable[..., transport.Response]


class Upstream(Exception):
    """The source failed or answered with something unusable."""


class Fetcher:
    def __init__(self, sources: dict[str, Any] | None = None, send: Send = transport.send,
                 resolver: policy.Resolver = policy.resolve, env: dict[str, str] | None = None,
                 clock: Callable[[], float] | None = None) -> None:
        self.sources = sources or policy.load_sources()
        self.send = send
        self.resolver = resolver
        self.env = os.environ if env is None else env
        timer = {} if clock is None else {"clock": clock}
        self.pacer = limits.Pacer(**timer)
        self.cache = limits.Cache(self.sources["cache_seconds"], self.sources["cache_entries"], **timer)
        self.robots = limits.Cache(3600, 100, **timer)

    def fetch(self, url: Any, method: str = "GET", payload: Any = None) -> dict[str, Any]:
        if method not in ("GET", "POST"):
            raise policy.Refused("only GET and POST are allowed")
        body = None
        if method == "POST":
            body = json.dumps(payload, sort_keys=True).encode()
        key = f"{method} {url} {body!r}"
        cached = self.cache.get(key)
        if cached is not None:
            return {**cached, "cached": True}
        paced: set[str] = set()
        for _ in range(self.sources["max_redirects"] + 1):
            parts, rules = policy.check_url(url, self.sources)
            if method == "POST" and not rules.get("post"):
                raise policy.Refused("POST is not allowed for this domain")
            host = str(parts.hostname).rstrip(".")
            if host not in paced:
                self.pacer.take(host, rules["min_interval"])
                paced.add(host)
            if rules["robots"]:
                self._check_robots(parts, rules, url)
            reply = self._exchange(method, parts, rules, body)
            if reply.status == 429 or reply.status >= 500:
                self.pacer.failed(host, reply.headers.get("retry-after"))
            if reply.status in (301, 302, 303, 307, 308):
                if method == "POST" or "location" not in reply.headers:
                    raise Upstream(f"unusable redirect from {host}")
                url = urljoin(url, reply.headers["location"])
                continue
            result = self._result(url, parts, reply)
            self.pacer.succeeded(host)
            self.cache.put(key, result)
            return {**result, "cached": False}
        raise Upstream("too many redirects")

    def _check_robots(self, parts: SplitResult, rules: dict[str, Any], url: str) -> None:
        host = str(parts.hostname).rstrip(".")
        parser = self.robots.get(host)
        if parser is None:
            reply = self._exchange("GET", parts._replace(path="/robots.txt", query=""), rules, None)
            parser = RobotFileParser()
            if reply.status in (404, 410):
                parser.parse([])  # no rules published
            elif reply.status == 200 and len(reply.body) <= self.sources["max_bytes"]:
                parser.parse(reply.body.decode("utf-8", errors="replace").splitlines())
            else:  # unreadable rules are not permission
                self.pacer.failed(host, reply.headers.get("retry-after"))
                raise Upstream(f"cannot read robots.txt of {host} ({reply.status})")
            self.robots.put(host, parser)
        if not parser.can_fetch(self.sources["user_agent"], url):
            raise policy.Refused(f"robots.txt of {host} does not allow this path")

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
            self.pacer.failed(host)
            raise Upstream(str(error)) from None

    def _result(self, url: str, parts: SplitResult, reply: transport.Response) -> dict[str, Any]:
        if reply.status >= 400:
            raise Upstream(f"{parts.hostname} answered {reply.status}")
        if len(reply.body) > self.sources["max_bytes"]:
            raise Upstream("the response is too large")
        content_type = reply.headers.get("content-type", "").split(";")[0].strip().lower()
        if not content_type.startswith(TEXT_TYPES):
            raise Upstream(f"unsupported content type: {content_type or 'none'}")
        content, removed = sanitise.sanitise(reply.body.decode("utf-8", errors="replace"), content_type)
        return {"url": url, "status": reply.status, "content_type": content_type,
                "content": content, "removed_instructions": removed,
                "retrieved_at": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")}
