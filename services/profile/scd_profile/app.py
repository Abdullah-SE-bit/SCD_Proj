"""M2 profile: routes. Rules are in services.py, SQL in repositories.py.

These routes are internal: only the gateway authenticates users and the cluster network is the boundary.
Without a database address the probes work and the other routes answer 503.
"""

import os
from collections.abc import Callable
from typing import Any

from scd_profile import compare, history
from scd_profile.base import Request, Service, log
from scd_profile.cache import Redis, VerdictCache
from scd_profile.db import Database, url_from_env
from scd_profile.services import BadCredentials, Exists, Invalid, NotFound, ProfileService

Answer = tuple[int, Any]
Action = Callable[[ProfileService, Request], Answer]


def ready(database: Database | None) -> bool:
    """A configured database has to answer; with none configured there is nothing to wait for."""
    if database is None:
        return True
    try:
        with database.transaction() as tx:
            tx.run("SELECT 1")
    except Exception:  # any driver or network error means "not ready"
        return False
    return True


url = url_from_env(os.environ)
database = Database.from_url(url) if url else None
service = Service("profile", "M2", ready=lambda: ready(database))
cache_url = os.environ.get("REDIS_URL", "")
verdicts = VerdictCache(Redis(cache_url) if cache_url else None)  # no address, no cache: every lookup misses


def api(method: str, path: str) -> Callable[[Action], None]:
    """A route over the service layer that turns its errors into answers."""

    def register(action: Action) -> None:
        def handle(request: Request) -> Answer:
            if database is None:
                return 503, {"error": "the database is not configured"}
            try:
                return action(ProfileService(database), request)
            except Invalid as error:
                return 400, {"error": str(error)}
            except Exists as error:
                return 409, {"error": str(error)}
            except NotFound as error:
                return 404, {"error": str(error)}
            except BadCredentials:
                return 401, {"error": "wrong email or password"}

        service.route(method, path)(handle)

    return register


@api("POST", "/users")
def add_user(records: ProfileService, request: Request) -> Answer:
    return 201, {"user_id": records.register(request["body"].get("email"), request["body"].get("password"))}


@api("POST", "/sessions")
def open_session(records: ProfileService, request: Request) -> Answer:
    return 200, {"user_id": records.authenticate(request["body"].get("email"), request["body"].get("password"))}


@api("GET", "/users/{user_id}/profile")
def read_profile(records: ProfileService, request: Request) -> Answer:
    return 200, records.profile(request["params"]["user_id"])


@api("PUT", "/users/{user_id}/profile")
def write_profile(records: ProfileService, request: Request) -> Answer:
    return 200, records.save_profile(request["params"]["user_id"], request["body"])


@api("POST", "/users/{user_id}/ideas")
def add_idea(records: ProfileService, request: Request) -> Answer:
    body = request["body"]
    return 201, records.create_idea(request["params"]["user_id"], body.get("title"), body.get("text"),
                                    body.get("source", "own"))


@api("GET", "/users/{user_id}/ideas")
def list_ideas(records: ProfileService, request: Request) -> Answer:
    return 200, history.ideas(records, request["params"]["user_id"])


@api("POST", "/users/{user_id}/ideas/{idea_id}/versions")
def add_version(records: ProfileService, request: Request) -> Answer:
    params = request["params"]
    return 201, records.revise_idea(params["user_id"], params["idea_id"], request["body"].get("text"))


@api("GET", "/users/{user_id}/ideas/{idea_id}/versions")
def list_versions(records: ProfileService, request: Request) -> Answer:
    return 200, history.versions(records, request["params"]["user_id"], request["params"]["idea_id"])


@api("POST", "/users/{user_id}/ideas/{idea_id}/versions/{version}/verdict")
def add_verdict(records: ProfileService, request: Request) -> Answer:
    params = request["params"]
    return 201, history.save_verdict(records, params["user_id"], params["idea_id"], params["version"],
                                     request["body"])


@api("POST", "/users/{user_id}/compare")
def compare_ideas(records: ProfileService, request: Request) -> Answer:
    return 200, compare.compare(records, request["params"]["user_id"], request["body"].get("ideas"))


CACHE = "/users/{user_id}/ideas/{idea_id}/versions/{version}/cache"


def parts_of(records: ProfileService, request: Request) -> dict[str, Any]:
    params = request["params"]
    return history.cache_parts(records, params["user_id"], params["idea_id"], params["version"], request["body"])


@api("POST", f"{CACHE}/lookup")
def look_up(records: ProfileService, request: Request) -> Answer:
    found = verdicts.get(parts_of(records, request))
    if found is not None:
        log(service="profile", run_id=request["run_id"], event="cache_hit", verdict=found.get("verdict"))
    return 200, {"hit": found is not None, "verdict": found}


@api("PUT", CACHE)
def remember(records: ProfileService, request: Request) -> Answer:
    document = request["body"].get("verdict")
    if not isinstance(document, dict):
        raise Invalid("not a verdict document")
    history.check_verdict(document)
    return 200, {"stored": verdicts.put(parts_of(records, request), document)}


@service.route("GET", "/metrics")
def metrics(request: Request) -> Answer:
    return 200, verdicts.metrics()


if __name__ == "__main__":
    service.run()
