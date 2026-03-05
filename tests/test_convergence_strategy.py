"""Phase η-2: 적응적 SCF 수렴 테스트."""

import logging

import pytest

pyscf = pytest.importorskip("pyscf")
from pyscf import gto, scf

from qcviz_mcp.backends.pyscf_backend import (
    ConvergenceStrategy,
    PySCFBackend,
)

backend = PySCFBackend()


class TestConvergenceStrategy:
    def test_levels_count(self):
        assert len(ConvergenceStrategy.LEVELS) == 5

    def test_levels_immutable(self):
        assert isinstance(ConvergenceStrategy.LEVELS, tuple)

    def test_apply_level0(self):
        mol = gto.M(atom="H 0 0 0; H 0 0 0.74", basis="sto-3g", verbose=0)
        mf = scf.RHF(mol)
        mf = ConvergenceStrategy.apply(mf, 0)
        assert mf.max_cycle == 100

    def test_apply_invalid(self):
        mol = gto.M(atom="H 0 0 0; H 0 0 0.74", basis="sto-3g", verbose=0)
        mf = scf.RHF(mol)
        with pytest.raises(ValueError):
            ConvergenceStrategy.apply(mf, 99)

    def test_level_name(self):
        assert ConvergenceStrategy.level_name(0) == "diis_default"
        assert ConvergenceStrategy.level_name(3) == "soscf"


class TestAdaptiveSCF:
    def test_water_converges(self):
        mol = gto.M(
            atom="O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587", basis="sto-3g", verbose=0
        )
        mf, _ = backend.compute_scf_adaptive(mol, spin=0)
        assert mf.converged

    def test_adaptive_via_flexible(self):
        mf, _ = backend.compute_scf_flexible(
            "O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587",
            basis="sto-3g",
            adaptive=True,
        )
        assert mf.converged

    def test_preserves_energy(self):
        atom = "O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587"
        mf_std, _ = backend.compute_scf_flexible(atom, basis="sto-3g", adaptive=False)
        mf_adp, _ = backend.compute_scf_flexible(atom, basis="sto-3g", adaptive=True)
        assert abs(mf_std.e_tot - mf_adp.e_tot) < 1e-6

    def test_logged(self, caplog):
        mol = gto.M(atom="H 0 0 0; H 0 0 0.74", basis="sto-3g", verbose=0)
        with caplog.at_level(logging.INFO):
            backend.compute_scf_adaptive(mol, spin=0)
        assert any("SCF converged at level" in r.message for r in caplog.records)

    @pytest.mark.slow
    def test_o2_triplet(self):
        mol = gto.M(atom="O 0 0 0; O 0 0 1.208", basis="sto-3g", spin=2, verbose=0)
        mf, _ = backend.compute_scf_adaptive(mol, spin=2)
        assert mf.converged
