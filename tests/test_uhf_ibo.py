"""Phase ζ-2: UHF/ROHF IBO 테스트."""

import pytest

pyscf = pytest.importorskip("pyscf")

from qcviz_mcp.backends.pyscf_backend import PySCFBackend

backend = PySCFBackend()


class TestUHFIBO:
    def test_o2_triplet_scf_converges(self):
        """O₂ 삼중항 UHF SCF 수렴."""
        mf, mol = backend.compute_scf_flexible("O 0 0 0; O 0 0 1.208", "sto-3g", spin=2)
        assert mf.converged
        # UHF: mo_coeff is either tuple or ndarray with ndim=3
        import numpy as np

        if isinstance(mf.mo_coeff, np.ndarray):
            assert mf.mo_coeff.ndim == 3  # shape=(2, nao, nmo)
        else:
            assert isinstance(mf.mo_coeff, (tuple, list))

    def test_o2_triplet_iao_uhf(self):
        """O₂ 삼중항 IAO: alpha/beta 분리."""
        mf, mol = backend.compute_scf_flexible("O 0 0 0; O 0 0 1.208", "sto-3g", spin=2)
        iao_res = backend.compute_iao_uhf(mf, mol)
        assert iao_res["is_uhf"]
        assert iao_res["alpha"]["n_iao"] > 0
        assert iao_res["beta"]["n_iao"] > 0

    def test_o2_triplet_ibo_alpha_gt_beta(self):
        """O₂ 삼중항 IBO: alpha > beta (2 unpaired e⁻)."""
        mf, mol = backend.compute_scf_flexible("O 0 0 0; O 0 0 1.208", "sto-3g", spin=2)
        iao_res = backend.compute_iao_uhf(mf, mol)
        ibo_res = backend.compute_ibo_uhf(mf, iao_res, mol)
        assert ibo_res["alpha"]["n_ibo"] > ibo_res["beta"]["n_ibo"]
        assert ibo_res["total_ibo"] > 0

    def test_no_radical_ibo(self):
        """NO 라디칼 (doublet): alpha = beta + 1."""
        mf, mol = backend.compute_scf_flexible("N 0 0 0; O 0 0 1.151", "sto-3g", spin=1)
        iao_res = backend.compute_iao_uhf(mf, mol)
        ibo_res = backend.compute_ibo_uhf(mf, iao_res, mol)
        assert ibo_res["alpha"]["n_ibo"] == ibo_res["beta"]["n_ibo"] + 1

    def test_uhf_charges_sum_zero(self):
        """UHF Mulliken 전하 합 ≈ 0 (중성 O₂)."""
        mf, mol = backend.compute_scf_flexible("O 0 0 0; O 0 0 1.208", "sto-3g", spin=2)
        charges = backend.compute_uhf_charges(mf, mol)
        assert abs(sum(charges)) < 0.01
        assert len(charges) == 2

    def test_rhf_path_unchanged(self):
        """RHF (spin=0)는 mo_coeff가 단일 ndarray."""
        mf, mol = backend.compute_scf_flexible(
            "O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587", "sto-3g", spin=0
        )
        # RHF: mo_coeff is 2D ndarray
        import numpy as np

        assert isinstance(mf.mo_coeff, np.ndarray) and mf.mo_coeff.ndim == 2
        assert mf.converged
