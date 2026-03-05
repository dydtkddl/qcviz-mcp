#!/usr/bin/env python3
"""전체 벤치마크 실행 스크립트.

사용법:
    python -m benchmark.run_benchmark

출력:
    - 콘솔: 분자별 결과 테이블
    - benchmark/results/summary.json: 전체 결과
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

from benchmark.molecules import MOLECULES
from qcviz_mcp.backends.pyscf_backend import PySCFBackend

RESULTS_DIR = Path(__file__).parent / "results"


def main() -> int:
    backend = PySCFBackend()
    results = []
    passed = 0
    failed = 0

    header = (
        f"{'Molecule':<20} {'Basis':<8} {'E(Hartree)':<14} "
        f"{'n_IBO(exp/act)':<17} {'Σ charge':<12} {'Time':<8}"
    )
    print("=" * len(header))
    print(header)
    print("=" * len(header))

    for mol in MOLECULES:
        t0 = time.time()
        try:
            scf_res, mol_obj = backend.compute_scf(
                mol.atom_spec, basis=mol.basis, method="HF"
            )
            iao_res = backend.compute_iao(scf_res, mol_obj)
            ibo_res = backend.compute_ibo(scf_res, iao_res, mol_obj)

            elapsed = time.time() - t0
            charge_sum = float(np.sum(iao_res.charges))
            ibo_match = ibo_res.n_ibo == mol.expected_n_ibo
            mark = "✅" if ibo_match else "❌"

            if ibo_match and abs(charge_sum) < 1e-4:
                passed += 1
            else:
                failed += 1

            print(
                f"{mol.name:<20} {mol.basis:<8} {scf_res.energy_hartree:<14.6f} "
                f"{mol.expected_n_ibo:>3} / {ibo_res.n_ibo:<3} {mark}    "
                f"{charge_sum:<12.6f} {elapsed:.1f}s"
            )

            results.append({
                "name": mol.name,
                "basis": mol.basis,
                "energy_hartree": round(scf_res.energy_hartree, 6),
                "expected_n_ibo": mol.expected_n_ibo,
                "actual_n_ibo": ibo_res.n_ibo,
                "ibo_match": ibo_match,
                "charge_sum": round(charge_sum, 6),
                "elapsed_s": round(elapsed, 2),
                "status": "pass" if (ibo_match and abs(charge_sum) < 1e-4) else "fail",
            })

        except Exception as e:
            elapsed = time.time() - t0
            failed += 1
            print(f"{mol.name:<20} ERROR: {e}")
            results.append({
                "name": mol.name,
                "status": "error",
                "error": str(e),
                "elapsed_s": round(elapsed, 2),
            })

    print("=" * len(header))
    print(f"Total: {len(MOLECULES)} molecules, {passed} passed, {failed} failed")

    # 결과 저장
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = RESULTS_DIR / "summary.json"
    summary_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"Results saved to {summary_path}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
