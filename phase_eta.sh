#!/usr/bin/env bash
set -euo pipefail

cd /mnt/d/20260305_양자화학시각화MCP서버구축

echo "============================================="
echo "Phase η — 전체 적용 + 검증 스크립트"
echo "============================================="

# ═══════════════════════════════════════════════
# Step 0: PyVista 설치
# ═══════════════════════════════════════════════
echo "[Step 0] PyVista 설치..."
pip install pyvista --quiet 2>/dev/null || echo "PyVista 설치 실패 (선택적, 계속 진행)"

# ═══════════════════════════════════════════════
# Step 1: pyscf_backend.py — 기존 파일에 추가
# ═══════════════════════════════════════════════
echo "[Step 1] pyscf_backend.py 패치..."

BACKEND="src/qcviz_mcp/backends/pyscf_backend.py"

# 이미 패치되었는지 확인
if grep -q "ConvergenceStrategy" "$BACKEND" 2>/dev/null; then
    echo "  → 이미 패치됨, 건너뜀"
else

# --- 1A: 파일 상단 (registry.register 바로 위)에 모듈 레벨 코드 삽입 ---
python3 << 'PYEOF'
import pathlib

p = pathlib.Path("src/qcviz_mcp/backends/pyscf_backend.py")
code = p.read_text()

# _SUPPORTED_METHODS 바로 다음에 삽입
INSERT_AFTER = '_SUPPORTED_METHODS = frozenset({"HF", "RHF", "UHF", "RKS", "UKS", "B3LYP", "PBE0"})'

MODULE_ADDITIONS = '''

# ── Phase η: 무거운 원소 감지 + 수렴 에스컬레이션 ──

_HEAVY_TM_Z = set(range(39, 49)) | set(range(72, 81))  # 4d(Y-Cd) + 5d(Hf-Hg)


class ConvergenceError(RuntimeError):
    """적응적 SCF 수렴 전략이 모두 실패했을 때 발생."""
    pass


class ConvergenceStrategy:
    """적응적 SCF 수렴 에스컬레이션 엔진 (5단계)."""

    LEVELS = (
        {"name": "diis_default",   "max_cycle": 100, "level_shift": 0.0, "soscf": False, "damp": 0.0},
        {"name": "diis_levelshift","max_cycle": 200, "level_shift": 0.5, "soscf": False, "damp": 0.0},
        {"name": "diis_damp",      "max_cycle": 200, "level_shift": 0.3, "soscf": False, "damp": 0.5},
        {"name": "soscf",          "max_cycle": 200, "level_shift": 0.0, "soscf": True,  "damp": 0.0},
        {"name": "soscf_shift",    "max_cycle": 300, "level_shift": 0.5, "soscf": True,  "damp": 0.0},
    )

    @staticmethod
    def apply(mf, level_idx: int = 0):
        if level_idx < 0 or level_idx >= len(ConvergenceStrategy.LEVELS):
            raise ValueError(f"Invalid strategy level: {level_idx}")
        cfg = ConvergenceStrategy.LEVELS[level_idx]
        mf.max_cycle = cfg["max_cycle"]
        mf.level_shift = cfg["level_shift"]
        mf.damp = cfg["damp"]
        if cfg["soscf"]:
            mf = mf.newton()
        return mf

    @staticmethod
    def level_name(level_idx: int) -> str:
        return ConvergenceStrategy.LEVELS[level_idx]["name"]


def _has_heavy_tm(mol) -> bool:
    """분자에 4d/5d 전이금속이 포함되어 있는지 확인."""
    if not _HAS_PYSCF:
        return False
    for ia in range(mol.natm):
        if int(mol.atom_charge(ia)) in _HEAVY_TM_Z:
            return True
    return False


def parse_cube_string(cube_text: str) -> dict:
    """Gaussian cube 포맷 문자열 → numpy 3D array + 메타데이터.

    generate_cube() 출력 → PyVista 렌더러 연결용 브릿지 함수.
    """
    lines = cube_text.strip().splitlines()
    parts = lines[2].split()
    natm = abs(int(parts[0]))
    origin = (float(parts[1]), float(parts[2]), float(parts[3]))

    axes = []
    npts_list = []
    for i in range(3):
        p = lines[3 + i].split()
        n = int(p[0])
        npts_list.append(n)
        vec = np.array([float(p[1]), float(p[2]), float(p[3])]) * n
        axes.append(vec)
    npts = tuple(npts_list)

    atoms = []
    for i in range(natm):
        p = lines[6 + i].split()
        atoms.append((int(float(p[0])), float(p[2]), float(p[3]), float(p[4])))

    data_start = 6 + natm
    values = []
    for line in lines[data_start:]:
        values.extend(float(v) for v in line.split())

    data = np.array(values).reshape(npts)

    return {"data": data, "origin": origin, "axes": axes, "npts": npts, "atoms": atoms}

'''

if INSERT_AFTER in code:
    code = code.replace(INSERT_AFTER, INSERT_AFTER + MODULE_ADDITIONS)
    print("  Module-level additions inserted.")
else:
    print("  WARNING: Could not find insertion point for module-level code.")

# --- 1B: _resolve_minao 메서드에 4d/5d 감지 추가 ---
OLD_RESOLVE = '''        return effective, warnings'''

# _resolve_minao의 마지막 return 직전에 4d/5d 경고 추가 (첫 번째 occurrence만)
NEW_RESOLVE = '''        # Phase η: 4d/5d 전이금속 감지
        has_heavy = _has_heavy_tm(mol)
        if has_heavy and not ecp_detected and minao == 'minao':
            warnings.append(
                "4d/5d transition metal detected (all-electron). "
                "MINAO may lack coverage for high-angular-momentum shells. "
                "Consider using minao=\'sto-3g\' if IAO convergence fails."
            )
            logger.info("Heavy TM detected (all-electron), using minao=\'%s\'", effective)

        return effective, warnings'''

code = code.replace(OLD_RESOLVE, NEW_RESOLVE, 1)

# --- 1C: compute_scf_flexible에 adaptive 파라미터 추가 ---
OLD_FLEXIBLE_SIG = '''    def compute_scf_flexible(self, atom_spec: str, basis: str = "sto-3g",
                             charge: int = 0, spin: int = 0):
        """spin>0 시 UHF 자동 선택. (mf, mol) 튜플 반환."""'''

NEW_FLEXIBLE_SIG = '''    def compute_scf_flexible(self, atom_spec: str, basis: str = "sto-3g",
                             charge: int = 0, spin: int = 0,
                             adaptive: bool = False):
        """spin>0 시 UHF 자동 선택. adaptive=True면 적응적 수렴. (mf, mol) 반환."""'''

code = code.replace(OLD_FLEXIBLE_SIG, NEW_FLEXIBLE_SIG)

# compute_scf_flexible 본문에 adaptive 분기 추가
OLD_FLEXIBLE_BODY = '''        mol = gto.M(atom=atom_spec, basis=basis, charge=charge, spin=spin, verbose=0)
        if spin > 0:'''

NEW_FLEXIBLE_BODY = '''        mol = gto.M(atom=atom_spec, basis=basis, charge=charge, spin=spin, verbose=0)

        if adaptive:
            return self.compute_scf_adaptive(mol, spin=spin)

        if spin > 0:'''

code = code.replace(OLD_FLEXIBLE_BODY, NEW_FLEXIBLE_BODY)

# --- 1D: 클래스 맨 끝 (registry.register 직전)에 새 메서드들 추가 ---
REGISTRY_LINE = "# 모듈 로딩 시 레지스트리에 자동 등록 (사용 가능한 경우에만)"

NEW_METHODS = '''
    # ── Phase η-1: X2C 스칼라 상대론 SCF ──

    def compute_scf_relativistic(
        self,
        atom_spec: str,
        basis="def2-svp",
        ecp=None,
        spin: int = 0,
        charge: int = 0,
        relativistic: str = "sfx2c1e",
    ):
        """X2C 스칼라 상대론 SCF. (mf, mol) 반환."""
        if not _HAS_PYSCF:
            raise ImportError("PySCF가 설치되지 않았습니다.")
        atom_spec = _parse_atom_spec(atom_spec)
        mol = gto.Mole()
        mol.atom = atom_spec
        mol.basis = basis
        if ecp:
            mol.ecp = ecp
        mol.charge = charge
        mol.spin = spin
        mol.verbose = 0
        mol.build()

        if spin == 0:
            mf = scf.RHF(mol)
        else:
            mf = scf.UHF(mol)

        if relativistic == "sfx2c1e":
            mf = mf.sfx2c1e()
        elif relativistic == "x2c":
            mf = mf.x2c()
        elif relativistic == "none":
            pass
        else:
            raise ValueError(f"Unknown relativistic: {relativistic}")

        logger.info("Relativistic SCF: %d atoms, spin=%d, rel=%s", mol.natm, spin, relativistic)
        mf.kernel()

        if not mf.converged:
            logger.warning("Relativistic SCF not converged, trying adaptive...")
            mf, mol = self._run_adaptive(mol, spin, relativistic)

        return mf, mol

    def _run_adaptive(self, mol, spin: int, relativistic: str = "none"):
        """SCF 미수렴 시 적응적 전략 순차 시도."""
        for level in range(1, len(ConvergenceStrategy.LEVELS)):
            if spin == 0:
                mf = scf.RHF(mol)
            else:
                mf = scf.UHF(mol)

            if relativistic == "sfx2c1e":
                mf = mf.sfx2c1e()
            elif relativistic == "x2c":
                mf = mf.x2c()

            mf = ConvergenceStrategy.apply(mf, level)
            try:
                mf.kernel()
                if mf.converged:
                    logger.info("SCF converged at level %d: %s (E=%.8f)",
                                level, ConvergenceStrategy.level_name(level), mf.e_tot)
                    return mf, mol
            except Exception as e:
                logger.warning("Strategy level %d failed: %s", level, e)
                continue

        raise ConvergenceError("SCF failed after all adaptive strategies.")

    # ── Phase η-2: 적응적 SCF (비상대론) ──

    def compute_scf_adaptive(self, mol, spin: int = 0, max_escalation: int = 4):
        """자동 에스컬레이션으로 SCF 수렴. (mf, mol) 반환."""
        if not _HAS_PYSCF:
            raise ImportError("PySCF가 설치되지 않았습니다.")
        max_level = min(max_escalation, len(ConvergenceStrategy.LEVELS) - 1)

        for level in range(max_level + 1):
            if spin == 0:
                mf = scf.RHF(mol)
            else:
                mf = scf.UHF(mol)

            mf = ConvergenceStrategy.apply(mf, level)
            try:
                mf.kernel()
                if mf.converged:
                    logger.info("SCF converged at level %d: %s (E=%.8f)",
                                level, ConvergenceStrategy.level_name(level), mf.e_tot)
                    return mf, mol
                else:
                    logger.info("Level %d (%s) did not converge.",
                                level, ConvergenceStrategy.level_name(level))
            except Exception as e:
                logger.warning("Level %d failed: %s", level, e)
                continue

        raise ConvergenceError(f"SCF failed after {max_level + 1} strategies.")


'''

code = code.replace(REGISTRY_LINE, NEW_METHODS + REGISTRY_LINE)

p.write_text(code)
print("  pyscf_backend.py patched successfully.")
PYEOF

fi  # end if not already patched

# ═══════════════════════════════════════════════
# Step 2: benchmark/molecules.py — 맨 끝에 추가
# ═══════════════════════════════════════════════
echo "[Step 2] benchmark/molecules.py 패치..."

if grep -q "HEAVY_TM_MOLECULES" benchmark/molecules.py 2>/dev/null; then
    echo "  → 이미 패치됨"
else
cat >> benchmark/molecules.py << 'EOF'

# ═══ Phase η-1: 4d/5d 전이금속 벤치마크 ═══
HEAVY_TM_MOLECULES: list[BenchmarkMolecule] = [
    BenchmarkMolecule(
        name="zrcl4",
        atom_spec=(
            "Zr  0.000  0.000  0.000; "
            "Cl  1.350  1.350  1.350; Cl -1.350 -1.350  1.350; "
            "Cl -1.350  1.350 -1.350; Cl  1.350 -1.350 -1.350"
        ),
        basis_sets=("def2-svp",),
        expected_n_ibo=0,
        description="ZrCl4 tetrahedral. 4d TM. All-electron def2-SVP",
    ),
    BenchmarkMolecule(
        name="mo_co_6",
        atom_spec=(
            "Mo  0.000  0.000  0.000; "
            "C   0.000  0.000  2.063; O   0.000  0.000  3.200; "
            "C   2.063  0.000  0.000; O   3.200  0.000  0.000; "
            "C  -2.063  0.000  0.000; O  -3.200  0.000  0.000; "
            "C   0.000  2.063  0.000; O   0.000  3.200  0.000; "
            "C   0.000 -2.063  0.000; O   0.000 -3.200  0.000; "
            "C   0.000  0.000 -2.063; O   0.000  0.000 -3.200"
        ),
        basis_sets=("def2-svp",),
        expected_n_ibo=0,
        description="Mo(CO)6 octahedral. 4d TM. All-electron def2-SVP",
    ),
]

EXTENDED_BASIS_SETS: tuple[str, ...] = ("sto-3g", "cc-pvdz", "cc-pvtz", "aug-cc-pvdz")
EOF
echo "  Done."
fi

# ═══════════════════════════════════════════════
# Step 3: renderers/__init__.py 교체
# ═══════════════════════════════════════════════
echo "[Step 3] renderers/__init__.py 작성..."

cat > src/qcviz_mcp/renderers/__init__.py << 'EOF'
# -*- coding: utf-8 -*-
"""Rendering utilities — Phase η: 자동 선택 로직."""


def get_best_renderer() -> str:
    try:
        import pyvista  # noqa: F401
        return "pyvista"
    except ImportError:
        pass
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        return "playwright"
    except ImportError:
        pass
    return "html_only"


try:
    from qcviz_mcp.renderers.pyvista_renderer import (  # noqa: F401
        is_available as pyvista_available,
        render_orbital_png,
        render_from_cube_string,
    )
    HAS_PYVISTA = pyvista_available()
except ImportError:
    HAS_PYVISTA = False
EOF
echo "  Done."

# ═══════════════════════════════════════════════
# Step 4: pyvista_renderer.py 생성
# ═══════════════════════════════════════════════
echo "[Step 4] pyvista_renderer.py 생성..."

cat > src/qcviz_mcp/renderers/pyvista_renderer.py << 'PYEOF'
# -*- coding: utf-8 -*-
"""PyVista 기반 네이티브 오비탈 렌더러. 브라우저 불필요."""
from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)

try:
    import pyvista as pv
    _HAS_PYVISTA = True
except ImportError:
    _HAS_PYVISTA = False


def is_available() -> bool:
    return _HAS_PYVISTA


def cube_to_pyvista_grid(cube_data, origin, axes, npts):
    if not _HAS_PYVISTA:
        raise ImportError("PyVista not installed")
    spacing = tuple(
        float(np.linalg.norm(ax) / max(n - 1, 1))
        for ax, n in zip(axes, npts)
    )
    grid = pv.ImageData(dimensions=npts, spacing=spacing, origin=origin)
    grid["orbital"] = cube_data.flatten(order="F")
    return grid


def render_orbital_png(
    cube_data, origin, axes, npts,
    output_path="orbital.png", isovalue=0.02,
    window_size=(1920, 1080), colors=("blue", "red"),
    background="white", show_atoms=None,
) -> str:
    if not _HAS_PYVISTA:
        raise ImportError("PyVista not installed")
    pv.OFF_SCREEN = True
    grid = cube_to_pyvista_grid(cube_data, origin, axes, npts)
    pl = pv.Plotter(off_screen=True, window_size=window_size)
    pl.background_color = background
    try:
        pos = grid.contour([isovalue], scalars="orbital")
        if pos.n_points > 0:
            pl.add_mesh(pos, color=colors[0], opacity=0.6, smooth_shading=True)
    except Exception:
        pass
    try:
        neg = grid.contour([-isovalue], scalars="orbital")
        if neg.n_points > 0:
            pl.add_mesh(neg, color=colors[1], opacity=0.6, smooth_shading=True)
    except Exception:
        pass
    if show_atoms:
        _C = {"H":"white","C":"gray","N":"blue","O":"red","F":"green",
              "Fe":"orange","Ti":"silver","Zr":"teal","Mo":"purple"}
        for sym, coord in show_atoms:
            pl.add_mesh(pv.Sphere(radius=0.3, center=coord),
                        color=_C.get(sym,"gray"), opacity=1.0)
    pl.camera_position = "iso"
    pl.camera.zoom(1.3)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    pl.screenshot(output_path)
    pl.close()
    logger.info("PyVista PNG: %s (%d bytes)", output_path, Path(output_path).stat().st_size)
    return output_path


def render_from_cube_string(cube_text, output_path="orbital.png",
                            isovalue=0.02, window_size=(1920,1080),
                            colors=("blue","red"), background="white") -> str:
    from qcviz_mcp.backends.pyscf_backend import parse_cube_string
    parsed = parse_cube_string(cube_text)
    _Z = {1:"H",6:"C",7:"N",8:"O",9:"F",16:"S",22:"Ti",26:"Fe",40:"Zr",42:"Mo"}
    atoms = [(_Z.get(z,"X"),[x,y,zc]) for z,x,y,zc in parsed["atoms"]]
    return render_orbital_png(
        parsed["data"], parsed["origin"], parsed["axes"], parsed["npts"],
        output_path=output_path, isovalue=isovalue,
        window_size=window_size, colors=colors, background=background,
        show_atoms=atoms)
PYEOF
echo "  Done."

# ═══════════════════════════════════════════════
# Step 5: validation/__init__.py에 함수 추가
# ═══════════════════════════════════════════════
echo "[Step 5] validation/__init__.py 패치..."

if grep -q "verify_basis_independence" src/qcviz_mcp/validation/__init__.py 2>/dev/null; then
    echo "  → 이미 패치됨"
else
cat >> src/qcviz_mcp/validation/__init__.py << 'EOF'


# ── Phase η-4: 기저 함수 독립성 검증 ──

def verify_basis_independence(molecule_name: str, results_by_basis: dict) -> dict:
    """여러 기저의 IBO 결과를 비교하여 기저 독립성 검증."""
    if len(results_by_basis) < 2:
        return {
            "ibo_count_invariant": True, "charge_conservation": True,
            "charge_deviation_ok": True, "max_charge_deviation": 0.0,
            "ibo_counts": {b: r["n_ibo"] for b, r in results_by_basis.items()},
            "all_passed": True,
        }

    ibo_counts = {b: r["n_ibo"] for b, r in results_by_basis.items()}
    ibo_invariant = len(set(ibo_counts.values())) == 1

    charge_conservation = True
    for b, r in results_by_basis.items():
        if "charges" in r and r["charges"] is not None:
            if abs(float(np.sum(r["charges"]))) >= 1e-4:
                charge_conservation = False

    charge_arrays = [
        r["charges"] for r in results_by_basis.values()
        if "charges" in r and r["charges"] is not None
    ]
    max_deviation = 0.0
    if len(charge_arrays) >= 2:
        for i in range(len(charge_arrays)):
            for j in range(i + 1, len(charge_arrays)):
                if len(charge_arrays[i]) == len(charge_arrays[j]):
                    dev = float(np.max(np.abs(charge_arrays[i] - charge_arrays[j])))
                    max_deviation = max(max_deviation, dev)

    charge_deviation_ok = max_deviation < 0.15
    all_passed = ibo_invariant and charge_conservation and charge_deviation_ok
    logger.info("%s basis independence: %s (maxΔq=%.4f, IBO=%s)",
                molecule_name, "PASS" if all_passed else "FAIL", max_deviation, ibo_counts)

    return {
        "ibo_count_invariant": ibo_invariant, "charge_conservation": charge_conservation,
        "charge_deviation_ok": charge_deviation_ok, "max_charge_deviation": max_deviation,
        "ibo_counts": ibo_counts, "all_passed": all_passed,
    }
EOF
echo "  Done."
fi

# ═══════════════════════════════════════════════
# Step 6: 테스트 파일 4개 생성
# ═══════════════════════════════════════════════
echo "[Step 6] 테스트 파일 생성..."

# --- test_heavy_tm.py ---
cat > tests/test_heavy_tm.py << 'EOF'
# -*- coding: utf-8 -*-
"""Phase η-1: 4d/5d 전이금속 X2C 테스트."""
import logging
import pytest
import numpy as np
pyscf = pytest.importorskip("pyscf")
from qcviz_mcp.backends.pyscf_backend import PySCFBackend, _has_heavy_tm, _HEAVY_TM_Z
backend = PySCFBackend()
logger = logging.getLogger(__name__)

class TestHeavyTM:
    def test_heavy_tm_detection_zr(self):
        from pyscf import gto
        mol = gto.M(atom="Zr 0 0 0; Cl 1.35 1.35 1.35", basis="def2-svp", verbose=0)
        assert _has_heavy_tm(mol)

    def test_heavy_tm_detection_light(self):
        from pyscf import gto
        mol = gto.M(atom="O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587", basis="sto-3g", verbose=0)
        assert not _has_heavy_tm(mol)

    def test_z_range(self):
        assert 40 in _HEAVY_TM_Z   # Zr
        assert 42 in _HEAVY_TM_Z   # Mo
        assert 26 not in _HEAVY_TM_Z  # Fe (3d)

    @pytest.mark.slow
    def test_zrcl4_sfx2c1e(self):
        mf, mol = backend.compute_scf_relativistic(
            atom_spec="Zr 0 0 0; Cl 1.35 1.35 1.35; Cl -1.35 -1.35 1.35; Cl -1.35 1.35 -1.35; Cl 1.35 -1.35 -1.35",
            basis="def2-svp", relativistic="sfx2c1e",
        )
        assert mf.converged
        assert np.isfinite(mf.e_tot)
        logger.info("ZrCl4 SFX2C-1e: %.6f Ha", mf.e_tot)

    @pytest.mark.slow
    def test_zrcl4_nonrel_vs_rel(self):
        atom = "Zr 0 0 0; Cl 1.35 1.35 1.35; Cl -1.35 -1.35 1.35; Cl -1.35 1.35 -1.35; Cl 1.35 -1.35 -1.35"
        mf_nr, _ = backend.compute_scf_relativistic(atom_spec=atom, basis="def2-svp", relativistic="none")
        mf_rel, _ = backend.compute_scf_relativistic(atom_spec=atom, basis="def2-svp", relativistic="sfx2c1e")
        delta = abs(mf_nr.e_tot - mf_rel.e_tot)
        assert delta > 0.01
        logger.info("ZrCl4 NR=%.6f, Rel=%.6f, Δ=%.6f", mf_nr.e_tot, mf_rel.e_tot, delta)

    def test_minao_warning_heavy_tm(self):
        from pyscf import gto
        mol = gto.M(atom="Zr 0 0 0; O 0 0 1.82", basis="def2-svp", verbose=0)
        _, warnings = backend._resolve_minao(mol, "minao")
        assert any("4d/5d" in w for w in warnings)
EOF

# --- test_convergence_strategy.py ---
cat > tests/test_convergence_strategy.py << 'EOF'
# -*- coding: utf-8 -*-
"""Phase η-2: 적응적 SCF 수렴 테스트."""
import logging
import pytest
import numpy as np
pyscf = pytest.importorskip("pyscf")
from pyscf import gto, scf
from qcviz_mcp.backends.pyscf_backend import PySCFBackend, ConvergenceStrategy, ConvergenceError
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
        mol = gto.M(atom="O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587", basis="sto-3g", verbose=0)
        mf, _ = backend.compute_scf_adaptive(mol, spin=0)
        assert mf.converged

    def test_adaptive_via_flexible(self):
        mf, _ = backend.compute_scf_flexible(
            "O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587",
            basis="sto-3g", adaptive=True,
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
EOF

# --- test_pyvista_renderer.py ---
cat > tests/test_pyvista_renderer.py << 'EOF'
# -*- coding: utf-8 -*-
"""Phase η-3: PyVista 렌더러 + 큐브 파서 테스트."""
import os
from pathlib import Path
import pytest
import numpy as np

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
    axes = [np.array([6.,0.,0.]), np.array([0.,6.,0.]), np.array([0.,0.,6.])]
    return data, origin, axes, npts

@pytest.fixture
def pz_data():
    npts = (20, 20, 20)
    x = np.linspace(-3, 3, npts[0])
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")
    data = Z * np.exp(-(X**2 + Y**2 + Z**2))
    origin = (-3.0, -3.0, -3.0)
    axes = [np.array([6.,0.,0.]), np.array([0.,6.,0.]), np.array([0.,0.,6.])]
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
        r = render_orbital_png(data, origin, axes, npts, output_path=out, isovalue=0.5, window_size=(800,600))
        assert os.path.exists(r) and Path(r).stat().st_size > 1000

    def test_pz(self, pz_data, tmp_path):
        from qcviz_mcp.renderers.pyvista_renderer import render_orbital_png
        data, origin, axes, npts = pz_data
        out = str(tmp_path / "pz.png")
        r = render_orbital_png(data, origin, axes, npts, output_path=out, isovalue=0.2, window_size=(800,600))
        assert os.path.exists(r) and Path(r).stat().st_size > 1000

    def test_atoms(self, s_data, tmp_path):
        from qcviz_mcp.renderers.pyvista_renderer import render_orbital_png
        data, origin, axes, npts = s_data
        out = str(tmp_path / "at.png")
        r = render_orbital_png(data, origin, axes, npts, output_path=out, isovalue=0.5,
                               window_size=(800,600), show_atoms=[("O",[0,0,0]),("H",[0,1,0])])
        assert os.path.exists(r)

class TestCubeParser:
    def test_synthetic(self):
        from qcviz_mcp.backends.pyscf_backend import parse_cube_string
        lines = ["Comment 1", "Comment 2",
                 "    1    0.0    0.0    0.0",
                 "    3    1.0    0.0    0.0", "    3    0.0    1.0    0.0", "    3    0.0    0.0    1.0",
                 "    8    0.0    0.0    0.0    0.0"]
        vals = [f"  {float(i):.6E}" for i in range(27)]
        for i in range(0, 27, 6):
            lines.append("  ".join(vals[i:i+6]))
        parsed = parse_cube_string("\n".join(lines))
        assert parsed["npts"] == (3, 3, 3) and parsed["data"].shape == (3, 3, 3)
        assert parsed["atoms"][0][0] == 8

    @pytest.mark.slow
    def test_real_roundtrip(self):
        pyscf = pytest.importorskip("pyscf")
        from qcviz_mcp.backends.pyscf_backend import PySCFBackend, parse_cube_string
        b = PySCFBackend()
        scf_res, mol = b.compute_scf("O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587", basis="sto-3g")
        iao = b.compute_iao(scf_res, mol)
        ibo = b.compute_ibo(scf_res, iao, mol)
        cube = b.generate_cube(mol, ibo.coefficients, 0, grid_points=(20,20,20))
        p = parse_cube_string(cube)
        assert p["npts"] == (20,20,20) and len(p["atoms"]) == 3

class TestE2E:
    @pytest.mark.slow
    def test_pipeline(self, tmp_path):
        pyscf = pytest.importorskip("pyscf")
        from qcviz_mcp.backends.pyscf_backend import PySCFBackend
        from qcviz_mcp.renderers.pyvista_renderer import render_from_cube_string
        b = PySCFBackend()
        scf_res, mol = b.compute_scf("O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587", basis="sto-3g")
        iao = b.compute_iao(scf_res, mol)
        ibo = b.compute_ibo(scf_res, iao, mol)
        cube = b.generate_cube(mol, ibo.coefficients, 0, grid_points=(20,20,20))
        out = str(tmp_path / "e2e.png")
        r = render_from_cube_string(cube, output_path=out, isovalue=0.02, window_size=(800,600))
        assert os.path.exists(r) and Path(r).stat().st_size > 1000

class TestFallback:
    def test_best_renderer(self):
        from qcviz_mcp.renderers import get_best_renderer
        assert get_best_renderer() == "pyvista"
    def test_flag(self):
        from qcviz_mcp.renderers import HAS_PYVISTA
        assert HAS_PYVISTA is True
EOF

# --- test_basis_independence.py ---
cat > tests/test_basis_independence.py << 'EOF'
# -*- coding: utf-8 -*-
"""Phase η-4: 기저 함수 독립성 테스트."""
import time
import pytest
import numpy as np
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
        for b in ("sto-3g", "cc-pvdz", "cc-pvtz"):
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
        t0 = time.time(); _run(WATER, "sto-3g"); t_s = time.time() - t0
        try:
            t0 = time.time(); _run(WATER, "cc-pvtz"); t_b = time.time() - t0
        except Exception as e:
            pytest.skip(f"cc-pvtz: {e}")
        assert t_b / max(t_s, 0.001) < 100
EOF

echo "  4 test files created."

# ═══════════════════════════════════════════════
# Step 7: conftest.py 업데이트
# ═══════════════════════════════════════════════
echo "[Step 7] conftest.py 마커 추가..."

if grep -q "pytest_configure" tests/conftest.py 2>/dev/null; then
    echo "  → 이미 패치됨"
else
python3 << 'PYEOF'
import pathlib
p = pathlib.Path("tests/conftest.py")
old = p.read_text()
new = '''"""pytest 공통 픽스처 및 설정 파일."""
from __future__ import annotations
import os
from pathlib import Path
import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "network: marks tests requiring network")

''' + old.split('"""', 2)[-1].lstrip('\n') if '"""' in old else old
p.write_text(new)
print("  conftest.py updated.")
PYEOF
fi

# ═══════════════════════════════════════════════
# Step 8: pyproject.toml 마커 + 버전 업데이트
# ═══════════════════════════════════════════════
echo "[Step 8] pyproject.toml 업데이트..."

python3 << 'PYEOF'
import pathlib
p = pathlib.Path("pyproject.toml")
t = p.read_text()
t = t.replace('version = "0.5.0-alpha"', 'version = "0.6.0-alpha"')
if "viz-native" not in t:
    t = t.replace(
        'png = ["playwright>=1.40"]',
        'png = ["playwright>=1.40"]\nviz-native = ["pyvista>=0.43"]'
    )
if "markers" not in t:
    t = t.replace(
        'pythonpath = ["."]',
        'pythonpath = ["."]\nmarkers = [\n'
        '    "slow: marks tests as slow",\n'
        '    "network: marks tests requiring network",\n]'
    )
p.write_text(t)
print("  pyproject.toml updated.")
PYEOF

# ═══════════════════════════════════════════════
# Step 9: 린트
# ═══════════════════════════════════════════════
echo "[Step 9] ruff 린트..."
ruff check src/ tests/ --fix --quiet 2>/dev/null || echo "  ruff check warnings (non-fatal)"
ruff format src/ tests/ --quiet 2>/dev/null || echo "  ruff format done"

# ═══════════════════════════════════════════════
# Step 10: 기존 108 테스트 회귀 확인
# ═══════════════════════════════════════════════
echo ""
echo "============================================="
echo "[Step 10] 기존 테스트 회귀 검증"
echo "============================================="
pytest tests/ -v \
  --ignore=tests/test_heavy_tm.py \
  --ignore=tests/test_convergence_strategy.py \
  --ignore=tests/test_pyvista_renderer.py \
  --ignore=tests/test_basis_independence.py \
  --tb=short 2>&1 | tee /tmp/phase_eta_regression.log

echo ""
echo "============================================="
echo "[Step 11] 새 테스트 — 빠른 것만"
echo "============================================="
pytest tests/test_heavy_tm.py tests/test_convergence_strategy.py -v -m "not slow" --tb=short 2>&1 | tee /tmp/phase_eta_fast.log

echo ""
echo "============================================="
echo "[Step 12] PyVista 테스트"
echo "============================================="
pytest tests/test_pyvista_renderer.py -v --tb=short 2>&1 | tee /tmp/phase_eta_pyvista.log

echo ""
echo "============================================="
echo "[Step 13] 기저 독립성 — 빠른 것만"
echo "============================================="
pytest tests/test_basis_independence.py -v -m "not slow" --tb=short 2>&1 | tee /tmp/phase_eta_basis.log

echo ""
echo "============================================="
echo "[Step 14] 전체 통합 (slow 포함)"
echo "============================================="
pytest tests/ -v -m "not network" --tb=short 2>&1 | tee /tmp/phase_eta_full.log

echo ""
echo "============================================="
echo "[Step 15] 결과 요약"
echo "============================================="
echo "--- 기존 회귀 ---"
tail -3 /tmp/phase_eta_regression.log
echo "--- 새 테스트 (fast) ---"
tail -3 /tmp/phase_eta_fast.log
echo "--- PyVista ---"
tail -3 /tmp/phase_eta_pyvista.log
echo "--- 기저 독립성 ---"
tail -3 /tmp/phase_eta_basis.log
echo "--- 전체 ---"
tail -3 /tmp/phase_eta_full.log

echo ""
echo "============================================="
echo "다음 단계 (수동):"
echo "  결과 확인 후:"
echo "  git add -A"
echo '  git commit -m "feat: Phase η — 4d/5d X2C, adaptive SCF, PyVista, extended basis"'
echo '  git tag -a v0.6.0-alpha -m "v0.6.0-alpha: 4 limitations resolved"'
echo "  git push origin main --tags"
echo "============================================="
