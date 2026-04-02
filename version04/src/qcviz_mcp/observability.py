import logging
import time
import functools
import math
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict, is_dataclass
from typing import Any

logger = logging.getLogger("qcviz_mcp")

@dataclass
class ToolInvocation:
    tool_name: str
    request_id: str
    start_time: float = field(default_factory=time.monotonic)
    end_time: float | None = None
    status: str = "running"
    parameters: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    @property
    def duration_ms(self) -> float:
        if self.end_time is None:
            return (time.monotonic() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000

    def finish(self, status: str = "success", **extra_metrics):
        self.end_time = time.monotonic()
        self.status = status
        self.metrics.update(extra_metrics)

    def to_log_dict(self) -> dict:
        d = asdict(self)
        d["duration_ms"] = self.duration_ms
        return d


class MetricsCollector:
    """In-process metrics aggregation. 
    Enterprise deployment would export to Prometheus/OTLP."""
    
    def __init__(self):
        self._invocations: list[ToolInvocation] = []
        self._counters: dict[str, int] = {}
        self._observations: dict[str, list[float]] = {}
    
    def record(self, invocation: ToolInvocation):
        self._invocations.append(invocation)
        self._counters[f"{invocation.tool_name}.{invocation.status}"] = (
            self._counters.get(f"{invocation.tool_name}.{invocation.status}", 0) + 1
        )

    def increment(self, name: str, amount: int = 1) -> None:
        if not name:
            return
        self._counters[name] = self._counters.get(name, 0) + int(amount)

    def observe(self, name: str, value: Any) -> None:
        if not name:
            return
        try:
            observed = float(value)
        except Exception:
            return
        if not math.isfinite(observed):
            return
        self._observations.setdefault(name, []).append(observed)

    def _distribution_summary(self, values: list[float]) -> dict[str, float]:
        if not values:
            return {}
        ordered = sorted(values)

        def _pct(p: float) -> float:
            if len(ordered) == 1:
                return ordered[0]
            idx = max(0, min(len(ordered) - 1, round((len(ordered) - 1) * p)))
            return ordered[idx]

        return {
            "count": float(len(ordered)),
            "avg": sum(ordered) / len(ordered),
            "min": ordered[0],
            "p50": _pct(0.50),
            "p95": _pct(0.95),
            "p99": _pct(0.99),
            "max": ordered[-1],
        }
    
    def get_summary(self) -> dict:
        return {
            "total_invocations": len(self._invocations),
            "counters": dict(self._counters),
            "avg_duration_ms": {
                name: sum(
                    inv.duration_ms for inv in self._invocations 
                    if inv.tool_name == name
                ) / max(1, sum(1 for inv in self._invocations if inv.tool_name == name))
                for name in {inv.tool_name for inv in self._invocations}
            },
            "observations": {
                name: self._distribution_summary(values)
                for name, values in self._observations.items()
            },
        }

    def summary(self) -> dict[str, int]:
        """Return a flat counter map for lightweight call sites."""
        return dict(self._counters)

# Singleton
metrics = MetricsCollector()


@contextmanager
def track_operation(tool_name: str, *, request_id: str | None = None, parameters: dict[str, Any] | None = None):
    """Context manager for lightweight route/service observability."""
    import uuid

    invocation = ToolInvocation(
        tool_name=tool_name,
        request_id=request_id or str(uuid.uuid4())[:8],
        parameters={k: _safe_repr(v) for k, v in (parameters or {}).items()},
    )
    try:
        yield invocation
    except Exception as exc:
        invocation.finish(status="error")
        invocation.error = f"{type(exc).__name__}: {exc}"
        metrics.record(invocation)
        raise
    else:
        invocation.finish(status="success")
        metrics.record(invocation)


def traced_tool(func):
    """Decorator for MCP tool functions with automatic tracing."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        import uuid
        invocation = ToolInvocation(
            tool_name=func.__name__,
            request_id=str(uuid.uuid4())[:8],
            parameters={k: _safe_repr(v) for k, v in kwargs.items()},
        )
        logger.info(
            "tool.start",
            extra={"invocation": invocation.to_log_dict()}
        )
        try:
            result = await func(*args, **kwargs)
            invocation.finish(
                status="success",
                result_size=len(str(result)) if result else 0,
            )
            logger.info(
                "tool.success",
                extra={"invocation": invocation.to_log_dict()}
            )
            metrics.record(invocation)
            return result
        except Exception as e:
            invocation.finish(status="error")
            invocation.error = f"{type(e).__name__}: {e}"
            logger.error(
                "tool.error",
                extra={"invocation": invocation.to_log_dict()},
                exc_info=True,
            )
            metrics.record(invocation)
            raise
    return wrapper


def _safe_repr(v: Any, max_len: int = 200) -> str:
    """Truncate large values for logging."""
    s = repr(v)
    return s[:max_len] + "..." if len(s) > max_len else s


def _as_trace_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if hasattr(value, "model_dump") and callable(value.model_dump):
        try:
            dumped = value.model_dump(exclude_none=False)
            if isinstance(dumped, dict):
                return dict(dumped)
        except Exception:
            pass
    if is_dataclass(value):
        try:
            dumped = asdict(value)
            if isinstance(dumped, dict):
                return dict(dumped)
        except Exception:
            pass
    if hasattr(value, "__dict__"):
        try:
            dumped = vars(value)
            if isinstance(dumped, dict):
                return dict(dumped)
        except Exception:
            pass
    return {}


def extract_context_tracking(trace_data: Any) -> dict[str, Any]:
    payload = _as_trace_mapping(trace_data)
    stage_outputs = payload.get("stage_outputs")
    stage_outputs = stage_outputs if isinstance(stage_outputs, dict) else {}

    sources = [
        payload,
        stage_outputs.get("stage1_ingress"),
        stage_outputs.get("fallback"),
        stage_outputs.get("stage2_router"),
    ]

    def _first_text(*keys: str) -> str | None:
        for source in sources:
            if not isinstance(source, dict):
                continue
            for key in keys:
                value = source.get(key)
                text = str(value).strip() if value is not None else ""
                if text:
                    return text
        return None

    def _first_bool(*keys: str) -> bool | None:
        for source in sources:
            if not isinstance(source, dict):
                continue
            for key in keys:
                value = source.get(key)
                if value is None:
                    continue
                if isinstance(value, bool):
                    return value
                return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}
        return None

    active_molecule = _first_text("context_molecule_name")
    implicit_follow_up = _first_text("implicit_follow_up_type", "follow_up_type")
    follow_up_detected = _first_bool("follow_up_detected", "is_follow_up")
    if follow_up_detected is None and implicit_follow_up is not None:
        follow_up_detected = True

    return {
        "active_molecule": active_molecule,
        "implicit_follow_up": implicit_follow_up,
        "follow_up_detected": follow_up_detected,
    }


# ── Phase 4: Phase 2~3 observability ─────────────────────────

_PHASE2_METRIC_KEYS = [
    "modification_lane_entered",
    "modification_candidates_generated",
    "modification_candidates_empty",
    "modification_rdkit_unavailable",
    "modification_validation_failed",
]

_PHASE3_METRIC_KEYS = [
    "comparison_submitted",
    "comparison_completed",
    "comparison_failed",
    "comparison_timeout",
    "comparison_single_side_failure",
    "comparison_identical_molecules",
]


def register_phase2_3_metrics() -> None:
    """Pre-register Phase 2~3 metric keys in the MetricsCollector."""
    for key in _PHASE2_METRIC_KEYS + _PHASE3_METRIC_KEYS:
        metrics.increment(key, 0)


def get_phase_summary() -> dict[str, dict[str, int]]:
    """Return a summary of Phase 2~3 metrics."""
    summary = metrics.summary()
    return {
        "modification": {
            k: int(summary.get(k, 0)) for k in _PHASE2_METRIC_KEYS
        },
        "comparison": {
            k: int(summary.get(k, 0)) for k in _PHASE3_METRIC_KEYS
        },
    }
