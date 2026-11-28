"""No file that goes into an image carries a hard-coded local address (CMN-005)."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCAL = re.compile(r"localhost|127\.0\.0\.1", re.I)
SHIPPED = ("Dockerfile", "scd_*/**/*.py", "src/**/*", "nginx/**/*", "index.html")


def test_no_local_address_in_image_files():
    modules = [*ROOT.glob("services/*"), *ROOT.glob("jobs/*")]
    files = [p for module in modules for pattern in SHIPPED for p in module.glob(pattern)
             if p.is_file() and ".test." not in p.name]
    assert {"app.py", "api.ts", "default.conf.template"} <= {p.name for p in files}, "the scan reaches both sides"
    assert [p.relative_to(ROOT).as_posix() for p in files if LOCAL.search(p.read_text(encoding="utf-8"))] == []
