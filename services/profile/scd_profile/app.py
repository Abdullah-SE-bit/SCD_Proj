"""M2 profile: routes. Rules are in services.py, SQL in repositories.py.

These routes are internal: only the gateway authenticates users and the cluster network is the boundary.
Without a database address the probes work and the other routes answer 503.
"""

import os
from collections.abc import Callable
from typing import Any

from scd_profile.base import Request, Service
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


if __name__ == "__main__":
    service.run()
