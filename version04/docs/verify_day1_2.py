#!/usr/bin/env python3
"""Day 1-2 verification script for ActiveMolecule CRUD behavior."""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

os.environ["QCVIZ_CONTEXT_TRACKING_ENABLED"] = "true"

from qcviz_mcp.web.conversation_state import (
    ActiveMolecule,
    clear_active_molecule,
    get_active_molecule,
    get_molecule_history,
    set_active_molecule,
)

PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  OK  {name}")
        return
    FAIL += 1
    print(f"  FAIL {name} :: {detail}")


SID = "test-verify-day1-2"
print("=" * 60)
print("Day 1-2 Verification: ActiveMolecule CRUD")
print("=" * 60)

print("\n[1] Initial state")
mol = get_active_molecule(SID)
check("active_molecule is None initially", mol is None, f"got {mol}")

print("\n[2] set_active_molecule")
set_active_molecule(
    SID,
    {
        "canonical_name": "methylethylamine",
        "smiles": "CCNC",
        "formula": "C3H9N",
        "source": "test",
        "set_at_turn": 1,
    },
)
mol = get_active_molecule(SID)
check("active_molecule is set", mol is not None, "got None")
check("canonical_name correct", mol and mol.get("canonical_name") == "methylethylamine", f"got {mol}")
check("smiles correct", mol and mol.get("smiles") == "CCNC", f"got {mol}")

print("\n[3] Replace molecule and update history")
set_active_molecule(
    SID,
    {
        "canonical_name": "diethylamine",
        "smiles": "CCNCC",
        "source": "test",
        "set_at_turn": 2,
    },
)
mol = get_active_molecule(SID)
check("new active_molecule is diethylamine", mol and mol["canonical_name"] == "diethylamine", f"got {mol}")
hist = get_molecule_history(SID)
check("history has 1 entry", len(hist) == 1, f"len={len(hist)}")
check(
    "history[0] is methylethylamine",
    len(hist) > 0 and hist[0].get("canonical_name") == "methylethylamine",
    f"got {hist}",
)

print("\n[4] Same molecule re-set leaves history unchanged")
set_active_molecule(
    SID,
    {
        "canonical_name": "diethylamine",
        "smiles": "CCNCC",
        "source": "test",
        "set_at_turn": 3,
    },
)
hist = get_molecule_history(SID)
check("history still 1 entry", len(hist) == 1, f"len={len(hist)}")

print("\n[5] Third molecule grows history")
set_active_molecule(
    SID,
    {
        "canonical_name": "trimethylamine",
        "smiles": "CN(C)C",
        "source": "test",
        "set_at_turn": 4,
    },
)
hist = get_molecule_history(SID)
check("history has 2 entries", len(hist) == 2, f"len={len(hist)}")
check(
    "history[0] is diethylamine",
    len(hist) > 0 and hist[0].get("canonical_name") == "diethylamine",
    f"got {hist[0] if hist else 'empty'}",
)

print("\n[6] clear_active_molecule")
clear_active_molecule(SID)
mol = get_active_molecule(SID)
check("active_molecule is None after clear", mol is None, f"got {mol}")
hist = get_molecule_history(SID)
check("history preserved after clear", len(hist) == 2, f"len={len(hist)}")

print("\n[7] Feature flag off makes set a no-op")
os.environ["QCVIZ_CONTEXT_TRACKING_ENABLED"] = "false"
SID2 = "test-flag-off"
set_active_molecule(
    SID2,
    {
        "canonical_name": "water",
        "smiles": "O",
        "source": "test",
        "set_at_turn": 1,
    },
)
mol = get_active_molecule(SID2)
check("molecule NOT set when flag is off", mol is None, f"got {mol}")
os.environ["QCVIZ_CONTEXT_TRACKING_ENABLED"] = "true"

print("\n[8] Missing canonical_name makes set a no-op")
SID3 = "test-no-name"
invalid_molecule: ActiveMolecule = {
    "smiles": "CCNC",
    "source": "test",
    "set_at_turn": 1,
}
set_active_molecule(SID3, invalid_molecule)
mol = get_active_molecule(SID3)
check("molecule NOT set without canonical_name", mol is None, f"got {mol}")

print("\n[9] Type import check")
check("ActiveMolecule is importable", ActiveMolecule is not None)

print("\n" + "=" * 60)
total = PASS + FAIL
print(f"Results: {PASS}/{total} passed, {FAIL} failed")
if FAIL:
    print("SOME TESTS FAILED")
    raise SystemExit(1)
print("ALL PASS")
