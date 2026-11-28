"""The verdict-unit-tests check runs this directory; engine tests arrive with P03.01."""

from scd_verdict.app import service


def test_probes():
    assert service.handle("GET", "/health")[0] == 200
    assert service.handle("GET", "/ready")[0] == 200
