from __future__ import annotations

from typing import Any, Mapping, Optional

from qcviz_mcp.observability import metrics
from qcviz_mcp.llm.schemas import ExecutionDecision, GroundingCandidate, GroundingOutcome


class ExecutionGuardViolation(RuntimeError):
    pass


def _coerce_payload(payload: Optional[Mapping[str, Any]]) -> dict[str, Any]:
    return dict(payload or {})


def _payload_has_structure(payload: Mapping[str, Any]) -> bool:
    return bool(
        payload.get("structure_query")
        or payload.get("structures")
        or payload.get("xyz")
        or payload.get("atom_spec")
        or payload.get("selected_molecules")
    )


def _comparison_requested(payload: Mapping[str, Any]) -> bool:
    action_plan = payload.get("action_plan")
    if not isinstance(action_plan, Mapping):
        return False
    comparison = action_plan.get("comparison")
    if not isinstance(comparison, Mapping):
        return False
    enabled = comparison.get("enabled")
    if isinstance(enabled, bool):
        return enabled
    if enabled is None:
        return False
    return str(enabled).strip().lower() in {"1", "true", "yes", "y", "on"}


def execution_guard(outcome: GroundingOutcome, payload: Optional[Mapping[str, Any]] = None) -> ExecutionDecision:
    payload_dict = _coerce_payload(payload)
    semantic_outcome = outcome.semantic_outcome

    if semantic_outcome in {"chat_only"}:
        metrics.increment("pipeline.guard.action.chat_response")
        return ExecutionDecision(action="chat_response", payload=None, candidates=outcome.candidates)

    if semantic_outcome == "grounded_direct_answer":
        if outcome.resolved_structure is None:
            metrics.increment("pipeline.guard.action.chat_response")
            return ExecutionDecision(action="chat_response", payload=None, candidates=outcome.candidates)
        metrics.increment("pipeline.guard.action.chat_with_structure")
        return ExecutionDecision(
            action="chat_with_structure",
            payload={"resolved_structure": outcome.resolved_structure.model_dump(exclude_none=True)},
            candidates=outcome.candidates,
        )

    if semantic_outcome == "modification_candidates_ready":
        if outcome.resolved_structure is None:
            metrics.increment("pipeline.guard.action.clarification")
            return ExecutionDecision(action="clarification", payload=None, candidates=outcome.candidates)
        metrics.increment("pipeline.guard.action.modification_preview")
        metrics.increment("modification_lane_entered")
        return ExecutionDecision(
            action="modification_preview",
            payload={
                "resolved_structure": (
                    outcome.resolved_structure.model_dump(exclude_none=True)
                    if hasattr(outcome.resolved_structure, "model_dump")
                    else outcome.resolved_structure
                ),
                "modification_candidates": [
                    candidate.model_dump(exclude_none=True)
                    if hasattr(candidate, "model_dump")
                    else candidate
                    for candidate in (outcome.candidates or [])
                ],
            },
            candidates=outcome.candidates,
        )

    if semantic_outcome in {
        "single_candidate_confirm",
        "grounding_clarification",
        "custom_only_clarification",
    }:
        metrics.increment("pipeline.guard.action.clarification")
        return ExecutionDecision(action="clarification", payload=None, candidates=outcome.candidates)

    if semantic_outcome != "compute_ready":
        metrics.increment("pipeline.guard_rejection_rate")
        raise ExecutionGuardViolation(f"Unhandled semantic outcome: {semantic_outcome}")

    if outcome.resolved_structure is None and not _payload_has_structure(payload_dict):
        metrics.increment("pipeline.guard_rejection_rate")
        raise ExecutionGuardViolation("compute_ready without resolved structure or payload structure")

    if outcome.resolved_structure is not None and not payload_dict.get("structure_query"):
        payload_dict["structure_query"] = outcome.resolved_structure.name
    metrics.increment("pipeline.guard.action.compute")
    if _comparison_requested(payload_dict):
        metrics.increment("comparison_submitted")
    return ExecutionDecision(action="compute", payload=payload_dict, candidates=outcome.candidates)


def execution_guard_from_payload(payload: Optional[Mapping[str, Any]]) -> ExecutionDecision:
    payload_dict = _coerce_payload(payload)
    lane = str(payload_dict.get("planner_lane") or payload_dict.get("query_kind") or "").strip()
    has_structure = _payload_has_structure(payload_dict)
    if lane == "chat_only":
        metrics.increment("pipeline.guard.action.chat_response")
        return ExecutionDecision(action="chat_response", payload=None)
    if payload_dict.get("needs_clarification") and not has_structure:
        candidates = []
        for name in list(payload_dict.get("canonical_candidates") or []):
            text = str(name).strip()
            if text:
                candidates.append(GroundingCandidate(name=text, source="plan"))
        metrics.increment("pipeline.guard.action.clarification")
        return ExecutionDecision(action="clarification", payload=None, candidates=candidates)
    if not has_structure:
        metrics.increment("pipeline.guard_rejection_rate")
        raise ExecutionGuardViolation("missing_structure_payload")
    metrics.increment("pipeline.guard.action.compute")
    if _comparison_requested(payload_dict):
        metrics.increment("comparison_submitted")
    return ExecutionDecision(action="compute", payload=payload_dict)
