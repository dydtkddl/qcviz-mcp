from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

from qcviz_mcp.llm.schemas import ResultExplanation


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _safe_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def _confidence_score(advisor: Optional[Mapping[str, Any]]) -> Optional[float]:
    payload = dict(advisor or {})
    confidence = payload.get("confidence") or {}
    data = confidence.get("data") if isinstance(confidence, dict) else None
    if not isinstance(data, Mapping):
        return None
    return _safe_float(
        data.get("overall_score")
        or data.get("score")
        or data.get("confidence")
        or data.get("final_score")
    )


def _confidence_recommendations(advisor: Optional[Mapping[str, Any]]) -> List[str]:
    payload = dict(advisor or {})
    confidence = payload.get("confidence") or {}
    data = confidence.get("data") if isinstance(confidence, dict) else None
    if not isinstance(data, Mapping):
        return []
    recommendations = data.get("recommendations") or []
    if not isinstance(recommendations, list):
        return []
    return [str(item).strip() for item in recommendations if str(item).strip()]


def _top_charge_atoms(result: Mapping[str, Any]) -> Dict[str, Optional[Mapping[str, Any]]]:
    charges = result.get("partial_charges") or result.get("mulliken_charges") or []
    if not isinstance(charges, list) or not charges:
        return {"most_negative": None, "most_positive": None}
    ranked = [
        item
        for item in charges
        if isinstance(item, Mapping) and _safe_float(item.get("charge")) is not None
    ]
    if not ranked:
        return {"most_negative": None, "most_positive": None}
    return {
        "most_negative": min(ranked, key=lambda item: float(item.get("charge"))),
        "most_positive": max(ranked, key=lambda item: float(item.get("charge"))),
    }


def build_result_explanation(
    *,
    query: str,
    intent_name: str,
    result: Mapping[str, Any],
    advisor: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    job_type = _safe_str(result.get("job_type") or intent_name or "analyze")
    structure = _safe_str(
        result.get("structure_name") or result.get("structure_query") or query or "molecule"
    )
    explanation = ResultExplanation()

    total_energy_ev = _safe_float(result.get("total_energy_ev"))
    gap_ev = _safe_float(result.get("orbital_gap_ev"))
    converged = bool(result.get("scf_converged"))
    n_cycles = result.get("n_scf_cycles")
    confidence_score = _confidence_score(advisor)

    if job_type == "orbital_preview":
        explanation.summary = (
            f"Orbital analysis for {structure} is complete. "
            "You can review frontier-orbital energies and the HOMO-LUMO gap."
        )
        selected = result.get("selected_orbital") or {}
        if _safe_str(selected.get("label")):
            explanation.key_findings.append(
                f"Selected orbital: {_safe_str(selected.get('label'))} "
                f"({_safe_float(selected.get('energy_ev'), 0.0):.4f} eV)."
            )
        if gap_ev is not None:
            explanation.key_findings.append(f"HOMO-LUMO gap: {gap_ev:.4f} eV.")
            if gap_ev < 3.0:
                explanation.interpretation.append(
                    "A relatively small gap can indicate easier electronic excitation."
                )
            elif gap_ev > 6.0:
                explanation.interpretation.append(
                    "A relatively large gap can indicate increased electronic stability."
                )
        explanation.next_actions.extend([
            "Compare nearby occupied/unoccupied orbitals to check orbital-distribution changes.",
            "Run ESP mapping next to localize likely reactive regions.",
        ])
    elif job_type == "esp_map":
        explanation.summary = (
            f"ESP analysis for {structure} is complete. "
            "The potential map can be used to inspect electrophilic and nucleophilic regions."
        )
        range_kcal = _safe_float(result.get("esp_auto_range_kcal"))
        if range_kcal is not None:
            explanation.key_findings.append(f"ESP display range: +/-{range_kcal:.2f} kcal/mol.")
        explanation.interpretation.append(
            "Potential extrema often indicate regions of strong intermolecular interaction."
        )
        explanation.next_actions.extend([
            "Cross-check with partial-charge analysis for atom-level consistency.",
            "Repeat ESP from optimized geometry for a cleaner comparison.",
        ])
    elif job_type == "partial_charges":
        explanation.summary = (
            f"Partial-charge analysis for {structure} is complete. "
            "Charge distribution trends are available for reactive-site discussion."
        )
        charge_summary = _top_charge_atoms(result)
        most_negative = charge_summary["most_negative"]
        most_positive = charge_summary["most_positive"]
        if most_negative:
            explanation.key_findings.append(
                f"Most negative atom: {_safe_str(most_negative.get('symbol'))} "
                f"({float(most_negative.get('charge')):.4f})."
            )
        if most_positive:
            explanation.key_findings.append(
                f"Most positive atom: {_safe_str(most_positive.get('symbol'))} "
                f"({float(most_positive.get('charge')):.4f})."
            )
        explanation.interpretation.append(
            "Charge distribution helps explain polarity and preferred interaction sites."
        )
        explanation.next_actions.extend([
            "Overlay ESP to inspect spatial correspondence with partial charges.",
            "Re-run after geometry optimization to compare structural sensitivity.",
        ])
    elif job_type == "geometry_optimization":
        explanation.summary = (
            f"Geometry optimization for {structure} is complete. "
            "Optimized coordinates are ready for downstream single-point or property analysis."
        )
        explanation.interpretation.append(
            "Optimized structures are usually the safest starting point for follow-up calculations."
        )
        explanation.next_actions.extend([
            "Run single-point, orbital, or ESP calculations on the optimized structure.",
            "If needed, compare with a larger basis set to test method sensitivity.",
        ])
    elif job_type == "geometry_analysis":
        explanation.summary = (
            f"Geometry analysis for {structure} is complete. "
            "Bond lengths/angles can now be reviewed for structural trends."
        )
        explanation.interpretation.append(
            "Geometry summaries are useful baselines for optimization and literature comparison."
        )
        explanation.next_actions.extend([
            "Compare with optimized geometry or literature values.",
            "Use the geometry pattern to guide ESP/orbital follow-up analysis.",
        ])
    else:
        explanation.summary = (
            f"Computation for {structure} is complete. "
            "Core energy and convergence outputs are ready for interpretation."
        )
        if total_energy_ev is not None:
            explanation.key_findings.append(f"Total energy: {total_energy_ev:.4f} eV.")
        explanation.next_actions.extend([
            "Add orbital, ESP, or charge analysis depending on your target property.",
            "If you need higher accuracy, compare methods/basis sets in a follow-up run.",
        ])

    if converged:
        cycle_text = f"{n_cycles} cycles" if n_cycles is not None else "reported cycles"
        explanation.key_findings.append(f"SCF converged in {cycle_text}.")
    else:
        explanation.cautions.append(
            "SCF did not fully converge. Treat quantitative values with caution."
        )

    final_delta = _safe_float(result.get("scf_final_delta_e_hartree"))
    if final_delta is not None and abs(final_delta) > 1e-3:
        explanation.cautions.append(
            "Final SCF dE is relatively large; consider tighter convergence settings."
        )

    if confidence_score is not None:
        explanation.key_findings.append(f"Advisor confidence score: {confidence_score:.2f}.")
        if confidence_score < 0.45:
            explanation.cautions.append(
                "Advisor confidence is low; method/basis tuning may be required."
            )

    for item in _confidence_recommendations(advisor):
        if item not in explanation.next_actions:
            explanation.next_actions.append(item)

    literature = (advisor or {}).get("literature") if isinstance(advisor, Mapping) else None
    if isinstance(literature, Mapping) and literature.get("status") == "error":
        explanation.cautions.append(
            "Literature validation was unavailable or insufficient for this result."
        )

    explanation.key_findings = explanation.key_findings[:5]
    explanation.interpretation = explanation.interpretation[:4]
    explanation.cautions = explanation.cautions[:4]
    explanation.next_actions = explanation.next_actions[:5]
    return explanation.model_dump()


def explain_comparison(
    *,
    delta: Mapping[str, Any],
    result_a: Mapping[str, Any],
    result_b: Mapping[str, Any],
    job_type: str = "analyze",
    advisor_data: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Generate a natural-language explanation from a comparison delta payload."""
    mol_a = _safe_str(delta.get("molecule_a") or delta.get("mol_a") or "molecule A")
    mol_b = _safe_str(delta.get("molecule_b") or delta.get("mol_b") or "molecule B")

    explanation = ResultExplanation()
    explanation.summary = (
        f"Comparison between {mol_a} and {mol_b} is complete. "
        "Energy, orbital-gap, and charge-redistribution deltas are summarized below."
    )

    energy_delta_ev = _safe_float(delta.get("energy_delta_ev"))
    energy_delta_kcal = _safe_float(delta.get("energy_delta_kcal"))
    if energy_delta_ev is not None:
        if energy_delta_kcal is not None:
            explanation.key_findings.append(
                f"Total-energy delta: {energy_delta_ev:+.4f} eV ({energy_delta_kcal:+.2f} kcal/mol)."
            )
        else:
            explanation.key_findings.append(
                f"Total-energy delta: {energy_delta_ev:+.4f} eV."
            )

    gap_delta = _safe_float(delta.get("gap_delta_ev"))
    if gap_delta is not None:
        direction = "increase" if gap_delta > 0 else "decrease"
        explanation.key_findings.append(
            f"HOMO-LUMO gap change: {gap_delta:+.4f} eV ({direction})."
        )
        if abs(gap_delta) > 0.5:
            explanation.interpretation.append(
                "The gap shift is large enough to suggest a meaningful electronic-structure difference."
            )

    max_charge_diff = _safe_float(delta.get("max_charge_diff"))
    if max_charge_diff is not None:
        explanation.key_findings.append(
            f"Maximum partial-charge difference: {max_charge_diff:.4f} e."
        )
        if max_charge_diff > 0.1:
            explanation.interpretation.append(
                "Charge redistribution is substantial and may alter reactive-site preference."
            )

    if not delta.get("both_converged"):
        explanation.cautions.append(
            "At least one side did not fully converge; interpret quantitative differences conservatively."
        )

    explanation.next_actions.extend([
        "Inspect atom-resolved charges to localize where the largest difference appears.",
        "Overlay ESP maps of both molecules to compare reactive regions directly.",
    ])

    if _safe_str(job_type):
        explanation.interpretation.append(
            f"This comparison used `{_safe_str(job_type)}` calculations."
        )

    if result_a.get("warnings") or result_b.get("warnings"):
        explanation.cautions.append(
            "Review warning messages from each run before final conclusions."
        )

    advisor_recommendation = ""
    if isinstance(advisor_data, Mapping):
        advisor_recommendation = _safe_str(
            advisor_data.get("summary")
            or advisor_data.get("recommendation")
        )
        if advisor_recommendation:
            follow_up = _safe_str(advisor_data.get("next_action"))
            if not follow_up:
                follow_up = (
                    "Run a follow-up comparison with the advisor-recommended setup "
                    "to confirm the trend."
                )
            if follow_up and follow_up not in explanation.next_actions:
                explanation.next_actions.append(follow_up)

    explanation.key_findings = explanation.key_findings[:5]
    explanation.interpretation = explanation.interpretation[:4]
    explanation.cautions = explanation.cautions[:4]
    explanation.next_actions = explanation.next_actions[:5]
    payload = explanation.model_dump()
    if advisor_recommendation:
        payload["advisor_recommendation"] = advisor_recommendation
    return payload
