"""HTTP base shared by every service: /health, /ready, /info, JSON routes and JSON logs.

Copied into each module so every image builds from its own directory; tests/unit/test_services.py keeps the copies
identical. Standard library only.
"""

import json
import os
import re
import signal
import sys
import time
import uuid
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

MAX_BODY = 1_000_000
Request = dict[str, Any]  # body, params, headers (lower-case names), run_id
Handler = Callable[[Request], tuple[int, Any]]


def log(**fields: Any) -> None:
    print(json.dumps({"ts": round(time.time(), 3), **fields}, default=str), flush=True)


class Service:
    def __init__(self, name: str, module: str, ready: Callable[[], bool] = lambda: True) -> None:
        self.name = name
        self.ready = ready
        self.routes: list[tuple[str, re.Pattern[str], Handler]] = []
        self.route("GET", "/health")(lambda _: (200, {"status": "ok", "service": name}))
        self.route("GET", "/ready")(self._ready)
        self.route("GET", "/info")(lambda _: (200, {"service": name, "module": module}))

    def _ready(self, _: Request) -> tuple[int, Any]:
        ok = self.ready()
        return (200 if ok else 503), {"ready": ok, "service": self.name}

    def route(self, method: str, path: str) -> Callable[[Handler], Handler]:
        """Register a handler. `{name}` in the path becomes request["params"]["name"]."""
        pattern = re.compile("^" + re.sub(r"\{(\w+)\}", r"(?P<\1>[^/]+)", path) + "$")

        def register(handler: Handler) -> Handler:
            self.routes.append((method, pattern, handler))
            return handler

        return register

    def handle(self, method: str, path: str, raw: bytes = b"",
               headers: dict[str, str] | None = None) -> tuple[int, Any]:
        lowered = {k.lower(): v for k, v in (headers or {}).items()}
        path = path.split("?", 1)[0]
        run_id = lowered.get("x-run-id") or uuid.uuid4().hex
        status, body = self._dispatch(method, path, raw, lowered, run_id)
        if path not in ("/health", "/ready"):
            log(service=self.name, run_id=run_id, method=method, path=path, status=status)
        return status, body

    def _dispatch(self, method: str, path: str, raw: bytes, headers: dict[str, str],
                  run_id: str) -> tuple[int, Any]:
        for verb, pattern, handler in self.routes:
            found = pattern.match(path)
            if verb == method and found:
                return self._call(handler, found.groupdict(), raw, headers, run_id)
        return 404, {"error": "not found"}

    def _call(self, handler: Handler, params: dict[str, str], raw: bytes, headers: dict[str, str],
              run_id: str) -> tuple[int, Any]:
        if len(raw) > MAX_BODY:
            return 413, {"error": "body too large"}
        try:
            data = json.loads(raw) if raw else {}
        except ValueError:
            return 400, {"error": "invalid JSON"}
        if not isinstance(data, dict):
            return 400, {"error": "body must be a JSON object"}
        try:
            return handler({"body": data, "params": params, "headers": headers, "run_id": run_id})
        except Exception as exc:  # one failing request must not stop the service
            log(service=self.name, run_id=run_id, error=type(exc).__name__)
            return 500, {"error": "internal error"}

    def server(self, port: int) -> ThreadingHTTPServer:
        service = self

        class RequestHandler(BaseHTTPRequestHandler):
            timeout = 30

            def _serve(self) -> None:
                try:
                    length = int(self.headers.get("Content-Length") or 0)
                except ValueError:
                    length = -1
                if length < 0:
                    status, body = 400, {"error": "bad Content-Length"}
                elif length > MAX_BODY:
                    status, body = 413, {"error": "body too large"}
                else:
                    raw = self.rfile.read(length)
                    status, body = service.handle(self.command, self.path, raw, dict(self.headers))
                payload = json.dumps(body).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            do_GET = do_POST = do_PUT = do_DELETE = _serve

            def log_message(self, format: str, *args: Any) -> None:  # handle() logs as JSON
                pass

        return ThreadingHTTPServer(("0.0.0.0", port), RequestHandler)

    def run(self) -> None:
        signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))  # PID 1 ignores SIGTERM otherwise
        port = int(os.environ.get("PORT", "8000"))
        log(service=self.name, event="listening", port=port)
        self.server(port).serve_forever()
