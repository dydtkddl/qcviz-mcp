from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from qcviz_mcp.observability import extract_context_tracking, metrics

logger = logging.getLogger(__name__)


@dataclass
class PipelineTrace:
    trace_id: str
    session_id: Optional[str] = None
    raw_input: str = ""
    stage_outputs: Dict[str, Any] = field(default_factory=dict)
    stage_latencies_ms: Dict[str, float] = field(default_factory=dict)
    provider: Optional[str] = None
    fallback_stage: Optional[str] = None
    fallback_reason: Optional[str] = None
    failure_class: Optional[str] = None
    locked_lane: Optional[str] = None
    repair_count: int = 0
    serve_mode: Optional[str] = None
    llm_vs_heuristic_agreement: Optional[bool] = None
    total_latency_ms: Optional[float] = None
    context_molecule_name: Optional[str] = None
    context_molecule_smiles: Optional[str] = None
    implicit_follow_up_type: Optional[str] = None
    follow_up_detected: Optional[bool] = None

    def to_log_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "raw_input": self.raw_input,
            "stage_outputs": self.stage_outputs,
            "stage_latencies_ms": self.stage_latencies_ms,
            "provider": self.provider,
            "fallback_stage": self.fallback_stage,
            "fallback_reason": self.fallback_reason,
            "failure_class": self.failure_class,
            "locked_lane": self.locked_lane,
            "repair_count": self.repair_count,
            "serve_mode": self.serve_mode,
            "llm_vs_heuristic_agreement": self.llm_vs_heuristic_agreement,
            "total_latency_ms": self.total_latency_ms,
            "context_tracking": extract_context_tracking(self),
        }


def emit_pipeline_trace(trace: PipelineTrace) -> None:
    metrics.increment("pipeline.trace.count")
    if trace.stage_outputs.get("stage1_ingress", {}).get("llm_rewrite_used"):
        metrics.increment("pipeline.stage1.rewrite_rate")
    if trace.stage_outputs.get("stage2_router"):
        metrics.increment("pipeline.stage2.main_success_rate")
    if trace.repair_count > 0 and not trace.fallback_stage:
        metrics.increment("pipeline.stage2.repair_success_rate")
    if trace.fallback_stage:
        metrics.increment("pipeline.stage2.fallback_rate")
        metrics.increment(f"pipeline.fallback_stage.{trace.fallback_stage}")
    if trace.locked_lane:
        metrics.increment(f"pipeline.lane_distribution.{trace.locked_lane}")
    if trace.total_latency_ms is not None:
        metrics.observe("pipeline.e2e_latency_ms", trace.total_latency_ms)
    for stage_name, latency_ms in trace.stage_latencies_ms.items():
        metrics.observe(f"pipeline.{stage_name}.latency_ms", latency_ms)
    if trace.llm_vs_heuristic_agreement is not None:
        metrics.increment(
            "pipeline.llm_vs_heuristic_agreement.match"
            if trace.llm_vs_heuristic_agreement
            else "pipeline.llm_vs_heuristic_agreement.mismatch"
        )
    logger.info("QCViz pipeline trace: %s", trace.to_log_dict())


def _now_iso() -> str:
    """Return current UTC time in ISO 8601 format."""
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def trace_modification_span(
    base_molecule: str,
    from_group: str | None,
    to_group: str | None,
    candidate_count: int,
) -> dict[str, Any]:
    """Create a trace span dict for a modification exploration."""
    return {
        "span_type": "modification_exploration",
        "base_molecule": base_molecule,
        "from_group": from_group,
        "to_group": to_group,
        "candidate_count": candidate_count,
        "timestamp": _now_iso(),
    }


def trace_comparison_span(
    mol_a: str,
    mol_b: str,
    job_ids: tuple[str, str] | None = None,
    status: str = "submitted",
) -> dict[str, Any]:
    """Create a trace span dict for a comparison workflow."""
    return {
        "span_type": "comparison",
        "mol_a": mol_a,
        "mol_b": mol_b,
        "job_ids": list(job_ids) if job_ids else [],
        "status": status,
        "timestamp": _now_iso(),
    }
