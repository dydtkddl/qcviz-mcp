#!/usr/bin/env python3
"""Day 7 final regression wrapper.

This file is the docs-facing launcher for the root regression script.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "verify_regression_all.py"

if not ENTRY.exists():
    raise SystemExit(f"Missing regression entry script: {ENTRY}")

sys.path.insert(0, str(ROOT))
runpy.run_path(str(ENTRY), run_name="__main__")

