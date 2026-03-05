"""Phase η-1: 4d/5d 전이금속 X2C 테스트."""

import logging

import numpy as np
import pytest

pyscf = pytest.importorskip("pyscf")
from qcviz_mcp.backends.pyscf_backend import _HEAVY_TM_Z, PySCFBackend, _has_heavy_tm

backend = PySCFBackend()
logger = logging.getLogger(__name__)


class TestHeavyTM:
    def test_heavy_tm_detection_zr(self):
        from pyscf import gto

        mol = gto.M(atom="Zr 0 0 0; Cl 2.4 0 0; Cl 0 2.4 0; Cl 0 0 2.4; Cl -2.4 0 0", spin=0, charge=0, basis="def2-svp", verbose=0)
        assert _has_heavy_tm(mol)

    def test_heavy_tm_detection_light(self):
        from pyscf import gto

        mol = gto.M(
            atom="O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587", basis="sto-3g", verbose=0
        )
        assert not _has_heavy_tm(mol)

    def test_z_range(self):
        assert 40 in _HEAVY_TM_Z  # Zr
        assert 42 in _HEAVY_TM_Z  # Mo
        assert 26 not in _HEAVY_TM_Z  # Fe (3d)

    @pytest.mark.slow
    def test_zrcl4_sfx2c1e(self):
        mf, mol = backend.compute_scf_relativistic(
            atom_spec="Zr 0 0 0; Cl 1.35 1.35 1.35; Cl -1.35 -1.35 1.35; Cl -1.35 1.35 -1.35; Cl 1.35 -1.35 -1.35",
            basis="def2-svp",
            relativistic="sfx2c1e",
        )
        assert mf.converged
        assert np.isfinite(mf.e_tot)
        logger.info("ZrCl4 SFX2C-1e: %.6f Ha", mf.e_tot)

    @pytest.mark.slow
    def test_zrcl4_nonrel_vs_rel(self):
        atom = "Zr 0 0 0; Cl 1.35 1.35 1.35; Cl -1.35 -1.35 1.35; Cl -1.35 1.35 -1.35; Cl 1.35 -1.35 -1.35"
        mf_nr, _ = backend.compute_scf_relativistic(
            atom_spec=atom, basis="def2-svp", relativistic="none"
        )
        mf_rel, _ = backend.compute_scf_relativistic(
            atom_spec=atom, basis="def2-svp", relativistic="sfx2c1e"
        )
        delta = abs(mf_nr.e_tot - mf_rel.e_tot)
        assert delta > 0.01
        logger.info("ZrCl4 NR=%.6f, Rel=%.6f, Δ=%.6f", mf_nr.e_tot, mf_rel.e_tot, delta)

    def test_minao_warning_heavy_tm(self):
        from pyscf import gto

        mol = gto.M(atom="Zr 0 0 0; O 0 0 1.82", basis="def2-svp", verbose=0)
        _, warnings = backend._resolve_minao(mol, "minao")
        assert any("4d/5d" in w for w in warnings)
