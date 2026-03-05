"""
통합 테스트: MCP 도구 및 FastMCP 서버 연결 기능 확인
"""
import json
import pytest
from qcviz_mcp.mcp_server import mcp
from qcviz_mcp.tools import core

def test_mcp_tools_registered():
    """서버 모듈에 도구들이 정상적으로 정의되었는지 확인합니다."""
    assert hasattr(core, "compute_ibo")
    assert hasattr(core, "visualize_orbital")
    assert hasattr(core, "parse_output")
    assert hasattr(core, "compute_partial_charges")
    assert hasattr(core, "convert_format")
    assert hasattr(core, "analyze_bonding")

def test_compute_ibo_tool(sample_water_xyz):
    """compute_ibo가 JSON dict를 반환하고 핵심 필드를 포함하는지 확인."""
    pytest.importorskip("pyscf")

    result_str = core.compute_ibo(sample_water_xyz, basis="sto-3g", method="hf")
    result = json.loads(result_str)
    assert result["status"] == "success"
    assert result["n_ibo"] == 5
    assert result["energy_hartree"] < -74.0
    assert "IBO 계산 완료" in result["message"]

def test_compute_ibo_with_visualization(sample_water_xyz):
    """E2E: compute_ibo → cube → HTML 전체 파이프라인."""
    pytest.importorskip("pyscf")
    pytest.importorskip("py3Dmol")

    result_str = core.compute_ibo(sample_water_xyz, basis="sto-3g", method="hf")
    result = json.loads(result_str)
    assert result["status"] == "success"
    assert result["visualization_html"] is not None
    assert "3Dmol" in result["visualization_html"]
    assert "시각화 포함" in result["message"]

def test_visualize_orbital_tool(sample_water_xyz):
    pytest.importorskip("py3Dmol")

    result = core.visualize_orbital(sample_water_xyz)
    assert "성공적으로 오비탈 렌더링 HTML 생성 완료" in result
    assert "<div" in result or "3Dmol" in result

def test_compute_partial_charges_tool(sample_water_xyz):
    """compute_partial_charges 도구 호출 테스트."""
    pytest.importorskip("pyscf")

    result = core.compute_partial_charges(sample_water_xyz, basis="sto-3g")
    assert "부분 전하" in result
    assert "O:" in result

def test_convert_format_tool(sample_water_xyz, tmp_output_dir):
    """convert_format 도구 호출 테스트."""
    pytest.importorskip("ase")

    xyz_path = tmp_output_dir / "tool_convert.xyz"
    xyz_path.write_text(sample_water_xyz)
    cif_path = tmp_output_dir / "tool_convert.cif"

    result = core.convert_format(str(xyz_path), str(cif_path))
    assert "성공" in result

def test_analyze_bonding_tool(sample_water_xyz):
    """analyze_bonding 도구 호출 테스트."""
    pytest.importorskip("pyscf")

    result = core.analyze_bonding(sample_water_xyz)
    assert "IBO" in result
    assert "5" in result  # 물 분자의 IBO 개수

def test_compute_ibo_error_handling():
    """잘못된 입력에 대한 에러 처리 확인."""
    result_str = core.compute_ibo("invalid xyz data")
    result = json.loads(result_str)
    assert result["status"] == "error"
    assert "error" in result
