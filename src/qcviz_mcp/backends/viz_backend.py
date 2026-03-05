"""py3Dmol 기반 양자화학 3D 분자 및 오비탈 시각화 백엔드 구현."""

from __future__ import annotations

import logging

from qcviz_mcp.backends.base import VisualizationBackend
from qcviz_mcp.backends.registry import registry

try:
    import py3Dmol

    _HAS_PY3DMOL = True
except ImportError:
    _HAS_PY3DMOL = False

logger = logging.getLogger(__name__)


class Py3DmolBackend(VisualizationBackend):
    """py3Dmol을 이용한 상호작용 가능한 3D 시각화 백엔드.

    주로 HTML 문자열을 반환하여 클라이언트 측 렌더링을 지원합니다.
    """

    @classmethod
    def name(cls) -> str:
        return "py3dmol"

    @classmethod
    def is_available(cls) -> bool:
        return _HAS_PY3DMOL

    def render_molecule(self, xyz_data: str, style: str = "stick") -> str:
        if not _HAS_PY3DMOL:
            raise ImportError("py3Dmol이 설치되지 않았습니다.")

        view = py3Dmol.view(width=800, height=600)
        view.addModel(xyz_data, "xyz")

        style_dict = {}
        if style == "stick":
            style_dict = {"stick": {}}
        elif style == "sphere":
            style_dict = {"sphere": {}}
        elif style == "ball_stick":
            style_dict = {"stick": {"radius": 0.15}, "sphere": {"scale": 0.3}}
        else:
            style_dict = {"stick": {}}  # 기본값

        view.setStyle(style_dict)
        view.zoomTo()

        html: str = view._make_html()
        return html

    def render_orbital(
        self,
        xyz_data: str,
        cube_data: str,
        isovalue: float = 0.05,
        colors: tuple[str, str] = ("blue", "red"),
        style: str = "stick",
    ) -> str:
        if not _HAS_PY3DMOL:
            raise ImportError("py3Dmol이 설치되지 않았습니다.")

        view = py3Dmol.view(width=800, height=600)
        view.addModel(xyz_data, "xyz")

        # 분자 스타일 적용
        style_dict = {}
        if style == "stick":
            style_dict = {"stick": {}}
        elif style == "sphere":
            style_dict = {"sphere": {}}
        elif style == "ball_stick":
            style_dict = {"stick": {"radius": 0.15}, "sphere": {"scale": 0.3}}
        else:
            style_dict = {"stick": {}}

        view.setStyle(style_dict)

        # 등치면 렌더링 (양의 등치면 및 음의 등치면)
        view.addVolumetricData(
            cube_data, "cube", {"isoval": isovalue, "color": colors[0], "opacity": 0.8}
        )
        view.addVolumetricData(
            cube_data, "cube", {"isoval": -isovalue, "color": colors[1], "opacity": 0.8}
        )

        view.zoomTo()

        html: str = view._make_html()
        return html

    def render_orbital_from_cube(
        self,
        cube_text: str,
        geometry_xyz: str,
        isovalue: float = 0.05,
        positive_color: str = "blue",
        negative_color: str = "red",
        opacity: float = 0.8,
    ) -> str:
        """Cube 텍스트 + 분자 좌표를 받아 py3Dmol HTML을 반환.

        양/음 isosurface를 동시에 렌더링합니다.

        Args:
            cube_text: Gaussian cube 포맷 문자열.
            geometry_xyz: 분자 좌표 (XYZ 포맷 또는 PySCF 포맷).
            isovalue: 등치면 값.
            positive_color: 양의 등치면 색상.
            negative_color: 음의 등치면 색상.
            opacity: 등치면 투명도.

        Returns:
            str: py3Dmol HTML 렌더링 문자열.

        """
        if not _HAS_PY3DMOL:
            raise ImportError("py3Dmol이 설치되지 않았습니다.")

        view = py3Dmol.view(width=800, height=600)
        view.addModel(geometry_xyz, "xyz")
        view.setStyle({"stick": {"radius": 0.15}, "sphere": {"scale": 0.3}})

        # 양의 등치면
        view.addVolumetricData(
            cube_text,
            "cube",
            {"isoval": isovalue, "color": positive_color, "opacity": opacity},
        )
        # 음의 등치면
        view.addVolumetricData(
            cube_text,
            "cube",
            {"isoval": -isovalue, "color": negative_color, "opacity": opacity},
        )

        view.zoomTo()
        html: str = view._make_html()
        return html


registry.register(Py3DmolBackend)
