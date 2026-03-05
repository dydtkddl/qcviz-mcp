"""MCP 서버 시작 및 도구 목록 반환 테스트."""

import pytest


def test_server_imports():
    """서버 모듈이 에러 없이 import되는지 확인."""
    from qcviz_mcp.mcp_server import mcp

    assert mcp is not None
    assert mcp.name == "QCViz-MCP"


def test_server_has_tools():
    """tools/core.py가 import되고 6개 함수가 존재하는지 확인."""
    from qcviz_mcp.tools import core

    tool_names = [
        "compute_ibo",
        "visualize_orbital",
        "parse_output",
        "compute_partial_charges",
        "convert_format",
        "analyze_bonding",
    ]
    for name in tool_names:
        assert hasattr(core, name), f"Missing tool: {name}"


@pytest.mark.asyncio
async def test_server_list_tools():
    """FastMCP Client로 도구 목록 6개를 확인."""
    from fastmcp import Client

    from qcviz_mcp.mcp_server import mcp

    async with Client(mcp) as client:
        tools = await client.list_tools()
        tool_names = [t.name for t in tools]
        assert len(tool_names) >= 6
        assert "compute_ibo" in tool_names
        assert "visualize_orbital" in tool_names
        assert "parse_output" in tool_names
        assert "compute_partial_charges" in tool_names
        assert "convert_format" in tool_names
        assert "analyze_bonding" in tool_names


@pytest.mark.asyncio
async def test_server_call_compute_ibo():
    """compute_ibo 도구를 MCP 프로토콜로 호출하는 통합 테스트."""
    pytest.importorskip("pyscf")
    from fastmcp import Client

    from qcviz_mcp.mcp_server import mcp

    async with Client(mcp) as client:
        result = await client.call_tool(
            "compute_ibo",
            {
                "xyz_string": "O 0 0 0; H 0 0 0.96; H 0 0.96 0",
                "basis": "sto-3g",
            },
        )
        # FastMCP 3.x: result는 list of content blocks
        assert result is not None
        text = str(result)
        assert "success" in text or "IBO" in text
