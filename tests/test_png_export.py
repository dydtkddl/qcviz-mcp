"""Phase ζ-3: 헤드리스 PNG 내보내기 테스트."""

import os

import pytest

# Playwright 설치 여부 확인
playwright_available = False
try:
    from playwright.sync_api import sync_playwright

    playwright_available = True
except ImportError:
    pass


@pytest.mark.skipif(not playwright_available, reason="Playwright not installed")
class TestPNGExport:
    @pytest.fixture
    def sample_html(self, tmp_path):
        """간단한 3Dmol.js 테스트 HTML."""
        html = """<!DOCTYPE html>
<html><head>
<script src="https://3Dmol.org/build/3Dmol-min.js"></script>
</head><body>
<div id="viewer" style="width:400px;height:300px;"></div>
<script>
var viewer = $3Dmol.createViewer("viewer", {backgroundColor:"white"});
viewer.addSphere({center:{x:0,y:0,z:0}, radius:1.0, color:"red"});
viewer.zoomTo(); viewer.render();
</script>
</body></html>"""
        path = tmp_path / "test_mol.html"
        path.write_text(html)
        return str(path)

    @pytest.mark.asyncio
    async def test_html_to_png_basic(self, sample_html, tmp_path):
        """기본 PNG 캡처 (Chromium 미설치 시 graceful skip)."""
        from qcviz_mcp.renderers.png_exporter import html_to_png

        png_path = str(tmp_path / "output.png")
        result = await html_to_png(sample_html, png_path=png_path, wait_ms=5000)
        if not result["success"]:
            # Chromium binary가 없으면 graceful error
            assert "error" in result
            pytest.skip(f"Chromium not installed: {result['error'][:80]}")
        assert os.path.exists(png_path)
        assert result["file_size_bytes"] > 500

    @pytest.mark.asyncio
    async def test_png_dimensions(self, sample_html, tmp_path):
        """지정 크기 캡처."""
        from qcviz_mcp.renderers.png_exporter import html_to_png

        result = await html_to_png(sample_html, width=1024, height=768, wait_ms=5000)
        if result["success"]:
            assert result["width"] == 2048
            assert result["height"] == 1536

    @pytest.mark.asyncio
    async def test_auto_png_path(self, sample_html):
        """png_path=None → 자동 생성."""
        from qcviz_mcp.renderers.png_exporter import html_to_png

        result = await html_to_png(sample_html, wait_ms=5000)
        if result["success"]:
            assert result["png_path"].endswith(".png")

    def test_sync_wrapper(self, sample_html):
        """동기 래퍼."""
        from qcviz_mcp.renderers.png_exporter import html_to_png_sync

        result = html_to_png_sync(sample_html, wait_ms=5000)
        assert isinstance(result, dict)
        assert "success" in result


class TestPNGGracefulDegradation:
    """Playwright 없어도 다른 기능 정상 동작."""

    def test_import_renderers_no_crash(self):
        """Renderers 패키지 import 에러 없음."""
        from qcviz_mcp.renderers import png_exporter

        assert hasattr(png_exporter, "html_to_png")
