#!/usr/bin/env python3
"""Day 3-4 verification script for implicit follow-up detection."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from qcviz_mcp.llm.normalizer import detect_implicit_follow_up
from qcviz_mcp.llm.schemas import IngressResult

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


print("=" * 64)
print("Day 3-4 Verification: Implicit Follow-up Detection")
print("=" * 64)

print("\n[1] Modification intent - Korean")
result = detect_implicit_follow_up(
    "치환기를 하나만 바꾸면?",
    has_active_molecule=True,
    has_explicit_molecule_name=False,
)
check("korean modification implicit", result["is_implicit_follow_up"] is True, str(result))
check("korean modification type", result["follow_up_type"] == "modification_request", str(result))
check("korean modification signal", result["modification_detected"] is True, str(result))

result = detect_implicit_follow_up(
    "메틸기를 에틸기로 교체하면 어떻게 돼?",
    has_active_molecule=True,
    has_explicit_molecule_name=False,
)
check("group swap modification", result["follow_up_type"] == "modification_request", str(result))

result = detect_implicit_follow_up(
    "작용기를 제거하면?",
    has_active_molecule=True,
    has_explicit_molecule_name=False,
)
check("functional group removal", result["is_implicit_follow_up"] is True, str(result))

print("\n[2] Modification intent - English")
result = detect_implicit_follow_up(
    "what if I swap the methyl group?",
    has_active_molecule=True,
    has_explicit_molecule_name=False,
)
check("english swap modification", result["follow_up_type"] == "modification_request", str(result))

result = detect_implicit_follow_up(
    "if we replace the substituent with ethyl",
    has_active_molecule=True,
    has_explicit_molecule_name=False,
)
check("english replace modification", result["is_implicit_follow_up"] is True, str(result))

print("\n[3] Comparison intent")
result = detect_implicit_follow_up(
    "이성질체랑 비교하면?",
    has_active_molecule=True,
    has_explicit_molecule_name=False,
)
check("isomer comparison korean", result["follow_up_type"] == "comparison_request", str(result))

result = detect_implicit_follow_up(
    "compare with the isomer",
    has_active_molecule=True,
    has_explicit_molecule_name=False,
)
check("isomer comparison english", result["follow_up_type"] == "comparison_request", str(result))

result = detect_implicit_follow_up(
    "차이가 뭐야?",
    has_active_molecule=True,
    has_explicit_molecule_name=False,
)
check("difference question comparison", result["follow_up_type"] == "comparison_request", str(result))

print("\n[4] Subject-absent patterns")
result = detect_implicit_follow_up(
    "그럼 에너지는?",
    has_active_molecule=True,
    has_explicit_molecule_name=False,
)
check("subject absent energy", result["follow_up_type"] == "structure_reference", str(result))

result = detect_implicit_follow_up(
    "그럼 HOMO는 어떻게 생겼어?",
    has_active_molecule=True,
    has_explicit_molecule_name=False,
)
check("subject absent homo", result["is_implicit_follow_up"] is True, str(result))

result = detect_implicit_follow_up(
    "만약 온도를 올리면?",
    has_active_molecule=True,
    has_explicit_molecule_name=False,
)
check("subject absent conditional", result["is_implicit_follow_up"] is True, str(result))

print("\n[5] Negative: no active_molecule")
result = detect_implicit_follow_up(
    "치환기를 하나만 바꾸면?",
    has_active_molecule=False,
    has_explicit_molecule_name=False,
)
check("needs active molecule", result["is_implicit_follow_up"] is False, str(result))
check("pattern still detected", result["modification_detected"] is True, str(result))

print("\n[6] Negative: explicit molecule name present")
result = detect_implicit_follow_up(
    "벤젠의 치환기를 바꾸면?",
    has_active_molecule=True,
    has_explicit_molecule_name=True,
)
check("explicit molecule suppresses implicit", result["is_implicit_follow_up"] is False, str(result))

print("\n[7] Negative: plain question with no signals")
result = detect_implicit_follow_up(
    "양자화학이 뭐야?",
    has_active_molecule=True,
    has_explicit_molecule_name=False,
)
check("plain question ignored", result["is_implicit_follow_up"] is False, str(result))

result = detect_implicit_follow_up(
    "안녕하세요",
    has_active_molecule=True,
    has_explicit_molecule_name=False,
)
check("greeting ignored", result["is_implicit_follow_up"] is False, str(result))

print("\n[8] Edge case: empty input")
result = detect_implicit_follow_up("", has_active_molecule=True, has_explicit_molecule_name=False)
check("empty string ignored", result["is_implicit_follow_up"] is False, str(result))

result = detect_implicit_follow_up(None, has_active_molecule=True, has_explicit_molecule_name=False)
check("None ignored", result["is_implicit_follow_up"] is False, str(result))

print("\n[9] schemas.py field check")
schema = IngressResult()
check("IngressResult.context_molecule_name exists", hasattr(schema, "context_molecule_name"), "field missing")
check(
    "IngressResult.context_molecule_smiles exists",
    hasattr(schema, "context_molecule_smiles"),
    "field missing",
)
check("context_molecule_name defaults to None", schema.context_molecule_name is None, str(schema.context_molecule_name))
check(
    "context_molecule_smiles defaults to None",
    schema.context_molecule_smiles is None,
    str(schema.context_molecule_smiles),
)

print("\n" + "=" * 64)
total = PASS + FAIL
print(f"Results: {PASS}/{total} passed, {FAIL} failed")
if FAIL:
    print("SOME TESTS FAILED")
    raise SystemExit(1)
print("ALL PASS")
