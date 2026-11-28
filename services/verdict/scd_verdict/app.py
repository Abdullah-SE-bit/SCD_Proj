"""M11 verdict engine service. The only module that produces verdicts (CMN-003)."""

from typing import Any

from scd_verdict import api
from scd_verdict import config as rules
from scd_verdict.base import Request, Service


def ready() -> bool:
    try:
        rules.load()
    except (OSError, ValueError):
        return False
    return True


service = Service("verdict", "M11", ready=ready)


@service.route("POST", "/verdict")
def post_verdict(request: Request) -> tuple[int, Any]:
    try:
        return 200, api.verdict(request["body"], request["run_id"])
    except rules.InvalidInput as error:
        return 400, {"error": str(error)}


@service.route("POST", "/whatif")
def post_whatif(request: Request) -> tuple[int, Any]:
    try:
        return 200, api.whatif(request["body"], request["run_id"])
    except rules.InvalidInput as error:
        return 400, {"error": str(error)}


if __name__ == "__main__":
    service.run()
