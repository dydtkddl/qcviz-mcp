"""Molden 내보내기 + IBO 검증 테스트."""

import os

import pytest

pyscf = pytest.importorskip("pyscf")

from qcviz_mcp.backends.pyscf_backend import PySCFBackend

backend = PySCFBackend()
WATER = "O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587"


class TestMoldenExport:
    """Molden 내보내기 테스트."""

    def test_export_ibo_water_molden(self, tmp_path):
        """Water sto-3g → IBO .molden 파일 생성."""
        scf_res, mol = backend.compute_scf(WATER, basis="sto-3g")
        iao_res = backend.compute_iao(scf_res, mol)
        ibo_res = backend.compute_ibo(scf_res, iao_res, mol)

        molden_path = str(tmp_path / "water_ibo.molden")
        result = backend.export_molden(mol, ibo_res.coefficients, molden_path)

        assert os.path.exists(molden_path)
        content = open(molden_path).read()
        assert "[Molden Format]" in content
        assert "[MO]" in content

    def test_export_canonical_molden(self, tmp_path):
        """Canonical MO → .molden."""
        scf_res, mol = backend.compute_scf(WATER, basis="sto-3g")
        molden_path = str(tmp_path / "water_canonical.molden")
        backend.export_molden(mol, scf_res.mo_coeff, molden_path)

        assert os.path.exists(molden_path)

    def test_molden_ibo_count(self, tmp_path):
        """IBO molden의 MO 수 == 점유 궤도 수."""
        scf_res, mol = backend.compute_scf(WATER, basis="sto-3g")
        iao_res = backend.compute_iao(scf_res, mol)
        ibo_res = backend.compute_ibo(scf_res, iao_res, mol)

        molden_path = str(tmp_path / "water_ibo_count.molden")
        backend.export_molden(mol, ibo_res.coefficients, molden_path)

        content = open(molden_path).read()
        mo_count = content.count("Ene=")
        assert mo_count == ibo_res.n_ibo


class TestIBOValidation:
    """IBO 품질 검증 테스트."""

    def test_water_spread(self):
        """Water sto-3g IBO spread < 5.0 Å² (보수적 기준)."""
        from qcviz_mcp.validation import compute_orbital_spread

        scf_res, mol = backend.compute_scf(WATER, basis="sto-3g")
        iao_res = backend.compute_iao(scf_res, mol)
        ibo_res = backend.compute_ibo(scf_res, iao_res, mol)

        result = compute_orbital_spread(mol, ibo_res.coefficients)
        assert result["max_spread"] < 5.0, f"Max spread = {result['max_spread']}"
        assert len(result["spreads"]) == ibo_res.n_ibo

    def test_molden_roundtrip_water(self, tmp_path):
        """Molden export → re-import → 계수 일치."""
        from qcviz_mcp.validation import verify_molden_roundtrip

        scf_res, mol = backend.compute_scf(WATER, basis="sto-3g")
        iao_res = backend.compute_iao(scf_res, mol)
        ibo_res = backend.compute_ibo(scf_res, iao_res, mol)

        molden_path = str(tmp_path / "roundtrip.molden")
        backend.export_molden(mol, ibo_res.coefficients, molden_path)

        result = verify_molden_roundtrip(mol, ibo_res.coefficients, molden_path)
        assert result["passed"], f"Frobenius norm = {result['frobenius_norm']}"

    def test_charge_sign_agreement(self):
        """IAO vs Mulliken 전하 부호 일치."""
        from qcviz_mcp.validation import compare_charges

        scf_res, mol = backend.compute_scf(WATER, basis="sto-3g")
        iao_res = backend.compute_iao(scf_res, mol)

        # Mulliken charges
        from pyscf import scf as pyscf_scf

        mf = pyscf_scf.RHF(mol).run()
        _, mulliken_chg = mf.mulliken_pop(verbose=0)

        result = compare_charges(iao_res.charges, mulliken_chg)
        assert result["sign_agreement"] >= 0.5, (
            f"Sign agreement = {result['sign_agreement']}"
        )
