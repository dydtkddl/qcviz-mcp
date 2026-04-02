# Phase 2 Day 10-14: 한국어 치환기 사전 + normalizer 연동 + pipeline 연결 + 통합 검증

## 변경 파일 목록

```
📄 파일: src/qcviz_mcp/services/ko_aliases.py
   변경 유형: MODIFY
   변경 라인 수: ~55줄 추가
   의존성 변경: 새 import: re (이미 있으면 확인만)

📄 파일: src/qcviz_mcp/llm/normalizer.py
   변경 유형: MODIFY
   변경 라인 수: ~100줄 추가
   의존성 변경: 새 import: ko_aliases.translate_substituent

📄 파일: src/qcviz_mcp/llm/pipeline.py
   변경 유형: MODIFY
   변경 라인 수: ~30줄 추가
   의존성 변경: 새 import: normalizer.parse_modification_intent, schemas.ModificationIntent
```

---

## Patch 1/3: ko_aliases.py — 치환기 한→영 번역 사전 + 함수

> **위치**: 파일 끝, 기존 `KO_TO_EN` dict와 `translate()` 함수 아래
> **이유**: "메틸기를 에틸기로" 같은 한국어 치환기명을 영어 키로 정확히 변환

```python
import re  # 이미 있으면 확인만


# ── Phase 2: Substituent Korean → English dictionary ─────────
SUBSTITUENT_KO_TO_EN: Dict[str, str] = {
    # alkyl
    "메틸": "methyl", "메틸기": "methyl",
    "에틸": "ethyl", "에틸기": "ethyl",
    "프로필": "propyl", "프로필기": "propyl",
    "부틸": "butyl", "부틸기": "butyl",
    # oxygen-containing
    "하이드록시": "hydroxy", "하이드록시기": "hydroxy",
    "히드록시": "hydroxy", "히드록시기": "hydroxy",
    "수산기": "hydroxy", "수산화기": "hydroxy",
    "메톡시": "methoxy", "메톡시기": "methoxy",
    "에톡시": "ethoxy", "에톡시기": "ethoxy",
    "포밀": "formyl", "알데히드": "formyl",
    "아세틸": "acetyl", "아세틸기": "acetyl",
    "카르복실": "carboxyl", "카르복시": "carboxyl", "카복실": "carboxyl",
    # nitrogen-containing
    "아미노": "amino", "아미노기": "amino",
    "니트로": "nitro", "니트로기": "nitro",
    "시아노": "cyano", "시안": "cyano",
    # halogens
    "플루오로": "fluoro", "플루오르": "fluoro",
    "클로로": "chloro", "염소": "chloro",
    "브로모": "bromo", "브롬": "bromo",
    "아이오도": "iodo", "요오드": "iodo",
    # aryl / misc
    "페닐": "phenyl", "페닐기": "phenyl",
    "벤질": "benzyl", "벤질기": "benzyl",
    "비닐": "vinyl", "비닐기": "vinyl",
    "아릴": "aryl", "알킬": "alkyl",
    "설포닐": "sulfonyl", "설폰": "sulfonyl",
    "포스포": "phospho",
    "트리플루오로메틸": "trifluoromethyl",
    # special
    "수소": "hydrogen",
}


def translate_substituent(text: str) -> "str | None":
    """Translate a Korean substituent name to its English key.

    Strips common Korean particles (기를, 기로, 를, 로, etc.) before
    looking up the dictionary.

    Args:
        text: Korean substituent name, possibly with particles attached.

    Returns:
        English substituent key (e.g. "methyl"), or None if not found.

    # Test scenario: translate_substituent("메틸기를") → "methyl"
    """
    cleaned = str(text or "").strip()
    if not cleaned:
        return None
    # 조사/어미 제거
    cleaned = re.sub(
        r"(기를|기로|기가|기는|기에|기의|를|로|을|으로|이|가|는|은|도)$",
        "", cleaned,
    ).strip()
    return (
        SUBSTITUENT_KO_TO_EN.get(cleaned)
        or SUBSTITUENT_KO_TO_EN.get(cleaned + "기")
        or SUBSTITUENT_KO_TO_EN.get(cleaned + "기")  # fallback
    )
```

---

## Patch 2/3: normalizer.py — modification intent 파싱 정규식 + 함수

### 변경 A: import 추가

> **위치**: 프로젝트 내부 import 섹션
> **이유**: ko_aliases의 치환기 번역 사용

```python
from qcviz_mcp.services.ko_aliases import translate_substituent
```

> 순환 import 주의: `services.ko_aliases` → `llm.normalizer`는 방향이 맞음.
> 만약 역방향 참조 문제 시 함수 내 지연 import 사용.

### 변경 B: modification intent 정규식 5개 추가

> **위치**: 기존 `_IMPLICIT_FOLLOW_UP_MODIFICATION_RE` (Phase 1) 정의 아래
> **이유**: "메틸기를 에틸기로 바꾸면?" 에서 from/to 그룹을 정확히 캡처

```python
# ── Phase 2: Modification intent parsing patterns ────────────

# "메틸기를 에틸기로 바꾸면?"
_MODIFICATION_SWAP_RE = re.compile(
    r"(?P<from_ko>[가-힣]+(?:기)?)\s*(?:를|을)?\s*"
    r"(?P<to_ko>[가-힣]+(?:기)?)\s*(?:로|으로)\s*"
    r"(?:바꾸|교체|치환|변경|대체|변환|교환|스왑|swap)",
    re.IGNORECASE,
)

# "바꾸면?" 먼저 나오는 순서: "치환 메틸 → 에틸"
_MODIFICATION_REPLACE_RE = re.compile(
    r"(?:바꾸|교체|치환|변경|대체|변환|교환|replace|substitute|swap)\s*"
    r"(?P<from_ko>[가-힣]+(?:기)?)\s*(?:를|을)?\s*"
    r"(?:with|→|->|에서|로부터)?\s*"
    r"(?P<to_ko>[가-힣]+(?:기)?)",
    re.IGNORECASE,
)

# "메틸기를 에틸기로 바꾸면"  (conditional ending)
_MODIFICATION_CONDITIONAL_RE_P2 = re.compile(
    r"(?P<from_ko>[가-힣]+(?:기)?)\s*(?:를|을|이|가)?\s*"
    r"(?P<to_ko>[가-힣]+(?:기)?)\s*(?:로|으로)\s*"
    r"(?:바꾸면|교체하면|치환하면|변경하면|대체하면)",
    re.IGNORECASE,
)

# "니트로기를 붙이면?" (addition)
_MODIFICATION_ADD_RE = re.compile(
    r"(?P<to_ko>[가-힣]+(?:기)?)\s*(?:를|을)?\s*"
    r"(?:붙이|달|추가|첨가|도입|넣)",
    re.IGNORECASE,
)

# "메틸기를 떼면?" (removal)
_MODIFICATION_REMOVE_RE = re.compile(
    r"(?P<from_ko>[가-힣]+(?:기)?)\s*(?:를|을)?\s*"
    r"(?:떼|제거|빼|탈리|없앨|없애)",
    re.IGNORECASE,
)
```

### 변경 C: `parse_modification_intent()` 함수 신규

> **위치**: `detect_implicit_follow_up()` 함수 아래에 삽입
> **이유**: 한국어 modification 쿼리에서 from_group/to_group 정확 추출

```python
def parse_modification_intent(text: str) -> "Dict[str, Any] | None":
    """Parse a Korean modification query to extract from/to substituent groups.

    Supports swap ("A를 B로 바꾸면"), addition ("A를 붙이면"),
    and removal ("A를 떼면") patterns.

    Args:
        text: Raw user input in Korean (or English).

    Returns:
        Dict with keys from_group, to_group, from_group_ko, to_group_ko,
        modification_type, confidence.  None if no modification intent.

    # Test scenario: parse_modification_intent("메틸기를 에틸기로 바꾸면?")
    #   → {"from_group": "methyl", "to_group": "ethyl", ...}
    """
    cleaned = str(text or "").strip()
    if not cleaned:
        return None

    # ── swap / conditional patterns ──────────────────────────
    for pattern, mod_type in [
        (_MODIFICATION_SWAP_RE, "swap"),
        (_MODIFICATION_CONDITIONAL_RE_P2, "swap"),
        (_MODIFICATION_REPLACE_RE, "swap"),
    ]:
        m = pattern.search(cleaned)
        if m:
            from_ko = m.group("from_ko").strip()
            to_ko = m.group("to_ko").strip()
            from_en = translate_substituent(from_ko)
            to_en = translate_substituent(to_ko)
            if from_en and to_en:
                return {
                    "from_group": from_en,
                    "to_group": to_en,
                    "from_group_ko": from_ko,
                    "to_group_ko": to_ko,
                    "modification_type": mod_type,
                    "confidence": 0.85,
                }

    # ── addition pattern ─────────────────────────────────────
    m = _MODIFICATION_ADD_RE.search(cleaned)
    if m:
        to_ko = m.group("to_ko").strip()
        to_en = translate_substituent(to_ko)
        if to_en:
            return {
                "from_group": "hydrogen",
                "to_group": to_en,
                "from_group_ko": "수소",
                "to_group_ko": to_ko,
                "modification_type": "addition",
                "confidence": 0.75,
            }

    # ── removal pattern ──────────────────────────────────────
    m = _MODIFICATION_REMOVE_RE.search(cleaned)
    if m:
        from_ko = m.group("from_ko").strip()
        from_en = translate_substituent(from_ko)
        if from_en:
            return {
                "from_group": from_en,
                "to_group": "hydrogen",
                "from_group_ko": from_ko,
                "to_group_ko": "수소",
                "modification_type": "removal",
                "confidence": 0.75,
            }

    return None
```

---

## Patch 3/3: pipeline.py — modification lane 라우팅 연결

### 변경 A: import 추가

> **위치**: 프로젝트 내부 import 섹션, Phase 1 import 아래
> **이유**: modification intent 파싱 + ModificationIntent 모델 사용

```python
from qcviz_mcp.llm.normalizer import parse_modification_intent
from qcviz_mcp.llm.schemas import ModificationIntent
```

### 변경 B: `_run_ingress_rewrite()` — intent를 context에 저장

> **위치**: Phase 1에서 추가한 implicit follow-up 블록 바로 아래
> **이유**: modification intent 파싱 결과를 stage2로 전달

```python
        # ── Phase 2: parse modification intent ───────────────
        _mod_intent = parse_modification_intent(raw_text)
        if (
            _mod_intent
            and fallback.is_follow_up
            and getattr(fallback, "follow_up_type", None)
            in ("modification_request", "modification")
        ):
            context["_modification_intent"] = _mod_intent
            logger.debug(
                "Modification intent parsed: %s → %s (conf=%.2f)",
                _mod_intent.get("from_group"),
                _mod_intent.get("to_group"),
                _mod_intent.get("confidence", 0),
            )
```

### 변경 C: `_run_action_planner()` — modification lane 라우팅

> **위치**: plan 결과 후처리 영역, 기존 `_validate_planner_lane()` 호출 바로 아래
> **이유**: modification intent가 있고 confidence가 threshold 이상이면
> lane을 modification_exploration으로 강제 라우팅

```python
        # ── Phase 2: modification lane routing ───────────────
        _mod_intent_data = context.get("_modification_intent")
        if (
            _mod_intent_data
            and _env_flag("QCVIZ_MODIFICATION_LANE_ENABLED", False)
        ):
            try:
                from qcviz_mcp.llm.routing_config import (
                    MODIFICATION_CONFIDENCE_THRESHOLD,
                )
                _conf = float(_mod_intent_data.get("confidence", 0))
                if _conf >= MODIFICATION_CONFIDENCE_THRESHOLD:
                    plan_dict["planner_lane"] = "modification_exploration"
                    plan_dict["query_kind"] = "modification_exploration"
                    plan_dict["modification_intent"] = _mod_intent_data
                    logger.info(
                        "Routed to modification_exploration: %s → %s "
                        "(confidence=%.2f >= %.2f)",
                        _mod_intent_data.get("from_group"),
                        _mod_intent_data.get("to_group"),
                        _conf,
                        MODIFICATION_CONFIDENCE_THRESHOLD,
                    )
            except Exception as exc:
                logger.warning(
                    "Modification lane routing failed: %s", exc
                )
```

> `plan_dict`는 LLM 반환값을 담는 dict. 변수명이 다르면 실제 코드에 맞게 치환.
> `_env_flag`는 pipeline.py에 이미 존재하는 헬퍼.

---

## 검증 명령

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04

# 1. ko_aliases 치환기 번역 확인
PYTHONPATH=src python -c "
from qcviz_mcp.services.ko_aliases import translate_substituent, SUBSTITUENT_KO_TO_EN
assert translate_substituent('메틸기를') == 'methyl', 'FAIL: 메틸기를'
assert translate_substituent('에틸') == 'ethyl', 'FAIL: 에틸'
assert translate_substituent('하이드록시기로') == 'hydroxy', 'FAIL: 하이드록시기로'
assert translate_substituent('니트로') == 'nitro', 'FAIL: 니트로'
assert translate_substituent('양자화학') is None, 'FAIL: should be None'
print(f'✅ translate_substituent OK ({len(SUBSTITUENT_KO_TO_EN)} entries)')
"

# 2. parse_modification_intent 5시나리오
PYTHONPATH=src python -c "
from qcviz_mcp.llm.normalizer import parse_modification_intent

# swap
r = parse_modification_intent('메틸기를 에틸기로 바꾸면?')
assert r and r['from_group'] == 'methyl' and r['to_group'] == 'ethyl', f'FAIL 1: {r}'
print('✓ 시나리오 1: swap')

# conditional
r = parse_modification_intent('하이드록시기를 아미노기로 치환하면 어떻게 되나요?')
assert r and r['from_group'] == 'hydroxy' and r['to_group'] == 'amino', f'FAIL 2: {r}'
print('✓ 시나리오 2: conditional')

# addition
r = parse_modification_intent('니트로기를 붙이면?')
assert r and r['from_group'] == 'hydrogen' and r['to_group'] == 'nitro', f'FAIL 3: {r}'
print('✓ 시나리오 3: addition')

# removal
r = parse_modification_intent('메틸기를 떼면?')
assert r and r['from_group'] == 'methyl' and r['to_group'] == 'hydrogen', f'FAIL 4: {r}'
print('✓ 시나리오 4: removal')

# non-modification
r = parse_modification_intent('벤젠의 HOMO를 보여줘')
assert r is None, f'FAIL 5: should be None but got {r}'
print('✓ 시나리오 5: non-modification')

print('\\n🎉 모든 시나리오 통과!')
"

# 3. pipeline import chain 확인
PYTHONPATH=src python -c "
from qcviz_mcp.llm.normalizer import parse_modification_intent
from qcviz_mcp.llm.schemas import ModificationIntent
from qcviz_mcp.llm.pipeline import QCVizPromptPipeline
print('✅ Pipeline import chain OK')
"

# 4. 전체 import (순환 없음)
PYTHONPATH=src QCVIZ_CONTEXT_TRACKING_ENABLED=true \
  QCVIZ_MODIFICATION_LANE_ENABLED=true python -c "
from qcviz_mcp.web.app import create_app
app = create_app()
print('✅ App creation OK with both flags enabled')
"

# 5. 기존 테스트 무결성
PYTHONPATH=src pytest tests/ -x -q 2>&1 | tail -5
```

---

## Phase 2 완성 — 전체 변경 요약

| Day | 파일 | 핵심 | 상태 |
|-----|------|------|------|
| 1-3 | `structure_intelligence.py` (CREATE), `errors.py`, `__init__.py` | RDKit 변형 엔진 | ✅ |
| 4-6 | `schemas.py`, `lane_lock.py`, `routing_config.py` | 타입/lane/설정 | ✅ |
| 7-9 | `grounding_merge.py`, `execution_guard.py`, `chat.py` | 파이프라인 관통 | ✅ |
| 10-14 | `ko_aliases.py`, `normalizer.py`, `pipeline.py` | 한국어 파싱 + 라우팅 | ✅ |

**총 수정 파일**: 12개 (신규 1개)
**총 추가 코드**: ~650줄
**기존 코드 수정**: ~10줄 (모두 Literal 확장, additive)

---

## Phase 2 E2E 데이터 흐름 (전체 완성)

```
User: "메틸기를 에틸기로 바꾸면?"
  (active_molecule = methylethylamine, SMILES = CCNC)

① normalizer.py
   detect_implicit_follow_up() → is_implicit=True, type=modification_request
   parse_modification_intent() → {from: "methyl", to: "ethyl", conf: 0.85}

② pipeline.py
   _run_ingress_rewrite(): context["_modification_intent"] = ^
   _run_action_planner(): conf 0.85 >= 0.60
     → plan.lane = "modification_exploration"
     → plan.modification_intent = ModificationIntent(from=methyl, to=ethyl)

③ grounding_merge.py
   lane=modification_exploration → MODIFICATION_CANDIDATES_READY

④ execution_guard.py
   modification_candidates_ready → action="modification_preview"

⑤ chat.py
   _handle_modification_exploration()
   → generate_modification_candidates("CCNC", "methyl", "ethyl")
   → WS: {type: "modification_candidates", candidates: [...]}

User sees: "methylethylamine에서 methyl → ethyl 변환 후보 2개"
```

---

## .env.example 추가 (Phase 2)

```ini
# Phase 2: Modification Exploration Lane
# Enables RDKit-based molecular modification exploration.
# Requires Phase 1 context tracking to be enabled.
QCVIZ_MODIFICATION_LANE_ENABLED=false
```
