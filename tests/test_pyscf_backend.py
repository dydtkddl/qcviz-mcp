"""
pyscf_backend 모듈 단위 테스트.
"""
import pytest
import numpy as np

pytest.importorskip("pyscf")

from qcviz_mcp.backends.registry import registry

@pytest.fixture
def pyscf_backend():
    """PySCF 백엔드 객체를 반환합니다."""
    return registry.get("pyscf")

def test_compute_scf(pyscf_backend, sample_water_xyz):
    result, mol = pyscf_backend.compute_scf(
        atom_spec=sample_water_xyz, basis="sto-3g", method="hf"
    )
    assert result.converged is True
    assert result.energy_hartree < -74.0 # 전형적인 물의 HF/STO-3G 에너지
    assert result.mo_coeff is not None
    assert mol.natm == 3

def test_compute_ibo_water(pyscf_backend, sample_water_xyz):
    # 기초 계산 수행 (이 과정에서 IAO도 내부적으로 거침)
    scf_res, mol = pyscf_backend.compute_scf(sample_water_xyz, basis="sto-3g", method="hf")
    iao_res = pyscf_backend.compute_iao(scf_res, mol)
    
    assert iao_res.charges is not None
    assert len(iao_res.charges) == 3
    assert np.isclose(np.sum(iao_res.charges), 0.0, atol=1e-5) # 중성 분자의 부분 전하 합은 0
    
    # IBO 계산
    ibo_res = pyscf_backend.compute_ibo(scf_res, iao_res, mol)
    assert ibo_res.n_ibo == 5 # 물분자 점유 오비탈: Core 1s, O-H bond x2, lone pair x2

def test_unsupported_method(pyscf_backend, sample_water_xyz):
    with pytest.raises(ValueError, match="지원하지 않는 메서드 유형"):
        pyscf_backend.compute_scf(atom_spec=sample_water_xyz, method="UNKNOWN")

def test_generate_cube_water(pyscf_backend, sample_water_xyz):
    """generate_cube가 유효한 Gaussian cube 포맷 문자열을 반환하는지 확인."""
    scf_res, mol = pyscf_backend.compute_scf(sample_water_xyz, basis="sto-3g")
    iao_res = pyscf_backend.compute_iao(scf_res, mol)
    ibo_res = pyscf_backend.compute_ibo(scf_res, iao_res, mol)

    cube_text = pyscf_backend.generate_cube(
        mol, ibo_res.coefficients, 0, grid_points=(20, 20, 20),
    )

    assert isinstance(cube_text, str)
    assert len(cube_text) > 500  # cube 파일은 최소 수백 바이트
    # cube 포맷 검증: 첫 두 줄은 코멘트, 셋째 줄은 원자 수
    lines = cube_text.strip().splitlines()
    assert len(lines) > 10
    third_line_parts = lines[2].split()
    n_atoms = abs(int(third_line_parts[0]))
    assert n_atoms == 3  # 물 분자
