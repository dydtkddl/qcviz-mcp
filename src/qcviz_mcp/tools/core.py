"""
QCViz-MCP의 6가지 핵심 도구(Tools) 구현 및 FastMCP 서버 등록.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from qcviz_mcp.mcp_server import mcp
from qcviz_mcp.backends.registry import registry, BackendNotAvailableError
from qcviz_mcp.backends.base import (
    OrbitalBackend, ParserBackend, VisualizationBackend, StructureBackend
)

logger = logging.getLogger(__name__)

# 각 도구에 대해 백엔드 인스턴스를 동적으로 얻어와서 실행합니다.

@mcp.tool()
def compute_ibo(xyz_string: str, basis: str = "cc-pvdz", method: str = "RHF") -> str:
    """
    주어진 분자 구조의 SCF 계산을 수행하고 Intrinsic Bond Orbitals(IBO)를 계산합니다.
    첫 번째 IBO에 대한 3D 시각화 HTML도 함께 생성합니다.

    Args:
        xyz_string: 분석할 분자의 XYZ 형식 문자열 (예: 물, 불화수소 등)
        basis: 사용할 기저 함수 세트 (예: "sto-3g", "cc-pvdz")
        method: 전자 구조 방법 (예: "RHF", "B3LYP")

    Returns:
        JSON 형태의 결과 문자열 (status, n_ibo, energy 등).
    """
    try:
        backend: OrbitalBackend = registry.get("pyscf")
        scf_result, mol_obj = backend.compute_scf(xyz_string, basis=basis, method=method)
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
            "message": f"IBO 계산 완료: {n_ibo} IBOs 생성",
        }

        # cube 생성 + HTML 렌더링 (시각화 백엔드가 있을 때만)
        try:
            cube_text = backend.generate_cube(
                mol_obj, ibo_result.coefficients, orbital_index=0,
                grid_points=(40, 40, 40),  # 속도/크기 절충
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
        return json.dumps({
            "status": "error",
            "error": str(e),
            "suggestion": "입력 분자 구조(XYZ 형식)를 확인하세요.",
        }, ensure_ascii=False)

@mcp.tool()
def visualize_orbital(xyz_string: str, orbital_type: str = "HOMO") -> str:
    """
    분자의 특정 오비탈(예: HOMO, LUMO)을 3D로 시각화하기 위한 HTML 코드를 생성합니다.
    (현재는 py3Dmol을 사용한 기본 시각화 HTML 템플릿 반환 시뮬레이션입니다.)

    Args:
        xyz_string: 분자 구조 (XYZ 형식)
        orbital_type: 오비탈 유형, 구형 또는 번호.

    Returns:
        오비탈을 렌더링하는 HTML 코드(문자열).
    """
    try:
        viz_backend: VisualizationBackend = registry.get("py3dmol")
        
        # 임시로 dummy cube 데이터를 생성하여 렌더링을 시연함
        dummy_cube = "기본 큐브 데이터 (Phase β에서 실제 데이터로 연결됨)\n"
        
        # 파일/데이터 대신 HTML 반환
        html = viz_backend.render_orbital(xyz_string, dummy_cube, isovalue=0.03)
        return f"성공적으로 오비탈 렌더링 HTML 생성 완료:\n\n{html[:200]}...\n(길이: {len(html)} bytes)"
    except Exception as e:
        return f"오류 발생: {str(e)}"

@mcp.tool()
def parse_output(file_path: str) -> str:
    """
    양자화학 프로그램(예: Gaussian, ORCA 등) 출력 파일을 직접 읽어 분석합니다.

    Args:
        file_path: 출력 파일 경로 (절대/상대 경로)

    Returns:
        추출된 주요 데이터 요약(에너지, 원자 수 등).
    """
    try:
        parser_backend: ParserBackend = registry.get("cclib")
        parsed = parser_backend.parse_file(file_path)

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
def compute_partial_charges(xyz_string: str, basis: str = "sto-3g", method: str = "RHF") -> str:
    """
    분자의 기저 상태에 대한 부분 전하(Partial Charges)를 IAO 표상을 사용하여 분할 계산합니다.
    Mulliken/Lowdin 등보다 계산 기저에 훨씬 덜 의존적이고 화학적으로 직관적인 결과를 제공.

    Args:
        xyz_string: 분자의 XYZ 좌표 문자열
        basis: 계산 기저 세트
        method: SCF 분석 방법
        
    Returns:
        각 원자의 부분 전하 목록.
    """
    try:
        backend: OrbitalBackend = registry.get("pyscf")
        scf_result, mol_obj = backend.compute_scf(xyz_string, basis=basis, method=method)
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
    """
    주어진 분자 구조 파일을 다른 형식의 파일로 변환합니다. (예: .xyz -> .cif, .mol -> .xyz 등)
    
    Args:
        input_path: 입력 파일의 경로
        output_path: 저장될 생성 파일 경로 (확장자로 포맷 자동 결정)
        
    Returns:
        변환 결과 상태 및 경로.
    """
    try:
        ase_backend: StructureBackend = registry.get("ase")
        # Ensure path strings
        result_path = ase_backend.convert_format(input_path, output_path)
        return f"파일 변환 성공: {result_path.absolute()}"
    except Exception as e:
        return f"파일 변환 중 오류: {str(e)}"

@mcp.tool()
def analyze_bonding(xyz_string: str) -> str:
    """
    입력 분자의 구조 및 오비탈 데이터를 기반으로 주요 결합 특성을 분석합니다.
    (현재는 PySCF 백엔드의 IBO 결과를 이용하여 공유 결합 패턴에 대한 기본 휴리스틱을 제공.)
    
    Args:
        xyz_string: 분자의 XYZ 좌표 문자열
        
    Returns:
        분할된 IBO 결합 분석 보고서 문자열.
    """
    try:
        # 이 기능은 Phase γ 단계에서 고도화될 예정이므로, 여기서는 stub만 실행.
        backend: OrbitalBackend = registry.get("pyscf")
        scf_result, mol_obj = backend.compute_scf(xyz_string, basis="sto-3g", method="hf")
        iao_result = backend.compute_iao(scf_result, mol_obj)
        ibo_result = backend.compute_ibo(scf_result, iao_result, mol_obj)

        n_ibo = ibo_result.n_ibo
        
        return (
            f"결합 특성 분석 (Stub):\n"
            f"주어진 분자에 대해 총 {n_ibo}개의 최적화된 IBO를 검출함.\n"
            f"이 중 원자간 공유 결합을 이루거나 비공유 전자쌍을 포함하고 있음.\n"
            f"(점유도: {ibo_result.occupations.tolist()})"
        )
    except Exception as e:
        return f"분석 오류 발생: {str(e)}"
