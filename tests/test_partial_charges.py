# -*- coding: utf-8 -*-
"""compute_partial_charges 도구 테스트."""
import json
import pytest

pyscf = pytest.importorskip("pyscf")

from qcviz_mcp.tools.core import compute_partial_charges


WATER = "O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587"
METHANE = "C 0 0 0; H 0.629 0.629 0.629; H -0.629 -0.629 0.629; H -0.629 0.629 -0.629; H 0.629 -0.629 -0.629"


class TestPartialCharges:
    """부분 전하 계산 테스트."""

    def test_iao_water(self):
        """IAO 기반 물 분자 부분 전하."""
        result = compute_partial_charges(WATER, basis="sto-3g", method="RHF")
        assert "부분 전하" in result
        assert "O:" in result
        # O는 음전하, H는 양전하
        lines = result.strip().split("\n")
        for line in lines:
            if "O:" in line:
                charge_val = float(line.split(":")[1].strip())
                assert charge_val < 0, f"O should be negative, got {charge_val}"
            elif "H:" in line:
                charge_val = float(line.split(":")[1].strip())
                assert charge_val > 0, f"H should be positive, got {charge_val}"

    def test_iao_methane(self):
        """메탄 부분 전하."""
        result = compute_partial_charges(METHANE, basis="sto-3g", method="RHF")
        assert "부분 전하" in result
        assert "C:" in result

    def test_charge_sum_neutral(self):
        """중성 분자 전하 합 ≈ 0."""
        result = compute_partial_charges(WATER, basis="sto-3g")
        lines = result.strip().split("\n")
        total = 0.0
        for line in lines:
            if ":" in line and ("O:" in line or "H:" in line):
                val = float(line.split(":")[1].strip())
                total += val
        assert abs(total) < 1e-3, f"Charge sum = {total}, expected ~0.0"

    def test_error_on_invalid_input(self):
        """잘못된 입력 → 에러 메시지."""
        result = compute_partial_charges("invalid data")
        assert "오류" in result
