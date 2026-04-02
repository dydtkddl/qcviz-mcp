# Phase 3 Day 5-7: routes 및 job store에 comparison flow 연동

## 변경 파일 목록

```
📄 파일: src/qcviz_mcp/web/routes/compute.py
   변경 유형: MODIFY
   변경 라인 수: ~80줄 추가
   의존성 변경: 새 import (지연): pyscf_runner.compute_delta, result_explainer.explain_comparison

📄 파일: src/qcviz_mcp/web/routes/chat.py
   변경 유형: MODIFY
   변경 라인 수: ~70줄 추가
   의존성 변경: 없음 (asyncio 이미 import됨)

📄 파일: src/qcviz_mcp/worker/arq_worker.py
   변경 유형: MODIFY
   변경 라인 수: ~45줄 추가
   의존성 변경: 새 import (지연): compute._run_comparison_compute
```

---

## Patch 1/3: compute.py — comparison 엔진 + 엔드포인트

### 변경 A: feature flag 헬퍼

> **위치**: 기존 utility 함수 영역 (`_modification_lane_enabled` 등 근처)
> **이유**: comparison 기능 on/off 제어

```python
def _comparison_enabled() -> bool:
    """Check if the comparison feature is enabled.

    Returns:
        True if QCVIZ_COMPARISON_ENABLED env var is truthy.
    """
    return os.getenv(
        "QCVIZ_COMPARISON_ENABLED", "false"
    ).lower() in ("true", "1", "yes")
```

### 변경 B: `_run_comparison_compute()` 함수

> **위치**: `_run_direct_compute()` 함수 아래에 삽입
> **이유**: 두 구조의 계산을 순차 실행하고 delta + explanation 생성

```python
def _run_comparison_compute(
    payload_a: Dict[str, Any],
    payload_b: Dict[str, Any],
    *,
    job_type: str = "analyze",
    progress_callback: "Callable | None" = None,
) -> Dict[str, Any]:
    """Run two calculations sequentially and compute property deltas.

    Enforces the same method/basis for both molecules to ensure
    a fair comparison.  Calls ``_run_direct_compute()`` twice,
    then ``compute_delta()`` and ``explain_comparison()``.

    Args:
        payload_a: Compute payload for molecule A.
        payload_b: Compute payload for molecule B.
        job_type: Calculation type (e.g. "analyze").
        progress_callback: Optional progress reporter.

    Returns:
        Dict with keys: comparison (bool), result_a, result_b,
        delta, explanation, method, basis.

    # Test scenario: _run_comparison_compute(
    #     {"structure_query": "benzene", "method": "HF", "basis": "sto-3g"},
    #     {"structure_query": "toluene", "method": "HF", "basis": "sto-3g"},
    # ) → comparison=True, delta has energy_delta_ev
    """
    from qcviz_mcp.compute.pyscf_runner import compute_delta
    from qcviz_mcp.web.result_explainer import explain_comparison

    # Enforce identical method/basis
    method = payload_a.get("method") or payload_b.get("method")
    basis = payload_a.get("basis") or payload_b.get("basis")
    payload_a["method"] = method
    payload_a["basis"] = basis
    payload_b["method"] = method
    payload_b["basis"] = basis

    result_a = None
    result_b = None
    error_a = None
    error_b = None

    # ── Calculate molecule A ─────────────────────────────────
    if progress_callback:
        try:
            progress_callback(
                progress=5.0, step="comparison_a",
                message=f"분자 A 계산 시작: "
                        f"{payload_a.get('structure_query', '?')}",
            )
        except Exception:
            pass
    try:
        result_a = _run_direct_compute(
            payload_a, progress_callback=progress_callback,
        )
    except Exception as exc:
        error_a = str(exc)
        logger.warning("Comparison molecule A failed: %s", exc)

    # ── Calculate molecule B ─────────────────────────────────
    if progress_callback:
        try:
            progress_callback(
                progress=50.0, step="comparison_b",
                message=f"분자 B 계산 시작: "
                        f"{payload_b.get('structure_query', '?')}",
            )
        except Exception:
            pass
    try:
        result_b = _run_direct_compute(
            payload_b, progress_callback=progress_callback,
        )
    except Exception as exc:
        error_b = str(exc)
        logger.warning("Comparison molecule B failed: %s", exc)

    # ── Compute delta ────────────────────────────────────────
    delta = {}
    explanation = {}
    if result_a and result_b:
        if progress_callback:
            try:
                progress_callback(
                    progress=90.0, step="comparison_delta",
                    message="비교 delta 계산 중...",
                )
            except Exception:
                pass
        try:
            delta = compute_delta(result_a, result_b)
            explanation = explain_comparison(
                delta=delta,
                result_a=result_a,
                result_b=result_b,
                job_type=job_type,
            )
        except Exception as exc:
            logger.warning("Delta/explanation failed: %s", exc)

    if progress_callback:
        try:
            progress_callback(
                progress=100.0, step="comparison_done",
                message="비교 분석 완료",
            )
        except Exception:
            pass

    return {
        "comparison": True,
        "result_a": result_a,
        "result_b": result_b,
        "error_a": error_a,
        "error_b": error_b,
        "delta": delta,
        "explanation": explanation,
        "method": method,
        "basis": basis,
    }
```

### 변경 C: REST 엔드포인트

> **위치**: 기존 `@router.post("/jobs")` 아래에 추가
> **이유**: 외부에서 comparison 계산을 제출할 수 있는 API

```python
@router.post("/api/comparison")
async def submit_comparison_job(
    request: Request,
    payload: Optional[Dict[str, Any]] = Body(default=None),
) -> Dict[str, Any]:
    """Submit a comparison calculation for two molecules.

    Expects payload with ``structure_a``, ``structure_b``, and
    optional ``method``, ``basis``, ``job_type``.

    Returns:
        Comparison result dict or error.
    """
    if not _comparison_enabled():
        raise HTTPException(
            status_code=501,
            detail="비교 기능이 비활성화되어 있습니다. "
                   "QCVIZ_COMPARISON_ENABLED=true로 설정하세요.",
        )

    body = dict(payload or {})
    structure_a = body.get("structure_a") or body.get("molecule_a", "")
    structure_b = body.get("structure_b") or body.get("molecule_b", "")

    if not structure_a or not structure_b:
        raise HTTPException(
            status_code=400,
            detail="structure_a와 structure_b 모두 필요합니다.",
        )

    method = body.get("method", "HF")
    basis = body.get("basis", "sto-3g")
    job_type = body.get("job_type", "analyze")

    payload_a = {
        "structure_query": structure_a,
        "method": method,
        "basis": basis,
        "job_type": job_type,
    }
    payload_b = {
        "structure_query": structure_b,
        "method": method,
        "basis": basis,
        "job_type": job_type,
    }

    import asyncio
    try:
        result = await asyncio.to_thread(
            _run_comparison_compute,
            payload_a, payload_b,
            job_type=job_type,
        )
        return {"ok": True, "result": result}
    except Exception as exc:
        logger.exception("Comparison job failed")
        raise HTTPException(
            status_code=500,
            detail=f"비교 계산 실패: {exc}",
        )
```

---

## Patch 2/3: chat.py — comparison 분기 handler

### 변경 A: `_handle_comparison_request()` 함수

> **위치**: 기존 `_handle_modification_exploration()` 아래에 삽입
> **이유**: WebSocket 채팅에서 comparison 의도 감지 시 비교 계산 실행

```python
async def _handle_comparison_request(
    websocket,
    session_id: str,
    plan: dict,
    action_plan,
) -> None:
    """Handle a comparison request from the chat pipeline.

    Extracts two target molecules from the action plan, runs
    comparison compute, and sends results via WebSocket.

    Args:
        websocket: WebSocket connection.
        session_id: Current session identifier.
        plan: Parsed plan dict.
        action_plan: ActionPlan object with comparison.targets.
    """
    targets = list(action_plan.comparison.targets)[:2]

    if len(targets) < 2:
        await _ws_send(
            websocket, "clarify",
            session_id=session_id,
            message="비교하려면 두 개의 분자가 필요합니다. "
                    "어떤 분자들을 비교할까요?",
            timestamp=_now_ts(),
        )
        return

    await _ws_send(
        websocket, "comparison_started",
        session_id=session_id,
        targets=targets,
        message=f"'{targets[0]}'와(과) '{targets[1]}'의 "
                f"비교 계산을 시작합니다...",
        timestamp=_now_ts(),
    )

    base_payload = {
        "job_type": plan.get("job_type", "analyze"),
        "method": plan.get("method"),
        "basis": plan.get("basis"),
        "charge": plan.get("charge", 0),
        "multiplicity": plan.get("multiplicity", 1),
        "session_id": session_id,
    }
    payload_a = {**base_payload, "structure_query": targets[0]}
    payload_b = {**base_payload, "structure_query": targets[1]}

    import asyncio
    try:
        # 지연 import
        from qcviz_mcp.web.routes.compute import (
            _run_comparison_compute,
        )
        result = await asyncio.to_thread(
            _run_comparison_compute,
            payload_a, payload_b,
            job_type=base_payload["job_type"],
        )

        await _ws_send(
            websocket, "comparison_result",
            session_id=session_id,
            result=result,
            message=(
                f"'{targets[0]}'와(과) '{targets[1]}'의 "
                f"비교 분석이 완료되었습니다."
            ),
            timestamp=_now_ts(),
        )

    except Exception as exc:
        logger.exception("Comparison compute failed")
        await _ws_send(
            websocket, "error",
            session_id=session_id,
            message=f"비교 계산 중 오류가 발생했습니다: {exc}",
            timestamp=_now_ts(),
        )
```

### 변경 B: 기존 dispatch에 comparison 분기 삽입

> **위치 찾기**:
> ```bash
> grep -n "action_plan\|ActionPlan\|comparison.*enabled\|batch_request" \
>   src/qcviz_mcp/web/routes/chat.py | head -20
> ```
>
> **삽입 지점**: 기존 ExecutionDecision/ActionPlan 분기 처리 영역,
> modification_preview 분기 바로 아래

```python
            # ── Phase 3: comparison 분기 ─────────────────────
            if (
                hasattr(action_plan, "comparison")
                and action_plan.comparison
                and getattr(action_plan.comparison, "enabled", False)
                and len(getattr(action_plan.comparison, "targets", [])) >= 2
                and _comparison_enabled()
            ):
                await _handle_comparison_request(
                    websocket, session_id, plan_dict, action_plan,
                )
                continue  # 또는 return
```

> `_comparison_enabled`는 compute.py에 정의됨. chat.py에서도
> 같은 패턴으로 별도 정의하거나 import:
> ```python
> def _comparison_enabled() -> bool:
>     return os.getenv("QCVIZ_COMPARISON_ENABLED", "false").lower() in ("true", "1", "yes")
> ```

---

## Patch 3/3: arq_worker.py — comparison task 등록

### 변경 A: `run_comparison_job()` 함수

> **위치**: `run_compute_job()` 함수 아래에 추가
> **이유**: Redis/Arq 워커에서 comparison 계산을 비동기 실행

```python
async def run_comparison_job(
    ctx: Dict[str, Any],
    job_id: str,
    payload: "Mapping[str, Any]",
) -> Dict[str, Any]:
    """Execute a comparison calculation in the Arq worker.

    Args:
        ctx: Arq worker context.
        job_id: Unique job identifier.
        payload: Dict with payload_a, payload_b, job_type.

    Returns:
        Dict with ok (bool), job_id, and optional error.
    """
    store = _build_store()
    ctx["_qcviz_active_jobs"] = int(
        ctx.get("_qcviz_active_jobs") or 0
    ) + 1
    store.mark_running(job_id, worker_id=_worker_id())

    progress_cb = _progress_callback_factory(store, job_id, {
        "job_id": job_id,
        "worker_id": _worker_id(),
        "type": "comparison",
    })

    try:
        from qcviz_mcp.web.routes.compute import (
            _run_comparison_compute,
        )
        payload_a = dict(payload.get("payload_a") or {})
        payload_b = dict(payload.get("payload_b") or {})
        job_type = _safe_str(payload.get("job_type"), "analyze")

        result = _run_comparison_compute(
            payload_a, payload_b,
            job_type=job_type,
            progress_callback=progress_cb,
        )
        store.mark_completed(job_id, result)
        return {"ok": True, "job_id": job_id}

    except Exception as exc:
        logger.exception("Comparison job %s failed", job_id)
        store.mark_failed(
            job_id,
            message=str(exc),
            error={
                "message": str(exc),
                "type": exc.__class__.__name__,
            },
        )
        return {"ok": False, "job_id": job_id, "error": str(exc)}

    finally:
        ctx["_qcviz_active_jobs"] = max(
            0, int(ctx.get("_qcviz_active_jobs") or 1) - 1
        )
```

### 변경 B: WorkerSettings.functions에 등록

> **위치**: `WorkerSettings` 클래스의 `functions` 리스트
> **이유**: Arq가 comparison task를 인식

```python
class WorkerSettings:
    functions = [run_compute_job, run_comparison_job]  # ← 추가
    ...
```

---

## 검증 명령

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04

# 1. compute.py comparison 함수 존재
grep -n "_run_comparison_compute\|_comparison_enabled\|/api/comparison" \
  src/qcviz_mcp/web/routes/compute.py
# 기대: 3줄 이상

# 2. chat.py comparison handler 존재
grep -n "_handle_comparison_request\|comparison_started\|comparison_result\|comparison_enabled" \
  src/qcviz_mcp/web/routes/chat.py
# 기대: 4줄 이상

# 3. arq_worker comparison task 존재
grep -n "run_comparison_job" src/qcviz_mcp/worker/arq_worker.py
# 기대: 2줄 이상 (함수 정의 + functions 리스트)

# 4. import chain 확인
PYTHONPATH=src python -c "
from qcviz_mcp.web.routes.compute import _comparison_enabled
from qcviz_mcp.web.routes.compute import _run_comparison_compute
print('✅ compute comparison imports OK')
"

# 5. 기존 테스트 무결성
PYTHONPATH=src pytest tests/ -x -q 2>&1 | tail -5
```

---

## Phase 3 데이터 흐름 (Day 1-7 완성 후)

```
User: "벤젠과 톨루엔 비교해줘"

→ pipeline: ActionPlan.comparison = {enabled: True, targets: ["benzene", "toluene"]}
→ chat.py: _handle_comparison_request()
    → WS: {type: "comparison_started", targets: ["benzene", "toluene"]}
    → compute.py: _run_comparison_compute(payload_a, payload_b)
        → _run_direct_compute(payload_a) → result_a  [PySCF: benzene]
        → _run_direct_compute(payload_b) → result_b  [PySCF: toluene]
        → compute_delta(result_a, result_b) → delta
        → explain_comparison(delta) → explanation
    → WS: {type: "comparison_result", result: {comparison: true, delta, explanation}}

User sees: "벤젠과 톨루엔의 비교 분석이 완료되었습니다. 에너지 차이: -14.8 eV..."
```

---

## 다음 Day 연결점

- **Day 8-11**: 프론트엔드에 듀얼 3Dmol.js 뷰어 (`viewer.js`),
  비교 결과 테이블 (`results.js`), comparison 모드 UI (`chat.js`, `app.js`),
  듀얼 뷰어 CSS (`style.css`), 컨테이너 HTML (`index.html`)을 구현하여
  `comparison_result` WebSocket 메시지를 시각적으로 렌더링.
