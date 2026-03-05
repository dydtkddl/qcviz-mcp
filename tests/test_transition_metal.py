# -*- coding: utf-8 -*-
"""Phase ζ-1: 전이금속 IAO/IBO 테스트."""
import pytest

pyscf = pytest.importorskip("pyscf")

from qcviz_mcp.backends.pyscf_backend import PySCFBackend

backend = PySCFBackend()
WATER = "O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587"


class TestTransitionMetal:
    def test_ecp_detection_lanl2dz(self):
        """ECP 기저(LANL2DZ) 감지."""
        from pyscf import gto
        mol = gto.M(atom="Fe 0 0 0", basis="lanl2dz", ecp="lanl2dz", spin=4)
        assert mol.has_ecp()

    def test_allelectron_no_ecp(self):
        """All-electron 기저(def2-svp)는 ECP 없음."""
        from pyscf import gto
        mol = gto.M(atom="Fe 0 0 0", basis="def2-svp", spin=4)
        assert not mol.has_ecp()

    def test_resolve_minao_ecp(self):
        """ECP 시 minao 자동 폴백 → 'sto-3g'."""
        from pyscf import gto
        mol = gto.M(atom="Fe 0 0 0", basis="lanl2dz", ecp="lanl2dz", spin=4)
        effective, warnings = backend._resolve_minao(mol, "minao")
        assert effective == "sto-3g"
        assert len(warnings) > 0
        assert "ECP" in warnings[0]

    def test_resolve_minao_no_ecp(self):
        """ECP 없으면 minao 그대로."""
        from pyscf import gto
        mol = gto.M(atom=WATER, basis="sto-3g")
        effective, warnings = backend._resolve_minao(mol, "minao")
        assert effective == "minao"
        assert len(warnings) == 0

    def test_minao_explicit_override(self):
        """사용자 명시적 'sto-3g' 전달 시 그대로 사용."""
        from pyscf import gto
        mol = gto.M(atom=WATER, basis="sto-3g")
        effective, warnings = backend._resolve_minao(mol, "sto-3g")
        assert effective == "sto-3g"

    def test_water_ibo_with_minao_param(self):
        """water + minao='sto-3g' 명시적 전달 — IBO 5개."""
        scf_res, mol = backend.compute_scf(WATER, basis="sto-3g")
        iao_res = backend.compute_iao(scf_res, mol, minao="sto-3g")
        ibo_res = backend.compute_ibo(scf_res, iao_res, mol)
        assert ibo_res.coefficients.shape[1] == 5
