"""벤치마크 분자 정의.

각 분자는 name, atom_spec, basis, expected_n_ibo, description을 포함.
좌표는 PySCF 형식 (세미콜론 구분).
기대 IBO 수는 RHF에서의 점유 궤도 수 = 전자수/2.

좌표 출처: NIST CCCBDB 또는 표준 결합 길이에 기반한 이상적 구조.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkMolecule:
    """벤치마크 분자 데이터."""

    name: str
    atom_spec: str
    basis: str
    expected_n_ibo: int
    description: str


# fmt: off
MOLECULES: list[BenchmarkMolecule] = [
    BenchmarkMolecule(
        name="water",
        atom_spec="O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587",
        basis="sto-3g",
        expected_n_ibo=5,  # 10e / 2 = 5 (core + 2 bond + 2 lone pair)
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
        basis="sto-3g",
        expected_n_ibo=5,  # 10e / 2 = 5 (core + 4 C-H)
        description="C-H ≈1.09Å. 정사면체 대칭. Core 1개 + C-H bond 4개",
    ),
    BenchmarkMolecule(
        name="ethylene",
        atom_spec=(
            "C 0 0  0.667; C 0 0 -0.667; "
            "H 0  0.923  1.237; H 0 -0.923  1.237; "
            "H 0  0.923 -1.237; H 0 -0.923 -1.237"
        ),
        basis="sto-3g",
        expected_n_ibo=8,  # 16e / 2 = 8 (2 core + C=C σ+π + 4 C-H)
        description="C=C ≈1.33Å, C-H ≈1.09Å. 이중결합 테스트",
    ),
    BenchmarkMolecule(
        name="formaldehyde",
        atom_spec="C 0 0 0; O 0 0 1.203; H 0.934 0 -0.563; H -0.934 0 -0.563",
        basis="sto-3g",
        expected_n_ibo=8,  # 16e / 2 = 8 (2 core + C=O σ+π + 2 C-H + 2 O lp)
        description="C=O ≈1.20Å. 카르보닐기 테스트",
    ),
    BenchmarkMolecule(
        name="hydrogen_fluoride",
        atom_spec="H 0 0 0; F 0 0 0.917",
        basis="sto-3g",
        expected_n_ibo=5,  # 10e / 2 = 5 (core + H-F bond + 3 F lone pairs)
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
        basis="sto-3g",
        expected_n_ibo=5,  # 10e / 2 = 5 (core + 3 N-H + 1 lone pair)
        description="N-H ≈1.01Å. 비공유전자쌍 테스트",
    ),
    BenchmarkMolecule(
        name="carbon_monoxide",
        atom_spec="C 0 0 0; O 0 0 1.128",
        basis="sto-3g",
        expected_n_ibo=7,  # 14e / 2 = 7 (2 core + σ+2π + 2 lone pairs)
        description="C≡O ≈1.13Å. 삼중결합 + lone pair",
    ),
    BenchmarkMolecule(
        name="nitrogen",
        atom_spec="N 0 0 0; N 0 0 1.098",
        basis="sto-3g",
        expected_n_ibo=7,  # 14e / 2 = 7 (2 core + σ+2π + 2 lone pairs)
        description="N≡N ≈1.10Å. 호모핵 삼중결합",
    ),
    BenchmarkMolecule(
        name="hydrogen_cyanide",
        atom_spec="H 0 0 0; C 0 0 1.064; N 0 0 2.222",
        basis="sto-3g",
        expected_n_ibo=7,  # 14e / 2 = 7 (2 core + H-C + C≡N σ+2π + N lp)
        description="C-H ≈1.06Å, C≡N ≈1.16Å. 삼중결합 + 수소",
    ),
    BenchmarkMolecule(
        name="lithium_hydride",
        atom_spec="Li 0 0 0; H 0 0 1.596",
        basis="sto-3g",
        expected_n_ibo=2,  # 4e / 2 = 2 (core + Li-H bond)
        description="Li-H ≈1.60Å. 이온성 결합 한계 테스트",
    ),
]
# fmt: on
