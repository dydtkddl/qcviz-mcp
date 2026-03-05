"""QCViz-MCP의 6가지 핵심 도구(Tools) 구현 및 FastMCP 서버 등록."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

import numpy as np

from qcviz_mcp.backends.base import (
    OrbitalBackend,
    ParserBackend,
    StructureBackend,
    VisualizationBackend,
)
from qcviz_mcp.backends.registry import BackendNotAvailableError, registry
from qcviz_mcp.mcp_server import mcp

logger = logging.getLogger(__name__)

# ── 보안 헬퍼 ──────────────────────────────────────────────────

# 프로젝트 루트를 기준으로 허용 경로 설정
_PROJECT_ROOT = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)


def _validate_file_path(file_path: str, *, must_exist: bool = True) -> str:
    """경로 탐색 공격 방지를 위한 파일 경로 검증.

    Args:
        file_path: 검증할 파일 경로.
        must_exist: True면 파일 존재도 확인.

    Returns:
        정규화된 절대 경로.

    Raises:
        ValueError: 허용되지 않은 경로.
        FileNotFoundError: 파일 미존재 (must_exist=True일 때).

    """
    real_path = os.path.realpath(file_path)
    if not real_path.startswith(_PROJECT_ROOT):
        raise ValueError(
            "보안: 허용되지 않은 경로입니다. "
            "프로젝트 디렉토리 내부의 파일만 접근 가능합니다."
        )
    if must_exist and not os.path.isfile(real_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
    return real_path


def _validate_atom_spec(atom_spec: str, max_atoms: int = 200) -> str:
    """입력 분자 크기 제한.

    Raises:
        ValueError: 원자 수 초과.

    """
    lines = atom_spec.strip().splitlines()
    try:
        n_atoms = int(lines[0].strip())
        if n_atoms > max_atoms:
            raise ValueError(
                f"원자 수 {n_atoms}개가 최대 허용치 {max_atoms}개를 초과합니다."
            )
    except ValueError as e:
        if "초과" in str(e):
            raise
        # PySCF 직접 포맷: 세미콜론으로 구분
        n_atoms = len([seg for seg in atom_spec.split(";") if seg.strip()])
        if n_atoms > max_atoms:
            raise ValueError(
                f"원자 수 {n_atoms}개가 최대 허용치 {max_atoms}개를 초과합니다."
            )
    return atom_spec


# ── 도구 구현 ──────────────────────────────────────────────────


@mcp.tool()
def compute_ibo(xyz_string: str, basis: str = "cc-pvdz", method: str = "RHF") -> str:
    """주어진 분자 구조의 SCF 계산을 수행하고 Intrinsic Bond Orbitals(IBO)를 계산합니다.
    첫 번째 IBO에 대한 3D 시각화 HTML도 함께 생성합니다.

    Args:
        xyz_string: 분석할 분자의 XYZ 형식 문자열
        basis: 사용할 기저 함수 세트 (예: "sto-3g", "cc-pvdz")
        method: 전자 구조 방법 (예: "RHF", "B3LYP")

    Returns:
        JSON 형태의 결과 문자열.

    """
    try:
        _validate_atom_spec(xyz_string)
        backend: OrbitalBackend = registry.get("pyscf")
        scf_result, mol_obj = backend.compute_scf(
            xyz_string, basis=basis, method=method
        )
        iao_result = backend.compute_iao(scf_result, mol_obj)
        ibo_result = backend.compute_ibo(scf_result, iao_result, mol_obj)

        n_ibo = ibo_result.n_ibo
        energy = scf_result.energy_hartree
        charges = iao_result.charges.tolist()

        result: dict[str, Any] = {
            "status": "success",
            "n_ibo": n_ibo,
            "energy_hartree": round(energy, 6),
            "iao_charges": [round(c, 4) for c in charges],
            "warnings": [],
            "message": f"IBO 계산 완료: {n_ibo} IBOs 생성",
        }

        # cube 생성 + HTML 렌더링 (시각화 백엔드가 있을 때만)
        try:
            cube_text = backend.generate_cube(
                mol_obj,
                ibo_result.coefficients,
                orbital_index=0,
                grid_points=(80, 80, 80),
            )
            viz_backend = registry.get("py3dmol")
            html = viz_backend.render_orbital_from_cube(
                cube_text=cube_text,
                geometry_xyz=xyz_string,
                isovalue=0.05,
            )
            result["visualization_html"] = html
            result["message"] += ", 첫 번째 IBO 시각화 포함"
        except (BackendNotAvailableError, ImportError, Exception) as viz_err:
            logger.warning("시각화 생략: %s", str(viz_err))
            result["visualization_html"] = None
            result["message"] += " (시각화 생략)"

        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        logger.error("compute_ibo 실패: %s", str(e))
        return json.dumps(
            {
                "status": "error",
                "error": str(e),
                "suggestion": "입력 분자 구조(XYZ 형식)를 확인하세요.",
            },
            ensure_ascii=False,
        )


@mcp.tool()
def visualize_orbital(xyz_string: str, orbital_type: str = "HOMO") -> str:
    """분자의 특정 오비탈(예: HOMO, LUMO)을 3D로 시각화합니다.

    Args:
        xyz_string: 분자 구조 (XYZ 형식)
        orbital_type: 오비탈 유형.

    Returns:
        오비탈을 렌더링하는 HTML 코드(문자열).

    """
    try:
        viz_backend: VisualizationBackend = registry.get("py3dmol")
        dummy_cube = "기본 큐브 데이터 (Phase β에서 실제 데이터로 연결됨)\n"
        html = viz_backend.render_orbital(xyz_string, dummy_cube, isovalue=0.03)
        return f"성공적으로 오비탈 렌더링 HTML 생성 완료:\n\n{html[:200]}...\n(길이: {len(html)} bytes)"
    except Exception as e:
        return f"오류 발생: {str(e)}"


@mcp.tool()
def parse_output(file_path: str) -> str:
    """양자화학 프로그램 출력 파일을 읽어 분석합니다.

    Args:
        file_path: 출력 파일 경로 (프로젝트 디렉토리 내부만 허용)

    Returns:
        추출된 주요 데이터 요약.

    """
    try:
        validated_path = _validate_file_path(file_path)
        parser_backend: ParserBackend = registry.get("cclib")
        parsed = parser_backend.parse_file(validated_path)

        energy = parsed.energy_hartree if parsed.energy_hartree is not None else "N/A"
        n_atoms = len(parsed.atomic_numbers) if parsed.atomic_numbers else 0
        program = parsed.program

        return (
            f"파일 파싱 완료.\n"
            f"- 프로그램: {program}\n"
            f"- 원자 수: {n_atoms}\n"
            f"- 에너지(Hartree): {energy}\n"
        )
    except Exception as e:
        return f"오류 발생 (파싱 실패): {str(e)}"


@mcp.tool()
def compute_partial_charges(
    xyz_string: str, basis: str = "sto-3g", method: str = "RHF"
) -> str:
    """IAO 기반 부분 전하를 계산합니다.

    Args:
        xyz_string: 분자의 XYZ 좌표 문자열
        basis: 계산 기저 세트
        method: SCF 방법

    Returns:
        각 원자의 부분 전하 목록.

    """
    try:
        _validate_atom_spec(xyz_string)
        backend: OrbitalBackend = registry.get("pyscf")
        scf_result, mol_obj = backend.compute_scf(
            xyz_string, basis=basis, method=method
        )
        iao_result = backend.compute_iao(scf_result, mol_obj)

        charges = iao_result.charges
        symbols = [mol_obj.atom_symbol(i) for i in range(mol_obj.natm)]

        output = ["부분 전하 (IAO 기반 분할):"]
        for sym, chg in zip(symbols, charges):
            output.append(f"  {sym}: {chg:+.4f}")

        return "\n".join(output)
    except Exception as e:
        return f"전하 계산 중 오류: {str(e)}"


@mcp.tool()
def convert_format(input_path: str, output_path: str) -> str:
    """분자 구조 파일을 다른 형식으로 변환합니다.

    Args:
        input_path: 입력 파일의 경로 (프로젝트 디렉토리 내부)
        output_path: 출력 파일 경로 (프로젝트 디렉토리 내부)

    Returns:
        변환 결과 상태 및 경로.

    """
    try:
        validated_input = _validate_file_path(input_path)
        validated_output = _validate_file_path(output_path, must_exist=False)
        ase_backend: StructureBackend = registry.get("ase")
        result_path = ase_backend.convert_format(validated_input, validated_output)
        return f"파일 변환 성공: {result_path.absolute()}"
    except Exception as e:
        return f"파일 변환 중 오류: {str(e)}"


@mcp.tool()
def analyze_bonding(xyz_string: str) -> str:
    """입력 분자의 IBO 기반 결합 특성을 분석합니다.
    IAO 부분 전하와 IBO 점유 패턴으로 결합 구조를 보고합니다.

    Args:
        xyz_string: 분자의 XYZ 좌표 문자열

    Returns:
        IBO 결합 분석 보고서.

    """
    try:
        _validate_atom_spec(xyz_string)
        backend: OrbitalBackend = registry.get("pyscf")
        scf_result, mol_obj = backend.compute_scf(
            xyz_string, basis="sto-3g", method="hf"
        )
        iao_result = backend.compute_iao(scf_result, mol_obj)
        ibo_result = backend.compute_ibo(scf_result, iao_result, mol_obj)

        n_ibo = ibo_result.n_ibo
        symbols = [mol_obj.atom_symbol(i) for i in range(mol_obj.natm)]
        charges = iao_result.charges

        # 결합 분석: IBO 계수로 각 궤도의 원자 기여도 추산
        ibo_coeff = ibo_result.coefficients
        ao_labels = mol_obj.ao_labels(fmt=False)
        ovlp = mol_obj.intor_symmetric("int1e_ovlp")

        report_lines = [
            "결합 특성 분석:",
            f"분자: {' '.join(symbols)} ({mol_obj.natm}개 원자)",
            f"총 {n_ibo}개 IBO 검출",
            "",
            "IAO 부분 전하:",
        ]
        for sym, chg in zip(symbols, charges):
            report_lines.append(f"  {sym}: {chg:+.4f}")

        report_lines.append(f"\nIBO 점유도: {ibo_result.occupations.tolist()}")

        # 각 IBO의 원자별 기여도 분석
        report_lines.append("\nIBO별 원자 기여도:")
        for i in range(n_ibo):
            coeff_i = ibo_coeff[:, i]
            pop = (coeff_i**2) @ ovlp @ np.eye(len(coeff_i))
            # 원자별 합산
            atom_pop = np.zeros(mol_obj.natm)
            for j, label in enumerate(ao_labels):
                atom_pop[label[0]] += coeff_i[j] ** 2
            total = atom_pop.sum()
            if total > 0:
                atom_pop /= total
            dominant = [
                (symbols[k], atom_pop[k])
                for k in range(mol_obj.natm)
                if atom_pop[k] > 0.05
            ]
            dominant_str = ", ".join(f"{s}({p:.0%})" for s, p in dominant)
            report_lines.append(f"  IBO-{i}: {dominant_str}")

        return "\n".join(report_lines)
    except Exception as e:
        return f"분석 오류 발생: {str(e)}"
