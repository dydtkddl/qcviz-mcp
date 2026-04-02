#!/usr/bin/env python3
"""Day 5-7 verification script for pipeline context injection."""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

os.environ["QCVIZ_CONTEXT_TRACKING_ENABLED"] = "true"
logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")

from qcviz_mcp.llm.normalizer import normalize_user_text
from qcviz_mcp.llm.pipeline import QCVizPromptPipeline
from qcviz_mcp.llm.schemas import IngressRewriteResult
from qcviz_mcp.web.conversation_state import (
    clear_conversation_state,
    get_active_molecule,
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


class _CaptureActionPlannerPipeline(QCVizPromptPipeline):
    def __init__(self) -> None:
        super().__init__(
            provider="openai",
            openai_api_key="dummy",
            enabled=True,
            stage1_enabled=False,
            stage2_enabled=True,
        )
        self.captured_payload = None

    def _invoke_structured_stage(self, *, stage_name, response_model, payload, **kwargs):
        self.captured_payload = payload
        return response_model.model_validate(
            {
                "lane": "chat_only",
                "confidence": 0.88,
                "reasoning": "captured router output",
            }
        )


print("=" * 64)
print("Day 5-7 Verification: Pipeline Context Injection")
print("=" * 64)

session_id = "test-pipeline-day57"
set_active_molecule(
    session_id,
    {
        "canonical_name": "methylethylamine",
        "smiles": "CCNC",
        "formula": "C3H9N",
        "source": "test",
        "set_at_turn": 1,
    },
)

print("\n[0] Prerequisites: active_molecule")
active = get_active_molecule(session_id)
check(
    "active_molecule set successfully",
    active is not None and active.get("canonical_name") == "methylethylamine",
    f"got {active}",
)

print("\n[1] Import checks")
check("QCVizPromptPipeline importable", QCVizPromptPipeline is not None)

print("\n[2] _run_ingress_rewrite implicit follow-up detection")
pipe = QCVizPromptPipeline(enabled=False)
message = "치환기를 하나만 바꾸면?"
hint = normalize_user_text(message)
rewrite = pipe._run_ingress_rewrite(message, hint, {"session_id": session_id})
check("_run_ingress_rewrite executed", isinstance(rewrite, IngressRewriteResult), str(type(rewrite)))
check("is_follow_up = True", rewrite.is_follow_up is True, f"got {rewrite.is_follow_up}")
check(
    "context_molecule_name = methylethylamine",
    rewrite.context_molecule_name == "methylethylamine",
    f"got {rewrite.context_molecule_name}",
)
check(
    "context_molecule_smiles = CCNC",
    rewrite.context_molecule_smiles == "CCNC",
    f"got {rewrite.context_molecule_smiles}",
)

print("\n[3] _run_action_planner conversation context payload")
capture = _CaptureActionPlannerPipeline()
plan = capture._run_action_planner(message, rewrite, hint, {"session_id": session_id}, None)
conversation_context = capture.captured_payload.get("conversation_context") if capture.captured_payload else None
check("planner returned lane", plan.get("lane") == "chat_only", str(plan))
check("conversation_context exists", isinstance(conversation_context, dict), str(conversation_context))
check(
    "conversation_context.active_molecule.name set",
    conversation_context and conversation_context.get("active_molecule", {}).get("name") == "methylethylamine",
    str(conversation_context),
)
check(
    "conversation_context.is_follow_up set",
    conversation_context and conversation_context.get("is_follow_up") is True,
    str(conversation_context),
)

print("\n[4] heuristic fallback receives active_molecule")
captured_context = {}


def _heuristic_stub(raw_text, context, normalized_hint):
    captured_context.update(context)
    return {
        "intent": "chat",
        "job_type": "chat",
        "query_kind": "chat_only",
        "planner_lane": "chat_only",
        "provider": "heuristic",
    }


pipe.execute(message, {"session_id": session_id}, heuristic_planner=_heuristic_stub)
check(
    "heuristic context has active_molecule",
    captured_context.get("active_molecule", {}).get("canonical_name") == "methylethylamine",
    str(captured_context),
)

print("\n[5] Explicit molecule name suppresses implicit follow-up")
explicit_hint = normalize_user_text("벤젠의 치환기를 바꾸면?")
explicit_rewrite = pipe._run_ingress_rewrite("벤젠의 치환기를 바꾸면?", explicit_hint, {"session_id": session_id})
check("explicit molecule keeps context empty", explicit_rewrite.context_molecule_name in (None, ""), str(explicit_rewrite))

print("\n[6] action_planner.md content check")
planner_path = REPO_ROOT / "src" / "qcviz_mcp" / "llm" / "prompt_assets" / "action_planner.md"
content = planner_path.read_text(encoding="utf-8")
check("'Conversation Context' section exists", "Conversation Context" in content, "section not found")
check("'molecule_from_context' mentioned", "molecule_from_context" in content, "keyword not found")
check("'methylethylamine' example present", "methylethylamine" in content, "example not found")

clear_conversation_state(session_id)

print("\n" + "=" * 64)
total = PASS + FAIL
print(f"Results: {PASS}/{total} passed, {FAIL} failed")
if FAIL:
    print("SOME TESTS FAILED")
    raise SystemExit(1)
print("ALL PASS")
