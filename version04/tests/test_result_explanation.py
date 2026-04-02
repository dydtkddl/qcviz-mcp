from __future__ import annotations

from qcviz_mcp.web.result_explainer import build_result_explanation, explain_comparison


def test_build_result_explanation_for_orbital_preview():
    result = {
        "job_type": "orbital_preview",
        "structure_name": "water",
        "selected_orbital": {"label": "HOMO", "energy_ev": -8.5},
        "orbital_gap_ev": 6.8,
        "scf_converged": True,
        "n_scf_cycles": 12,
    }
    advisor = {
        "confidence": {
            "data": {
                "overall_score": 0.82,
                "recommendations": ["Consider ESP mapping for complementary interpretation."],
            }
        }
    }
    explanation = build_result_explanation(
        query="water",
        intent_name="orbital",
        result=result,
        advisor=advisor,
    )
    assert explanation["summary"]
    assert any("gap" in item.lower() for item in explanation["key_findings"])
    assert any("ESP" in item or "esp" in item for item in explanation["next_actions"])


def test_build_result_explanation_adds_caution_for_unconverged_result():
    result = {
        "job_type": "single_point",
        "structure_name": "acetone",
        "scf_converged": False,
        "scf_final_delta_e_hartree": -0.01,
    }
    explanation = build_result_explanation(
        query="acetone",
        intent_name="single_point",
        result=result,
        advisor=None,
    )
    assert explanation["summary"]
    assert explanation["cautions"]


def test_explain_comparison_includes_advisor_recommendation():
    explanation = explain_comparison(
        delta={
            "molecule_a": "benzene",
            "molecule_b": "toluene",
            "energy_delta_ev": -0.05,
            "energy_delta_kcal": -1.15,
            "gap_delta_ev": 0.02,
            "both_converged": True,
        },
        result_a={},
        result_b={},
        advisor_data={"summary": "Use def2-TZVP for a tighter comparison."},
    )
    assert explanation["summary"]
    assert explanation["advisor_recommendation"] == "Use def2-TZVP for a tighter comparison."
    assert any("advisor-recommended" in item for item in explanation["next_actions"])
