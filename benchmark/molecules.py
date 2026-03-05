# -*- coding: utf-8 -*-
"""벤치마크 분자 정의.

각 분자는 name, atom_spec, basis_sets, expected_n_ibo, description을 포함.
좌표는 PySCF 형식 (세미콜론 구분).
기대 IBO 수는 RHF에서의 점유 궤도 수 = 전자수/2.

좌표 출처: NIST CCCBDB 또는 표준 결합 길이에 기반한 이상적 구조.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BenchmarkMolecule:
    """벤치마크 분자 데이터."""

    name: str
    atom_spec: str
    basis_sets: tuple[str, ...] = ("sto-3g",)
    expected_n_ibo: int = 0
    description: str = ""
    spin: int = 0
    charge: int = 0


# fmt: off
MOLECULES: list[BenchmarkMolecule] = [
    BenchmarkMolecule(
        name="water",
        atom_spec="O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587",
        basis_sets=("sto-3g", "cc-pvdz"),
        expected_n_ibo=5,
        description="O-H ≈0.96Å. Core 1개 + O-H bond 2개 + lone pair 2개",
    ),
    BenchmarkMolecule(
        name="methane",
        atom_spec=(
            "C 0 0 0; "
            "H  0.629  0.629  0.629; "
            "H -0.629 -0.629  0.629; "
            "H -0.629  0.629 -0.629; "
            "H  0.629 -0.629 -0.629"
        ),
        basis_sets=("sto-3g", "cc-pvdz"),
        expected_n_ibo=5,
        description="C-H ≈1.09Å. 정사면체 대칭. Core 1개 + C-H bond 4개",
    ),
    BenchmarkMolecule(
        name="ethylene",
        atom_spec=(
            "C 0 0  0.667; C 0 0 -0.667; "
            "H 0  0.923  1.237; H 0 -0.923  1.237; "
            "H 0  0.923 -1.237; H 0 -0.923 -1.237"
        ),
        basis_sets=("sto-3g", "cc-pvdz"),
        expected_n_ibo=8,
        description="C=C ≈1.33Å, C-H ≈1.09Å. 이중결합 테스트",
    ),
    BenchmarkMolecule(
        name="formaldehyde",
        atom_spec="C 0 0 0; O 0 0 1.203; H 0.934 0 -0.563; H -0.934 0 -0.563",
        basis_sets=("sto-3g", "cc-pvdz"),
        expected_n_ibo=8,
        description="C=O ≈1.20Å. 카르보닐기 테스트",
    ),
    BenchmarkMolecule(
        name="hydrogen_fluoride",
        atom_spec="H 0 0 0; F 0 0 0.917",
        basis_sets=("sto-3g", "cc-pvdz"),
        expected_n_ibo=5,
        description="H-F ≈0.92Å. 강한 전기음성도 차이",
    ),
    BenchmarkMolecule(
        name="ammonia",
        atom_spec=(
            "N 0 0 0.116; "
            "H 0 0.939 -0.270; "
            "H 0.813 -0.470 -0.270; "
            "H -0.813 -0.470 -0.270"
        ),
        basis_sets=("sto-3g", "cc-pvdz"),
        expected_n_ibo=5,
        description="N-H ≈1.01Å. 비공유전자쌍 테스트",
    ),
    BenchmarkMolecule(
        name="carbon_monoxide",
        atom_spec="C 0 0 0; O 0 0 1.128",
        basis_sets=("sto-3g", "cc-pvdz"),
        expected_n_ibo=7,
        description="C≡O ≈1.13Å. 삼중결합 + lone pair",
    ),
    BenchmarkMolecule(
        name="nitrogen",
        atom_spec="N 0 0 0; N 0 0 1.098",
        basis_sets=("sto-3g", "cc-pvdz"),
        expected_n_ibo=7,
        description="N≡N ≈1.10Å. 호모핵 삼중결합",
    ),
    BenchmarkMolecule(
        name="hydrogen_cyanide",
        atom_spec="H 0 0 0; C 0 0 1.064; N 0 0 2.222",
        basis_sets=("sto-3g", "cc-pvdz"),
        expected_n_ibo=7,
        description="C-H ≈1.06Å, C≡N ≈1.16Å. 삼중결합 + 수소",
    ),
    BenchmarkMolecule(
        name="lithium_hydride",
        atom_spec="Li 0 0 0; H 0 0 1.596",
        basis_sets=("sto-3g", "cc-pvdz"),
        expected_n_ibo=2,
        description="Li-H ≈1.60Å. 이온성 결합 한계 테스트",
    ),
]
# fmt: on

# UHF 전용 벤치마크 (IBO 개수 = alpha 점유 궤도 수)
UHF_MOLECULES: list[BenchmarkMolecule] = [
    BenchmarkMolecule(
        name="oxygen_triplet",
        atom_spec="O 0 0 0; O 0 0 1.208",
        basis_sets=("sto-3g",),
        expected_n_ibo=0,  # UHF IBO는 alpha/beta 별도 → 별도 검증
        description="O₂ triplet ground state (spin=2). UHF required",
        spin=2,
        charge=0,
    ),
]
