"""M1 public API: accounts, profile and the walking-skeleton run.

/validate and /runs serve one fixed verdict, labelled FIXTURE DATA, and need no login until the UI has one
(P02.04). Nothing is evaluated and the orchestrator is not called yet; the real flow arrives with P05.04.
"""

import os
import re
import secrets
from typing import Any

from scd_gateway import tokens
from scd_gateway.base import Request, log
from scd_gateway.limits import RateLimiter
from scd_gateway.query import QueryService, parameters
from scd_gateway.upstream import Client, Unavailable

MAX_IDEA = 2000
IDEA_ID = re.compile(r"[A-Za-z0-9_]{1,80}")
RUN_ID = "fixture-run"
SCORES = {"demand_pain": (3.5, 15), "competition": (2.0, 15), "differentiation": (3.0, 15),
          "feasibility": (4.0, 25), "risk": (3.5, 10), "learning": (4.5, 20)}  # dimension: score, weight
RUN: dict[str, Any] = {
    "run_id": RUN_ID,
    "status": "completed",
    "label": "FIXTURE DATA",
    "verdict": {
        "idea_id": "fixture-idea", "version": 1, "run_id": RUN_ID,
        "verdict": "GO", "stability": "BORDERLINE", "score": 70.5, "confidence": 0.74,
        "gates": {"evidence": "pass", "feasibility": "pass", "risk": "pass", "duplicate": "pass"},
        "weights": {dimension: weight for dimension, (_, weight) in SCORES.items()},
        "thresholds": {"T_go": 70, "T_no": 50, "floor": 1.5},
        "scores": [{"dimension": dimension, "score": score, "confidence": 0.7,
                    "evidence_ids": ["fixture_card#c0"], "features": {},
                    "reason": "FIXTURE DATA: no evidence was collected or scored.",
                    "rubric_version": f"{dimension}@v0", "model": "fixture"}
                   for dimension, (score, _) in SCORES.items()],
        "weakest_dimension": "competition",
        "what_would_make_go": [],
        "sensitivity": {"runs": 14, "flipped": 3},
        "versions": {"engine": "fixture", "rubrics": "fixture", "profile_weights": "fixture"},
    },
}

# per minute: logins for one email; all registrations; all validations (a request carries no client address)
LOGINS, REGISTRATIONS, VALIDATIONS = 5, 20, 60
service = QueryService("gateway", "M1")
profile = Client(os.environ.get("PROFILE_URL", "http://profile:8000"))
limiter = RateLimiter()
key = os.environ.get("JWT_SIGNING_KEY", "").encode()
if len(key) < 32:  # never a built-in key: without one, logins end when the process does
    log(service="gateway", event="JWT_SIGNING_KEY missing or shorter than 32 characters; using a temporary key")
    key = secrets.token_bytes(32)


def limited(name: str, limit: int) -> tuple[int, Any] | None:
    wait = limiter.wait(name, limit)
    return (429, {"error": "too many requests", "retry_after": wait}) if wait else None


def credentials(body: dict[str, Any]) -> bool:
    """Shape and size only; the profile service holds the rules."""
    return (set(body) == {"email", "password"} and all(isinstance(value, str) for value in body.values())
            and len(body["email"]) <= 254 and len(body["password"]) <= 128)


def forward(method: str, path: str, body: Any = None) -> tuple[int, Any]:
    try:
        return profile(method, path, body)
    except Unavailable as error:
        log(service="gateway", error=f"profile: {error}")
        return 503, {"error": "accounts are unavailable"}


@service.route("POST", "/auth/register")
def register(request: Request) -> tuple[int, Any]:
    if not credentials(request["body"]):
        return 400, {"error": "send an email and a password"}
    return limited("register", REGISTRATIONS) or forward("POST", "/users", request["body"])


@service.route("POST", "/auth/login")
def login(request: Request) -> tuple[int, Any]:
    body = request["body"]
    if not credentials(body):
        return 400, {"error": "send an email and a password"}
    refused = limited(f"login:{body['email'].strip().lower()}", LOGINS)
    if refused:
        return refused
    status, answer = forward("POST", "/sessions", body)
    return (200, {"token": tokens.issue(answer["user_id"], key)}) if status == 200 else (status, answer)


def signed_in(request: Request) -> str | None:
    scheme, _, token = request["headers"].get("authorization", "").partition(" ")
    return tokens.user_of(token.strip(), key) if scheme.lower() == "bearer" else None


@service.route("GET", "/profile")
def read_profile(request: Request) -> tuple[int, Any]:
    user = signed_in(request)
    return forward("GET", f"/users/{user}/profile") if user else (401, {"error": "log in first"})


@service.route("PUT", "/profile")
def write_profile(request: Request) -> tuple[int, Any]:
    user = signed_in(request)
    if not user:
        return 401, {"error": "log in first"}
    if request["body"].get("user_id", user) != user:
        return 403, {"error": "this is not your profile"}
    return forward("PUT", f"/users/{user}/profile", request["body"] | {"user_id": user})


@service.route("GET", "/ideas")
def list_ideas(request: Request) -> tuple[int, Any]:
    user = signed_in(request)
    return forward("GET", f"/users/{user}/ideas") if user else (401, {"error": "log in first"})


@service.route("GET", "/ideas/{id}/versions")
def list_versions(request: Request) -> tuple[int, Any]:
    user = signed_in(request)
    if not user:
        return 401, {"error": "log in first"}
    idea_id = request["params"]["id"]
    if not IDEA_ID.fullmatch(idea_id):  # it becomes part of an internal address
        return 404, {"error": "no such idea"}
    return forward("GET", f"/users/{user}/ideas/{idea_id}/versions")


@service.route("GET", "/compare")
def compare(request: Request) -> tuple[int, Any]:
    user = signed_in(request)
    if not user:
        return 401, {"error": "log in first"}
    query = parameters(request)
    chosen = [value for name in ("a", "b") for value in query.get(name, [])[:1]]
    if len(chosen) != 2 or chosen[0] == chosen[1] or not all(IDEA_ID.fullmatch(value) for value in chosen):
        return 400, {"error": "name two different ideas as a and b"}
    return forward("POST", f"/users/{user}/compare", {"ideas": chosen})


@service.route("GET", "/metrics")
def metrics(request: Request) -> tuple[int, Any]:
    """Counts only, no user data."""
    status, answer = forward("GET", "/metrics")
    return (200, {"cache": answer}) if status == 200 else (status, answer)


@service.route("POST", "/validate")
def validate(request: Request) -> tuple[int, Any]:
    idea = request["body"].get("idea")
    if not isinstance(idea, str) or not idea.strip() or len(idea) > MAX_IDEA:
        return 400, {"error": f"idea must be text of 1 to {MAX_IDEA} characters"}
    return limited("validate", VALIDATIONS) or (200, {"run_id": RUN_ID})


@service.route("GET", "/runs/{id}")
def run(request: Request) -> tuple[int, Any]:
    if request["params"]["id"] != RUN_ID:
        return 404, {"error": "unknown run"}
    return 200, RUN


if __name__ == "__main__":
    service.run()
