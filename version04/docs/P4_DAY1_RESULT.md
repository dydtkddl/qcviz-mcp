# Phase 4 Day 1: Security 강화 — 입력 Sanitization 확장

## 변경 파일 목록

```
📄 파일: src/qcviz_mcp/security.py
   변경 유형: MODIFY
   변경 라인 수: ~55줄 추가
   의존성 변경: 없음 (re 이미 import됨)

📄 파일: src/qcviz_mcp/web/routes/chat.py
   변경 유형: MODIFY
   변경 라인 수: ~12줄 추가
   의존성 변경: 새 import: security.validate_modification_input, validate_comparison_input
```

---

## Patch 1/2: security.py — modification + comparison 입력 검증 함수

> **위치**: 파일 끝, 기존 validation 함수 아래에 추가
> **이유**: Phase 2~3에서 추가된 입력 경로(치환기명, SMILES, 분자명)에
> 셸 인젝션 문자 차단 및 길이 제한 적용

```python
# ── Phase 4: Input sanitization for Phase 2~3 ───────────────

_FORBIDDEN_SUBSTITUENT_CHARS = re.compile(r"[;|&$`\\<>{}()\[\]!]")
_MAX_SUBSTITUENT_NAME_LEN = 50


def validate_modification_input(
    from_group: "str | None",
    to_group: "str | None",
    base_smiles: "str | None",
    *,
    max_smiles_len: int = 500,
) -> None:
    """Validate Phase 2 modification request inputs.

    Checks substituent group names for forbidden characters and
    length limits.  Checks base SMILES length.

    Args:
        from_group: Source substituent key (e.g. "methyl").
        to_group: Target substituent key (e.g. "ethyl").
        base_smiles: SMILES string of the base molecule.
        max_smiles_len: Maximum allowed SMILES length.

    Raises:
        ValidationError: If any input fails validation.

    # Test scenario: validate_modification_input("methyl; rm -rf /", None, None)
    #   → raises ValidationError
    """
    for label, val in [("from_group", from_group), ("to_group", to_group)]:
        if val is None:
            continue
        if len(val) > _MAX_SUBSTITUENT_NAME_LEN:
            raise ValidationError(
                f"{label} too long (max {_MAX_SUBSTITUENT_NAME_LEN})"
            )
        if _FORBIDDEN_SUBSTITUENT_CHARS.search(val):
            raise ValidationError(
                f"{label} contains forbidden characters"
            )
    if base_smiles is not None and len(base_smiles) > max_smiles_len:
        raise ValidationError(
            f"base_smiles too long (max {max_smiles_len})"
        )


def validate_comparison_input(
    mol_a: str,
    mol_b: str,
    *,
    max_name_len: int = 200,
) -> None:
    """Validate Phase 3 comparison request inputs.

    Checks molecule names/SMILES for emptiness, length, and
    forbidden characters.

    Args:
        mol_a: Name or SMILES of molecule A.
        mol_b: Name or SMILES of molecule B.
        max_name_len: Maximum allowed name/SMILES length.

    Raises:
        ValidationError: If any input fails validation.

    # Test scenario: validate_comparison_input("", "toluene")
    #   → raises ValidationError
    """
    for label, val in [("mol_a", mol_a), ("mol_b", mol_b)]:
        if not val or not val.strip():
            raise ValidationError(f"{label} must not be empty")
        if len(val) > max_name_len:
            raise ValidationError(
                f"{label} too long (max {max_name_len})"
            )
        if _FORBIDDEN_SUBSTITUENT_CHARS.search(val):
            raise ValidationError(
                f"{label} contains forbidden characters"
            )
```

> **주의**: `ValidationError`는 security.py에 이미 정의된 예외 클래스.
> 없으면 `errors.py`의 `QCVizError`를 사용하거나:
> ```python
> class ValidationError(Exception):
>     pass
> ```

---

## Patch 2/2: chat.py — handler 진입부에 validation 호출 삽입

### 변경 A: modification handler에 sanitization 추가

> **위치**: `_handle_modification_exploration()` 함수 상단,
> 기존 `_RDKIT_AVAILABLE` 체크 바로 위
> **이유**: 사용자 입력이 RDKit/structure_intelligence에 도달하기 전 sanitize

```python
        # ── Phase 4: input sanitization ──────────────────────
        try:
            from qcviz_mcp.security import validate_modification_input
            validate_modification_input(
                from_group, to_group, base_smiles,
            )
        except Exception as exc:
            await _ws_send(
                websocket, "error",
                session_id=session_id,
                message=f"입력 검증 실패: {exc}",
                timestamp=_now_ts(),
            )
            return
```

### 변경 B: comparison handler에 sanitization 추가

> **위치**: `_handle_comparison_request()` 함수 상단,
> targets 추출 직후
> **이유**: 분자명/SMILES가 compute에 도달하기 전 검증

```python
        # ── Phase 4: input sanitization ──────────────────────
        try:
            from qcviz_mcp.security import validate_comparison_input
            validate_comparison_input(targets[0], targets[1])
        except Exception as exc:
            await _ws_send(
                websocket, "error",
                session_id=session_id,
                message=f"비교 요청 검증 실패: {exc}",
                timestamp=_now_ts(),
            )
            return
```

---

## 검증 명령

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04

# 1. security.py 함수 존재 확인
grep -n "validate_modification_input\|validate_comparison_input" \
  src/qcviz_mcp/security.py
# 기대: 2줄 (함수 정의)

# 2. chat.py 호출 확인
grep -n "validate_modification_input\|validate_comparison_input" \
  src/qcviz_mcp/web/routes/chat.py
# 기대: 2줄 이상

# 3. 기능 테스트
PYTHONPATH=src python -c "
from qcviz_mcp.security import validate_modification_input, validate_comparison_input

# 정상 케이스
validate_modification_input('methyl', 'ethyl', 'c1ccccc1')
validate_comparison_input('benzene', 'toluene')
print('✅ Normal cases pass')

# 비정상: 셸 인젝션 문자
try:
    validate_modification_input('methyl; rm -rf /', None, None)
    print('❌ FAIL: should have raised')
except Exception as e:
    print(f'✅ Injection blocked: {e}')

# 비정상: 빈 값
try:
    validate_comparison_input('', 'toluene')
    print('❌ FAIL: should have raised')
except Exception as e:
    print(f'✅ Empty blocked: {e}')

# 비정상: 길이 초과
try:
    validate_modification_input('A' * 100, None, None)
    print('❌ FAIL: should have raised')
except Exception as e:
    print(f'✅ Length blocked: {e}')

# 비정상: SMILES 길이 초과
try:
    validate_modification_input(None, None, 'C' * 600)
    print('❌ FAIL: should have raised')
except Exception as e:
    print(f'✅ SMILES length blocked: {e}')

print('\\n🎉 All security validation tests passed')
"

# 4. 기존 테스트 무결성
PYTHONPATH=src pytest tests/ -x -q 2>&1 | tail -5
```

---

## 다음 Day 연결점

- **Day 2**: Rate-limit 정책에 Phase 2~3 작업 비용을 반영 (modification은
  단일 compute보다 가볍지만 structure_intelligence 호출 비용, comparison은
  2배 compute 비용). `errors.py`에 Phase 2~3 예외를 체계적으로 통합 등록.
