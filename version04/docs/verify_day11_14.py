#!/usr/bin/env python3
"""Verification for Day 11-14 prompt/context additions."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

os.environ["QCVIZ_CONTEXT_TRACKING_ENABLED"] = "true"

from qcviz_mcp.config import ServerConfig
from qcviz_mcp.llm.normalizer import detect_implicit_follow_up
from qcviz_mcp.llm.schemas import IngressResult, PlanResponse
from qcviz_mcp.llm.trace import PipelineTrace
from qcviz_mcp.web.conversation_state import (
    clear_conversation_state,
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
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        suffix = f" :: {detail}" if detail else ""
        print(f"  [FAIL] {name}{suffix}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


print("=" * 64)
print("Day 11-14 Verification")
print("=" * 64)

print("\n[1] Schema fields")
plan = PlanResponse.model_validate(
    {
        "intent": "analyze",
        "context_molecule_name": "  ",
        "context_molecule_smiles": "",
        "implicit_follow_up_type": "modification_request",
    }
)
check("PlanResponse.context_molecule_name exists", hasattr(plan, "context_molecule_name"))
check("PlanResponse.context_molecule_smiles exists", hasattr(plan, "context_molecule_smiles"))
check("PlanResponse.implicit_follow_up_type exists", hasattr(plan, "implicit_follow_up_type"))
check(
    "PlanResponse blank strings normalize to None",
    plan.context_molecule_name is None and plan.context_molecule_smiles is None,
    f"{plan.context_molecule_name!r}, {plan.context_molecule_smiles!r}",
)
check(
    "PlanResponse keeps implicit follow-up type",
    plan.implicit_follow_up_type == "modification_request",
    repr(plan.implicit_follow_up_type),
)

print("\n[2] Existing context carriers")
ingress = IngressResult()
check("IngressResult.context_molecule_name exists", hasattr(ingress, "context_molecule_name"))
check("IngressResult.context_molecule_smiles exists", hasattr(ingress, "context_molecule_smiles"))

print("\n[3] Config flag")
cfg = ServerConfig()
check("context_tracking_enabled exists", hasattr(cfg, "context_tracking_enabled"))
check("context_tracking_enabled default is False", cfg.context_tracking_enabled is False)

print("\n[4] Prompt assets")
prompt_dir = ROOT / "src" / "qcviz_mcp" / "llm" / "prompt_assets"
prompt_checks = [
    ("ingress_rewrite.md", ["Korean Implicit Follow-up Patterns", "modification_request", "치환기를 바꾸면?"]),
    ("grounding_decider.md", ["Follow-up Context Rule", 'decision="direct_answer"']),
    ("semantic_expansion.md", ["Modification Queries", "scaffold molecule"]),
    ("action_planner.md", ["Conversation Context", "molecule_from_context"]),
]
for filename, keywords in prompt_checks:
    content = read_text(prompt_dir / filename)
    missing = [keyword for keyword in keywords if keyword not in content]
    check(f"{filename} contains expected additions", not missing, ", ".join(missing))

print("\n[5] Environment template")
env_content = read_text(ROOT / ".env.example")
check(
    ".env.example documents context tracking flag",
    "QCVIZ_CONTEXT_TRACKING_ENABLED=false" in env_content,
)

print("\n[6] Pipeline trace context tracking")
trace = PipelineTrace(
    trace_id="trace-day11-14",
    context_molecule_name="methylethylamine",
    context_molecule_smiles="CCNC",
    implicit_follow_up_type="modification_request",
    follow_up_detected=True,
)
trace_payload = trace.to_log_dict()
check("trace contains context_tracking block", "context_tracking" in trace_payload)
check(
    "trace context block includes active molecule and follow-up",
    trace_payload.get("context_tracking")
    == {
        "active_molecule": "methylethylamine",
        "implicit_follow_up": "modification_request",
        "follow_up_detected": True,
    },
    repr(trace_payload.get("context_tracking")),
)

print("\n[7] E2E context simulation")
session_id = "verify-day11-14"
try:
    set_active_molecule(
        session_id,
        {
            "canonical_name": "methylethylamine",
            "smiles": "CCNC",
            "formula": "C3H9N",
            "source": "chat_grounding",
            "set_at_turn": 1,
        },
    )
    active = get_active_molecule(session_id)
    check(
        "active molecule persists",
        bool(active and active.get("canonical_name") == "methylethylamine"),
        repr(active),
    )

    follow_up = detect_implicit_follow_up(
        "치환기를 하나만 바꿔보면?",
        has_active_molecule=True,
        has_explicit_molecule_name=False,
    )
    check(
        "implicit follow-up detection works",
        follow_up["is_implicit_follow_up"] and follow_up["follow_up_type"] == "modification_request",
        repr(follow_up),
    )

    set_active_molecule(
        session_id,
        {
            "canonical_name": "benzene",
            "smiles": "c1ccccc1",
            "source": "chat_grounding",
            "set_at_turn": 2,
        },
    )
    history = get_molecule_history(session_id)
    current = get_active_molecule(session_id)
    check(
        "active molecule updates to latest value",
        bool(current and current.get("canonical_name") == "benzene"),
        repr(current),
    )
    check(
        "previous molecule moves to history",
        bool(history and history[0].get("canonical_name") == "methylethylamine"),
        repr(history),
    )
finally:
    clear_conversation_state(session_id)

print("\n" + "=" * 64)
total = PASS + FAIL
print(f"Results: {PASS}/{total} passed, {FAIL} failed")
if FAIL:
    sys.exit(1)
