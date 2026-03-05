# -*- coding: utf-8 -*-
"""보안 테스트: 경로 검증 및 입력 크기 제한."""
import pytest
from qcviz_mcp.tools.core import _validate_file_path, _validate_atom_spec


def test_path_traversal_blocked():
    """경로 탐색 공격이 차단되는지 확인."""
    with pytest.raises(ValueError, match="보안"):
        _validate_file_path("../../../etc/passwd")


def test_path_traversal_windows_blocked():
    """Windows 스타일 경로 탐색 공격."""
    with pytest.raises((ValueError, FileNotFoundError)):
        _validate_file_path("C:\\Windows\\System32\\config\\sam")


def test_nonexistent_file_raises():
    """프로젝트 외부 경로는 ValueError로 차단."""
    with pytest.raises(ValueError, match="보안"):
        _validate_file_path("/tmp/nonexistent_qcviz_test_file.xyz")


def test_atom_count_limit():
    """201개 원자 입력 시 ValueError."""
    huge_spec = "; ".join(f"H 0 0 {i}" for i in range(201))
    with pytest.raises(ValueError, match="초과"):
        _validate_atom_spec(huge_spec, max_atoms=200)


def test_atom_count_xyz_format_limit():
    """XYZ 포맷에서 원자 수 제한."""
    lines = ["201", "too many atoms"]
    lines.extend(f"H 0.0 0.0 {i:.1f}" for i in range(201))
    xyz = "\n".join(lines)
    with pytest.raises(ValueError, match="초과"):
        _validate_atom_spec(xyz, max_atoms=200)


def test_atom_count_normal():
    """정상 크기 입력은 통과."""
    spec = "O 0 0 0; H 0 0 1; H 0 1 0"
    result = _validate_atom_spec(spec, max_atoms=200)
    assert result == spec
