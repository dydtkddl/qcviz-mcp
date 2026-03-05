# -*- coding: utf-8 -*-
"""IBO 품질 검증 모듈.

IBO 로컬라이제이션 결과의 정량적 품질 지표:
- Orbital spread (σ²)
- Molden roundtrip fidelity
- Charge method comparison
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def compute_orbital_spread(mol_obj: Any, orbital_coeff: np.ndarray) -> dict:
    """각 궤도의 공간적 퍼짐(spread, σ²)을 계산.

    σ² = <r²> - <r>² for each orbital.

    Args:
        mol_obj: PySCF Mole 객체.
        orbital_coeff: 궤도 계수 행렬 (n_ao, n_orb).

    Returns:
        dict: spreads (list[float]), mean_spread, max_spread.
    """
    # 다이폴 적분: <μ|r_α|ν>  (α = x, y, z)
    r_ints = mol_obj.intor("int1e_r", comp=3)  # shape: (3, nao, nao)

    # 쿼드러폴 (r²) 적분: <μ|r²|ν>
    # PySCF: int1e_r2 = x² + y² + z²
    r2_int = mol_obj.intor("int1e_r2")  # shape: (nao, nao)

    n_orb = orbital_coeff.shape[1]
    spreads = []

    for i in range(n_orb):
        c = orbital_coeff[:, i]
        # <r²> = c^T @ r2 @ c
        r2_expect = c @ r2_int @ c
        # <r>² = Σ_α (c^T @ r_α @ c)²
        r_expect_sq = sum((c @ r_ints[a] @ c) ** 2 for a in range(3))
        spread = float(r2_expect - r_expect_sq)
        spreads.append(max(spread, 0.0))  # 수치 오차로 음수 방지

    return {
        "spreads": spreads,
        "mean_spread": float(np.mean(spreads)),
        "max_spread": float(np.max(spreads)),
    }


def verify_molden_roundtrip(
    mol_obj: Any, original_coeff: np.ndarray, molden_path: str
) -> dict:
    """Molden export → re-import → 계수 비교.

    Returns:
        dict: frobenius_norm, max_abs_diff, passed (bool).
    """
    from pyscf.tools import molden

    _, _, mo_energy, mo_coeff, _, _ = molden.load(molden_path)

    n_orb = min(original_coeff.shape[1], mo_coeff.shape[1])

    # 부호 자유도 보정: 각 열의 최대 절대값 원소의 부호를 맞춤
    orig = original_coeff[:, :n_orb].copy()
    loaded = mo_coeff[:, :n_orb].copy()

    for i in range(n_orb):
        if np.dot(orig[:, i], loaded[:, i]) < 0:
            loaded[:, i] *= -1

    diff = orig - loaded
    frob = float(np.linalg.norm(diff, "fro"))
    max_abs = float(np.max(np.abs(diff)))

    return {
        "frobenius_norm": frob,
        "max_abs_diff": max_abs,
        "passed": frob < 1e-6,
    }


def compare_charges(charges_a: np.ndarray, charges_b: np.ndarray) -> dict:
    """두 전하 세트 간 일관성 비교.

    Returns:
        dict: correlation, max_diff, sign_agreement (0-1).
    """
    if len(charges_a) != len(charges_b):
        return {"correlation": 0.0, "max_diff": float("inf"), "sign_agreement": 0.0}

    corr = float(np.corrcoef(charges_a, charges_b)[0, 1]) if len(charges_a) > 1 else 1.0
    max_diff = float(np.max(np.abs(charges_a - charges_b)))
    sign_match = np.sum(np.sign(charges_a) == np.sign(charges_b))
    sign_agree = float(sign_match / len(charges_a))

    return {
        "correlation": corr,
        "max_diff": max_diff,
        "sign_agreement": sign_agree,
    }
