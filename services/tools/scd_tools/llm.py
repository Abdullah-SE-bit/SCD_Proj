"""POST /llm: the hosted model through M5, so the key stays here and no other module needs the internet.

The provider is OpenAI-compatible (Groq free tier by default). Every call is counted against a budget per run and per
day, reserved before the call so parallel callers cannot overshoot. The answer is untrusted data for the caller.

ponytail: budgets are in memory (one replica, reset on restart); persist them if M5 is scaled or restarted often.
"""

import datetime
import json
import os
import threading
from typing import Any
from urllib.parse import urlsplit

from scd_tools import policy, transport

DEFAULT_BASE = "https://api.groq.com/openai/v1"
PROVIDERS = ("api.groq.com",)
MAX_OUTPUT, MAX_PROMPT_CHARS = 2048, 60_000
RUN_CAP, DAY_CAP = 40_000, 400_000
ROLES = ("system", "user", "assistant")


class Invalid(ValueError):
    pass


class Unavailable(Exception):
    """No provider is configured."""


class OverBudget(Exception):
    pass


class ProviderError(Exception):
    def __init__(self, message: str, retry_after: str | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class Budget:
    def __init__(self, run_cap: int, day_cap: int, today: Any = None) -> None:
        self.run_cap, self.day_cap = run_cap, day_cap
        self.today = today or (lambda: datetime.datetime.now(datetime.UTC).date())
        self.day, self.day_used = self.today(), 0
        self.runs: dict[str, int] = {}
        self.lock = threading.Lock()

    def reserve(self, run_id: str, tokens: int) -> None:
        with self.lock:
            if self.today() != self.day:
                self.day, self.day_used, self.runs = self.today(), 0, {}
            if self.runs.get(run_id, 0) + tokens > self.run_cap:
                raise OverBudget(f"run token budget of {self.run_cap} would be exceeded")
            if self.day_used + tokens > self.day_cap:
                raise OverBudget(f"daily token budget of {self.day_cap} would be exceeded")
            self.runs[run_id] = self.runs.get(run_id, 0) + tokens
            self.day_used += tokens

    def settle(self, run_id: str, reserved: int, used: int) -> int:
        """Replace a reservation with what the call really used."""
        with self.lock:
            self.runs[run_id] = max(0, self.runs.get(run_id, 0) - reserved + used)
            self.day_used = max(0, self.day_used - reserved + used)
            return self.runs[run_id]


def check_request(body: dict[str, Any]) -> dict[str, Any]:
    messages = body.get("messages")
    if not isinstance(messages, list) or not 1 <= len(messages) <= 50 or not all(
            isinstance(m, dict) and m.get("role") in ROLES and isinstance(m.get("content"), str) for m in messages):
        raise Invalid("messages must be a list of role and content")
    if sum(len(m["content"]) for m in messages) > MAX_PROMPT_CHARS:
        raise Invalid(f"messages exceed {MAX_PROMPT_CHARS} characters")
    max_tokens = body.get("max_tokens", 512)
    if isinstance(max_tokens, bool) or not isinstance(max_tokens, int) or not 1 <= max_tokens <= MAX_OUTPUT:
        raise Invalid(f"max_tokens must be 1 to {MAX_OUTPUT}")
    temperature = body.get("temperature", 0)
    if isinstance(temperature, bool) or not isinstance(temperature, (int, float)) or not 0 <= temperature <= 2:
        raise Invalid("temperature must be 0 to 2")
    request: dict[str, Any] = {"messages": [{"role": m["role"], "content": m["content"]} for m in messages],
                               "max_tokens": max_tokens, "temperature": temperature}
    if body.get("json") is True:
        request["response_format"] = {"type": "json_object"}
    return request


class Proxy:
    def __init__(self, send: Any = transport.send, resolver: policy.Resolver = policy.resolve,
                 env: dict[str, str] | None = None, budget: Budget | None = None) -> None:
        self.send, self.resolver = send, resolver
        self.env = os.environ if env is None else env
        self.budget = budget or Budget(RUN_CAP, DAY_CAP)

    def complete(self, body: dict[str, Any], run_id: str) -> dict[str, Any]:
        request = check_request(body)
        run_id = body["run_id"] if isinstance(body.get("run_id"), str) and body["run_id"] else run_id
        key, model = self.env.get("HOSTED_LLM_API_KEY", ""), self.env.get("HOSTED_LLM_MODEL", "")
        base = urlsplit(self.env.get("HOSTED_LLM_BASE_URL") or DEFAULT_BASE)
        if not key or not model:
            raise Unavailable("the hosted model is not configured (API key and model name)")
        if base.scheme != "https" or base.hostname not in PROVIDERS:
            raise Unavailable("the hosted model address is not an allowed provider")
        reserved = sum(len(m["content"]) for m in request["messages"]) // 3 + request["max_tokens"]
        self.budget.reserve(run_id, reserved)
        used = 0
        try:
            answer = self._call(str(base.hostname), base.path.rstrip("/") + "/chat/completions", key,
                                {"model": model, **request})
            content = answer["choices"][0]["message"]["content"]
            usage = answer.get("usage") or {}
            used = int(usage.get("total_tokens") or reserved)  # unknown usage is charged in full
        except (KeyError, IndexError, TypeError, ValueError):
            used = reserved
            raise ProviderError("the provider answer was not understood") from None
        finally:
            total = self.budget.settle(run_id, reserved, used)
        return {"content": content, "model": answer.get("model", model), "usage": usage,
                "run_tokens_used": total, "run_tokens_cap": self.budget.run_cap}

    def _call(self, host: str, path: str, key: str, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                   "Accept-Encoding": "identity", "User-Agent": "idea-validator-course-project/0.1"}
        try:
            address = policy.public_address(host, self.resolver)
            reply = self.send("POST", host, address, path, headers, json.dumps(payload).encode(), 60, 2_000_000)
        except ConnectionError as error:
            raise ProviderError(str(error)) from None
        if reply.status != 200:  # the provider's body is not passed on: it may echo the request
            raise ProviderError(f"the provider answered {reply.status}", reply.headers.get("retry-after"))
        return json.loads(reply.body)
