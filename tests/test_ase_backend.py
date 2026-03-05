"""
ase_backend 모듈 테스트.
"""
import pytest
import os
from pathlib import Path

pytest.importorskip("ase")

from qcviz_mcp.backends.registry import registry
from qcviz_mcp.backends.base import AtomsData

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
    assert atoms_data.symbols == ['O', 'H', 'H']
    
    # Write it back as xyz to a different file
    out_path = tmp_output_dir / "water_out.xyz"
    result_path = ase_backend.write_structure(atoms_data, out_path, format="xyz")
    assert result_path.exists()
    
    # Convert directly via backend
    cif_path = tmp_output_dir / "water.cif"
    result_cif = ase_backend.convert_format(xyz_path, cif_path)
    assert result_cif.exists()
