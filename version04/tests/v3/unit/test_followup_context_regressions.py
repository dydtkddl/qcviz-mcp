from __future__ import annotations

import time

from qcviz_mcp.llm.normalizer import detect_implicit_follow_up
from qcviz_mcp.web.conversation_state import (
    clear_conversation_state,
    get_active_molecule,
    load_conversation_state,
    update_conversation_state_from_execution,
)


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
