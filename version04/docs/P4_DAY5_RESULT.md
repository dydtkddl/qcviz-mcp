# Phase 4 Day 5: Advisor 연동 — Modification & Comparison Context 전파

## 변경 파일 목록

```
📄 파일: src/qcviz_mcp/web/advisor_flow.py
   변경 유형: MODIFY
   변경 라인 수: ~40줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/tools/advisor_tools.py
   변경 유형: MODIFY
   변경 라인 수: ~25줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/web/result_explainer.py
   변경 유형: MODIFY
   변경 라인 수: ~15줄 추가
   의존성 변경: 없음
```

---

## Patch 1/3: advisor_flow.py — modification/comparison context 수용

> **위치**: `prepare_advisor_plan()` 함수 (또는 advisor plan을 구성하는 핵심 함수)
> **이유**: modification 워크플로우에서 base→modified 관계를, comparison에서
> delta 데이터를 advisor에 전달하여 맥락 기반 추천 가능

### 변경 A: 함수 시그니처에 Optional 파라미터 추가

> 기존 시그니처에 `modification_context`와 `comparison_context`를
> keyword-only 파라미터로 추가 (기본값 None → 기존 호출 깨지지 않음)

```python
def prepare_advisor_plan(
    geometry=None,
    job_type=None,
    *,
    modification_context: "dict | None" = None,   # Phase 4
    comparison_context: "dict | None" = None,      # Phase 4
    **kwargs,
) -> dict:
```

### 변경 B: plan 구성 로직 끝, return 직전에 context 반영 블록 삽입

```python
    # ── Phase 4: modification context for advisor ────────────
    if modification_context and isinstance(modification_context, dict):
        plan["modification"] = {
            "base_molecule": modification_context.get("base_molecule"),
            "modified_molecule": modification_context.get("modified_molecule"),
            "from_group": modification_context.get("from_group"),
            "to_group": modification_context.get("to_group"),
            "relationship": "substituent_swap",
        }
        # 시스템 타입 힌트 업데이트
        if plan.get("system_type") in (None, "unknown", ""):
            plan["system_type"] = "organic_modified"

    # ── Phase 4: comparison context for advisor ──────────────
    if comparison_context and isinstance(comparison_context, dict):
        _delta = comparison_context.get("delta") or {}
        plan["comparison"] = {
            "mol_a": comparison_context.get("mol_a"),
            "mol_b": comparison_context.get("mol_b"),
            "delta_energy": _delta.get("energy") or _delta.get("energy_delta_ev"),
            "delta_gap": (
                _delta.get("homo_lumo_gap")
                or _delta.get("gap_delta_ev")
            ),
        }
```

> `plan`은 함수 내에서 반환 대상인 dict 변수. 변수명이 다르면 치환.

---

## Patch 2/3: advisor_tools.py — enrich_result에 context 파라미터 전파

> **위치**: `enrich_result_with_advisor()` 함수 (또는 advisor enrichment 진입점)
> **이유**: chat.py에서 modification/comparison 결과를 advisor에 전달할 경로 확보

### 변경 A: 함수 시그니처 확장

```python
def enrich_result_with_advisor(
    result: dict,
    *,
    modification_context: "dict | None" = None,  # Phase 4
    comparison_context: "dict | None" = None,     # Phase 4
    **kwargs,
) -> dict:
```

### 변경 B: prepare_advisor_plan 호출 시 context 전달

> `prepare_advisor_plan()` 호출 부분을 찾아 context 파라미터 추가

```python
    plan = prepare_advisor_plan(
        geometry=result.get("geometry") or result.get("xyz"),
        job_type=result.get("job_type"),
        modification_context=modification_context,   # Phase 4
        comparison_context=comparison_context,        # Phase 4
    )
```

> 기존 호출에 keyword argument만 추가하므로 기존 동작 영향 없음.

---

## Patch 3/3: result_explainer.py — comparison explanation에 advisor 결과 반영

> **위치**: `explain_comparison()` 함수 내부, return 직전
> **이유**: advisor 추천이 있으면 comparison 설명에 포함

### 변경 A: 함수 시그니처에 advisor_data 추가

```python
def explain_comparison(
    *,
    delta: "Mapping[str, Any]",
    result_a: "Mapping[str, Any]",
    result_b: "Mapping[str, Any]",
    job_type: str = "analyze",
    advisor_data: "dict | None" = None,  # Phase 4
) -> Dict[str, Any]:
```

### 변경 B: return 직전에 advisor 반영 블록 삽입

```python
    # ── Phase 4: advisor recommendation in comparison ────────
    if advisor_data and isinstance(advisor_data, dict):
        _adv_summary = advisor_data.get("summary") or advisor_data.get("recommendation")
        if _adv_summary:
            explanation.setdefault("advisor_recommendation", _adv_summary)
        if advisor_data.get("modification"):
            explanation.next_actions.append(
                "추천 프리셋으로 변형 구조를 다시 계산하면 "
                "더 정확한 비교가 가능합니다."
            )
```

> `explanation`이 `ResultExplanation` Pydantic 모델이면
> `explanation.next_actions.append(...)`, dict이면 `explanation.setdefault("next_actions", []).append(...)`.

---

## 검증 명령

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04

# 1. advisor_flow modification context
PYTHONPATH=src python -c "
from qcviz_mcp.web.advisor_flow import prepare_advisor_plan
plan = prepare_advisor_plan(
    geometry='H 0 0 0',
    job_type='orbital_preview',
    modification_context={
        'base_molecule': 'benzene',
        'modified_molecule': 'toluene',
        'from_group': 'H',
        'to_group': 'methyl',
    },
)
assert 'modification' in plan, f'FAIL: {plan.keys()}'
assert plan['modification']['relationship'] == 'substituent_swap'
print(f'✅ Advisor modification context: {plan[\"modification\"]}')
"

# 2. advisor_flow comparison context
PYTHONPATH=src python -c "
from qcviz_mcp.web.advisor_flow import prepare_advisor_plan
plan = prepare_advisor_plan(
    geometry='H 0 0 0',
    job_type='orbital_preview',
    comparison_context={
        'mol_a': 'benzene', 'mol_b': 'toluene',
        'delta': {'energy_delta_ev': -0.05, 'gap_delta_ev': 0.02},
    },
)
assert 'comparison' in plan, f'FAIL: {plan.keys()}'
print(f'✅ Advisor comparison context: {plan[\"comparison\"]}')
"

# 3. advisor_tools 시그니처 확인
grep -n "modification_context\|comparison_context" \
  src/qcviz_mcp/tools/advisor_tools.py
# 기대: 2줄 이상

# 4. result_explainer advisor_data 확인
grep -n "advisor_data\|advisor_recommendation" \
  src/qcviz_mcp/web/result_explainer.py
# 기대: 2줄 이상

# 5. 기존 테스트 무결성
PYTHONPATH=src pytest tests/ -x -q 2>&1 | tail -5
```

---

## 다음 Day 연결점

- **Day 6**: Config 통합 — `routing_config.py`의 `MODIFICATION_CONFIDENCE_THRESHOLD`
  등을 `config.py`에서 import하도록 변경하여 중복 제거.
  `providers.py`에 timeout/retry 정책을 Phase 2~3 서비스 호출에 적용.
