# Phase 4 Day 2: Rate-Limit 확장 & Error 체계 통합

## 변경 파일 목록

```
📄 파일: src/qcviz_mcp/security.py
   변경 유형: MODIFY
   변경 라인 수: ~8줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/errors.py
   변경 유형: MODIFY
   변경 라인 수: ~65줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/services/structure_intelligence.py
   변경 유형: MODIFY
   변경 라인 수: ~3줄 변경 (import 교체)
   의존성 변경: errors.ModificationError, errors.StructureIntelligenceError

📄 파일: src/qcviz_mcp/compute/job_manager.py
   변경 유형: MODIFY
   변경 라인 수: ~2줄 추가 (import)
   의존성 변경: errors.ComparisonError
```

---

## Patch 1/4: security.py — TOOL_COSTS에 Phase 2~3 비용 추가

> **위치**: `TOOL_COSTS` dict 정의 근처 (기존 값 아래에 `.update()`)
> **이유**: modification은 RDKit 연산(중간 비용), comparison은 2× SCF(높은 비용)

```python
# ── Phase 4: Phase 2~3 tool costs ────────────────────────────
TOOL_COSTS.update({
    "modification_preview": 8,     # RDKit substituent scan
    "modification_apply": 12,      # RDKit + SMILES validation
    "comparison_submit": 15,       # 2× full SCF calculation
    "comparison_delta": 10,        # delta post-processing + explanation
})
```

> `TOOL_COSTS`가 dict가 아닌 다른 형태이면 기존 패턴에 맞게 추가.

---

## Patch 2/4: errors.py — Phase 2~3 예외 클래스 통합 등록

> **위치**: 파일 끝, 기존 예외 클래스 아래에 추가
> **이유**: 전 모듈이 `errors.py`의 중앙 에러 체계를 일관되게 사용.
> Phase 2 Day 1-3에서 이미 `ModificationError`/`StructureIntelligenceError`를
> 추가했다면 아래 코드로 **교체** (더 상세한 context 포함).

```python
# ── Phase 4: Consolidated Phase 2~3 error classes ────────────


class ModificationError(QCVizError):
    """Phase 2: Error during molecular structure modification.

    Raised when substituent identification, swapping, or candidate
    generation fails.

    Attributes:
        base_smiles: SMILES of the base molecule being modified.
        from_group: Source substituent key.
        to_group: Target substituent key.
    """

    def __init__(
        self,
        message: str,
        *,
        base_smiles: "str | None" = None,
        from_group: "str | None" = None,
        to_group: "str | None" = None,
        suggestion: str = (
            "Check that the base molecule contains the specified "
            "substituent."
        ),
        **kwargs,
    ) -> None:
        details = {
            k: v
            for k, v in {
                "base_smiles": base_smiles,
                "from_group": from_group,
                "to_group": to_group,
            }.items()
            if v is not None
        }
        merged = {**kwargs}
        merged["details"] = {**merged.get("details", {}), **details}
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            suggestion=suggestion,
            **merged,
        )


class StructureIntelligenceError(QCVizError):
    """Phase 2: Internal error in the structure intelligence service.

    Raised for RDKit failures, unsupported molecule sizes,
    or unexpected computation errors.
    """

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(
            message,
            category=ErrorCategory.BACKEND,
            **kwargs,
        )


class ComparisonError(QCVizError):
    """Phase 3: Error during molecular comparison workflow.

    Raised when one or both comparison calculations fail,
    or when delta computation encounters an error.

    Attributes:
        mol_a: Name/SMILES of molecule A.
        mol_b: Name/SMILES of molecule B.
    """

    def __init__(
        self,
        message: str,
        *,
        mol_a: "str | None" = None,
        mol_b: "str | None" = None,
        suggestion: str = (
            "Ensure both molecules resolve correctly before comparing."
        ),
        **kwargs,
    ) -> None:
        details = {
            k: v
            for k, v in {"mol_a": mol_a, "mol_b": mol_b}.items()
            if v is not None
        }
        merged = {**kwargs}
        merged["details"] = {**merged.get("details", {}), **details}
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            suggestion=suggestion,
            **merged,
        )


class ComparisonTimeoutError(ComparisonError):
    """Phase 3: Comparison job exceeded the allowed time limit."""

    def __init__(
        self,
        message: str = "Comparison job timed out",
        **kwargs,
    ) -> None:
        super().__init__(
            message,
            suggestion="Try simpler molecules or a smaller basis set.",
            **kwargs,
        )
```

> **주의**: `ErrorCategory` enum 값이 `VALIDATION`/`BACKEND` 대문자인지
> `validation`/`backend` 소문자인지 기존 코드 확인 후 맞출 것.
> `to_mcp_error()` 메서드가 `QCVizError`에 존재하면 자동 상속됨.

---

## Patch 3/4: structure_intelligence.py — import를 errors.py 중앙으로 교체

> **위치**: 파일 상단 import 블록
> **이유**: 로컬 예외 정의 → 중앙 errors.py로 일원화

Phase 2 Day 1-3에서 `structure_intelligence.py` 내에 로컬로 예외를 정의했다면 제거하고:

```python
# ── import 변경 (기존 로컬 정의 → 중앙) ──────────────────────
from qcviz_mcp.errors import ModificationError, StructureIntelligenceError
```

> 기존에 이미 `from qcviz_mcp.errors import ...` 형태로 import하고 있다면 변경 불필요.
> 로컬 `class ModificationError(Exception)` 같은 정의가 남아있으면 삭제.

---

## Patch 4/4: job_manager.py — ComparisonError import 추가

> **위치**: 파일 상단 import 블록
> **이유**: comparison 실패 시 `ComparisonError`를 raise할 수 있도록

```python
from qcviz_mcp.errors import ComparisonError
```

> `submit_comparison()` 내에서 실패 시 사용 예:
> ```python
> except Exception as exc:
>     raise ComparisonError(
>         f"Comparison submission failed: {exc}",
>         mol_a=kwargs_a.get("structure_query"),
>         mol_b=kwargs_b.get("structure_query"),
>     ) from exc
> ```
> 이 사용은 선택적 — import만 추가해두면 다음 Day에서 활용 가능.

---

## 검증 명령

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04

# 1. errors.py 클래스 확인
PYTHONPATH=src python -c "
from qcviz_mcp.errors import (
    ModificationError, StructureIntelligenceError,
    ComparisonError, ComparisonTimeoutError,
)

# ModificationError with context
e1 = ModificationError(
    'swap failed', base_smiles='c1ccccc1',
    from_group='methyl', to_group='ethyl',
)
print(f'✅ ModificationError: {e1}')
if hasattr(e1, 'to_mcp_error'):
    print(f'   MCP: {e1.to_mcp_error()}')

# ComparisonError with context
e2 = ComparisonError('calc failed', mol_a='benzene', mol_b='toluene')
print(f'✅ ComparisonError: {e2}')

# ComparisonTimeoutError
e3 = ComparisonTimeoutError()
print(f'✅ ComparisonTimeoutError: {e3}')

print('\\n🎉 All error classes OK')
"

# 2. TOOL_COSTS 확인
PYTHONPATH=src python -c "
from qcviz_mcp.security import TOOL_COSTS
assert 'modification_preview' in TOOL_COSTS, 'FAIL'
assert 'comparison_submit' in TOOL_COSTS, 'FAIL'
print(f'✅ TOOL_COSTS includes Phase 2~3: {list(k for k in TOOL_COSTS if \"modification\" in k or \"comparison\" in k)}')
"

# 3. structure_intelligence.py import 확인
grep -n "from qcviz_mcp.errors import" \
  src/qcviz_mcp/services/structure_intelligence.py

# 4. job_manager.py import 확인
grep -n "ComparisonError" src/qcviz_mcp/compute/job_manager.py

# 5. 기존 테스트 무결성
PYTHONPATH=src pytest tests/ -x -q 2>&1 | tail -5
```

---

## 다음 Day 연결점

- **Day 3**: Observability 메트릭 확장 — `observability.py`에 modification lane,
  comparison job, implicit follow-up 감지에 대한 카운터/히스토그램 추가.
  pipeline trace에 Phase 2~3 context 데이터 포함.
