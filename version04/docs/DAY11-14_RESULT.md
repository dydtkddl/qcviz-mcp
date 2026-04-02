# Day 11-14: 타입 확장 + 프롬프트 개선 + 통합 검증

## 변경 파일 목록

```
📄 파일: src/qcviz_mcp/llm/schemas.py
   변경 유형: MODIFY
   변경 라인 수: ~8줄 추가, ~2줄 수정
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/llm/prompt_assets/ingress_rewrite.md
   변경 유형: MODIFY
   변경 라인 수: ~10줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/llm/prompt_assets/grounding_decider.md
   변경 유형: MODIFY
   변경 라인 수: ~7줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/llm/prompt_assets/semantic_expansion.md
   변경 유형: MODIFY
   변경 라인 수: ~7줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/observability.py
   변경 유형: MODIFY
   변경 라인 수: ~10줄 추가
   의존성 변경: 없음

📄 파일: .env.example
   변경 유형: MODIFY
   변경 라인 수: ~3줄 추가
   의존성 변경: 없음
```

---

## Patch 1/6: schemas.py — PlanResponse 필드 확장

### 변경 ①: PlanResponse에 context 필드 3개 추가

> **위치**: `PlanResponse` 클래스 내부, 기존 필드 목록 끝
> **이유**: Router LLM이 conversation context 정보를 반환 구조체에 포함하여
> 후속 핸들러가 참조 가능하게

```python
    context_molecule_name: Optional[str] = None
    context_molecule_smiles: Optional[str] = None
    implicit_follow_up_type: Optional[str] = None
```

### 변경 ②: `_blank_to_none` validator에 새 필드 추가

> **위치**: PlanResponse의 `_blank_to_none` validator (또는 유사한
> blank-string-to-None 변환 validator)
> **이유**: Gemini가 빈 문자열을 반환했을 때 None으로 정규화

validator의 필드 목록에 추가:

```python
    "context_molecule_name",
    "context_molecule_smiles",
    "implicit_follow_up_type",
```

### 변경 ③: `_check_plan_invariants` 확인 (수정 불필요할 가능성)

> `PlanResult` validator에서 `compute_ready` lane의 molecule 필수 체크:

```python
# 기존에 이미 이렇게 되어 있는지 확인:
if self.lane == "compute_ready" and not (self.molecule_name or self.molecule_from_context):
    raise ValueError("compute_ready lane requires molecule_name or molecule_from_context")
```

> `molecule_from_context`가 이미 허용되어 있으면 수정 불필요.
> 만약 `molecule_name`만 체크하고 있다면:
> ```python
> # 변경 전
> if self.lane == "compute_ready" and not self.molecule_name:
> # 변경 후
> if self.lane == "compute_ready" and not (self.molecule_name or self.molecule_from_context):
> ```

---

## Patch 2/6: ingress_rewrite.md

> **위치**: 파일 **맨 끝**에 추가
> **이유**: normalizer의 LLM 호출 시 한국어 implicit follow-up 패턴을
> Gemini가 올바르게 인식하도록 지시

```markdown
## Korean Implicit Follow-up Patterns

- "치환기를 바꾸면?" → follow-up, modification_request
- "그럼 에너지는?" → follow-up, structure_reference
- "비교하면 어때?" → follow-up, comparison_request
- "하나만 바꿔보면?" → follow-up, modification_request

These patterns indicate the user is referencing the previously discussed
molecule. Do NOT strip these as noise. Mark is_follow_up=true.
```

---

## Patch 3/6: grounding_decider.md

> **위치**: 파일 **맨 끝**에 추가
> **이유**: implicit follow-up일 때 새 분자 grounding을 시도하지 않도록 지시

```markdown
## Follow-up Context Rule

If the input is identified as an implicit follow-up (modification,
comparison, or structure reference), do NOT attempt to ground a new
molecule. Instead, set decision="direct_answer" and let the downstream
handler use the active_molecule from conversation state.
```

---

## Patch 4/6: semantic_expansion.md

> **위치**: 파일 **맨 끝**에 추가
> **이유**: modification intent일 때 엉뚱한 분자명 확장을 방지

```markdown
## Modification Queries

For modification intent queries (substituent swap, R-group change),
do NOT expand into unrelated molecule names.
Instead, the grounding_queries should reference the scaffold molecule
from conversation context, e.g., "methylethylamine substituent
variations".
```

---

## Patch 5/6: observability.py — pipeline trace에 context 정보 추가

> **위치**: `emit_pipeline_trace()` 또는 trace 출력을 구성하는 함수 내부
> **이유**: context tracking 동작을 로그/트레이스에서 관측 가능하게

```bash
# 삽입 지점 찾기
grep -n "emit_pipeline_trace\|trace_data\|pipeline.*trace\|def.*trace" \
  src/qcviz_mcp/observability.py
```

trace dict 구성 부분에 다음 키 추가:

```python
    # ── Phase 1: context tracking trace ──────────────────
    "context_tracking": {
        "active_molecule": trace_data.get("context_molecule_name")
            if isinstance(trace_data, dict) else None,
        "implicit_follow_up": trace_data.get("implicit_follow_up_type")
            if isinstance(trace_data, dict) else None,
        "follow_up_detected": trace_data.get("is_follow_up")
            if isinstance(trace_data, dict) else None,
    },
```

> `trace_data`가 dict가 아닌 dataclass/Pydantic 모델이면:
> ```python
>     "context_tracking": {
>         "active_molecule": getattr(trace_data, "context_molecule_name", None),
>         "implicit_follow_up": getattr(trace_data, "implicit_follow_up_type", None),
>         "follow_up_detected": getattr(trace_data, "is_follow_up", None),
>     },
> ```

> `PipelineTrace` dataclass에 전용 필드를 추가하려면:
> ```python
> @dataclass
> class PipelineTrace:
>     ...
>     # Phase 1
>     context_molecule_name: Optional[str] = None
>     implicit_follow_up_type: Optional[str] = None
> ```
> 하지만 기존 `extra: Dict[str, Any]` 필드가 있다면 그쪽에 삽입해도 충분.

---

## Patch 6/6: .env.example

> **위치**: 파일 **맨 끝**에 추가
> **이유**: Phase 1 feature flag를 문서화

```ini
# Phase 1: Conversation Context Tracking
# Enables implicit follow-up detection and active molecule tracking.
# Set to "true" to activate. Default: false (no behavior change).
QCVIZ_CONTEXT_TRACKING_ENABLED=false
```

---

## 검증 명령

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04

# 1. PlanResponse 신규 필드 확인
PYTHONPATH=src python -c "
from qcviz_mcp.llm.schemas import PlanResponse
pr = PlanResponse(lane='chat_only')
assert pr.context_molecule_name is None, 'FAIL'
assert pr.context_molecule_smiles is None, 'FAIL'
assert pr.implicit_follow_up_type is None, 'FAIL'
print('✅ PlanResponse fields OK')
"

# 2. .env.example 확인
grep "CONTEXT_TRACKING" .env.example && echo "✅ .env.example OK"

# 3. prompt assets 변경 확인
grep -l "modification\|follow-up\|Follow-up" src/qcviz_mcp/llm/prompt_assets/*.md
# 기대: ingress_rewrite.md, grounding_decider.md, semantic_expansion.md, action_planner.md

# 4. 전체 import chain (순환 없는지)
PYTHONPATH=src QCVIZ_CONTEXT_TRACKING_ENABLED=true python -c "
from qcviz_mcp.web.conversation_state import set_active_molecule, get_active_molecule, ActiveMolecule
from qcviz_mcp.llm.normalizer import detect_implicit_follow_up
from qcviz_mcp.llm.pipeline import QCVizPromptPipeline
from qcviz_mcp.llm.schemas import PlanResponse, IngressResult
print('✅ ALL IMPORTS OK — NO CIRCULAR DEPENDENCY')
"

# 5. 전체 Phase 1 통합 검증
PYTHONPATH=src QCVIZ_CONTEXT_TRACKING_ENABLED=true python verify_day11_14.py

# 6. 기존 테스트 regression 확인
PYTHONPATH=src pytest tests/ -x -q 2>&1 | tail -5
```

---

## 수동 통합 테스트 시나리오

서버 기동 후 웹 UI에서 수행:

```
.env에 QCVIZ_CONTEXT_TRACKING_ENABLED=true 추가 후 서버 재시작

시나리오 1: 기본 follow-up
  턴 1: "메틸에틸아민이 뭐야?"
  → 기대: 정상 설명 응답, active_molecule=methylethylamine 설정
  턴 2: "치환기를 하나만 바꾸면?"
  → 기대: is_follow_up=True, 응답이 methylethylamine 맥락에서 치환기 변형 설명
  → 로그에 "Implicit follow-up detected: type=modification_request context_mol=methylethylamine"

시나리오 2: 명시적 분자명 (false positive 방지)
  턴 1: "벤젠이 뭐야?"
  턴 2: "톨루엔의 HOMO 보여줘"
  → 기대: is_follow_up=False (명시적 "톨루엔"), active_molecule→톨루엔으로 전환

시나리오 3: feature flag off (regression 없음)
  .env에서 QCVIZ_CONTEXT_TRACKING_ENABLED=false 설정
  동일 시나리오 반복
  → 기대: 기존 동작과 완전히 동일

시나리오 4: 연속 follow-up
  턴 1: "물 분자 설명해줘" → active=water
  턴 2: "그럼 에너지는?" → follow-up, active 유지
  턴 3: "벤젠도 해줘" → active=benzene으로 전환
  턴 4: "치환기 바꾸면?" → follow-up, context=benzene
```

---

## Phase 1 완성 — 전체 변경 요약

| Day | 파일 | 변경 | 역할 |
|-----|------|------|------|
| 1-2 | `config.py` | `context_tracking_enabled` flag | Feature gate |
| 1-2 | `conversation_state.py` | `ActiveMolecule` + CRUD 4개 | 맥락 저장소 |
| 3-4 | `schemas.py` | `IngressResult` + context 필드 | 데이터 타입 |
| 3-4 | `normalizer.py` | `detect_implicit_follow_up()` + 정규식 4개 | 패턴 감지 |
| 5-7 | `pipeline.py` | Ingress context injection + Router payload | 맥락 주입 |
| 5-7 | `action_planner.md` | Conversation Context 지시 | Router 프롬프트 |
| 8-10 | `chat.py` | set/get/inject 루프 | 루프 완성 |
| 11-14 | `schemas.py` | `PlanResponse` context 필드 | 반환 타입 확장 |
| 11-14 | `ingress_rewrite.md` | 한국어 패턴 예시 | Ingress 프롬프트 |
| 11-14 | `grounding_decider.md` | Follow-up Context Rule | Grounding 프롬프트 |
| 11-14 | `semantic_expansion.md` | Modification Queries | 확장 프롬프트 |
| 11-14 | `observability.py` | context_tracking trace | 관측성 |
| 11-14 | `.env.example` | flag 문서화 | 설정 |

**총 수정 파일**: 12개 (신규 0개)
**총 추가 코드**: ~350줄
**기존 코드 수정**: ~15줄 (모두 additive, 기존 동작 영향 zero)
