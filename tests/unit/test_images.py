"""Every module has its own image that is multi-stage, non-root and pinned (REP-002, DKR-001, DKR-002)."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
# every directory of the two roots that holds a Python package
MODULES = sorted({p.parents[1] for area in ("services", "jobs") for p in ROOT.glob(f"{area}/*/scd_*/__init__.py")})


def test_at_least_six_module_images():
    assert len([m for m in MODULES if (m / "Dockerfile").is_file()]) >= 6


@pytest.mark.parametrize("module", MODULES, ids=lambda m: m.name)
def test_image_rules(module):
    text = (module / "Dockerfile").read_text(encoding="utf-8")
    bases = re.findall(r"^FROM (\S+)", text, re.M)
    assert len(bases) >= 2, "multi-stage build"
    assert all(re.search(r"@sha256:[0-9a-f]{64}$", b) for b in bases), "base images pinned by digest"
    users = re.findall(r"^USER (\S+)", text, re.M)
    assert users and users[-1].split(":")[0] not in ("root", "0"), "non-root"
    assert (module / ".dockerignore").is_file()
    requirements = (module / "requirements.txt").read_text(encoding="utf-8").splitlines()
    assert all("==" in line for line in requirements if line.strip() and not line.startswith("#")), "pinned"
