from __future__ import annotations

import time

from qcviz_mcp.llm.normalizer import normalize_user_text
from qcviz_mcp.llm.pipeline import QCVizPromptPipeline
from qcviz_mcp.llm.schemas import IngressRewriteResult
from qcviz_mcp.web.conversation_state import clear_conversation_state, set_active_molecule


def _seed_active_molecule(session_id: str) -> None:
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


class _ContextAwareStage1Pipeline(QCVizPromptPipeline):
    def __init__(self) -> None:
        super().__init__(
            provider="openai",
            openai_api_key="dummy",
            enabled=True,
            stage1_enabled=True,
            stage2_enabled=False,
        )

    def _should_use_stage1_rewrite(self, raw_text, normalized_hint) -> bool:
        return True

    def _invoke_structured_stage(self, *, stage_name, response_model, payload, **kwargs):
        assert stage_name == "stage1"
        return response_model.model_validate(
            {
                "original_text": payload["raw_text"],
                "cleaned_text": payload["raw_text"],
                "language_hint": "ko",
                "rewrite_confidence": 0.91,
            }
        )


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
        assert stage_name == "stage2"
        self.captured_payload = payload
        return response_model.model_validate(
            {
                "lane": "chat_only",
                "confidence": 0.87,
                "reasoning": "captured router output",
            }
        )


def test_run_ingress_rewrite_injects_active_molecule_into_fallback(monkeypatch):
    monkeypatch.setenv("QCVIZ_CONTEXT_TRACKING_ENABLED", "true")
    session_id = f"pipeline-day57-fallback-{time.time_ns()}"
    try:
        _seed_active_molecule(session_id)
        pipeline = QCVizPromptPipeline(enabled=False)
        message = "치환기를 하나만 바꾸면?"
        normalized_hint = normalize_user_text(message)

        rewrite = pipeline._run_ingress_rewrite(message, normalized_hint, {"session_id": session_id})

        assert rewrite.is_follow_up is True
        assert rewrite.follow_up_type == "modification_request"
        assert rewrite.context_molecule_name == "methylethylamine"
        assert rewrite.context_molecule_smiles == "CCNC"
    finally:
        clear_conversation_state(session_id)


def test_run_ingress_rewrite_preserves_context_after_stage1_result(monkeypatch):
    monkeypatch.setenv("QCVIZ_CONTEXT_TRACKING_ENABLED", "true")
    session_id = f"pipeline-day57-stage1-{time.time_ns()}"
    try:
        _seed_active_molecule(session_id)
        pipeline = _ContextAwareStage1Pipeline()
        message = "치환기를 하나만 바꾸면?"
        normalized_hint = normalize_user_text(message)

        rewrite = pipeline._run_ingress_rewrite(message, normalized_hint, {"session_id": session_id})

        assert rewrite.llm_rewrite_used is True
        assert rewrite.is_follow_up is True
        assert rewrite.follow_up_type == "modification_request"
        assert rewrite.context_molecule_name == "methylethylamine"
        assert rewrite.context_molecule_smiles == "CCNC"
    finally:
        clear_conversation_state(session_id)


def test_run_action_planner_payload_includes_conversation_context():
    pipeline = _CaptureActionPlannerPipeline()
    rewrite = IngressRewriteResult(
        original_text="치환기를 하나만 바꾸면?",
        cleaned_text="치환기를 하나만 바꾸면?",
        is_follow_up=True,
        follow_up_type="modification_request",
        context_molecule_name="methylethylamine",
        context_molecule_smiles="CCNC",
    )
    normalized_hint = normalize_user_text("치환기를 하나만 바꾸면?")

    plan = pipeline._run_action_planner(
        "치환기를 하나만 바꾸면?",
        rewrite,
        normalized_hint,
        {"session_id": "capture-session"},
        None,
    )

    assert plan["lane"] == "chat_only"
    assert plan["context_molecule_name"] == "methylethylamine"
    assert plan["context_molecule_smiles"] == "CCNC"
    assert plan["implicit_follow_up_type"] == "modification_request"
    assert pipeline.captured_payload["conversation_context"] == {
        "active_molecule": {
            "name": "methylethylamine",
            "smiles": "CCNC",
        },
        "is_follow_up": True,
        "follow_up_type": "modification_request",
    }


def test_fallback_injects_active_molecule_into_heuristic_context(monkeypatch):
    monkeypatch.setenv("QCVIZ_CONTEXT_TRACKING_ENABLED", "true")
    session_id = f"pipeline-day57-heuristic-{time.time_ns()}"
    captured_context = {}

    def _heuristic_stub(message, context, normalized_hint):
        captured_context.update(context)
        return {
            "intent": "chat",
            "job_type": "chat",
            "query_kind": "chat_only",
            "planner_lane": "chat_only",
            "provider": "heuristic",
        }

    try:
        _seed_active_molecule(session_id)
        pipeline = QCVizPromptPipeline(enabled=False)
        pipeline.execute(
            "치환기를 하나만 바꾸면?",
            {"session_id": session_id},
            heuristic_planner=_heuristic_stub,
        )

        assert captured_context["session_id"] == session_id
        assert captured_context["active_molecule"]["canonical_name"] == "methylethylamine"
        assert captured_context["active_molecule"]["smiles"] == "CCNC"
    finally:
        clear_conversation_state(session_id)
