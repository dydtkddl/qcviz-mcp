"""
pytest 공통 픽스처 및 설정 파일.
"""
from __future__ import annotations

import os
from pathlib import Path
import pytest

@pytest.fixture
def sample_water_xyz() -> str:
    """물 분자(H2O)의 XYZ 좌표 형식 문자열을 반환합니다."""
    return """3
Water structure
O          0.00000        0.00000        0.11730
H          0.00000        0.75720       -0.46920
H          0.00000       -0.75720       -0.46920
"""

@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """테스트용 임시 디렉토리를 반환합니다."""
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir
