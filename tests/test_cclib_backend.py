"""
cclib_backend 모듈 단위 테스트.
"""
import pytest
from pathlib import Path

pytest.importorskip("cclib")

from qcviz_mcp.backends.registry import registry

@pytest.fixture
def cclib_backend():
    return registry.get("cclib")

def test_cclib_supported_programs(cclib_backend):
    programs = cclib_backend.supported_programs()
    assert isinstance(programs, list)
    assert "Gaussian" in programs
    assert "ORCA" in programs

def test_parse_invalid_file(cclib_backend, tmp_output_dir):
    invalid_file = tmp_output_dir / "invalid.out"
    invalid_file.write_text("This is not a valid QC output file.\n")
    
    with pytest.raises(ValueError, match="파싱 실패:"):
        cclib_backend.parse_file(invalid_file)

# 실제 출력 파일이 없는 환경에서의 동작 위주로 테스트.
# 실제 파싱 엔진 테스트용 dummy log 생성은 복잡하므로 CI 상에서는 생략.
