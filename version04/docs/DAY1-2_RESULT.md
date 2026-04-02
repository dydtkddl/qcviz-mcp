# Day 1-2: ConversationState에 ActiveMolecule 추가

## 변경 파일 목록

```
📄 파일: src/qcviz_mcp/config.py
   변경 유형: MODIFY (기존 파일 수정)
   변경 라인 수: ~2줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/web/conversation_state.py
   변경 유형: MODIFY (기존 파일 수정)
   변경 라인 수: ~110줄 추가, ~3줄 수정
   의존성 변경: 새 import: typing.TypedDict, typing.List
```

---

## Patch 1/2: config.py

### 변경 ①: ServerConfig에 feature flag 필드 추가
> **이유**: 신규 context tracking 로직을 feature flag 뒤에 숨겨 기존 동작을 보호

`ServerConfig` dataclass의 **마지막 필드 뒤**에 추가:

```python
    context_tracking_enabled: bool = False
```

### 변경 ②: from_env()에 환경변수 매핑 추가
> **이유**: QCVIZ_CONTEXT_TRACKING_ENABLED 환경변수로 런타임 on/off 제어

`from_env()` 내부의 `alt_env_keys` 딕셔너리에 추가:

```python
            "context_tracking_enabled": "QCVIZ_CONTEXT_TRACKING_ENABLED",
```

---

## Patch 2/2: conversation_state.py

### 변경 A: import 확장 + ActiveMolecule 타입 정의
> **위치**: 파일 상단 import 블록 끝 → 첫 번째 함수 정의 전
> **이유**: Phase 1 전체에서 참조되는 핵심 대화 맥락 타입

기존 `typing` import에 `TypedDict`, `List`를 병합 (또는 새 import 추가):

```python
from typing import TypedDict, List  # 기존 typing import에 병합
```

import 블록 직후, 첫 함수 정의 전에 삽입:

```python
# ── Phase 1: Active Molecule Context ─────────────────────────
_MAX_MOLECULE_HISTORY = 10


class ActiveMolecule(TypedDict, total=False):
    """Semantic context for the molecule currently under discussion.

    All fields are optional (total=False), but ``canonical_name`` must
    be present for the instance to be considered valid.

    Attributes:
        canonical_name: Normalised English name, e.g. "methylethylamine".
        smiles: Canonical SMILES string, e.g. "CCNC".
        formula: Molecular formula, e.g. "C3H9N".
        cid: PubChem Compound ID.
        source: How this molecule was identified.
            One of "chat_grounding", "compute_result", "user_confirm".
        set_at_turn: Conversation turn number when this was set.
    """

    canonical_name: str
    smiles: str
    formula: str
    cid: int
    source: str
    set_at_turn: int
```

### 변경 B: CRUD 함수 4개 + 내부 헬퍼 1개
> **위치**: `clear_conversation_state()` 함수 정의 바로 **위**에 삽입
> **이유**: active_molecule의 읽기/쓰기/초기화/이력 조회 API

```python
def _is_context_tracking_enabled() -> bool:
    """Check whether the context-tracking feature flag is active.

    Returns:
        True if QCVIZ_CONTEXT_TRACKING_ENABLED is set to a truthy value.
    """
    import os
    return os.getenv("QCVIZ_CONTEXT_TRACKING_ENABLED", "").lower() in (
        "1", "true", "yes",
    )


def get_active_molecule(
    session_id: str,
    *,
    manager=None,
) -> "ActiveMolecule | None":
    """Return the active molecule for *session_id*, or ``None``.

    Args:
        session_id: WebSocket / REST session identifier.
        manager: Optional job-manager instance (passed through to
            ``load_conversation_state``).

    Returns:
        An ``ActiveMolecule`` dict if one is set and has a valid
        ``canonical_name``; ``None`` otherwise.
    """
    state = load_conversation_state(session_id, manager=manager)
    mol = state.get("active_molecule")
    if not isinstance(mol, dict) or not mol.get("canonical_name"):
        return None
    return mol  # type: ignore[return-value]


def set_active_molecule(
    session_id: str,
    molecule: "ActiveMolecule",
    *,
    manager=None,
) -> None:
    """Set or replace the active molecule for *session_id*.

    When the canonical name changes, the previous molecule is pushed
    onto ``molecule_history`` (max ``_MAX_MOLECULE_HISTORY`` entries,
    FIFO).

    Does nothing when:
    * The context-tracking feature flag is disabled, **or**
    * *molecule* lacks ``canonical_name``.

    Args:
        session_id: Session identifier.
        molecule: New active molecule data.
        manager: Optional job-manager instance.
    """
    if not _is_context_tracking_enabled():
        return
    if not molecule.get("canonical_name"):
        return

    state = load_conversation_state(session_id, manager=manager)
    history: list = list(state.get("molecule_history", []))

    prev = state.get("active_molecule")
    if (
        isinstance(prev, dict)
        and prev.get("canonical_name")
        and prev["canonical_name"] != molecule.get("canonical_name")
    ):
        history.insert(0, prev)
        history = history[:_MAX_MOLECULE_HISTORY]

    update_conversation_state(
        session_id,
        {"active_molecule": dict(molecule), "molecule_history": history},
        manager=manager,
    )
    logger.debug(
        "active_molecule updated: session=%s name=%s",
        session_id,
        molecule.get("canonical_name"),
    )


def clear_active_molecule(
    session_id: str,
    *,
    manager=None,
) -> None:
    """Clear the active molecule while preserving history.

    Args:
        session_id: Session identifier.
        manager: Optional job-manager instance.
    """
    update_conversation_state(
        session_id,
        {"active_molecule": None},
        manager=manager,
    )
    logger.debug("active_molecule cleared: session=%s", session_id)


def get_molecule_history(
    session_id: str,
    *,
    manager=None,
) -> "List[ActiveMolecule]":
    """Return the molecule history list (most-recent first).

    Args:
        session_id: Session identifier.
        manager: Optional job-manager instance.

    Returns:
        List of previously active molecules, newest first.  May be empty.
    """
    state = load_conversation_state(session_id, manager=manager)
    return list(state.get("molecule_history", []))
```

### 변경 C: build_execution_state() 연동
> **위치**: `build_execution_state()` 함수 내부, `return` 문 **직전**
> **이유**: compute 결과에서 분자 정보를 자동 추출하여 호출자(chat.py)가 set_active_molecule()에 전달할 수 있도록

return문 직전에 삽입:

```python
    # ── Phase 1: auto-extract pending active molecule ────────
    _pending_mol: dict = {}
    if structure_name:
        _pending_mol["canonical_name"] = structure_name
    if isinstance(result, dict):
        if result.get("smiles"):
            _pending_mol["smiles"] = result["smiles"]
        if result.get("formula"):
            _pending_mol["formula"] = result["formula"]
    _pending_mol["source"] = "compute_result"
    _pending_mol["set_at_turn"] = 0  # placeholder — caller sets real value
```

return dict에 키 추가:

```python
        "_pending_active_molecule": _pending_mol if _pending_mol.get("canonical_name") else None,
```

---

## 검증 명령

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04

# 1. 타입 import 확인
python -c "from qcviz_mcp.web.conversation_state import ActiveMolecule; print('✅ ActiveMolecule importable')"

# 2. config feature flag 확인
python -c "from qcviz_mcp.config import ServerConfig; c = ServerConfig(); assert c.context_tracking_enabled == False; print('✅ config OK')"

# 3. grep으로 삽입 위치 확인
grep -n "active_molecule\|ActiveMolecule\|_pending_active_molecule" src/qcviz_mcp/web/conversation_state.py

# 4. 전체 CRUD 검증 (verify_day1_2.py를 프로젝트 루트에 복사 후)
PYTHONPATH=src QCVIZ_CONTEXT_TRACKING_ENABLED=true python verify_day1_2.py

# 5. 기존 테스트 깨지지 않았는지 확인
PYTHONPATH=src pytest tests/ -x -q 2>&1 | tail -5
```

---

## 다음 Day 연결점

- **Day 3-4**: `normalizer.py`가 `get_active_molecule(session_id)`를 호출하여
  active molecule이 존재하고 + 사용자 입력에 명시적 분자명이 없으면
  `is_follow_up: True`로 판정. `follow_up_type`도 세분화.
- **Day 8-10**: `chat.py`가 응답 완료 시 `build_execution_state()` 반환값의
  `_pending_active_molecule`을 꺼내 `set_active_molecule()`을 호출하여
  대화 맥락을 자동 갱신.
