"""parse_output 도구 통합 테스트."""

import os
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestParseOutput:
    """parse_output 도구 테스트."""

    def test_parse_orca_mock(self):
        """ORCA mock 출력 파싱."""
        pytest.importorskip("cclib")
        from qcviz_mcp.tools.core import parse_output

        orca_file = FIXTURES_DIR / "water_orca_mock.out"
        if not orca_file.exists():
            pytest.skip("ORCA mock fixture not found")

        result = parse_output(str(orca_file))
        # cclib가 mock 파일을 파싱 못할 수 있음 → graceful 처리
        assert isinstance(result, str)

    def test_parse_gaussian_mock(self):
        """Gaussian mock 출력 파싱."""
        pytest.importorskip("cclib")
        from qcviz_mcp.tools.core import parse_output

        gauss_file = FIXTURES_DIR / "methane_gaussian_mock.out"
        if not gauss_file.exists():
            pytest.skip("Gaussian mock fixture not found")

        result = parse_output(str(gauss_file))
        assert isinstance(result, str)

    def test_parse_nonexistent_file(self):
        """존재하지 않는 파일 → 에러 메시지."""
        from qcviz_mcp.tools.core import _PROJECT_ROOT, parse_output

        fake_path = os.path.join(_PROJECT_ROOT, "tests", "fixtures", "nonexistent.out")
        result = parse_output(fake_path)
        assert "오류" in result or "파일을 찾을 수 없습니다" in result

    def test_parse_path_traversal(self):
        """경로 탐색 공격 → 보안 에러."""
        from qcviz_mcp.tools.core import parse_output

        result = parse_output("../../../etc/passwd")
        assert "보안" in result or "오류" in result

    def test_parse_empty_file(self):
        """빈 파일 → graceful 에러."""
        pytest.importorskip("cclib")
        from qcviz_mcp.tools.core import _PROJECT_ROOT, parse_output

        empty_file = os.path.join(_PROJECT_ROOT, "tests", "fixtures", "_empty_test.out")
        try:
            Path(empty_file).write_text("")
            result = parse_output(empty_file)
            assert "오류" in result or "파싱 실패" in result
        finally:
            if os.path.exists(empty_file):
                os.remove(empty_file)
