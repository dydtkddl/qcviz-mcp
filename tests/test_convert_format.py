"""convert_format 도구 통합 테스트."""

import os
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"

ase = pytest.importorskip("ase")


class TestConvertFormat:
    """convert_format 도구 테스트."""

    def _project_path(self, *parts):
        from qcviz_mcp.tools.core import _PROJECT_ROOT

        return os.path.join(_PROJECT_ROOT, *parts)

    def test_xyz_to_cif(self, tmp_path):
        """water.xyz → .cif 변환."""
        from qcviz_mcp.tools.core import convert_format

        input_xyz = str(FIXTURES_DIR / "water.xyz")
        # 출력을 프로젝트 내부에 생성
        out_dir = self._project_path("tests", "fixtures", "_tmp_fmt")
        os.makedirs(out_dir, exist_ok=True)
        out_cif = os.path.join(out_dir, "water.cif")

        try:
            result = convert_format(input_xyz, out_cif)
            assert "성공" in result
            assert os.path.exists(out_cif)
        finally:
            import shutil

            shutil.rmtree(out_dir, ignore_errors=True)

    def test_xyz_to_extxyz(self):
        """water.xyz → .extxyz 변환."""
        from qcviz_mcp.tools.core import convert_format

        input_xyz = str(FIXTURES_DIR / "water.xyz")
        out_dir = self._project_path("tests", "fixtures", "_tmp_fmt2")
        os.makedirs(out_dir, exist_ok=True)
        out_extxyz = os.path.join(out_dir, "water.extxyz")

        try:
            result = convert_format(input_xyz, out_extxyz)
            assert "성공" in result
        finally:
            import shutil

            shutil.rmtree(out_dir, ignore_errors=True)

    def test_invalid_input_path(self):
        """존재하지 않는 입력 파일."""
        from qcviz_mcp.tools.core import convert_format

        fake_in = self._project_path("tests", "fixtures", "nonexistent.xyz")
        fake_out = self._project_path("tests", "fixtures", "out.cif")
        result = convert_format(fake_in, fake_out)
        assert "오류" in result

    def test_path_traversal_output(self):
        """출력 경로 탐색 공격 차단."""
        from qcviz_mcp.tools.core import convert_format

        result = convert_format(str(FIXTURES_DIR / "water.xyz"), "../../etc/passwd")
        assert "보안" in result or "오류" in result
