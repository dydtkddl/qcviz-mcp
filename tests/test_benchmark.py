"""벤치마크 분자에 대한 파라미터화 테스트."""

import numpy as np
import pytest

pyscf = pytest.importorskip("pyscf")

from benchmark.molecules import MOLECULES
from qcviz_mcp.backends.pyscf_backend import PySCFBackend

backend = PySCFBackend()

# sto-3g + cc-pVDZ 모든 조합 생성
_PARAMS = []
for mol in MOLECULES:
    for basis in mol.basis_sets:
        _PARAMS.append((mol, basis))

_IDS = [f"{mol.name}_{basis}" for mol, basis in _PARAMS]


@pytest.mark.parametrize("mol,basis", _PARAMS, ids=_IDS)
def test_ibo_count(mol, basis):
    """각 분자·기저함수의 IBO 개수가 기대값과 일치하는지 확인."""
    scf_res, mol_obj = backend.compute_scf(mol.atom_spec, basis=basis, method="HF")
    assert scf_res.converged
    iao_res = backend.compute_iao(scf_res, mol_obj)
    ibo_res = backend.compute_ibo(scf_res, iao_res, mol_obj)

    assert ibo_res.n_ibo == mol.expected_n_ibo, (
        f"{mol.name}/{basis}: expected {mol.expected_n_ibo} IBOs, got {ibo_res.n_ibo}"
    )


@pytest.mark.parametrize("mol,basis", _PARAMS, ids=_IDS)
def test_charge_conservation(mol, basis):
    """각 분자의 IAO 부분 전하 합이 0에 가까운지 확인."""
    scf_res, mol_obj = backend.compute_scf(mol.atom_spec, basis=basis, method="HF")
    iao_res = backend.compute_iao(scf_res, mol_obj)

    charge_sum = float(np.sum(iao_res.charges))
    assert abs(charge_sum) < 1e-4, (
        f"{mol.name}/{basis}: charge sum = {charge_sum:.6f}, expected ~0.0"
    )
