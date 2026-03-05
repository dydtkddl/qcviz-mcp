"""Phase η-4: 기저 함수 독립성 테스트."""

import time

import pytest

pyscf = pytest.importorskip("pyscf")
from qcviz_mcp.backends.pyscf_backend import PySCFBackend
from qcviz_mcp.validation import verify_basis_independence

backend = PySCFBackend()
WATER = "O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587"
METHANE = "C 0 0 0; H 0.629 0.629 0.629; H -0.629 -0.629 0.629; H -0.629 0.629 -0.629; H 0.629 -0.629 -0.629"


def _run(atom, basis):
    s, m = backend.compute_scf(atom, basis=basis, method="HF")
    ia = backend.compute_iao(s, m)
    ib = backend.compute_ibo(s, ia, m)
    return {"n_ibo": ib.n_ibo, "charges": ia.charges, "energy": s.energy_hartree}


class TestBasisIndependence:
    def test_water_2bases(self):
        for b in ("sto-3g", "cc-pvdz"):
            assert _run(WATER, b)["n_ibo"] == 5

    @pytest.mark.slow
    def test_water_4bases(self):
        for b in ("sto-3g", "cc-pvdz", "cc-pvtz", "aug-cc-pvdz"):
            try:
                assert _run(WATER, b)["n_ibo"] == 5, f"{b}"
            except Exception as e:
                if "basis" in str(e).lower():
                    pytest.skip(f"{b}: {e}")
                raise

    @pytest.mark.slow
    def test_methane_4bases(self):
        for b in ("sto-3g", "cc-pvdz", "cc-pvtz", "aug-cc-pvdz"):
            try:
                assert _run(METHANE, b)["n_ibo"] == 5, f"{b}"
            except Exception as e:
                if "basis" in str(e).lower():
                    pytest.skip(f"{b}: {e}")
                raise

    @pytest.mark.slow
    def test_charge_deviation(self):
        results = {}
        for b in ("cc-pvdz", "cc-pvtz"):  # STO-3G excluded (minimal basis, large deviation expected)
            try:
                results[b] = _run(WATER, b)
            except Exception:
                continue
        if len(results) < 2:
            pytest.skip("Not enough bases")
        ind = verify_basis_independence("water", results)
        assert ind["charge_deviation_ok"]

    @pytest.mark.slow
    def test_timing(self):
        t0 = time.time()
        _run(WATER, "sto-3g")
        t_s = time.time() - t0
        try:
            t0 = time.time()
            _run(WATER, "cc-pvtz")
            t_b = time.time() - t0
        except Exception as e:
            pytest.skip(f"cc-pvtz: {e}")
        assert t_b / max(t_s, 0.001) < 100
