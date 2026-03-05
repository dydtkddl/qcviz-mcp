"""Phase η-3: PyVista 렌더러 + 큐브 파서 테스트."""

import os
from pathlib import Path

import numpy as np
import pytest

try:
    import pyvista as pv

    _HAS_PYVISTA = True
except ImportError:
    _HAS_PYVISTA = False

pytestmark = pytest.mark.skipif(not _HAS_PYVISTA, reason="PyVista not installed")


@pytest.fixture
def s_data():
    npts = (20, 20, 20)
    x = np.linspace(-3, 3, npts[0])
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    data = np.exp(-(X**2 + Y**2 + Z**2))
    origin = (-3.0, -3.0, -3.0)
    axes = [
        np.array([6.0, 0.0, 0.0]),
        np.array([0.0, 6.0, 0.0]),
        np.array([0.0, 0.0, 6.0]),
    ]
    return data, origin, axes, npts


@pytest.fixture
def pz_data():
    npts = (20, 20, 20)
    x = np.linspace(-3, 3, npts[0])
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    data = Z * np.exp(-(X**2 + Y**2 + Z**2))
    origin = (-3.0, -3.0, -3.0)
    axes = [
        np.array([6.0, 0.0, 0.0]),
        np.array([0.0, 6.0, 0.0]),
        np.array([0.0, 0.0, 6.0]),
    ]
    return data, origin, axes, npts


class TestGrid:
    def test_shape(self, s_data):
        from qcviz_mcp.renderers.pyvista_renderer import cube_to_pyvista_grid

        data, origin, axes, npts = s_data
        grid = cube_to_pyvista_grid(data, origin, axes, npts)
        assert grid.dimensions == npts
        assert "orbital" in grid.array_names


class TestPNG:
    def test_s_orbital(self, s_data, tmp_path):
        from qcviz_mcp.renderers.pyvista_renderer import render_orbital_png

        data, origin, axes, npts = s_data
        out = str(tmp_path / "s.png")
        r = render_orbital_png(
            data,
            origin,
            axes,
            npts,
            output_path=out,
            isovalue=0.5,
            window_size=(800, 600),
        )
        assert os.path.exists(r) and Path(r).stat().st_size > 1000

    def test_pz(self, pz_data, tmp_path):
        from qcviz_mcp.renderers.pyvista_renderer import render_orbital_png

        data, origin, axes, npts = pz_data
        out = str(tmp_path / "pz.png")
        r = render_orbital_png(
            data,
            origin,
            axes,
            npts,
            output_path=out,
            isovalue=0.2,
            window_size=(800, 600),
        )
        assert os.path.exists(r) and Path(r).stat().st_size > 1000

    def test_atoms(self, s_data, tmp_path):
        from qcviz_mcp.renderers.pyvista_renderer import render_orbital_png

        data, origin, axes, npts = s_data
        out = str(tmp_path / "at.png")
        r = render_orbital_png(
            data,
            origin,
            axes,
            npts,
            output_path=out,
            isovalue=0.5,
            window_size=(800, 600),
            show_atoms=[("O", [0, 0, 0]), ("H", [0, 1, 0])],
        )
        assert os.path.exists(r)


class TestCubeParser:
    def test_synthetic(self):
        from qcviz_mcp.backends.pyscf_backend import parse_cube_string

        lines = [
            "Comment 1",
            "Comment 2",
            "    1    0.0    0.0    0.0",
            "    3    1.0    0.0    0.0",
            "    3    0.0    1.0    0.0",
            "    3    0.0    0.0    1.0",
            "    8    0.0    0.0    0.0    0.0",
        ]
        vals = [f"  {float(i):.6E}" for i in range(27)]
        for i in range(0, 27, 6):
            lines.append("  ".join(vals[i : i + 6]))
        parsed = parse_cube_string("\n".join(lines))
        assert parsed["npts"] == (3, 3, 3) and parsed["data"].shape == (3, 3, 3)
        assert parsed["atoms"][0][0] == 8

    @pytest.mark.slow
    def test_real_roundtrip(self):
        pyscf = pytest.importorskip("pyscf")
        from qcviz_mcp.backends.pyscf_backend import PySCFBackend, parse_cube_string

        b = PySCFBackend()
        scf_res, mol = b.compute_scf(
            "O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587", basis="sto-3g"
        )
        iao = b.compute_iao(scf_res, mol)
        ibo = b.compute_ibo(scf_res, iao, mol)
        cube = b.generate_cube(mol, ibo.coefficients, 0, grid_points=(20, 20, 20))
        p = parse_cube_string(cube)
        assert p["npts"] == (20, 20, 20) and len(p["atoms"]) == 3


class TestE2E:
    @pytest.mark.slow
    def test_pipeline(self, tmp_path):
        pyscf = pytest.importorskip("pyscf")
        from qcviz_mcp.backends.pyscf_backend import PySCFBackend
        from qcviz_mcp.renderers.pyvista_renderer import render_from_cube_string

        b = PySCFBackend()
        scf_res, mol = b.compute_scf(
            "O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587", basis="sto-3g"
        )
        iao = b.compute_iao(scf_res, mol)
        ibo = b.compute_ibo(scf_res, iao, mol)
        cube = b.generate_cube(mol, ibo.coefficients, 0, grid_points=(20, 20, 20))
        out = str(tmp_path / "e2e.png")
        r = render_from_cube_string(
            cube, output_path=out, isovalue=0.02, window_size=(800, 600)
        )
        assert os.path.exists(r) and Path(r).stat().st_size > 1000


class TestFallback:
    def test_best_renderer(self):
        from qcviz_mcp.renderers import get_best_renderer

        assert get_best_renderer() == "pyvista"

    def test_flag(self):
        from qcviz_mcp.renderers import HAS_PYVISTA

        assert HAS_PYVISTA is True
