"""Tests for advisor-to-runner preset application."""

from qcviz_mcp.web import advisor_flow
from qcviz_mcp.web.advisor_flow import (
    apply_preset_to_runner_kwargs,
    prepare_advisor_plan_from_geometry,
)


def test_apply_preset_uses_clean_runner_method():
    prepared = {"_method_user_supplied": False, "_basis_user_supplied": False}
    advisor_plan = {
        "applied_functional": "UM06-2X-D3(0)",
        "applied_basis": "def2-TZVP",
        "preset": {
            "status": "success",
            "data": {
                "pyscf_settings": {"xc": "m062x"},
            },
        },
    }
    merged = apply_preset_to_runner_kwargs(prepared, advisor_plan)
    assert merged["method"] == "M06-2X"
    assert merged["basis"] == "def2-TZVP"


def test_apply_preset_does_not_override_user_method():
    prepared = {
        "method": "PBE0",
        "_method_user_supplied": True,
        "_basis_user_supplied": False,
    }
    advisor_plan = {
        "applied_functional": "B3LYP-D3(BJ)",
        "applied_basis": "def2-SVP",
        "preset": {
            "status": "success",
            "data": {
                "pyscf_settings": {"xc": "b3lyp"},
            },
        },
    }
    merged = apply_preset_to_runner_kwargs(prepared, advisor_plan)
    assert merged["method"] == "PBE0"
    assert merged["basis"] == "def2-SVP"


def test_prepare_advisor_plan_from_geometry_includes_modification_context(monkeypatch):
    monkeypatch.setattr(
        advisor_flow,
        "_call_tool_candidates",
        lambda *_args, **_kwargs: {
            "status": "success",
            "data": {"functional": "B3LYP", "basis": "def2-SVP"},
        },
        raising=True,
    )
    plan = prepare_advisor_plan_from_geometry(
        intent_name="single_point",
        xyz_text="1\nH\nH 0.0 0.0 0.0",
        modification_context={
            "base_molecule": "benzene",
            "modified_molecule": "toluene",
            "from_group": "hydrogen",
            "to_group": "methyl",
        },
    )
    assert plan["modification"]["base_molecule"] == "benzene"
    assert plan["modification"]["relationship"] == "substituent_swap"
    assert plan["system_type"] == "organic_modified"


def test_prepare_advisor_plan_from_geometry_includes_comparison_context(monkeypatch):
    monkeypatch.setattr(
        advisor_flow,
        "_call_tool_candidates",
        lambda *_args, **_kwargs: {
            "status": "success",
            "data": {"functional": "B3LYP", "basis": "def2-SVP"},
        },
        raising=True,
    )
    plan = prepare_advisor_plan_from_geometry(
        intent_name="single_point",
        xyz_text="1\nH\nH 0.0 0.0 0.0",
        comparison_context={
            "mol_a": "benzene",
            "mol_b": "toluene",
            "delta": {"energy_delta_ev": -0.05, "gap_delta_ev": 0.02},
        },
    )
    assert plan["comparison"]["mol_a"] == "benzene"
    assert plan["comparison"]["mol_b"] == "toluene"
    assert plan["comparison"]["delta_energy"] == -0.05
    assert plan["comparison"]["delta_gap"] == 0.02
