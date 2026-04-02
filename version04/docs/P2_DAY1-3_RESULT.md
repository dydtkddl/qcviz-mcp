# Phase 2 Day 1-3: services/structure_intelligence.py 신규 생성

## 변경 파일 목록

```
📄 파일: src/qcviz_mcp/services/structure_intelligence.py
   변경 유형: CREATE (신규 파일)
   변경 라인 수: ~340줄
   의존성 변경: rdkit (optional, try/except guard)

📄 파일: src/qcviz_mcp/errors.py
   변경 유형: MODIFY
   변경 라인 수: ~12줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/services/__init__.py
   변경 유형: MODIFY
   변경 라인 수: ~3줄 추가
   의존성 변경: 없음
```

---

## Patch 1/3: structure_intelligence.py (CREATE)

> 별도 파일로 제공됨 → `structure_intelligence.py` 전체를
> `src/qcviz_mcp/services/structure_intelligence.py`에 복사

핵심 API:

| 함수 | 입력 | 출력 | 용도 |
|------|------|------|------|
| `identify_substituents(smiles)` | SMILES | `[{atom_idx, current_group, ...}]` | 교체 가능 위치 탐색 |
| `swap_substituent(smiles, idx, key)` | SMILES + 위치 + 그룹 | modified SMILES or None | 단일 치환 수행 |
| `generate_modification_candidates(smiles, from, to)` | base + from/to group | `[{candidate_smiles, property_delta, ...}]` | 후보 일괄 생성 |
| `preview_property_delta(base, modified)` | 두 SMILES | `{mw_delta, logp_delta, tpsa_delta}` | 물성 변화 미리보기 |
| `SUBSTITUENT_SMARTS` | — | dict (13개 치환기) | 치환기 SMARTS 사전 |

---

## Patch 2/3: errors.py — Phase 2 예외 추가

> **위치**: `errors.py` 파일 끝, 기존 예외 클래스 아래에 추가
> **이유**: modification lane 전용 예외를 에러 계층에 등록

```python
class ModificationError(QCVizError):
    """Raised when a molecular modification operation fails.

    Examples: invalid substituent key, RDKit sanitization failure,
    unsupported modification type.
    """

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, ErrorCategory.VALIDATION, **kwargs)


class StructureIntelligenceError(QCVizError):
    """Raised when the structure intelligence backend encounters an error.

    Examples: RDKit unavailable, SMILES parsing failure,
    molecule too large.
    """

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, ErrorCategory.BACKEND, **kwargs)
```

---

## Patch 3/3: services/__init__.py — export 추가

> **위치**: 기존 export 목록 끝에 추가
> **이유**: 다른 모듈에서 `from qcviz_mcp.services import structure_intelligence` 가능

```python
# ── Phase 2: Structure Intelligence ──────────────────────────
try:
    from qcviz_mcp.services import structure_intelligence  # noqa: F401
except ImportError:
    pass  # RDKit optional — module may fail to fully load
```

> 또는 기존 `__init__.py`가 `__all__` 리스트를 사용하면:
> ```python
> __all__ = [
>     ...existing...,
>     "structure_intelligence",
> ]
> ```

---

## 검증 명령

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04

# 1. 모듈 import + RDKit 가용성 확인
PYTHONPATH=src python -c "
from qcviz_mcp.services.structure_intelligence import (
    identify_substituents, swap_substituent,
    generate_modification_candidates, preview_property_delta,
    SUBSTITUENT_SMARTS, _RDKIT_AVAILABLE
)
print(f'✅ Module imported. RDKit available: {_RDKIT_AVAILABLE}')
print(f'   Substituent count: {len(SUBSTITUENT_SMARTS)}')
"

# 2. 예외 클래스 확인
PYTHONPATH=src python -c "
from qcviz_mcp.errors import ModificationError, StructureIntelligenceError
print('✅ Error classes OK')
"

# 3. 기능 테스트 (RDKit 필요)
PYTHONPATH=src python -c "
from qcviz_mcp.services.structure_intelligence import (
    generate_modification_candidates, preview_property_delta,
    identify_substituents, _RDKIT_AVAILABLE
)
if not _RDKIT_AVAILABLE:
    print('⚠️  RDKit not installed — skipping functional tests')
    print('   Install: pip install rdkit-pypi')
    exit(0)

# Test 1: 벤젠 H→methyl = 톨루엔
candidates = generate_modification_candidates('c1ccccc1', 'hydrogen', 'methyl')
print(f'벤젠 H→methyl: {len(candidates)} candidates')
for c in candidates[:3]:
    print(f'  {c[\"candidate_smiles\"]} Δmw={c[\"property_delta\"][\"mw_delta\"]:.1f}')
assert len(candidates) > 0, 'FAIL: no candidates for benzene'

# Test 2: property delta
delta = preview_property_delta('c1ccccc1', 'Cc1ccccc1')
print(f'벤젠→톨루엔 delta: mw={delta[\"mw_delta\"]:.1f} logp={delta[\"logp_delta\"]:.2f}')
assert abs(delta['mw_delta'] - 14.0) < 1.0, f'FAIL: unexpected mw_delta {delta}'

# Test 3: identify substituents
subs = identify_substituents('CCNC')
print(f'CCNC substituents: {len(subs)} positions')

# Test 4: 빈 SMILES / 잘못된 SMILES
bad = generate_modification_candidates('', 'hydrogen', 'methyl')
assert bad == [], f'FAIL: should be empty for bad SMILES'
bad2 = generate_modification_candidates('INVALID', 'hydrogen', 'methyl')
assert bad2 == [], f'FAIL: should be empty for invalid SMILES'

print('✅ ALL FUNCTIONAL TESTS PASS')
"

# 4. 기존 테스트 무결성
PYTHONPATH=src pytest tests/ -x -q 2>&1 | tail -5
```

---

## 다음 Day 연결점

- **Day 4-6**: `generate_modification_candidates()`를 pipeline의
  `modification_exploration` lane에서 호출. `schemas.py`에 `PlannerLane`
  리터럴 확장 + `lane_lock.py`에 `allows_modification()` 추가 +
  `grounding_merge.py`에 modification 분기 추가.
