#!/usr/bin/env python3
"""Claude Code hook entry point. Usage: guard.py pre-tool|session-start|stop"""
import runpy
import sys
from pathlib import Path

scd = runpy.run_path(str(Path(__file__).resolve().parents[2] / "harness" / "verification" / "scd.py"))
sys.exit(scd["main"](["hook", *sys.argv[1:]]))
