# Day 3-4: normalizer.py에 Implicit Follow-up Detection 추가

## 변경 파일 목록

```
📄 파일: src/qcviz_mcp/llm/schemas.py
   변경 유형: MODIFY (기존 파일 수정)
   변경 라인 수: ~2줄 추가
   의존성 변경: 없음 (Optional은 이미 import됨)

📄 파일: src/qcviz_mcp/llm/normalizer.py
   변경 유형: MODIFY (기존 파일 수정)
   변경 라인 수: ~120줄 추가, ~8줄 수정
   의존성 변경: 없음 (re, typing은 이미 import됨)
```

---

## Patch 1/2: schemas.py — IngressResult에 context 필드 추가

> **이유**: Pipeline이 active_molecule 정보를 Ingress 결과에 태깅하여
> 후속 Stage(Router/Planner)에서 참조할 수 있도록

### 위치: `IngressResult` 클래스 내부, 기존 `unknown_tokens` 필드 뒤

```python
    context_molecule_name: Optional[str] = None
    context_molecule_smiles: Optional[str] = None
```

> `IngressRewriteResult`가 `IngressResult`를 상속하므로 자동 포함됨.
> `Optional`과 `None` 기본값이므로 기존 코드에 영향 없음.

---

## Patch 2/2: normalizer.py — Implicit Follow-up Detection

### 변경 A: 새 정규식 패턴 4개 추가

> **위치**: 기존 `_FOLLOW_UP_QUERY_CUE_RE` (또는 마지막 follow-up 관련 정규식) 정의 **바로 아래**
> **이유**: 한국어/영어 modification intent, conditional, comparison, 주어 생략 패턴 감지

```python
# ── Phase 1: Implicit follow-up patterns ─────────────────────

# modification / structural change intent
_IMPLICIT_FOLLOW_UP_MODIFICATION_RE = re.compile(
    r"(?:"
    r"치환기|작용기|곁사슬|side chain|substituent|functional group|"
    r"메틸기|에틸기|하이드록시기|카르복실기|아미노기|할로겐|"
    r"methyl|ethyl|hydroxyl?|carboxyl|amino|halogen|"
    r"R기|R-group|r.group"
    r")"
    r".*?"
    r"(?:"
    r"바꾸|바꿔|교체|변경|치환|대체|추가|제거|옮기|이동|"
    r"swap|replace|change|switch|add|remove|move|substitute"
    r")",
    re.IGNORECASE,
)

# conditional modification ("~하면?", "what if ~")
_IMPLICIT_FOLLOW_UP_CONDITIONAL_RE = re.compile(
    r"(?:"
    r"(?:을|를|이|가|는|은)?\s*(?:바꾸면|바꿔보면|교체하면|변경하면|치환하면|추가하면|제거하면|옮기면)"
    r"|(?:하나만|하나를|한 개만|한 개를)\s*(?:바꾸면|바꿔|교체|변경)"
    r"|if\s+(?:I|we)\s+(?:swap|replace|change|switch|add|remove)"
    r"|what\s+(?:if|about)\s+(?:swap|replac|chang)"
    r")",
    re.IGNORECASE,
)

# comparison intent
_IMPLICIT_FOLLOW_UP_COMPARISON_RE = re.compile(
    r"(?:"
    r"비교|차이|다른 점|다르|달라|versus|vs\.?|compare|differ|"
    r"이성질체|isomer|동족체|homolog"
    r")",
    re.IGNORECASE,
)

# subject-absent opening (주어 생략 + 접속사로 시작)
_IMPLICIT_FOLLOW_UP_SUBJECT_ABSENT_RE = re.compile(
    r"^(?:그[래런렇]|그러|그럼|만약|만일|혹시|if\b|what if\b)",
    re.IGNORECASE,
)
```

---

### 변경 B: `detect_implicit_follow_up()` 함수 추가

> **위치**: `analyze_follow_up_request()` 함수 정의 **바로 위**에 삽입
> **이유**: active_molecule 유무 + 패턴 매칭으로 implicit follow-up 판정의 핵심 로직

```python
def detect_implicit_follow_up(
    text: str,
    *,
    has_active_molecule: bool = False,
    has_explicit_molecule_name: bool = False,
) -> Dict[str, Any]:
    """Detect implicit follow-up that references previous molecule context.

    An implicit follow-up is a query where the user omits the molecule name
    but implies reference to a previously discussed molecule through
    modification verbs, conditional phrasing, comparison intent, or
    subject-absent sentence openings.

    Args:
        text: Raw user input.
        has_active_molecule: Whether session has an active_molecule set.
        has_explicit_molecule_name: Whether current input contains an
            explicit molecule name.

    Returns:
        Dict with keys:
            is_implicit_follow_up (bool): True if implicit follow-up detected.
            follow_up_type (str | None): One of "modification_request",
                "comparison_request", "structure_reference", or None.
            modification_detected (bool): True if modification intent found.
            comparison_detected (bool): True if comparison intent found.
            reasoning (str): Diagnostic string of matched signals.

    # Test scenario: detect_implicit_follow_up("치환기를 바꾸면?",
    #   has_active_molecule=True, has_explicit_molecule_name=False)
    #   → is_implicit_follow_up=True, follow_up_type="modification_request"
    """
    raw = re.sub(r"\s+", " ", str(text or "")).strip()
    if not raw:
        return {
            "is_implicit_follow_up": False,
            "follow_up_type": None,
            "modification_detected": False,
            "comparison_detected": False,
            "reasoning": "empty",
        }

    modification = bool(
        _IMPLICIT_FOLLOW_UP_MODIFICATION_RE.search(raw)
        or _IMPLICIT_FOLLOW_UP_CONDITIONAL_RE.search(raw)
    )
    comparison = bool(_IMPLICIT_FOLLOW_UP_COMPARISON_RE.search(raw))
    subject_absent = bool(_IMPLICIT_FOLLOW_UP_SUBJECT_ABSENT_RE.match(raw))

    # 핵심 판정 로직:
    # active_molecule 존재 + 명시적 분자명 부재 +
    # (modification OR comparison OR 주어 생략) → implicit follow-up
    is_implicit = (
        has_active_molecule
        and not has_explicit_molecule_name
        and (modification or comparison or subject_absent)
    )

    follow_up_type = None
    if is_implicit:
        if modification:
            follow_up_type = "modification_request"
        elif comparison:
            follow_up_type = "comparison_request"
        else:
            follow_up_type = "structure_reference"

    reasoning_parts = []
    if has_active_molecule:
        reasoning_parts.append("active_molecule_exists")
    if not has_explicit_molecule_name:
        reasoning_parts.append("no_explicit_molecule")
    if modification:
        reasoning_parts.append("modification_intent")
    if comparison:
        reasoning_parts.append("comparison_intent")
    if subject_absent:
        reasoning_parts.append("subject_absent")

    logger.debug(
        "implicit_follow_up: text=%r result=%s/%s reason=%s",
        raw[:60],
        is_implicit,
        follow_up_type,
        "+".join(reasoning_parts) if reasoning_parts else "none",
    )

    return {
        "is_implicit_follow_up": is_implicit,
        "follow_up_type": follow_up_type,
        "modification_detected": modification,
        "comparison_detected": comparison,
        "reasoning": "+".join(reasoning_parts) if reasoning_parts else "none",
    }
```

---

### 변경 C: `analyze_follow_up_request()` 기존 함수에 연결점 삽입

> **위치**: `analyze_follow_up_request()` 함수 내부, **return 문 직전**
> **이유**: 기존 명시적 follow-up 판정 결과에 implicit 분석 결과를 병합하여
> 후속 pipeline에서 통합 활용 가능하게

```python
    # ── Phase 1: implicit follow-up injection ────────────────
    # Note: has_active_molecule is False here (a placeholder).
    # The real value is injected by pipeline.py (Day 5-7) which
    # calls detect_implicit_follow_up() directly with session context.
    _implicit = detect_implicit_follow_up(
        text,
        has_active_molecule=False,  # pipeline에서 override됨
        has_explicit_molecule_name=bool(result.get("maybe_structure_hint")),
    )
    if _implicit.get("modification_detected"):
        result["modification_detected"] = True
    if _implicit.get("comparison_detected"):
        result["comparison_detected"] = True
    result["implicit_follow_up_analysis"] = _implicit
```

> **주의**: `result`는 `analyze_follow_up_request()` 함수 내에서 반환 대상 dict의
> 변수명입니다. 실제 코드에서 변수명이 다르면 (`info`, `ret`, `analysis` 등)
> 해당 변수명으로 치환하세요.

---

## 검증 명령

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04

# 1. schemas.py 필드 확인
PYTHONPATH=src python -c "
from qcviz_mcp.llm.schemas import IngressResult
r = IngressResult()
assert hasattr(r, 'context_molecule_name'), 'FAIL: context_molecule_name missing'
assert hasattr(r, 'context_molecule_smiles'), 'FAIL: context_molecule_smiles missing'
assert r.context_molecule_name is None
assert r.context_molecule_smiles is None
print('✅ schemas.py OK')
"

# 2. detect_implicit_follow_up import 확인
PYTHONPATH=src python -c "
from qcviz_mcp.llm.normalizer import detect_implicit_follow_up
print('✅ detect_implicit_follow_up importable')
"

# 3. 전체 CRUD 검증
PYTHONPATH=src python verify_day3_4.py

# 4. 기존 테스트 무결성
PYTHONPATH=src pytest tests/ -x -q 2>&1 | tail -5
```

---

## 다음 Day 연결점

- **Day 5-7**: `pipeline.py`가 Stage 1 Ingress에서 `detect_implicit_follow_up()`을
  직접 호출하되, `has_active_molecule=bool(get_active_molecule(session_id))`를
  전달하여 실제 세션 맥락 기반 판정 수행. 결과의 `context_molecule_name`/
  `context_molecule_smiles`를 `IngressResult`에 채워 Stage 2 Router로 전달.
- `schemas.py`의 `context_molecule_name`/`context_molecule_smiles` 필드는
  Day 5-7에서 pipeline이 active_molecule 정보로 채운다.
