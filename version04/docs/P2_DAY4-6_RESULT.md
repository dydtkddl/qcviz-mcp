# Phase 2 Day 4-6: Pipeline에 modification_exploration lane 분기 구현

## 변경 파일 목록

```
📄 파일: src/qcviz_mcp/llm/schemas.py
   변경 유형: MODIFY
   변경 라인 수: ~45줄 추가, ~5줄 수정
   의존성 변경: 없음 (BaseModel, field_validator 이미 import됨)

📄 파일: src/qcviz_mcp/llm/lane_lock.py
   변경 유형: MODIFY
   변경 라인 수: ~5줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/llm/routing_config.py
   변경 유형: MODIFY
   변경 라인 수: ~5줄 추가
   의존성 변경: 없음 (os 이미 import됨)
```

---

## Patch 1/3: schemas.py — PlannerLane + ModificationIntent + 관련 확장

### 변경 ①: PlannerLane 리터럴 확장

> **위치**: `PlannerLane = Literal[...]` 정의
> **이유**: modification lane을 pipeline의 공식 lane으로 등록

```python
# 변경 전:
PlannerLane = Literal["chat_only", "grounding_required", "compute_ready"]

# 변경 후:
PlannerLane = Literal["chat_only", "grounding_required", "compute_ready", "modification_exploration"]
```

---

### 변경 ②: ModificationIntent 모델 신규 추가

> **위치**: `PlanResult` 클래스 정의 **바로 위**에 삽입
> **이유**: modification lane에서 "어떤 치환기를 어떤 치환기로 바꿀 것인지"를
> 구조화된 타입으로 전달

```python
class ModificationIntent(BaseModel):
    """Parsed intent for a molecular structure modification request.

    Captures the from/to substituent groups, optional position hint,
    and the base molecule being modified.

    Attributes:
        from_group: Substituent key to replace (e.g. "methyl").
        to_group: Substituent key for replacement (e.g. "ethyl").
        from_group_ko: Korean name of the from-group (e.g. "메틸").
        to_group_ko: Korean name of the to-group (e.g. "에틸").
        position_hint: Position specifier (e.g. "para", "2번").
        base_molecule_name: Name of the scaffold molecule.
        base_molecule_smiles: SMILES of the scaffold molecule.
        confidence: Confidence score for this parse (0.0–1.0).
    """

    from_group: Optional[str] = None
    to_group: Optional[str] = None
    from_group_ko: Optional[str] = None
    to_group_ko: Optional[str] = None
    position_hint: Optional[str] = None
    base_molecule_name: Optional[str] = None
    base_molecule_smiles: Optional[str] = None
    confidence: float = 0.0

    @field_validator(
        "from_group", "to_group", "from_group_ko", "to_group_ko",
        "position_hint", "base_molecule_name", "base_molecule_smiles",
        mode="before",
    )
    @classmethod
    def _norm(cls, v: Any) -> Optional[str]:
        return _as_optional_text(v)

    @field_validator("confidence", mode="before")
    @classmethod
    def _clamp(cls, v: Any) -> float:
        return _clamp_confidence(v)
```

> **주의**: `_as_optional_text`와 `_clamp_confidence`는 schemas.py에 이미 존재하는
> 내부 헬퍼. 만약 이름이 다르면 (`_blank_to_none`, `_coerce_confidence` 등)
> 기존 코드의 실제 함수명으로 치환.
>
> `_as_optional_text`가 없으면 직접 정의:
> ```python
> def _as_optional_text(v: Any) -> Optional[str]:
>     if v is None:
>         return None
>     s = str(v).strip()
>     return s if s else None
> ```
>
> `_clamp_confidence`가 없으면:
> ```python
> def _clamp_confidence(v: Any) -> float:
>     try:
>         f = float(v)
>         return max(0.0, min(1.0, f))
>     except (TypeError, ValueError):
>         return 0.0
> ```

---

### 변경 ③: PlanResult에 modification_intent 필드 추가

> **위치**: `PlanResult` 클래스 내부, 기존 필드 목록 끝
> **이유**: modification lane일 때 intent 데이터를 PlanResult에 포함

```python
    modification_intent: Optional[ModificationIntent] = None
```

---

### 변경 ④: PlanResult validator에 modification lane 제약 추가

> **위치**: `_check_plan_invariants` validator 내부 (또는 유사 validator)
> **이유**: modification_exploration lane은 modification_intent 필수

기존 validator에 분기 추가:

```python
        if self.lane == "modification_exploration" and not self.modification_intent:
            raise ValueError(
                "modification_exploration lane requires modification_intent"
            )
```

> 기존에 `compute_ready` lane에 molecule_name 필수 체크가 있는 부분 근처에 삽입.

---

### 변경 ⑤: GroundingSemanticOutcome 리터럴 확장

> **위치**: `GroundingSemanticOutcome = Literal[...]` 정의
> **이유**: grounding_merge가 modification 후보 준비 완료 상태를 표현

```python
# 기존 리터럴에 추가:
"modification_candidates_ready"
```

> 예시: `GroundingSemanticOutcome = Literal["...", "...", "modification_candidates_ready"]`

---

### 변경 ⑥: ExecutionAction 리터럴 확장

> **위치**: `ExecutionAction = Literal[...]` 정의
> **이유**: execution_guard가 modification preview 액션을 반환 가능하게

```python
# 기존 리터럴에 추가:
"modification_preview"
```

> 예시: `ExecutionAction = Literal["...", "...", "modification_preview"]`

---

## Patch 2/3: lane_lock.py — allows_modification() 추가

> **위치**: `LaneLock` 클래스 내부, 기존 `allows_grounding()` 메서드 바로 아래
> **이유**: modification lane 여부를 체크하는 메서드

```python
    def allows_modification(self) -> bool:
        """Return True if the current lane is modification_exploration.

        Returns:
            True when the pipeline is in modification exploration mode.
        """
        return self._lane == "modification_exploration"
```

> `self._lane`이 실제 코드에서 다른 이름이면 (`self.lane`, `self._current_lane` 등)
> 기존 코드의 속성명으로 치환.

---

## Patch 3/3: routing_config.py — modification threshold 상수

> **위치**: 파일 끝, 기존 threshold 상수 아래에 추가
> **이유**: modification lane의 confidence 기준값과 최대 후보 수 설정

```python
# ── Phase 2: Modification Lane ───────────────────────────────
MODIFICATION_CONFIDENCE_THRESHOLD = _env_float_any(
    ["QCVIZ_MODIFICATION_CONFIDENCE_THRESHOLD"], 0.60
)
MODIFICATION_MAX_CANDIDATES = int(
    os.getenv("QCVIZ_MODIFICATION_MAX_CANDIDATES", "5")
)
```

> `_env_float_any`는 routing_config.py에 이미 존재하는 헬퍼.
> 없으면:
> ```python
> def _env_float_any(keys, default):
>     import os
>     for k in keys:
>         v = os.getenv(k)
>         if v:
>             try: return float(v)
>             except ValueError: pass
>     return default
> ```
>
> `import os`가 파일 상단에 없으면 추가.

---

## 검증 명령

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04

PYTHONPATH=src python -c "
import typing
from qcviz_mcp.llm.schemas import (
    PlannerLane, ModificationIntent, PlanResult,
)

# 1. PlannerLane에 modification_exploration 포함 확인
args = typing.get_args(PlannerLane)
assert 'modification_exploration' in args, f'FAIL: {args}'
print(f'✅ PlannerLane: {args}')

# 2. ModificationIntent 생성
mi = ModificationIntent(from_group='methyl', to_group='ethyl', confidence=0.8)
assert mi.from_group == 'methyl'
assert mi.to_group == 'ethyl'
assert mi.confidence == 0.8
print(f'✅ ModificationIntent: {mi.from_group} → {mi.to_group} (conf={mi.confidence})')

# 3. PlanResult에 modification_intent 포함
pr = PlanResult(lane='modification_exploration', modification_intent=mi)
assert pr.lane == 'modification_exploration'
assert pr.modification_intent.from_group == 'methyl'
print(f'✅ PlanResult lane={pr.lane}, intent={pr.modification_intent.from_group}→{pr.modification_intent.to_group}')

# 4. modification_exploration without intent → ValueError
try:
    PlanResult(lane='modification_exploration', modification_intent=None)
    print('❌ FAIL: should have raised ValueError')
except ValueError as e:
    print(f'✅ Validator rejects no-intent: {e}')
except Exception as e:
    print(f'⚠️  Different error type: {type(e).__name__}: {e}')

# 5. GroundingSemanticOutcome 확인
from qcviz_mcp.llm.schemas import GroundingSemanticOutcome
gso_args = typing.get_args(GroundingSemanticOutcome)
assert 'modification_candidates_ready' in gso_args, f'FAIL: {gso_args}'
print(f'✅ GroundingSemanticOutcome includes modification_candidates_ready')

# 6. ExecutionAction 확인
from qcviz_mcp.llm.schemas import ExecutionAction
ea_args = typing.get_args(ExecutionAction)
assert 'modification_preview' in ea_args, f'FAIL: {ea_args}'
print(f'✅ ExecutionAction includes modification_preview')

print()
"

# lane_lock 확인
PYTHONPATH=src python -c "
from qcviz_mcp.llm.lane_lock import LaneLock

# allows_modification 존재 확인
lock = LaneLock()
assert hasattr(lock, 'allows_modification'), 'FAIL: method missing'

# LaneLock 생성 방법에 따라 다를 수 있음
# 방법 1: from_lane 클래스메서드가 있는 경우
try:
    lock_mod = LaneLock.from_lane('modification_exploration')
    assert lock_mod.allows_modification(), 'FAIL'
    print('✅ LaneLock.allows_modification() = True (via from_lane)')
except AttributeError:
    # 방법 2: set() 메서드
    lock2 = LaneLock()
    lock2.set('modification_exploration')
    assert lock2.allows_modification(), 'FAIL'
    print('✅ LaneLock.allows_modification() = True (via set)')
"

# routing_config 확인
PYTHONPATH=src python -c "
from qcviz_mcp.llm.routing_config import (
    MODIFICATION_CONFIDENCE_THRESHOLD,
    MODIFICATION_MAX_CANDIDATES,
)
assert MODIFICATION_CONFIDENCE_THRESHOLD == 0.60
assert MODIFICATION_MAX_CANDIDATES == 5
print(f'✅ MODIFICATION_CONFIDENCE_THRESHOLD={MODIFICATION_CONFIDENCE_THRESHOLD}')
print(f'✅ MODIFICATION_MAX_CANDIDATES={MODIFICATION_MAX_CANDIDATES}')
"

# 기존 테스트 무결성
PYTHONPATH=src pytest tests/ -x -q 2>&1 | tail -5
```

---

## 다음 Day 연결점

- **Day 7-9**: `grounding_merge.py`에 modification lane 분기 추가
  (`lane == "modification_exploration"` → `generate_modification_candidates()` 호출
  → `GroundingOutcome`에 candidates 채움).
  `execution_guard.py`에 `"modification_preview"` 액션 분기.
  `chat.py`에 `_handle_modification_exploration()` 핸들러 신설.
