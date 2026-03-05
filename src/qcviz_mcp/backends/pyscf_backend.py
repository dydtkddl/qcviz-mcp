"""
PySCF 기반 IAO/IBO 계산 백엔드 구현.
"""
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
    for line in lines[2:2 + n_atoms]:
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

    def compute_scf(self, atom_spec: str, basis: str = "cc-pvdz", method: str = "RHF") -> SCFResult:
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

    def _resolve_minao(self, mol, minao='minao'):
        """ECP 감지 시 minao 자동 폴백."""
        warnings = []
        effective = minao
        if hasattr(mol, 'has_ecp') and mol.has_ecp() and minao == 'minao':
            effective = 'sto-3g'
            warnings.append(
                "ECP detected. Switched IAO reference basis from 'minao' to 'sto-3g'. "
                "For best results with transition metals, use all-electron "
                "basis (e.g., def2-SVP) without ECP."
            )
        return effective, warnings

    def compute_iao(self, scf_result: SCFResult, mol_obj: Any, minao: str = "minao") -> IAOResult:
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
            occupations=np.full(n_ibo, 2.0), # RHF 기준
            n_ibo=n_ibo,
        )

    def _compute_iao_charges(self, mol: Any, scf_result: SCFResult, iao_coeff: np.ndarray) -> np.ndarray:
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
        ao_labels = mol.ao_labels(fmt=False)
        n_iao = iao_orth.shape[1]
        charges = np.zeros(mol.natm)

        for j in range(n_iao):
            atom_idx = ao_labels[j][0]
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

        import tempfile
        import os

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

            with open(tmp_path, "r") as f:
                cube_text = f.read()

            logger.info(
                "Cube 생성 완료: orbital_index=%d, grid=%s, size=%d bytes",
                orbital_index, grid_points, len(cube_text),
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
        logger.info("Molden 파일 생성: %s (%d orbitals)", output_path, mo_coeff.shape[1])
        return str(Path(output_path).resolve())

    # ── UHF/ROHF 지원 (Phase ζ-2) ──────────────────────────

    def compute_scf_flexible(self, atom_spec: str, basis: str = "sto-3g",
                             charge: int = 0, spin: int = 0):
        """spin>0 시 UHF 자동 선택. (mf, mol) 튜플 반환."""
        if not _HAS_PYSCF:
            raise ImportError("PySCF가 설치되지 않았습니다.")
        atom_spec = _parse_atom_spec(atom_spec)
        mol = gto.M(atom=atom_spec, basis=basis, charge=charge, spin=spin, verbose=0)
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
        mo_a, mo_b = mf.mo_coeff
        occ_a, occ_b = mf.mo_occ
        mo_occ_a = mo_a[:, occ_a > 0]
        mo_occ_b = mo_b[:, occ_b > 0]
        iao_a = lo.iao.iao(mol, mo_occ_a, minao=effective)
        iao_b = lo.iao.iao(mol, mo_occ_b, minao=effective)
        return {
            "alpha": {"iao_coeff": iao_a, "n_iao": iao_a.shape[1]},
            "beta":  {"iao_coeff": iao_b, "n_iao": iao_b.shape[1]},
            "is_uhf": True,
            "minao_used": effective,
            "warnings": warnings,
        }

    def compute_ibo_uhf(self, mf, iao_result, mol):
        """UHF IBO: alpha/beta 각각 로컬라이즈."""
        mo_a, mo_b = mf.mo_coeff
        occ_a, occ_b = mf.mo_occ
        mo_occ_a = mo_a[:, occ_a > 0]
        mo_occ_b = mo_b[:, occ_b > 0]
        ibo_a = lo.ibo.ibo(mol, mo_occ_a, iaos=iao_result["alpha"]["iao_coeff"])
        ibo_b = lo.ibo.ibo(mol, mo_occ_b, iaos=iao_result["beta"]["iao_coeff"])
        return {
            "alpha": {"ibo_coeff": ibo_a, "n_ibo": ibo_a.shape[1]},
            "beta":  {"ibo_coeff": ibo_b, "n_ibo": ibo_b.shape[1]},
            "is_uhf": True,
            "total_ibo": ibo_a.shape[1] + ibo_b.shape[1],
        }

    def compute_uhf_charges(self, mf, mol):
        """UHF Mulliken 전하."""
        dm = mf.make_rdm1()
        s = mol.intor("int1e_ovlp")
        dm_total = dm[0] + dm[1] if isinstance(dm, (list, tuple)) else dm
        pop = np.einsum("ij,ji->i", dm_total, s)
        charges = []
        offset = 0
        for ia in range(mol.natm):
            nao_atom = sum(
                (2 * mol.bas_angular(ib) + 1) * mol.bas_nctr(ib)
                for ib in range(mol.nbas)
                if mol.bas_atom(ib) == ia
            )
            q = mol.atom_charge(ia) - sum(pop[offset:offset + nao_atom])
            charges.append(float(q))
            offset += nao_atom
        return charges


# 모듈 로딩 시 레지스트리에 자동 등록 (사용 가능한 경우에만)
registry.register(PySCFBackend)
