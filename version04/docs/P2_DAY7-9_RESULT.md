# Phase 2 Day 7-9: grounding_merge, execution_guard, chat.py에 modification handler

## 변경 파일 목록

```
📄 파일: src/qcviz_mcp/llm/grounding_merge.py
   변경 유형: MODIFY
   변경 라인 수: ~25줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/llm/execution_guard.py
   변경 유형: MODIFY
   변경 라인 수: ~18줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/web/routes/chat.py
   변경 유형: MODIFY
   변경 라인 수: ~90줄 추가
   의존성 변경: 새 import (지연): structure_intelligence
```

---

## Patch 1/3: grounding_merge.py — modification lane 분기

### 변경 ①: 상수 추가

> **위치**: 파일 상단의 기존 상수 정의 영역 (다른 `SEMANTIC_OUTCOME_*` 상수 옆)
> **이유**: modification 후보 준비 완료 상태를 명명

```python
SEMANTIC_OUTCOME_MODIFICATION_CANDIDATES_READY = "modification_candidates_ready"
```

### 변경 ②: `grounding_merge()` 함수에 modification 분기 삽입

> **위치**: `grounding_merge()` 함수 내부, `if lane == "chat_only":` 블록 **바로 위**
> **이유**: modification lane일 때 기존 grounding 경로를 건너뛰고
> base molecule 존재 여부만 확인 후 outcome 반환

```python
    # ── Phase 2: modification_exploration lane ───────────────
    if lane == "modification_exploration":
        # Base molecule이 이미 확정되어 있으면 candidates_ready 반환.
        # 실제 변형 후보 생성은 chat handler에서 structure_intelligence 호출.
        if synthetic is not None:
            return GroundingOutcome(
                semantic_outcome=SEMANTIC_OUTCOME_MODIFICATION_CANDIDATES_READY,
                resolved_structure=synthetic,
                candidates=candidates or [synthetic],
            )
        if primary is not None:
            return GroundingOutcome(
                semantic_outcome=SEMANTIC_OUTCOME_MODIFICATION_CANDIDATES_READY,
                resolved_structure=primary,
                candidates=candidates,
            )
        # base molecule 없으면 clarification 요청
        return GroundingOutcome(
            semantic_outcome=SEMANTIC_OUTCOME_CUSTOM_ONLY_CLARIFICATION,
            clarification_message=(
                "구조 변형을 위해 기준 분자가 필요합니다. "
                "어떤 분자를 변형할까요?"
            ),
        )
```

> **변수 참고**: `lane`, `synthetic`, `primary`, `candidates`는 grounding_merge()
> 내에서 이미 존재하는 지역 변수. 변수명이 다르면 기존 코드에 맞게 치환.
>
> `SEMANTIC_OUTCOME_CUSTOM_ONLY_CLARIFICATION`은 기존 상수.
> 없으면 `"custom_only_clarification"` 문자열로 직접 사용.

---

## Patch 2/3: execution_guard.py — modification_preview 액션 분기

> **위치**: `execution_guard()` 함수 내부,
> `if semantic_outcome == "grounded_direct_answer":` 블록 **바로 위**
> **이유**: modification 후보가 준비되면 preview 액션을 반환하여
> chat handler가 후보 리스트를 사용자에게 전송

```python
    # ── Phase 2: modification preview ────────────────────────
    if semantic_outcome == "modification_candidates_ready":
        if outcome.resolved_structure is None:
            metrics.increment("pipeline.guard.action.clarification")
            return ExecutionDecision(
                action="clarification",
                payload=None,
                candidates=outcome.candidates,
            )
        metrics.increment("pipeline.guard.action.modification_preview")
        return ExecutionDecision(
            action="modification_preview",
            payload={
                "resolved_structure": (
                    outcome.resolved_structure.model_dump(exclude_none=True)
                    if hasattr(outcome.resolved_structure, "model_dump")
                    else outcome.resolved_structure
                ),
                "modification_candidates": [
                    c.model_dump(exclude_none=True)
                    if hasattr(c, "model_dump") else c
                    for c in (outcome.candidates or [])
                ],
            },
            candidates=outcome.candidates,
        )
```

> `metrics`는 execution_guard.py에 이미 존재하는 카운터 객체.
> 없으면 해당 줄 제거하거나 `logger.info()` 로 대체.
>
> `outcome.resolved_structure`가 Pydantic 모델이면 `.model_dump()`,
> 일반 dict이면 그대로 사용. `hasattr` guard로 양쪽 처리.

---

## Patch 3/3: chat.py — modification handler + 분기 삽입

### 변경 A: feature flag 헬퍼 (파일 상단 utility 영역)

> **위치**: 기존 `_ws_send()` 같은 헬퍼 함수 근처
> **이유**: modification lane on/off 제어

```python
def _modification_lane_enabled() -> bool:
    """Check if the modification exploration lane is enabled.

    Returns:
        True if QCVIZ_MODIFICATION_LANE_ENABLED env var is truthy.
    """
    return os.getenv(
        "QCVIZ_MODIFICATION_LANE_ENABLED", "false"
    ).lower() in ("true", "1", "yes")
```

### 변경 B: `_handle_modification_exploration()` 함수 신규

> **위치**: chat.py 내 handler 함수 영역 (기존 `_handle_*` 함수들 근처)
> **이유**: modification lane의 핵심 핸들러 — structure_intelligence로 후보 생성 → WS 전송

```python
async def _handle_modification_exploration(
    websocket,
    session_id: str,
    plan: dict,
    active_molecule: dict,
    modification_intent: dict,
) -> None:
    """Handle the modification_exploration lane.

    Generates structural modification candidates using
    structure_intelligence and sends them to the client via WebSocket.

    Args:
        websocket: WebSocket connection.
        session_id: Current session identifier.
        plan: Parsed plan dict from the pipeline.
        active_molecule: Current active molecule dict from conversation state.
        modification_intent: Parsed modification intent dict.
    """
    # 지연 import — RDKit optional
    try:
        from qcviz_mcp.services.structure_intelligence import (
            generate_modification_candidates,
            _RDKIT_AVAILABLE,
        )
    except ImportError:
        await _ws_send(
            websocket, "assistant",
            session_id=session_id,
            message="구조 변형 모듈을 로드할 수 없습니다.",
            timestamp=_now_ts(),
        )
        return

    if not _RDKIT_AVAILABLE:
        await _ws_send(
            websocket, "assistant",
            session_id=session_id,
            message=(
                "구조 변형 기능을 사용하려면 RDKit이 필요합니다. "
                "현재 환경에 RDKit이 설치되어 있지 않습니다."
            ),
            timestamp=_now_ts(),
        )
        return

    base_smiles = str(active_molecule.get("smiles") or "").strip()
    from_group = str(modification_intent.get("from_group") or "").strip()
    to_group = str(modification_intent.get("to_group") or "").strip()
    base_name = str(
        active_molecule.get("canonical_name") or "분자"
    )

    if not base_smiles:
        await _ws_send(
            websocket, "clarify",
            session_id=session_id,
            message=(
                "기준 분자의 SMILES 정보가 없습니다. "
                "먼저 분자를 확인해주세요."
            ),
            timestamp=_now_ts(),
        )
        return

    if not from_group or not to_group:
        await _ws_send(
            websocket, "clarify",
            session_id=session_id,
            message=(
                "어떤 치환기를 어떤 치환기로 바꿀지 지정해주세요. "
                "예: '메틸기를 에틸기로 바꾸면?'"
            ),
            timestamp=_now_ts(),
        )
        return

    try:
        candidates = generate_modification_candidates(
            base_smiles,
            from_group,
            to_group,
            max_candidates=5,
        )
    except Exception as exc:
        logger.warning(
            "Modification candidate generation failed: %s", exc
        )
        candidates = []

    if not candidates:
        await _ws_send(
            websocket, "assistant",
            session_id=session_id,
            message=(
                f"'{base_name}'에서 {from_group} → {to_group} 변환 "
                f"가능한 위치를 찾지 못했습니다."
            ),
            timestamp=_now_ts(),
        )
        return

    # 변형 후보를 사용자에게 전송
    await _ws_send(
        websocket, "modification_candidates",
        session_id=session_id,
        base_molecule={
            "name": base_name,
            "smiles": base_smiles,
        },
        from_group=from_group,
        to_group=to_group,
        candidates=candidates,
        message=(
            f"'{base_name}'에서 {from_group} → {to_group} 변환 후보 "
            f"{len(candidates)}개를 찾았습니다. "
            f"계산할 후보를 선택해주세요."
        ),
        timestamp=_now_ts(),
    )
    logger.info(
        "Modification candidates sent: session=%s base=%s %s→%s count=%d",
        session_id, base_name, from_group, to_group, len(candidates),
    )
```

> **주의**: `_ws_send`, `_now_ts`, `logger`는 chat.py에 이미 존재하는 헬퍼/변수.
> 실제 함수명이 다르면 치환.

### 변경 C: 기존 dispatch 분기에 modification 액션 삽입

> **위치 찾기**:
> ```bash
> grep -n "action.*==\|decision.action\|_dispatch\|ExecutionDecision" \
>   src/qcviz_mcp/web/routes/chat.py | head -20
> ```
>
> **삽입 지점**: `ExecutionDecision.action` 분기 처리 영역에서
> 기존 `"compute"`, `"chat_with_structure"`, `"clarification"` 등을
> 처리하는 if/elif 체인에 추가
>
> **이유**: modification_preview 액션이 올 때 핸들러 호출

```python
            # ── Phase 2: modification preview dispatch ───────
            if (
                decision.action == "modification_preview"
                and _modification_lane_enabled()
            ):
                _mod_intent = {}
                if hasattr(plan, "modification_intent") and plan.modification_intent:
                    _mod_intent = (
                        plan.modification_intent.model_dump()
                        if hasattr(plan.modification_intent, "model_dump")
                        else dict(plan.modification_intent)
                    )
                elif isinstance(plan, dict):
                    _mod_intent = dict(plan.get("modification_intent") or {})

                _active_mol = None
                try:
                    _active_mol = get_active_molecule(session_id)
                except Exception:
                    pass

                if _active_mol:
                    await _handle_modification_exploration(
                        websocket,
                        session_id,
                        plan if isinstance(plan, dict) else {},
                        _active_mol,
                        _mod_intent,
                    )
                    continue  # 또는 return (루프 구조에 따라)
```

> `plan`이 Pydantic 모델이면 `.modification_intent`로 접근,
> dict이면 `.get("modification_intent")`로 접근. 양쪽 처리.
>
> `continue` vs `return`: WebSocket 루프 안이면 `continue`,
> HTTP POST 핸들러면 `return`.

---

## 검증 명령

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04

# 1. grounding_merge에 modification 분기 존재 확인
grep -n "modification_exploration\|modification_candidates_ready" \
  src/qcviz_mcp/llm/grounding_merge.py
# 기대: 2줄 이상

# 2. execution_guard에 modification_preview 분기 존재 확인
grep -n "modification_preview\|modification_candidates_ready" \
  src/qcviz_mcp/llm/execution_guard.py
# 기대: 2줄 이상

# 3. chat.py에 handler + dispatch 존재 확인
grep -n "_handle_modification_exploration\|modification_preview\|MODIFICATION_LANE_ENABLED" \
  src/qcviz_mcp/web/routes/chat.py
# 기대: 3줄 이상

# 4. import chain 확인
PYTHONPATH=src python -c "
from qcviz_mcp.web.routes import chat
print('✅ chat.py import OK')
"

# 5. 기존 테스트 무결성
PYTHONPATH=src pytest tests/ -x -q 2>&1 | tail -5
```

---

## Phase 2 데이터 흐름 (Day 1-9 완성 후)

```
User: "메틸기를 에틸기로 바꾸면?" (active_molecule = methylethylamine/CCNC)

→ normalizer: detect_implicit_follow_up → modification_request
→ pipeline:
    ingress: is_follow_up=True, context_molecule=methylethylamine
    router: lane=modification_exploration,
            modification_intent={from_group: "methyl", to_group: "ethyl"}
→ grounding_merge:
    lane=modification_exploration → MODIFICATION_CANDIDATES_READY
→ execution_guard:
    modification_candidates_ready → action="modification_preview"
→ chat.py:
    decision.action == "modification_preview"
    → _handle_modification_exploration()
    → generate_modification_candidates("CCNC", "methyl", "ethyl")
    → WS: {type: "modification_candidates", candidates: [...]}

User sees: "CCNC에서 methyl → ethyl 후보 2개를 찾았습니다."
```

---

## 다음 Day 연결점

- **Day 10-14**: `normalizer.py`에서 modification intent의 from_group/to_group을
  한국어 치환기명에서 정확히 추출하는 로직 구현 (기존 `_SUBSTITUENT_PREFIX_ALIASES`
  활용 + `ko_aliases.py` 확장). End-to-end 통합 테스트 수행.
  `.env.example`에 `QCVIZ_MODIFICATION_LANE_ENABLED=false` 추가.
