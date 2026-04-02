"""Rendering utilities and renderer auto-detection."""

from __future__ import annotations

from typing import Any, Callable


def get_best_renderer() -> str:
    try:
        import pyvista  # noqa: F401

        return "pyvista"
    except ImportError:
        pass
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401

        return "playwright"
    except ImportError:
        pass
    return "html_only"


def _pyvista_unavailable() -> bool:
    return False


HAS_PYVISTA = False
pyvista_available: Callable[[], bool] = _pyvista_unavailable
render_from_cube_string: Any = None
render_orbital_png: Any = None

try:
    from qcviz_mcp.renderers.pyvista_renderer import (
        is_available as pyvista_available,
        render_from_cube_string,
        render_orbital_png,
    )

    HAS_PYVISTA = pyvista_available()
except ImportError:
    pass


__all__ = [
    "HAS_PYVISTA",
    "get_best_renderer",
    "pyvista_available",
    "render_from_cube_string",
    "render_orbital_png",
]
