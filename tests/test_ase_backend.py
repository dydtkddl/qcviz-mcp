"""ase_backend 모듈 테스트."""

import pytest

pytest.importorskip("ase")

from qcviz_mcp.backends.registry import registry


@pytest.fixture
def ase_backend():
    return registry.get("ase")


def test_ase_read_write(ase_backend, sample_water_xyz, tmp_output_dir):
    # Create an xyz file to test
    xyz_path = tmp_output_dir / "water.xyz"
    with open(xyz_path, "w") as f:
        f.write(sample_water_xyz)

    # Read it
    atoms_data = ase_backend.read_structure(xyz_path)
    assert len(atoms_data.symbols) == 3
    assert atoms_data.symbols == ["O", "H", "H"]

    # Write it back as xyz to a different file
    out_path = tmp_output_dir / "water_out.xyz"
    result_path = ase_backend.write_structure(atoms_data, out_path, format="xyz")
    assert result_path.exists()

    # Convert directly via backend
    cif_path = tmp_output_dir / "water.cif"
    result_cif = ase_backend.convert_format(xyz_path, cif_path)
    assert result_cif.exists()


def test_ase_convert_xyz_to_cif_roundtrip(
    ase_backend, sample_water_xyz, tmp_output_dir
):
    """Xyz → cif → xyz 왕복 변환 테스트."""
    xyz_path = tmp_output_dir / "roundtrip.xyz"
    xyz_path.write_text(sample_water_xyz)

    cif_path = tmp_output_dir / "roundtrip.cif"
    ase_backend.convert_format(xyz_path, cif_path)

    xyz_back = tmp_output_dir / "roundtrip_back.xyz"
    ase_backend.convert_format(cif_path, xyz_back)
    assert xyz_back.exists()

    atoms = ase_backend.read_structure(xyz_back)
    assert len(atoms.symbols) == 3


def test_ase_read_non_existent(ase_backend):
    """존재하지 않는 파일 읽기 시 에러."""
    with pytest.raises(Exception):
        ase_backend.read_structure("/tmp/nonexistent_file_xyz_12345.xyz")
