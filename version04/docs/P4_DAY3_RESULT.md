# Phase 4 Day 3: Observability 확장 — 메트릭 & Trace 연동

## 변경 파일 목록

```
📄 파일: src/qcviz_mcp/observability.py
   변경 유형: MODIFY
   변경 라인 수: ~35줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/llm/trace.py (또는 프로젝트 내 trace 모듈)
   변경 유형: MODIFY
   변경 라인 수: ~35줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/llm/execution_guard.py
   변경 유형: MODIFY
   변경 라인 수: ~6줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/llm/grounding_merge.py
   변경 유형: MODIFY
   변경 라인 수: ~6줄 추가
   의존성 변경: 없음
```

---

## Patch 1/4: observability.py — Phase 2~3 메트릭 키 + 헬퍼

> **위치**: 파일 끝에 추가
> **이유**: modification/comparison 작업 흐름을 메트릭으로 추적

```python
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
    """Pre-register Phase 2~3 metric keys in the MetricsCollector.

    Initialises each key with a zero count so that the key exists
    even before the first increment, which simplifies dashboard queries.
    """
    for key in _PHASE2_METRIC_KEYS + _PHASE3_METRIC_KEYS:
        metrics.increment(key, 0)


def get_phase_summary() -> dict:
    """Return a summary of Phase 2~3 metrics.

    Returns:
        Dict with "modification" and "comparison" sub-dicts,
        each mapping metric key → current count.
    """
    summary = metrics.summary()
    return {
        "modification": {
            k: summary.get(k, 0) for k in _PHASE2_METRIC_KEYS
        },
        "comparison": {
            k: summary.get(k, 0) for k in _PHASE3_METRIC_KEYS
        },
    }
```

> `metrics`는 observability.py에 이미 존재하는 `MetricsCollector` 싱글턴.
> `.increment(key, delta)` 및 `.summary()` 메서드가 있어야 함.
> 없으면 `metrics`를 단순 `defaultdict(int)` 래퍼로 대체 가능.

---

## Patch 2/4: trace.py — modification/comparison span 헬퍼

> **위치**: `trace.py` (또는 `llm/trace.py`) 파일 끝에 추가
> **이유**: 구조화된 trace span으로 modification/comparison 작업 추적

```python
# ── Phase 4: Phase 2~3 trace spans ───────────────────────────


def _now_iso() -> str:
    """Return current UTC time in ISO 8601 format."""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def trace_modification_span(
    base_molecule: str,
    from_group: "str | None",
    to_group: "str | None",
    candidate_count: int,
) -> dict:
    """Create a trace span dict for a modification exploration.

    Args:
        base_molecule: Name or SMILES of the base molecule.
        from_group: Source substituent key.
        to_group: Target substituent key.
        candidate_count: Number of candidates generated.

    Returns:
        Trace span dict with span_type, molecule info, and timestamp.
    """
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
    job_ids: "tuple[str, str] | None" = None,
    status: str = "submitted",
) -> dict:
    """Create a trace span dict for a comparison workflow.

    Args:
        mol_a: Name/SMILES of molecule A.
        mol_b: Name/SMILES of molecule B.
        job_ids: Tuple of (job_id_a, job_id_b) if available.
        status: Current status ("submitted", "completed", "failed").

    Returns:
        Trace span dict with span_type, molecule info, and timestamp.
    """
    return {
        "span_type": "comparison",
        "mol_a": mol_a,
        "mol_b": mol_b,
        "job_ids": list(job_ids) if job_ids else [],
        "status": status,
        "timestamp": _now_iso(),
    }
```

---

## Patch 3/4: execution_guard.py — Phase 2~3 카운터 삽입

> **위치**: Day 4-6(Phase 2)에서 추가한 `modification_preview` 분기 내부,
> 및 Day 5-7(Phase 3)에서 추가한 comparison 분기 내부
> **이유**: modification/comparison 액션이 실행될 때 메트릭 기록

modification_preview 분기 내 (기존 `metrics.increment("pipeline.guard.action.modification_preview")` 근처):

```python
        # Phase 4: observability
        metrics.increment("modification_lane_entered")
```

comparison 관련 분기가 있다면:

```python
        # Phase 4: observability
        metrics.increment("comparison_submitted")
```

---

## Patch 4/4: grounding_merge.py — modification 후보 카운터

> **위치**: Day 4-6(Phase 2)에서 추가한 `modification_exploration` 분기 내부
> **이유**: 후보 생성 성공/실패를 메트릭으로 구분

`MODIFICATION_CANDIDATES_READY` 반환 직전:

```python
        # Phase 4: observability
        metrics.increment("modification_candidates_generated")
```

clarification 반환 (base molecule 없음) 직전:

```python
        # Phase 4: observability
        metrics.increment("modification_candidates_empty")
```

---

## 검증 명령

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04

# 1. observability 헬퍼 확인
PYTHONPATH=src python -c "
from qcviz_mcp.observability import (
    register_phase2_3_metrics, get_phase_summary, metrics,
)
register_phase2_3_metrics()
metrics.increment('modification_lane_entered', 3)
metrics.increment('comparison_submitted', 5)
s = get_phase_summary()
assert s['modification']['modification_lane_entered'] == 3, f'FAIL: {s}'
assert s['comparison']['comparison_submitted'] == 5, f'FAIL: {s}'
print(f'✅ Phase 2~3 metrics OK: {s}')
"

# 2. trace spans 확인
PYTHONPATH=src python -c "
from qcviz_mcp.llm.trace import trace_modification_span, trace_comparison_span
t1 = trace_modification_span('benzene', 'H', 'methyl', 4)
t2 = trace_comparison_span('benzene', 'toluene', ('job-1', 'job-2'))
assert t1['span_type'] == 'modification_exploration'
assert t2['span_type'] == 'comparison'
assert t1['candidate_count'] == 4
assert len(t2['job_ids']) == 2
print(f'✅ Trace spans OK')
print(f'   mod: {t1}')
print(f'   cmp: {t2}')
"

# 3. execution_guard/grounding_merge 카운터 확인
grep -n "modification_lane_entered\|modification_candidates_generated\|comparison_submitted" \
  src/qcviz_mcp/llm/execution_guard.py src/qcviz_mcp/llm/grounding_merge.py
# 기대: 3줄 이상

# 4. 기존 테스트 무결성
PYTHONPATH=src pytest tests/ -x -q 2>&1 | tail -5
```

---

## 다음 Day 연결점

- **Day 4**: Feature-flag 정리 — `env_bootstrap.py`에 Phase 1~3 flag
  (`QCVIZ_CONTEXT_TRACKING_ENABLED`, `QCVIZ_MODIFICATION_LANE_ENABLED`,
  `QCVIZ_COMPARISON_ENABLED`)를 통합 검증 로직으로 등록.
  `.env.example` 최종 문서화. Advisor 연동 시작.
