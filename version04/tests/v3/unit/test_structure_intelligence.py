from __future__ import annotations

import pytest

from qcviz_mcp.errors import ErrorCategory, ModificationError, StructureIntelligenceError
from qcviz_mcp.services import structure_intelligence


def test_structure_intelligence_exports_are_available():
    assert structure_intelligence is not None
    assert hasattr(structure_intelligence, "generate_modification_candidates")
    assert len(structure_intelligence.SUBSTITUENT_SMARTS) == 13


def test_structure_intelligence_error_classes_have_expected_categories():
    modification_error = ModificationError("bad modification")
    backend_error = StructureIntelligenceError("backend unavailable")

    assert modification_error.category == ErrorCategory.VALIDATION
    assert backend_error.category == ErrorCategory.BACKEND


def test_structure_intelligence_graceful_without_rdkit():
    if structure_intelligence._RDKIT_AVAILABLE:
        candidates = structure_intelligence.generate_modification_candidates(
            "c1ccccc1", "hydrogen", "methyl"
        )
        assert isinstance(candidates, list)
        return

    assert structure_intelligence.identify_substituents("c1ccccc1") == []
    assert structure_intelligence.swap_substituent("c1ccccc1", 0, "methyl") is None
    assert (
        structure_intelligence.generate_modification_candidates(
            "c1ccccc1", "hydrogen", "methyl"
        )
        == []
    )
    assert structure_intelligence.preview_property_delta("c1ccccc1", "Cc1ccccc1") == {
        "mw_delta": 0.0,
        "logp_delta": 0.0,
        "tpsa_delta": 0.0,
    }


def test_structure_intelligence_rdkit_functional_path():
    if not structure_intelligence._RDKIT_AVAILABLE:
        pytest.fail("RDKit is required for functional structure_intelligence assertions.")

    candidates = structure_intelligence.generate_modification_candidates(
        "c1ccccc1", "hydrogen", "methyl"
    )

    assert candidates
    assert candidates[0]["to_group"] == "methyl"
    assert "candidate_smiles" in candidates[0]
    assert candidates[0]["property_delta"]["mw_delta"] > 0

    delta = structure_intelligence.preview_property_delta("c1ccccc1", "Cc1ccccc1")
    assert abs(delta["mw_delta"] - 14.0) < 1.0
