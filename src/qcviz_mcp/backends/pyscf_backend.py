"""PySCF 기반 IAO/IBO 계산 백엔드 구현."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

from qcviz_mcp.backends.base import IAOResult, IBOResult, OrbitalBackend, SCFResult
from qcviz_mcp.backends.registry import registry

try:
    import pyscf
    from pyscf import gto, lo, scf
    from pyscf.tools import cubegen

    _HAS_PYSCF = True
except ImportError:
    _HAS_PYSCF = False

logger = logging.getLogger(__name__)

_SUPPORTED_METHODS = frozenset({"HF", "RHF", "UHF", "RKS", "UKS", "B3LYP", "PBE0"})

# ── Phase η: 무거운 원소 감지 + 수렴 에스컬레이션 ──

_HEAVY_TM_Z = set(range(39, 49)) | set(range(72, 81))  # 4d(Y-Cd) + 5d(Hf-Hg)


class ConvergenceError(RuntimeError):
    """적응적 SCF 수렴 전략이 모두 실패했을 때 발생."""

    pass


class ConvergenceStrategy:
    """적응적 SCF 수렴 에스컬레이션 엔진 (5단계)."""

    LEVELS = (
        {
            "name": "diis_default",
            "max_cycle": 100,
            "level_shift": 0.0,
            "soscf": False,
            "damp": 0.0,
        },
        {
            "name": "diis_levelshift",
            "max_cycle": 200,
            "level_shift": 0.5,
            "soscf": False,
            "damp": 0.0,
        },
        {
            "name": "diis_damp",
            "max_cycle": 200,
            "level_shift": 0.3,
            "soscf": False,
            "damp": 0.5,
        },
        {
            "name": "soscf",
            "max_cycle": 200,
            "level_shift": 0.0,
            "soscf": True,
            "damp": 0.0,
        },
        {
            "name": "soscf_shift",
            "max_cycle": 300,
            "level_shift": 0.5,
            "soscf": True,
            "damp": 0.0,
        },
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


def _parse_atom_spec(atom_spec: str) -> str:
    """XYZ 파일 포맷 또는 PySCF 포맷을 모두 받아 PySCF atom 문자열로 변환.

    XYZ 파일 포맷 (첫 줄=원자 수, 둘째 줄=코멘트):
        3
        Water
        O  0.0  0.0  0.117
        H  0.0  0.757 -0.469
        H  0.0 -0.757 -0.469

    PySCF 포맷 (세미콜론 구분):
        O 0 0 0.117; H 0 0.757 -0.469; H 0 -0.757 -0.469

    Returns:
        PySCF ``gto.M(atom=...)`` 호환 문자열.

    """
    lines = atom_spec.strip().splitlines()

    # 첫 줄이 정수면 XYZ 파일 포맷으로 판단
    try:
        n_atoms = int(lines[0].strip())
    except ValueError:
        # 이미 PySCF 포맷이거나 세미콜론 구분
        return atom_spec

    # XYZ 포맷: 줄0=원자수, 줄1=코멘트, 줄2~=좌표
    atom_lines: list[str] = []
    for line in lines[2 : 2 + n_atoms]:
        parts = line.split()
        if len(parts) >= 4:
            atom_lines.append(f"{parts[0]}  {parts[1]}  {parts[2]}  {parts[3]}")

    return "; ".join(atom_lines)


class PySCFBackend(OrbitalBackend):
    """PySCF 기반 IAO/IBO 궤도 계산 및 체적 렌더링 백엔드.

    References:
        Knizia, J. Chem. Theory Comput. 2013, 9, 4834-4843.
        Knizia & Klein, Angew. Chem. Int. Ed. 2015, 54, 5518-5522.

    """

    @classmethod
    def name(cls) -> str:
        return "pyscf"

    @classmethod
    def is_available(cls) -> bool:
        return _HAS_PYSCF

    def compute_scf(
        self, atom_spec: str, basis: str = "cc-pvdz", method: str = "RHF"
    ) -> SCFResult:
        if not _HAS_PYSCF:
            raise ImportError("PySCF가 설치되지 않았습니다.")

        # ── 메서드 유효성 검증 (분자 빌드 전) ──
        method_upper = method.upper()
        if method_upper not in _SUPPORTED_METHODS:
            raise ValueError(f"지원하지 않는 메서드 유형: {method}")

        # ── XYZ → PySCF 포맷 변환 ──
        atom_spec = _parse_atom_spec(atom_spec)

        mol = gto.M(atom=atom_spec, basis=basis, verbose=0)
        logger.info("SCF 시작: %d atoms, basis=%s, method=%s", mol.natm, basis, method)

        if method_upper in ("RHF", "HF"):
            mf = scf.RHF(mol).run()
        elif method_upper == "UHF":
            mf = scf.UHF(mol).run()
        elif method_upper in ("RKS", "UKS", "B3LYP", "PBE0"):
            mf = scf.RKS(mol)
            if method_upper not in ("RKS", "UKS"):
                mf.xc = method
            mf = mf.run()
        else:
            raise ValueError(f"지원하지 않는 메서드 유형: {method}")

        if not mf.converged:
            raise RuntimeError(
                f"SCF calculation did not converge for '{atom_spec}' with {method}/{basis}"
            )

        # RHF/RKS 기본 가설
        mo_coeff = mf.mo_coeff
        mo_occ = mf.mo_occ
        mo_energy = mf.mo_energy

        return SCFResult(
            converged=True,
            energy_hartree=float(mf.e_tot),
            mo_coeff=mo_coeff,
            mo_occ=mo_occ,
            mo_energy=mo_energy,
            basis=basis,
            method=method,
        ), mol

    def _resolve_minao(self, mol, minao="minao"):
        """ECP 감지 시 minao 자동 폴백."""
        warnings = []
        effective = minao
        ecp_detected = False
        if hasattr(mol, "has_ecp"):
            ecp_result = mol.has_ecp()
            ecp_detected = (
                bool(ecp_result)
                if not isinstance(ecp_result, dict)
                else len(ecp_result) > 0
            )
        if not ecp_detected and hasattr(mol, "_ecp") and mol._ecp:
            ecp_detected = True
        if ecp_detected and minao == "minao":
            effective = "sto-3g"
            warnings.append(
                "ECP detected. Switched IAO reference basis from 'minao' to 'sto-3g'. "
                "For best results with transition metals, use all-electron "
                "basis (e.g., def2-SVP) without ECP."
            )
        # Phase η: 4d/5d 전이금속 감지
        has_heavy = _has_heavy_tm(mol)
        if has_heavy and not ecp_detected and minao == "minao":
            warnings.append(
                "4d/5d transition metal detected (all-electron). "
                "MINAO may lack coverage for high-angular-momentum shells. "
                "Consider using minao='sto-3g' if IAO convergence fails."
            )
            logger.info("Heavy TM detected (all-electron), using minao='%s'", effective)

        return effective, warnings

    @staticmethod
    def _unpack_uhf(mo_coeff, mo_occ):
        """UHF mo_coeff/mo_occ 언패킹. tuple이든 3D ndarray든 처리."""
        import numpy as np

        if isinstance(mo_coeff, (tuple, list)):
            return mo_coeff[0], mo_coeff[1], mo_occ[0], mo_occ[1]
        elif isinstance(mo_coeff, np.ndarray) and mo_coeff.ndim == 3:
            return mo_coeff[0], mo_coeff[1], mo_occ[0], mo_occ[1]
        else:
            raise ValueError(
                f"Unexpected mo_coeff type: {type(mo_coeff)}, ndim={getattr(mo_coeff, 'ndim', '?')}"
            )

    def compute_iao(
        self, scf_result: SCFResult, mol_obj: Any, minao: str = "minao"
    ) -> IAOResult:
        if not _HAS_PYSCF:
            raise ImportError("PySCF가 설치되지 않았습니다.")

        effective_minao, _ = self._resolve_minao(mol_obj, minao)

        # 점유 오비탈 추출
        orbocc = scf_result.mo_coeff[:, scf_result.mo_occ > 0]
        iao_coeff = lo.iao.iao(mol_obj, orbocc, minao=effective_minao)

        charges = self._compute_iao_charges(mol_obj, scf_result, iao_coeff)

        return IAOResult(
            coefficients=iao_coeff,
            charges=charges,
        )

    def compute_ibo(
        self,
        scf_result: SCFResult,
        iao_result: IAOResult,
        mol_obj: Any,
        localization_method: str = "PM",
    ) -> IBOResult:
        if not _HAS_PYSCF:
            raise ImportError("PySCF가 설치되지 않았습니다.")

        orbocc = scf_result.mo_coeff[:, scf_result.mo_occ > 0]
        logger.info("IBO 계산 준비 중. 국소화 방법: %s", localization_method)

        if localization_method.upper() == "PM":
            # PM with IAO represents Intrinsic Bond Orbitals
            ibo_obj = lo.ibo.ibo(mol_obj, orbocc, iaos=iao_result.coefficients)
            ibo_coeff = ibo_obj
        elif localization_method.upper() == "BOYS":
            boys_loc = lo.Boys(mol_obj, orbocc)
            boys_loc.verbose = 0
            boys_loc.kernel()
            ibo_coeff = boys_loc.mo_coeff
        else:
            raise ValueError(f"지원하지 않는 국소화 방식: {localization_method}")

        n_ibo = ibo_coeff.shape[1]
        logger.info("IBO 계산 완료: %d IBOs 생상됨.", n_ibo)

        return IBOResult(
            coefficients=ibo_coeff,
            occupations=np.full(n_ibo, 2.0),  # RHF 기준
            n_ibo=n_ibo,
        )

    def _compute_iao_charges(
        self, mol: Any, scf_result: SCFResult, iao_coeff: np.ndarray
    ) -> np.ndarray:
        """IAO 기반 원자 부분 전하 — Löwdin 정규직교화 활용."""
        ovlp = mol.intor_symmetric("int1e_ovlp")
        orbocc = scf_result.mo_coeff[:, scf_result.mo_occ > 0]

        # ── 핵심: IAO를 명시적으로 정규직교화 ──
        # Löwdin 정규직교화: C_orth = C_iao @ S_iao^{-1/2}
        s_iao = iao_coeff.T @ ovlp @ iao_coeff
        eigvals, eigvecs = np.linalg.eigh(s_iao)
        s_iao_inv_half = eigvecs @ np.diag(1.0 / np.sqrt(eigvals)) @ eigvecs.T
        iao_orth = iao_coeff @ s_iao_inv_half

        # ── 정규직교 IAO 기저에서 밀도 행렬 ──
        # P_IAO = C_orth^T S C_occ C_occ^T S C_orth  (단위: 전자수)
        proj = iao_orth.T @ ovlp @ orbocc
        dm_iao = 2.0 * proj @ proj.T  # RHF: 2전자/궤도

        # ── 원자별 population 집계 ──
        # IAO는 reference(minao) 분자의 AO에 대응하므로
        # reference mol의 라벨을 사용해야 함
        from pyscf.lo.iao import reference_mol
        effective_minao, _ = self._resolve_minao(mol, "minao")
        pmol = reference_mol(mol, minao=effective_minao)
        ref_labels = pmol.ao_labels(fmt=False)
        n_iao = iao_orth.shape[1]
        charges = np.zeros(mol.natm)

        for j in range(n_iao):
            atom_idx = ref_labels[j][0]
            charges[atom_idx] += dm_iao[j, j]

        # charges 현재 = 각 원자의 전자수 → 부분전하 = 핵전하 - 전자수
        for i in range(mol.natm):
            charges[i] = mol.atom_charge(i) - charges[i]

        return charges

    def generate_cube(
        self,
        mol_obj: Any,
        orbital_coeff: np.ndarray,
        orbital_index: int,
        grid_points: tuple[int, int, int] = (80, 80, 80),
    ) -> str:
        """Gaussian cube 포맷 문자열을 반환.

        PySCF cubegen.orbital을 임시 파일로 쓰고 읽어서 반환합니다.

        Args:
            mol_obj: PySCF Mole 객체.
            orbital_coeff: 궤도 계수 행렬 (n_ao, n_orb).
            orbital_index: 시각화할 궤도 인덱스.
            grid_points: 각 축의 그리드 포인트 수.

        Returns:
            str: Gaussian cube 포맷 텍스트.
                 py3Dmol의 addVolumetricData(data, "cube", ...)에
                 직접 전달 가능한 형식.

        """
        if not _HAS_PYSCF:
            raise ImportError("PySCF가 설치되지 않았습니다.")

        import os
        import tempfile

        coeff_vector = orbital_coeff[:, orbital_index]

        # 임시 파일에 cube 데이터 쓰기
        tmp_path = None
        try:
            fd, tmp_path = tempfile.mkstemp(suffix=".cube")
            os.close(fd)  # cubegen이 직접 열어 씀

            cubegen.orbital(
                mol_obj,
                tmp_path,
                coeff_vector,
                nx=grid_points[0],
                ny=grid_points[1],
                nz=grid_points[2],
            )

            with open(tmp_path) as f:
                cube_text = f.read()

            logger.info(
                "Cube 생성 완료: orbital_index=%d, grid=%s, size=%d bytes",
                orbital_index,
                grid_points,
                len(cube_text),
            )
            return cube_text

        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    def export_molden(
        self,
        mol_obj: Any,
        mo_coeff: np.ndarray,
        output_path: str,
    ) -> str:
        """IBO/IAO/canonical 궤도를 Molden 포맷으로 내보내기."""
        if not _HAS_PYSCF:
            raise ImportError("PySCF가 설치되지 않았습니다.")

        from pyscf.tools import molden as molden_mod

        molden_mod.from_mo(mol_obj, output_path, mo_coeff)
        logger.info(
            "Molden 파일 생성: %s (%d orbitals)", output_path, mo_coeff.shape[1]
        )
        return str(Path(output_path).resolve())

    # ── UHF/ROHF 지원 (Phase ζ-2) ──────────────────────────

    def compute_scf_flexible(
        self,
        atom_spec: str,
        basis: str = "sto-3g",
        charge: int = 0,
        spin: int = 0,
        adaptive: bool = False,
    ):
        """spin>0 시 UHF 자동 선택. adaptive=True면 적응적 수렴. (mf, mol) 반환."""
        if not _HAS_PYSCF:
            raise ImportError("PySCF가 설치되지 않았습니다.")
        atom_spec = _parse_atom_spec(atom_spec)
        mol = gto.M(atom=atom_spec, basis=basis, charge=charge, spin=spin, verbose=0)

        if adaptive:
            return self.compute_scf_adaptive(mol, spin=spin)

        if spin > 0:
            mf = scf.UHF(mol)
        else:
            mf = scf.RHF(mol)
        mf.kernel()
        if not mf.converged:
            raise RuntimeError(f"SCF not converged for spin={spin}")
        return mf, mol

    def compute_iao_uhf(self, mf, mol, minao: str = "minao"):
        """UHF IAO: alpha/beta 스핀 채널 분리."""
        effective, warnings = self._resolve_minao(mol, minao)
        mo_a, mo_b, occ_a, occ_b = self._unpack_uhf(mf.mo_coeff, mf.mo_occ)
        mo_occ_a = mo_a[:, occ_a > 0]
        mo_occ_b = mo_b[:, occ_b > 0]
        iao_a = lo.iao.iao(mol, mo_occ_a, minao=effective)
        iao_b = lo.iao.iao(mol, mo_occ_b, minao=effective)
        return {
            "alpha": {"iao_coeff": iao_a, "n_iao": iao_a.shape[1]},
            "beta": {"iao_coeff": iao_b, "n_iao": iao_b.shape[1]},
            "is_uhf": True,
            "minao_used": effective,
            "warnings": warnings,
        }

    def compute_ibo_uhf(self, mf, iao_result, mol):
        """UHF IBO: alpha/beta 각각 로컬라이즈."""
        mo_a, mo_b, occ_a, occ_b = self._unpack_uhf(mf.mo_coeff, mf.mo_occ)
        mo_occ_a = mo_a[:, occ_a > 0]
        mo_occ_b = mo_b[:, occ_b > 0]
        ibo_a = lo.ibo.ibo(mol, mo_occ_a, iaos=iao_result["alpha"]["iao_coeff"])
        ibo_b = lo.ibo.ibo(mol, mo_occ_b, iaos=iao_result["beta"]["iao_coeff"])
        return {
            "alpha": {"ibo_coeff": ibo_a, "n_ibo": ibo_a.shape[1]},
            "beta": {"ibo_coeff": ibo_b, "n_ibo": ibo_b.shape[1]},
            "is_uhf": True,
            "total_ibo": ibo_a.shape[1] + ibo_b.shape[1],
        }

    def compute_uhf_charges(self, mf, mol):
        """UHF Mulliken 전하 계산. PySCF 내장 mulliken_pop 사용."""
        import numpy as np

        dm = mf.make_rdm1()
        if isinstance(dm, np.ndarray) and dm.ndim == 3:
            dm_total = dm[0] + dm[1]
        elif isinstance(dm, (list, tuple)):
            dm_total = dm[0] + dm[1]
        else:
            dm_total = dm
        s = mol.intor("int1e_ovlp")
        pop, chg = mf.mulliken_pop(mol, dm_total, s, verbose=0)
        return [float(c) for c in chg]

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

        logger.info(
            "Relativistic SCF: %d atoms, spin=%d, rel=%s", mol.natm, spin, relativistic
        )
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
                    logger.info(
                        "SCF converged at level %d: %s (E=%.8f)",
                        level,
                        ConvergenceStrategy.level_name(level),
                        mf.e_tot,
                    )
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
                    logger.info(
                        "SCF converged at level %d: %s (E=%.8f)",
                        level,
                        ConvergenceStrategy.level_name(level),
                        mf.e_tot,
                    )
                    return mf, mol
                else:
                    logger.info(
                        "Level %d (%s) did not converge.",
                        level,
                        ConvergenceStrategy.level_name(level),
                    )
            except Exception as e:
                logger.warning("Level %d failed: %s", level, e)
                continue

        raise ConvergenceError(f"SCF failed after {max_level + 1} strategies.")


# 모듈 로딩 시 레지스트리에 자동 등록 (사용 가능한 경우에만)
registry.register(PySCFBackend)
