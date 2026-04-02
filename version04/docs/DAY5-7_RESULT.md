# Day 5-7: pipeline.py + agent.py에 Conversation Context Injection

## 변경 파일 목록

```
📄 파일: src/qcviz_mcp/llm/pipeline.py
   변경 유형: MODIFY (기존 파일 수정)
   변경 라인 수: ~55줄 추가, ~0줄 수정
   의존성 변경: 새 import 2개 (프로젝트 내부)

📄 파일: src/qcviz_mcp/llm/prompt_assets/action_planner.md
   변경 유형: MODIFY (기존 파일 수정)
   변경 라인 수: ~25줄 추가
   의존성 변경: 없음
```

---

## Patch 1/2: pipeline.py

### 변경 A: import 추가

> **위치**: 파일 상단 import 블록, 프로젝트 내부 import 섹션 끝
> **이유**: Day 1-2의 `get_active_molecule`과 Day 3-4의 `detect_implicit_follow_up`을
> pipeline에서 호출하여 실제 세션 맥락 기반 판정 활성화

```python
# ── Phase 1 imports ──────────────────────────────────────────
from qcviz_mcp.web.conversation_state import get_active_molecule
from qcviz_mcp.llm.normalizer import detect_implicit_follow_up
```

> **순환 import 주의**: `conversation_state`는 `web` 패키지, `normalizer`는 `llm`
> 패키지이므로 순환 없음. 만약 기존 import 구조에서 충돌이 발생하면
> 함수 내 지연 import로 전환:
> ```python
> def _get_active_mol(session_id):
>     from qcviz_mcp.web.conversation_state import get_active_molecule
>     return get_active_molecule(session_id)
> ```

---

### 변경 B: `_run_ingress_rewrite()` — implicit follow-up 판정 주입

> **위치**: `_run_ingress_rewrite()` 함수 내부,
> 기존 `analyze_follow_up_request(raw_text)` 호출 **직후** (또는
> `fallback`/`result` 객체가 `is_follow_up` 값을 갖게 된 시점 직후)
> **이유**: Day 3-4에서 만든 `detect_implicit_follow_up()`에
> 실제 세션의 active_molecule 존재 여부를 전달하여 implicit follow-up 활성화

```python
        # ── Phase 1: implicit follow-up with active_molecule ────
        session_id = _coerce_text(context.get("session_id")) if context else ""
        active_mol = None
        if session_id and _env_flag("QCVIZ_CONTEXT_TRACKING_ENABLED", False):
            try:
                active_mol = get_active_molecule(session_id)
            except Exception:
                active_mol = None

        if active_mol and active_mol.get("canonical_name"):
            _has_explicit_name = bool(
                normalized_hint.get("maybe_structure_hint")
                or normalized_hint.get("primary_candidate")
            )
            implicit_result = detect_implicit_follow_up(
                raw_text,
                has_active_molecule=True,
                has_explicit_molecule_name=_has_explicit_name,
            )
            if implicit_result.get("is_implicit_follow_up"):
                fallback.is_follow_up = True
                fallback.follow_up_type = (
                    implicit_result.get("follow_up_type")
                    or fallback.follow_up_type
                )
                fallback.context_molecule_name = active_mol.get("canonical_name")
                fallback.context_molecule_smiles = active_mol.get("smiles")
                logger.info(
                    "Implicit follow-up detected: type=%s context_mol=%s",
                    fallback.follow_up_type,
                    fallback.context_molecule_name,
                )
```

> **변수명 주의**: 함수 내에서 ingress 결과 객체의 변수명이 `fallback`이 아닐 수
> 있음 (`result`, `rewrite`, `ingress_result` 등). 기존 코드에서
> `is_follow_up`을 설정하는 대상 변수명을 확인하여 치환할 것.
>
> `_coerce_text`와 `_env_flag`는 pipeline.py에 이미 존재하는 내부 헬퍼.
> 만약 없으면:
> ```python
> def _coerce_text(v): return str(v) if v else ""
> def _env_flag(key, default=False):
>     import os
>     return os.getenv(key, "").lower() in ("1", "true", "yes") if not default else True
> ```

---

### 변경 C: `_run_action_planner()` — Router payload에 conversation context 추가

> **위치**: `_run_action_planner()` 함수 내부,
> `_invoke_structured_stage()` 호출 시 `payload` dict 구성 부분
> **이유**: Gemini Router가 "현재 논의 중인 분자"를 인지하여 정확한 lane 배정

기존 payload dict에 다음 키를 추가:

```python
                # ── Phase 1: conversation context for Router ─────
                "conversation_context": {
                    "active_molecule": {
                        "name": (
                            _coerce_text(rewrite.context_molecule_name)
                            if hasattr(rewrite, "context_molecule_name")
                               and rewrite.context_molecule_name
                            else ""
                        ),
                        "smiles": (
                            _coerce_text(rewrite.context_molecule_smiles)
                            if hasattr(rewrite, "context_molecule_smiles")
                               and rewrite.context_molecule_smiles
                            else ""
                        ),
                    } if (
                        hasattr(rewrite, "context_molecule_name")
                        and rewrite.context_molecule_name
                    ) else None,
                    "is_follow_up": getattr(rewrite, "is_follow_up", False),
                    "follow_up_type": getattr(rewrite, "follow_up_type", None),
                },
```

> `rewrite`는 `_run_ingress_rewrite()`의 반환값. 변수명이 다르면 치환.

---

### 변경 D: heuristic fallback(`_fallback()`)에서도 context 전달

> **위치**: `_fallback()` 메서드 내부, heuristic_planner 호출 직전
> **이유**: LLM 미사용(heuristic) 경로에서도 active_molecule 맥락 활용

```python
        # ── Phase 1: inject active_molecule into heuristic context ──
        session_id = _coerce_text(context.get("session_id")) if context else ""
        if session_id and _env_flag("QCVIZ_CONTEXT_TRACKING_ENABLED", False):
            try:
                _active = get_active_molecule(session_id)
                if _active:
                    context["active_molecule"] = _active
            except Exception:
                pass
```

---

## Patch 2/2: action_planner.md — Conversation Context 지시 추가

> **위치**: 파일 끝의 "Input payload:" 설명 섹션 **앞**에 삽입
> **이유**: Gemini Router가 conversation context를 올바르게 해석하는 지시

```markdown
## Conversation Context

If `conversation_context.active_molecule` is present in the input payload,
it means the user has been discussing this molecule in prior turns.

When the user's query lacks an explicit molecule name but contains:
- modification language (swap, replace, change substituent, 치환기 바꾸면, etc.)
- comparison language (compare, vs, 비교, etc.)
- implicit reference (그럼, 그러면, if we, what about, etc.)

Then you MUST:
1. Set `is_follow_up: true`
2. Set `molecule_from_context` to the active molecule name
3. For modification queries: set `lane: "chat_only"` (the modification
   exploration will be handled downstream)
4. Do NOT generate random molecule candidates

Example:
- Active molecule: "methylethylamine"
- User: "치환기를 하나만 바꾸면?"
- Correct output: lane="chat_only", is_follow_up=true,
  molecule_from_context="methylethylamine"
```

---

## 검증 명령

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04

# 1. import 확인
PYTHONPATH=src python -c "
from qcviz_mcp.llm.pipeline import QCVizPromptPipeline
print('✅ pipeline import OK')
"

# 2. 전체 기능 검증
PYTHONPATH=src QCVIZ_CONTEXT_TRACKING_ENABLED=true python verify_day5_7.py

# 3. prompt asset 변경 확인
grep -c 'Conversation Context' src/qcviz_mcp/llm/prompt_assets/action_planner.md
# 기대값: 1 이상

# 4. 기존 테스트 무결성
PYTHONPATH=src pytest tests/ -x -q 2>&1 | tail -5
```

---

## 다음 Day 연결점

- **Day 8-10**: `chat.py`가 (a) 분자 설명/compute 응답 완료 후
  `_pending_active_molecule`에서 데이터를 추출해 `set_active_molecule()` 호출,
  (b) WebSocket 메시지에 `session_id`를 포함하여 pipeline context에 전달,
  (c) follow-up 시 `context_molecule_name`을 활용한 맥락적 LLM 응답 생성.
- pipeline의 `conversation_context` payload가 Gemini Router에 전달되므로,
  Router가 `molecule_from_context`를 반환하면 chat.py가 이를 structure 해석에 활용.
