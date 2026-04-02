# Phase 4 Day 4: Feature-Flag 통합 & .env.example 문서화

## 변경 파일 목록

```
📄 파일: src/qcviz_mcp/env_bootstrap.py
   변경 유형: MODIFY
   변경 라인 수: ~30줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/config.py
   변경 유형: MODIFY
   변경 라인 수: ~15줄 추가
   의존성 변경: 없음 (os 이미 import됨)

📄 파일: .env.example
   변경 유형: MODIFY
   변경 라인 수: ~35줄 추가
   의존성 변경: N/A
```

---

## Patch 1/3: env_bootstrap.py — feature flag 통합 보고

> **위치**: `bootstrap_runtime_env()` 함수 반환 직전,
> 또는 파일 끝에 독립 섹션
> **이유**: 서버 기동 시 Phase 2~3 flag 상태를 일괄 로깅하여 운영 가시성 확보

```python
# ── Phase 4: Feature flag registry ───────────────────────────

_FEATURE_FLAGS: Dict[str, tuple] = {
    "QCVIZ_CONTEXT_TRACKING_ENABLED": (
        "false", "Phase 1 conversation context tracking",
    ),
    "QCVIZ_MODIFICATION_LANE_ENABLED": (
        "false", "Phase 2 modification exploration lane",
    ),
    "QCVIZ_COMPARISON_ENABLED": (
        "false", "Phase 3 comparison & delta view",
    ),
}


def _log_feature_flags() -> Dict[str, bool]:
    """Check and log the status of all Phase 1~3 feature flags.

    Returns:
        Dict mapping flag name → enabled (bool).
    """
    flags: Dict[str, bool] = {}
    for key, (default, desc) in _FEATURE_FLAGS.items():
        raw = os.environ.get(key, default).strip().lower()
        enabled = raw in ("1", "true", "yes", "on")
        flags[key] = enabled
        logger.info(
            "Feature flag %s (%s): %s",
            key, desc, "ENABLED" if enabled else "disabled",
        )
    return flags


def get_feature_flags() -> Dict[str, bool]:
    """Return current feature flag states for external modules.

    Returns:
        Dict mapping flag name → enabled (bool).

    # Test scenario: get_feature_flags()
    #   → {"QCVIZ_CONTEXT_TRACKING_ENABLED": False, ...}
    """
    return _log_feature_flags()
```

> `bootstrap_runtime_env()` 내부에 `_log_feature_flags()` 호출을 삽입하면
> 서버 기동 시 자동으로 flag 상태가 로그에 출력됨:
> ```python
> def bootstrap_runtime_env(...):
>     ...  # 기존 로직
>     _log_feature_flags()  # ← 추가
>     return ...
> ```

---

## Patch 2/3: config.py — Phase 2~3 임계값 통합

> **위치**: `ServerConfig` 클래스 아래 또는 파일 끝의 모듈 레벨 상수 영역
> **이유**: `routing_config.py`와 중복되는 임계값을 `config.py`에 단일 진실 소스로 통합

```python
# ── Phase 4: Phase 2~3 configuration constants ───────────────
# These provide a single source of truth. routing_config.py
# should import from here instead of duplicating.

# Phase 2: Modification
MODIFICATION_CONFIDENCE_THRESHOLD: float = float(
    os.environ.get("QCVIZ_MODIFICATION_CONFIDENCE_THRESHOLD", "0.60")
)
MODIFICATION_MAX_CANDIDATES: int = int(
    os.environ.get("QCVIZ_MODIFICATION_MAX_CANDIDATES", "5")
)

# Phase 3: Comparison
COMPARISON_MAX_CONCURRENT: int = int(
    os.environ.get("QCVIZ_COMPARISON_MAX_CONCURRENT", "3")
)
COMPARISON_TIMEOUT_SEC: float = float(
    os.environ.get("QCVIZ_COMPARISON_TIMEOUT_SEC", "300.0")
)
```

> 이후 `routing_config.py`에서 이 값들을 import하도록 변경하면
> 중복 제거 완료 (Day 6 Config 통합에서 처리):
> ```python
> # routing_config.py
> from qcviz_mcp.config import MODIFICATION_CONFIDENCE_THRESHOLD
> ```

---

## Patch 3/3: .env.example — 전체 신규 환경변수 문서화

> **위치**: 파일 끝에 추가 (기존 내용 보존)
> **이유**: 모든 Phase 1~3 환경변수를 한 곳에서 참조 가능하도록

```ini
# ============================================================
# Phase 1: Conversation Context Tracking
# ============================================================
# Enables implicit follow-up detection and active molecule tracking.
# QCVIZ_CONTEXT_TRACKING_ENABLED=false

# ============================================================
# Phase 2: Modification Exploration
# ============================================================
# Enables RDKit-based molecular modification exploration.
# Requires Phase 1 context tracking to work effectively.
# QCVIZ_MODIFICATION_LANE_ENABLED=false
# QCVIZ_MODIFICATION_CONFIDENCE_THRESHOLD=0.60
# QCVIZ_MODIFICATION_MAX_CANDIDATES=5

# ============================================================
# Phase 3: Comparison & Delta View
# ============================================================
# Enables side-by-side molecular comparison calculations.
# QCVIZ_COMPARISON_ENABLED=false
# QCVIZ_COMPARISON_MAX_CONCURRENT=3
# QCVIZ_COMPARISON_TIMEOUT_SEC=300.0

# ============================================================
# Security / Rate Limiting
# ============================================================
# QCVIZ_RATE_LIMIT_CAPACITY=100
# QCVIZ_RATE_LIMIT_REFILL=1.0
```

---

## 검증 명령

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04

# 1. env_bootstrap feature flags
PYTHONPATH=src python -c "
from qcviz_mcp.env_bootstrap import get_feature_flags
flags = get_feature_flags()
assert 'QCVIZ_MODIFICATION_LANE_ENABLED' in flags, 'FAIL'
assert 'QCVIZ_COMPARISON_ENABLED' in flags, 'FAIL'
assert 'QCVIZ_CONTEXT_TRACKING_ENABLED' in flags, 'FAIL'
print(f'✅ Feature flags: {flags}')
"

# 2. config 임계값
PYTHONPATH=src python -c "
from qcviz_mcp.config import (
    MODIFICATION_CONFIDENCE_THRESHOLD, MODIFICATION_MAX_CANDIDATES,
    COMPARISON_MAX_CONCURRENT, COMPARISON_TIMEOUT_SEC,
)
assert MODIFICATION_CONFIDENCE_THRESHOLD == 0.60
assert MODIFICATION_MAX_CANDIDATES == 5
assert COMPARISON_MAX_CONCURRENT == 3
assert COMPARISON_TIMEOUT_SEC == 300.0
print(f'✅ Config: mod_threshold={MODIFICATION_CONFIDENCE_THRESHOLD}, '
      f'mod_max={MODIFICATION_MAX_CANDIDATES}, '
      f'cmp_concurrent={COMPARISON_MAX_CONCURRENT}, '
      f'cmp_timeout={COMPARISON_TIMEOUT_SEC}')
"

# 3. .env.example 변수 수 확인
grep -c "MODIFICATION\|COMPARISON\|CONTEXT_TRACKING" .env.example
# 기대: 7 이상

# 4. 기존 테스트 무결성
PYTHONPATH=src pytest tests/ -x -q 2>&1 | tail -5
```

---

## 다음 Day 연결점

- **Day 5**: Advisor 연동 — `advisor_flow.py`에 modification context
  (active_molecule + modification_intent)를 전파하여 advisor가 "이 변형이
  에너지적으로 유리한가?" 같은 추천 제공. `advisor_tools.py`에
  modification/comparison 전용 tool 등록.
