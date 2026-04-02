# Phase 4 Day 6: Config 통합 — Timeout/Retry 정책 & 중복 제거

## 변경 파일 목록

```
📄 파일: src/qcviz_mcp/llm/providers.py
   변경 유형: MODIFY
   변경 라인 수: ~20줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/llm/routing_config.py
   변경 유형: MODIFY
   변경 라인 수: +10줄, −8줄 (로컬 상수 → config import)
   의존성 변경: 새 import: config.MODIFICATION_*

📄 파일: src/qcviz_mcp/llm/bridge.py
   변경 유형: MODIFY
   변경 라인 수: ~8줄 추가
   의존성 변경: 새 import: providers.get_timeout_profile

📄 파일: src/qcviz_mcp/llm/prompts.py
   변경 유형: MODIFY
   변경 라인 수: ~25줄 추가
   의존성 변경: 없음
```

---

## Patch 1/4: providers.py — stage별 timeout/retry 프로필

> **위치**: 파일 끝에 추가
> **이유**: modification은 짧은 LLM 호출(15s), comparison 설명은 중간(25s),
> 기본은 30s. 작업 특성에 맞는 timeout/retry 정책 제공

```python
# ── Phase 4: Stage-specific timeout/retry profiles ───────────

_TIMEOUT_PROFILES: Dict[str, Dict[str, float]] = {
    "default": {"timeout": 30.0, "max_retries": 2},
    "action_planner": {"timeout": 20.0, "max_retries": 2},
    "ingress_rewrite": {"timeout": 15.0, "max_retries": 1},
    "modification_intent": {"timeout": 15.0, "max_retries": 1},
    "comparison_explain": {"timeout": 25.0, "max_retries": 2},
    "grounding_decider": {"timeout": 15.0, "max_retries": 1},
}


def get_timeout_profile(stage: str) -> Dict[str, float]:
    """Return timeout and retry settings for a pipeline stage.

    Args:
        stage: Pipeline stage name (e.g. "action_planner",
            "modification_intent", "comparison_explain").

    Returns:
        Dict with "timeout" (seconds) and "max_retries" (int).

    # Test scenario: get_timeout_profile("modification_intent")
    #   → {"timeout": 15.0, "max_retries": 1}
    """
    return dict(
        _TIMEOUT_PROFILES.get(stage, _TIMEOUT_PROFILES["default"])
    )
```

---

## Patch 2/4: routing_config.py — config.py로 리다이렉트

> **위치**: 파일 상단 import 영역 + 기존 로컬 상수 정의 제거
> **이유**: `config.py` Day 4에서 정의한 임계값을 단일 진실 소스로 사용,
> routing_config의 중복 정의 제거

### 변경 A: import 추가

```python
# ── Phase 4: single source of truth from config.py ───────────
from qcviz_mcp.config import (
    MODIFICATION_CONFIDENCE_THRESHOLD,
    MODIFICATION_MAX_CANDIDATES,
)
```

### 변경 B: 로컬 상수 정의 제거

> 기존에 `routing_config.py`에 있던 아래 라인을 삭제 (또는 주석 처리):

```python
# 삭제 대상:
# MODIFICATION_CONFIDENCE_THRESHOLD = _env_float_any(
#     ["QCVIZ_MODIFICATION_CONFIDENCE_THRESHOLD"], 0.60
# )
# MODIFICATION_MAX_CANDIDATES = int(
#     os.getenv("QCVIZ_MODIFICATION_MAX_CANDIDATES", "5")
# )
```

> 이미 `config.py`에서 동일 환경변수를 읽으므로 값이 동일.
> 다른 모듈이 `from routing_config import MODIFICATION_CONFIDENCE_THRESHOLD`로
> 접근해도 re-export되어 동작함.

---

## Patch 3/4: bridge.py — timeout profile 적용

> **위치**: LLM 호출 함수 (예: `_call_llm`, `_invoke_structured_stage`,
> 또는 Gemini/OpenAI 호출 래퍼) 내부
> **이유**: stage 이름에 따라 적절한 timeout을 자동 적용

### 변경 A: import 추가

```python
from qcviz_mcp.llm.providers import get_timeout_profile
```

### 변경 B: LLM 호출 시 profile 적용

> 기존 LLM 호출 부분을 찾아 (timeout이 하드코딩되어 있거나 기본값인 곳):

```python
        # ── Phase 4: stage-specific timeout ──────────────────
        _profile = get_timeout_profile(stage_name)
        _timeout = _profile["timeout"]
        _max_retries = int(_profile["max_retries"])
```

> `stage_name`은 함수 파라미터 또는 `self._current_stage` 등에서 가져옴.
> 기존 timeout 변수가 있으면 그 값을 `_timeout`으로 교체:
> ```python
> # 변경 전
> timeout = 30.0
> # 변경 후
> timeout = get_timeout_profile(stage_name).get("timeout", 30.0)
> ```

---

## Patch 4/4: prompts.py — modification/comparison 프롬프트 템플릿

> **위치**: 파일 끝에 추가
> **이유**: modification intent 추출과 comparison 설명 생성에 특화된 LLM 프롬프트

```python
# ── Phase 4: Phase 2~3 prompt templates ──────────────────────

MODIFICATION_INTENT_EXTRACTION_PROMPT = """\
You are analyzing a user's follow-up message about modifying a molecule.

Base molecule: {base_molecule}
User message: {user_message}

Extract the modification intent:
- from_group: the substituent to replace (or null if adding)
- to_group: the new substituent
- position_hint: any position specification (or null)
- confidence: 0.0-1.0

Return JSON only. No markdown fences."""


COMPARISON_EXPLANATION_PROMPT = """\
You are explaining quantum chemistry comparison results to a user.

Molecule A: {mol_a}
Molecule B: {mol_b}
Delta values: {delta_json}

Provide a clear, concise explanation in {language} covering:
1. Which molecule is more stable and by how much
2. Key electronic structure differences
3. Practical significance of the changes

Return natural language, not JSON."""
```

---

## 검증 명령

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04

# 1. timeout profiles
PYTHONPATH=src python -c "
from qcviz_mcp.llm.providers import get_timeout_profile
p = get_timeout_profile('modification_intent')
assert p['timeout'] == 15.0 and p['max_retries'] == 1, f'FAIL: {p}'
p2 = get_timeout_profile('comparison_explain')
assert p2['timeout'] == 25.0 and p2['max_retries'] == 2, f'FAIL: {p2}'
p3 = get_timeout_profile('unknown_stage')
assert p3['timeout'] == 30.0, f'FAIL default: {p3}'
print('✅ Timeout profiles OK')
"

# 2. config dedup 확인
PYTHONPATH=src python -c "
from qcviz_mcp.llm.routing_config import MODIFICATION_CONFIDENCE_THRESHOLD
from qcviz_mcp.config import MODIFICATION_CONFIDENCE_THRESHOLD as CFG
assert MODIFICATION_CONFIDENCE_THRESHOLD == CFG == 0.60, 'FAIL: values differ'
print(f'✅ Config dedup OK: {MODIFICATION_CONFIDENCE_THRESHOLD}')
"

# 3. prompt templates
PYTHONPATH=src python -c "
from qcviz_mcp.llm.prompts import (
    MODIFICATION_INTENT_EXTRACTION_PROMPT,
    COMPARISON_EXPLANATION_PROMPT,
)
assert '{base_molecule}' in MODIFICATION_INTENT_EXTRACTION_PROMPT
assert '{mol_a}' in COMPARISON_EXPLANATION_PROMPT
assert '{delta_json}' in COMPARISON_EXPLANATION_PROMPT
print('✅ Prompt templates OK')
"

# 4. bridge import 확인
grep -n "get_timeout_profile" src/qcviz_mcp/llm/bridge.py
# 기대: 1줄 이상

# 5. 기존 테스트 무결성
PYTHONPATH=src pytest tests/ -x -q 2>&1 | tail -5
```

---

## 다음 Day 연결점

- **Day 7 (최종)**: 전체 Phase 1~4 regression 테스트 매트릭스 수행 +
  성능 프로파일링 (modification candidate 생성 시간, comparison 2× SCF 시간).
  `.env.example` 최종 검수. 전체 완성 기준 체크리스트 확인.
