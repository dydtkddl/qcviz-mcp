#!/usr/bin/env python3
"""QCViz-MCP 예제 1: 물 분자 IBO 계산 + 시각화.

실행:
    python examples/01_water_ibo.py

출력:
    - 콘솔: SCF 에너지, IBO 수, IAO 부분 전하
    - 파일: examples/output/water_ibo_0.html (첫 번째 IBO 시각화)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# 백엔드 직접 사용 (MCP 서버 없이)
from qcviz_mcp.backends.registry import registry

WATER_XYZ = """3
Water molecule
O          0.00000        0.00000        0.11730
H          0.00000        0.75720       -0.46920
H          0.00000       -0.75720       -0.46920
"""

OUTPUT_DIR = Path(__file__).parent / "output"


def main() -> int:
    print("=" * 60)
    print("  QCViz-MCP 예제 1: 물 분자 IBO 분석")
    print("=" * 60)

    # ── 1. SCF 계산 ──
    backend = registry.get("pyscf")
    print("\n[1/5] SCF 계산 중 (HF/STO-3G)...")
    scf_result, mol = backend.compute_scf(WATER_XYZ, basis="sto-3g", method="hf")
    print(f"  ✓ 수렴 완료. 총 에너지: {scf_result.energy_hartree:.6f} Hartree")

    # ── 2. IAO 부분 전하 ──
    print("\n[2/5] IAO 부분 전하 계산 중...")
    iao_result = backend.compute_iao(scf_result, mol)
    for i in range(mol.natm):
        sym = mol.atom_symbol(i)
        chg = iao_result.charges[i]
        print(f"  {sym}: {chg:+.4f}")
    print(f"  합계: {sum(iao_result.charges):.6f} (0에 가까워야 함)")

    # ── 3. IBO 계산 ──
    print("\n[3/5] IBO 계산 중 (Pipek-Mezey)...")
    ibo_result = backend.compute_ibo(scf_result, iao_result, mol)
    print(f"  ✓ {ibo_result.n_ibo}개 IBO 생성")

    # ── 4. Cube 파일 생성 ──
    print("\n[4/5] 첫 번째 IBO의 cube 데이터 생성 중 (40x40x40 grid)...")
    cube_text = backend.generate_cube(
        mol, ibo_result.coefficients, orbital_index=0,
        grid_points=(40, 40, 40),
    )
    print(f"  ✓ Cube 데이터 생성 완료 ({len(cube_text):,} bytes)")

    # ── 5. HTML 시각화 ──
    print("\n[5/5] py3Dmol HTML 렌더링 중...")
    viz_backend = registry.get("py3dmol")
    html = viz_backend.render_orbital_from_cube(
        cube_text=cube_text,
        geometry_xyz=WATER_XYZ,
        isovalue=0.05,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "water_ibo_0.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"  ✓ 저장 완료: {output_path} ({len(html):,} bytes)")

    # ── 요약 ──
    print("\n" + "=" * 60)
    print("  요약")
    print("=" * 60)
    print(f"  에너지:     {scf_result.energy_hartree:.6f} Hartree")
    print(f"  IBO 개수:   {ibo_result.n_ibo}")
    print(f"  시각화:     {output_path.absolute()}")
    print(f"  (브라우저에서 열면 3D 오비탈 등치면 확인 가능)")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
