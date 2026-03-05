from __future__ import annotations

import pytest
import tempfile
from pathlib import Path


# ── Phase η markers ──
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "network: marks tests requiring network access")
    config.addinivalue_line("markers", "pyvista: marks tests requiring PyVista")


# ── Shared fixtures ──
@pytest.fixture
def sample_water_xyz() -> str:
    """Water molecule XYZ string."""
    return """3
water
O   0.000000   0.000000   0.117300
H   0.000000   0.757200   -0.469200
H   0.000000  -0.757200   -0.469200
"""


@pytest.fixture
def tmp_output_dir() -> Path:
    """Create a temporary directory for test outputs."""
    d = Path(tempfile.gettempdir()) / "qcviz_test_output"
    d.mkdir(parents=True, exist_ok=True)
    return d
