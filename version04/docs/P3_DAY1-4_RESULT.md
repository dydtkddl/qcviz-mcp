# Phase 3 Day 1-4: compute_delta + explain_comparison + comparison batch

## 변경 파일 목록

```
📄 파일: src/qcviz_mcp/compute/pyscf_runner.py
   변경 유형: MODIFY
   변경 라인 수: ~75줄 추가
   의존성 변경: 없음 (Mapping, Dict, Any 이미 import됨)

📄 파일: src/qcviz_mcp/web/result_explainer.py
   변경 유형: MODIFY
   변경 라인 수: ~80줄 추가
   의존성 변경: 없음

📄 파일: src/qcviz_mcp/compute/job_manager.py
   변경 유형: MODIFY
   변경 라인 수: ~30줄 추가
   의존성 변경: 없음
```

---

## Patch 1/3: pyscf_runner.py — `compute_delta()` 후처리 함수

> **위치**: 파일 **최하단**에 추가
> **이유**: 두 계산 결과 dict를 받아 에너지/gap/전하 차이를 계산하는
> 순수 후처리 함수. PySCF를 다시 호출하지 않음.

```python
# ── Phase 3: Comparison Delta ────────────────────────────────

# eV → kcal/mol 변환 상수 (이미 정의되어 있으면 재사용)
EV_TO_KCAL = 23.0609  # 1 eV = 23.0609 kcal/mol


def compute_delta(
    result_a: "Mapping[str, Any]",
    result_b: "Mapping[str, Any]",
) -> Dict[str, Any]:
    """Compute property deltas between two calculation results.

    This is a pure post-processing function — it does NOT invoke PySCF.
    It compares already-completed result dicts and returns a delta dict
    summarising differences in energy, orbital gaps, and charges.

    Args:
        result_a: Calculation result dict for molecule A (original).
        result_b: Calculation result dict for molecule B (modified/comparison).

    Returns:
        Delta dict with keys: molecule_a, molecule_b, energy_delta_ev,
        energy_delta_kcal, gap_delta_ev, homo/lumo deltas,
        charge redistribution stats, convergence flags, atom counts.

    # Test scenario: compute_delta(
    #     {"total_energy_ev": -2080.5, "orbital_gap_ev": 5.2},
    #     {"total_energy_ev": -2095.3, "orbital_gap_ev": 4.8},
    # ) → energy_delta_ev ≈ -14.8, gap_delta_ev ≈ -0.4
    """
    delta: Dict[str, Any] = {
        "molecule_a": _safe_str(
            result_a.get("structure_name")
            or result_a.get("structure_query")
        ),
        "molecule_b": _safe_str(
            result_b.get("structure_name")
            or result_b.get("structure_query")
        ),
        "method_a": _safe_str(result_a.get("method")),
        "method_b": _safe_str(result_b.get("method")),
        "basis_a": _safe_str(result_a.get("basis")),
        "basis_b": _safe_str(result_b.get("basis")),
    }

    # 1. Total energy delta
    energy_a = _safe_float(result_a.get("total_energy_ev"))
    energy_b = _safe_float(result_b.get("total_energy_ev"))
    if energy_a is not None and energy_b is not None:
        delta["energy_a_ev"] = energy_a
        delta["energy_b_ev"] = energy_b
        delta["energy_delta_ev"] = round(energy_b - energy_a, 6)
        delta["energy_delta_kcal"] = round(
            (energy_b - energy_a) * EV_TO_KCAL, 4
        )

    # 2. HOMO-LUMO gap delta
    gap_a = _safe_float(result_a.get("orbital_gap_ev"))
    gap_b = _safe_float(result_b.get("orbital_gap_ev"))
    if gap_a is not None and gap_b is not None:
        delta["gap_a_ev"] = gap_a
        delta["gap_b_ev"] = gap_b
        delta["gap_delta_ev"] = round(gap_b - gap_a, 6)

    # 3. HOMO / LUMO energy deltas
    for key in ("homo_energy_ev", "lumo_energy_ev"):
        val_a = _safe_float(result_a.get(key))
        val_b = _safe_float(result_b.get(key))
        if val_a is not None and val_b is not None:
            delta[f"{key}_a"] = val_a
            delta[f"{key}_b"] = val_b
            delta[f"{key}_delta"] = round(val_b - val_a, 6)

    # 4. Partial charge redistribution
    charges_a = (
        result_a.get("partial_charges")
        or result_a.get("mulliken_charges")
        or []
    )
    charges_b = (
        result_b.get("partial_charges")
        or result_b.get("mulliken_charges")
        or []
    )
    if isinstance(charges_a, list) and isinstance(charges_b, list):
        vals_a = [
            float(c.get("charge", 0))
            for c in charges_a
            if isinstance(c, dict)
        ]
        vals_b = [
            float(c.get("charge", 0))
            for c in charges_b
            if isinstance(c, dict)
        ]
        if vals_a and vals_b:
            delta["charge_count_a"] = len(vals_a)
            delta["charge_count_b"] = len(vals_b)
            if len(vals_a) == len(vals_b):
                diffs = [abs(b - a) for a, b in zip(vals_a, vals_b)]
                delta["max_charge_diff"] = (
                    round(max(diffs), 6) if diffs else None
                )
                delta["mean_charge_diff"] = (
                    round(sum(diffs) / len(diffs), 6) if diffs else None
                )

    # 5. SCF convergence
    delta["scf_converged_a"] = bool(result_a.get("scf_converged"))
    delta["scf_converged_b"] = bool(result_b.get("scf_converged"))
    delta["both_converged"] = (
        delta["scf_converged_a"] and delta["scf_converged_b"]
    )

    # 6. Atom count
    delta["atom_count_a"] = _safe_int(result_a.get("n_atoms"))
    delta["atom_count_b"] = _safe_int(result_b.get("n_atoms"))

    return delta
```

> **주의**: `_safe_str`, `_safe_float`, `_safe_int`는 pyscf_runner.py에 이미
> 존재하는 내부 헬퍼. 없으면:
> ```python
> def _safe_float(v):
>     try: return float(v) if v is not None else None
>     except (TypeError, ValueError): return None
> def _safe_int(v):
>     try: return int(v) if v is not None else None
>     except (TypeError, ValueError): return None
> ```
>
> `EV_TO_KCAL`이 이미 정의되어 있으면 중복 정의 제거.

---

## Patch 2/3: result_explainer.py — `explain_comparison()` 자연어 설명

> **위치**: 파일 **최하단**에 추가
> **이유**: delta dict를 한국어 자연어로 해석하여 사용자에게 제공

```python
# ── Phase 3: Comparison Explanation ──────────────────────────


def explain_comparison(
    *,
    delta: "Mapping[str, Any]",
    result_a: "Mapping[str, Any]",
    result_b: "Mapping[str, Any]",
    job_type: str = "analyze",
) -> Dict[str, Any]:
    """Generate a natural-language explanation of a comparison result.

    Args:
        delta: Output of ``compute_delta(result_a, result_b)``.
        result_a: Full result dict for molecule A.
        result_b: Full result dict for molecule B.
        job_type: Calculation type label.

    Returns:
        Dict matching ``ResultExplanation`` schema (summary,
        key_findings, interpretation, cautions, next_actions).

    # Test scenario: explain_comparison(
    #     delta={"energy_delta_ev": -14.8, "gap_delta_ev": -0.4,
    #            "molecule_a": "toluene", "molecule_b": "ethylbenzene",
    #            "both_converged": True},
    #     result_a={}, result_b={})
    #   → summary contains "비교 분석"
    """
    mol_a = _safe_str(delta.get("molecule_a") or "분자 A")
    mol_b = _safe_str(delta.get("molecule_b") or "분자 B")

    explanation = ResultExplanation()

    explanation.summary = (
        f"{mol_a}와(과) {mol_b}의 비교 분석이 완료되었습니다. "
        f"에너지, 궤도 구조, 전하 분포의 변화를 검토할 수 있습니다."
    )

    # ── Energy delta ─────────────────────────────────────────
    energy_delta_ev = _safe_float(delta.get("energy_delta_ev"))
    energy_delta_kcal = _safe_float(delta.get("energy_delta_kcal"))
    if energy_delta_ev is not None and energy_delta_kcal is not None:
        direction = "더 안정합니다" if energy_delta_ev < 0 else "덜 안정합니다"
        explanation.key_findings.append(
            f"총 에너지 차이: {energy_delta_ev:+.4f} eV "
            f"({energy_delta_kcal:+.2f} kcal/mol). "
            f"{mol_b}가 {mol_a}보다 {direction}."
        )

    # ── HOMO-LUMO gap delta ──────────────────────────────────
    gap_delta = _safe_float(delta.get("gap_delta_ev"))
    if gap_delta is not None:
        gap_dir = "증가" if gap_delta > 0 else "감소"
        explanation.key_findings.append(
            f"HOMO-LUMO gap 변화: {gap_delta:+.4f} eV ({gap_dir})."
        )
        if abs(gap_delta) > 0.5:
            explanation.interpretation.append(
                "gap 변화가 0.5 eV 이상으로 전자적 성질에 "
                "유의미한 차이가 있을 수 있습니다."
            )

    # ── Charge redistribution ────────────────────────────────
    max_charge_diff = _safe_float(delta.get("max_charge_diff"))
    if max_charge_diff is not None:
        explanation.key_findings.append(
            f"최대 부분 전하 변화: {max_charge_diff:.4f} e."
        )
        if max_charge_diff > 0.1:
            explanation.interpretation.append(
                "전하 재분배가 크므로 반응 중심이나 "
                "극성 변화에 주의가 필요합니다."
            )

    # ── Convergence warning ──────────────────────────────────
    if not delta.get("both_converged"):
        explanation.cautions.append(
            "하나 이상의 계산이 완전히 수렴하지 않았을 수 있으므로 "
            "수치 해석에 주의하세요."
        )

    # ── Next actions ─────────────────────────────────────────
    explanation.next_actions.extend([
        "특정 원자 위치의 전하 변화를 자세히 비교하려면 "
        "부분 전하 계산을 확인하세요.",
        "ESP 맵을 나란히 비교하면 반응성 변화를 "
        "시각적으로 확인할 수 있습니다.",
    ])

    # Truncate
    explanation.key_findings = explanation.key_findings[:5]
    explanation.interpretation = explanation.interpretation[:4]
    explanation.cautions = explanation.cautions[:4]
    explanation.next_actions = explanation.next_actions[:5]

    return explanation.model_dump()
```

> **주의**: `ResultExplanation`, `_safe_str`, `_safe_float`는
> result_explainer.py에 이미 존재하는 타입/헬퍼.
> `ResultExplanation`이 Pydantic 모델이면 `.model_dump()`,
> dataclass면 `dataclasses.asdict()`.

---

## Patch 3/3: job_manager.py — `submit_comparison()` 래퍼

> **위치**: `JobManager` 클래스 내부, 기존 `submit()` 메서드 아래
> **이유**: 두 구조의 계산을 동시에 제출하고 job_id 쌍을 반환하는 편의 래퍼

```python
    def submit_comparison(
        self,
        target: "Callable[..., Any]",
        *,
        kwargs_a: Dict[str, Any],
        kwargs_b: Dict[str, Any],
        label: str = "comparison",
    ) -> Dict[str, str]:
        """Submit two calculations simultaneously for comparison.

        Calls ``submit()`` twice with the given kwargs and returns
        both job IDs.  The caller is responsible for polling both
        jobs and calling ``compute_delta()`` when both complete.

        Args:
            target: The compute function to invoke (e.g. ``run_analyze``).
            kwargs_a: Keyword arguments for molecule A.
            kwargs_b: Keyword arguments for molecule B.
            label: Human-readable label prefix.

        Returns:
            Dict with job_id_a, job_id_b, comparison_label.

        # Test scenario:
        #   ids = jm.submit_comparison(target=fn, kwargs_a={...}, kwargs_b={...})
        #   → ids["job_id_a"] and ids["job_id_b"] are valid UUIDs
        """
        job_id_a = self.submit(
            target=target,
            kwargs=kwargs_a,
            label=f"{label}_A",
            name=f"{label}_A",
        )
        job_id_b = self.submit(
            target=target,
            kwargs=kwargs_b,
            label=f"{label}_B",
            name=f"{label}_B",
        )
        logger.info(
            "Comparison submitted: %s (A=%s, B=%s)",
            label, job_id_a, job_id_b,
        )
        return {
            "job_id_a": job_id_a,
            "job_id_b": job_id_b,
            "comparison_label": label,
        }
```

> **주의**: `self.submit()` 시그니처가 다르면 기존 코드에 맞게 파라미터 조정.
> `submit(target, kwargs, label, name)` 형태가 아닌 경우:
> `submit(payload={...})` → `submit(payload=kwargs_a)` 등으로 변환.

---

## 검증 명령

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축/version04

PYTHONPATH=src python -c "
# 1. compute_delta
from qcviz_mcp.compute.pyscf_runner import compute_delta
result_a = {
    'total_energy_ev': -2080.5, 'orbital_gap_ev': 5.2,
    'scf_converged': True, 'structure_name': 'toluene',
    'homo_energy_ev': -6.5, 'lumo_energy_ev': -1.3,
    'n_atoms': 15,
}
result_b = {
    'total_energy_ev': -2095.3, 'orbital_gap_ev': 4.8,
    'scf_converged': True, 'structure_name': 'ethylbenzene',
    'homo_energy_ev': -6.3, 'lumo_energy_ev': -1.5,
    'n_atoms': 18,
}
d = compute_delta(result_a, result_b)
assert d['energy_delta_ev'] < 0, 'B should be more stable'
assert d['gap_delta_ev'] < 0, 'gap should decrease'
assert d['both_converged'] is True
print(f'✅ compute_delta: ΔE={d[\"energy_delta_ev\"]:.2f} eV, Δgap={d[\"gap_delta_ev\"]:.2f} eV')

# 2. explain_comparison
from qcviz_mcp.web.result_explainer import explain_comparison
expl = explain_comparison(delta=d, result_a=result_a, result_b=result_b)
assert '비교 분석' in expl['summary'], f'FAIL: {expl[\"summary\"]}'
assert len(expl['key_findings']) > 0, 'FAIL: no findings'
print(f'✅ explain_comparison: {expl[\"summary\"][:50]}...')
print(f'   findings: {len(expl[\"key_findings\"])}, interp: {len(expl[\"interpretation\"])}')

# 3. submit_comparison
import time
from qcviz_mcp.compute.job_manager import JobManager
jm = JobManager(max_workers=2)
ids = jm.submit_comparison(
    target=lambda **kw: time.sleep(0.01) or {'ok': True},
    kwargs_a={'x': 1}, kwargs_b={'x': 2}, label='test_cmp',
)
assert 'job_id_a' in ids and 'job_id_b' in ids
print(f'✅ submit_comparison: A={ids[\"job_id_a\"][:8]}... B={ids[\"job_id_b\"][:8]}...')
jm.shutdown(wait=True)

print()
print('🎉 Phase 3 Day 1-4: ALL CHECKS PASSED')
"

# 4. 기존 테스트 무결성
PYTHONPATH=src pytest tests/ -x -q 2>&1 | tail -5
```

---

## 다음 Day 연결점

- **Day 5-7**: `routes/compute.py`에 `/compute/comparison` 엔드포인트 추가
  (`submit_comparison()` 호출 + 완료 폴링 + `compute_delta()` 후처리).
  `routes/chat.py`에서 `ActionPlan.comparison.enabled` 분기 추가
  (WebSocket으로 comparison progress 스트리밍).
  `redis_job_store.py`에 comparison job 메타데이터 지원.
