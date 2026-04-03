from __future__ import annotations

import asyncio
import time

from qcviz_mcp.llm.normalizer import detect_implicit_follow_up
from qcviz_mcp.web.conversation_state import (
    clear_conversation_state,
    get_active_molecule,
    load_conversation_state,
    update_conversation_state,
    update_conversation_state_from_execution,
)
from qcviz_mcp.web.routes import chat as chat_route
from qcviz_mcp.web.routes import compute as compute_route


def test_execution_update_promotes_pending_active_molecule(monkeypatch) -> None:
    monkeypatch.setenv("QCVIZ_CONTEXT_TRACKING_ENABLED", "true")
    session_id = f"followup-regression-{time.time_ns()}"
    clear_conversation_state(session_id)

    payload = {
        "session_id": session_id,
        "structure_query": "methane",
        "job_type": "geometry_optimization",
    }
    result = {
        "structure_name": "methane",
        "structure_query": "methane",
        "job_type": "geometry_optimization",
    }

    update_conversation_state_from_execution(payload, result, job_id="job-1")

    active = get_active_molecule(session_id)
    state = load_conversation_state(session_id)
    assert active is not None
    assert active["canonical_name"] == "methane"
    assert "_pending_active_molecule" not in state


def test_detect_implicit_follow_up_recognizes_remaining_analysis_phrase() -> None:
    message = "\ub098\uba38\uc9c0 \ubd84\uc11d\ub3c4 \u3131\u3131"
    result = detect_implicit_follow_up(
        message,
        has_active_molecule=True,
        has_explicit_molecule_name=False,
    )

    assert result["is_implicit_follow_up"] is True
    assert result["follow_up_type"] == "structure_reference"


def test_apply_session_continuation_uses_context_for_implicit_modification_followup(
    monkeypatch,
) -> None:
    session_id = f"followup-implicit-mod-{time.time_ns()}"
    clear_conversation_state(session_id)
    update_conversation_state(
        session_id,
        {
            "last_structure_query": "ethylamine",
            "last_resolved_name": "ethylamine",
            "last_resolved_artifact": {
                "structure_query": "ethylamine",
                "structure_name": "ethylamine",
                "smiles": "CCN",
            },
        },
    )
    monkeypatch.setattr(compute_route, "get_job_manager", lambda: None, raising=False)

    out = compute_route._apply_session_continuation(
        {
            "session_id": session_id,
            "query_kind": "grounding_required",
            "semantic_grounding_needed": True,
            "implicit_follow_up_type": "modification_request",
            "context_molecule_name": "ethylamine",
            "job_type": "analyze",
        },
        source_text="\uce58\ud658\uae30 \ud558\ub098\ub9cc \ubc14\uafd4\ubcf4\uace0\uc2f6\uc740\ub370",
    )

    assert out.get("follow_up_mode") == "reuse_last_structure"
    assert out.get("structure_query") == "ethylamine"
    assert out.get("structure_source") == "continuation"
    assert out.get("needs_clarification") is not True


def test_chat_only_context_persistence_stores_active_molecule(monkeypatch) -> None:
    monkeypatch.setenv("QCVIZ_CONTEXT_TRACKING_ENABLED", "true")
    monkeypatch.setattr(chat_route, "get_job_manager", lambda: None, raising=False)
    session_id = f"chat-only-context-{time.time_ns()}"
    clear_conversation_state(session_id)

    class _DummyMolChat:
        async def search(self, query: str, limit: int = 3):
            return {
                "results": [
                    {
                        "name": "ethylamine",
                        "canonical_smiles": "CCN",
                        "molecular_formula": "C2H7N",
                        "cid": 6342,
                    }
                ]
            }

    class _DummyResolver:
        molchat = _DummyMolChat()

    monkeypatch.setattr(chat_route, "_get_resolver", lambda: _DummyResolver(), raising=False)

    asyncio.run(
        chat_route._persist_chat_only_structure_context(
            session_id=session_id,
            plan={
                "query_kind": "chat_only",
                "canonical_candidates": ["\uba54\ud2f8\u3139ethylamine", "ethylamine"],
            },
            raw_message="\uba54\ud2f8\u3139\uc5d0\ud2f8\uc544\ubbfc",
            manager=None,
        )
    )

    active = get_active_molecule(session_id)
    state = load_conversation_state(session_id)

    assert active is not None
    assert active["canonical_name"] == "ethylamine"
    assert active["smiles"] == "CCN"
    assert state.get("last_structure_query") == "ethylamine"
    assert state.get("last_resolved_name") == "ethylamine"


def test_force_implicit_modification_lane_uses_active_context(monkeypatch) -> None:
    session_id = f"force-mod-lane-{time.time_ns()}"
    monkeypatch.setattr(chat_route, "_modification_lane_enabled", lambda: True, raising=False)
    monkeypatch.setattr(
        chat_route,
        "get_active_molecule",
        lambda session_id, manager=None: {"canonical_name": "ethylamine", "smiles": "CCN"},
        raising=False,
    )

    forced = chat_route._force_implicit_modification_lane(
        session_id,
        {
            "query_kind": "grounding_required",
            "planner_lane": "grounding_required",
            "implicit_follow_up_type": "modification_request",
            "semantic_grounding_needed": True,
        },
        manager=None,
    )

    assert forced["query_kind"] == "modification_exploration"
    assert forced["planner_lane"] == "modification_exploration"
    assert forced["context_molecule_name"] == "ethylamine"
    assert forced["context_molecule_smiles"] == "CCN"
    assert forced["modification_intent"]["from_group"] == ""
    assert forced["modification_intent"]["to_group"] == ""
