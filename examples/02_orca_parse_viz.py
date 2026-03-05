#!/usr/bin/env python3
"""QCViz-MCP 예제 2: 출력 파일 파싱 + 분자 구조 시각화.

실행:
    python examples/02_orca_parse_viz.py

출력:
    - 콘솔: 파싱 결과 요약
    - 파일: examples/output/molecule_viz.html (분자 구조 시각화)

Note:
    실제 ORCA/Gaussian 출력 파일 없이도 동작하도록
    cclib 파싱은 데모 목적으로 시뮬레이션하고,
    ASE 파일 변환 + py3Dmol 시각화는 실제 동작합니다.
"""
from __future__ import annotations

import sys
from pathlib import Path

from qcviz_mcp.backends.registry import registry

ETHANOL_XYZ = """9
Ethanol
C         -0.74830        0.00000        0.00000
C          0.74830        0.00000        0.00000
O          1.24830        1.20000        0.00000
H         -1.10830       -0.54000        0.88000
H         -1.10830       -0.54000       -0.88000
H         -1.10830        1.08000        0.00000
H          1.10830       -0.54000        0.88000
H          1.10830       -0.54000       -0.88000
H          1.89830        1.20000        0.73000
"""

OUTPUT_DIR = Path(__file__).parent / "output"


def main() -> int:
    print("=" * 60)
    print("  QCViz-MCP 예제 2: 분자 구조 시각화 + 포맷 변환")
    print("=" * 60)

    # ── 1. ASE 백엔드로 XYZ 파싱 ──
    print("\n[1/3] ASE 백엔드로 에탄올 구조 파싱 중...")
    ase_backend = registry.get("ase")

    # 임시 XYZ 파일 생성 후 읽기
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".xyz", mode="w", delete=False) as f:
        f.write(ETHANOL_XYZ)
        xyz_path = f.name

    try:
        atoms_data = ase_backend.read_structure(xyz_path)
        print(f"  ✓ 원자 수: {len(atoms_data.symbols)}")
        print(f"  ✓ 원소: {', '.join(set(atoms_data.symbols))}")

        # 포맷 변환 데모: XYZ → CIF (examples/output/)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cif_path = OUTPUT_DIR / "ethanol.cif"
        ase_backend.convert_format(xyz_path, str(cif_path))
        print(f"  ✓ CIF 변환 완료: {cif_path}")
    finally:
        import os
        os.remove(xyz_path)

    # ── 2. cclib 지원 프로그램 목록 ──
    print("\n[2/3] cclib 지원 프로그램 목록:")
    cclib_backend = registry.get("cclib")
    programs = cclib_backend.supported_programs()
    print(f"  {', '.join(programs[:8])}...")
    print(f"  (총 {len(programs)}개 프로그램 지원)")

    # ── 3. py3Dmol로 분자 구조 시각화 ──
    print("\n[3/3] py3Dmol 분자 구조 시각화 생성 중...")
    viz_backend = registry.get("py3dmol")
    html = viz_backend.render_molecule(ETHANOL_XYZ, style="ball_stick")

    output_path = OUTPUT_DIR / "molecule_viz.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"  ✓ 저장 완료: {output_path} ({len(html):,} bytes)")

    # ── 요약 ──
    print("\n" + "=" * 60)
    print("  요약")
    print("=" * 60)
    print(f"  시각화:  {output_path.absolute()}")
    print(f"  CIF:     {cif_path.absolute()}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
