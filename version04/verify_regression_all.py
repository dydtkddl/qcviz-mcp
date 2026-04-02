#!/usr/bin/env python3
"""Phase 1-4 full regression verification for QCViz v04.

Run:
    PYTHONPATH=src \
      QCVIZ_CONTEXT_TRACKING_ENABLED=true \
      QCVIZ_MODIFICATION_LANE_ENABLED=true \
      QCVIZ_COMPARISON_ENABLED=true \
      python verify_regression_all.py
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

os.environ.setdefault("QCVIZ_CONTEXT_TRACKING_ENABLED", "true")
os.environ.setdefault("QCVIZ_MODIFICATION_LANE_ENABLED", "true")
os.environ.setdefault("QCVIZ_COMPARISON_ENABLED", "true")


PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"[PASS] {name}")
    else:
        FAIL += 1
        suffix = f" :: {detail}" if detail else ""
        print(f"[FAIL] {name}{suffix}")


def fail(name: str, exc: BaseException) -> None:
    check(name, False, f"{type(exc).__name__}: {exc}")


def expect_raises(name: str, fn: Callable[[], object]) -> None:
    try:
        fn()
    except Exception:
        check(name, True)
        return
    check(name, False, "expected exception was not raised")


def phase1_context() -> None:
    print("\n" + "=" * 72)
    print("PHASE 1: Conversation context")
    print("=" * 72)
    from qcviz_mcp.web.conversation_state import (
        clear_active_molecule,
        get_active_molecule,
        get_molecule_history,
        set_active_molecule,
    )
    from qcviz_mcp.llm.normalizer import detect_implicit_follow_up

    sid = "p4-final-p1"
    os.environ["QCVIZ_CONTEXT_TRACKING_ENABLED"] = "true"
    clear_active_molecule(sid)

    set_active_molecule(
        sid,
        {
            "canonical_name": "toluene",
            "smiles": "Cc1ccccc1",
            "source": "regression",
            "set_at_turn": 1,
        },
    )
    mol = get_active_molecule(sid)
    check("1.1 set/get active molecule", bool(mol and mol.get("canonical_name") == "toluene"), str(mol))

    r = detect_implicit_follow_up(
        "what if we replace methyl with ethyl?",
        has_active_molecule=True,
        has_explicit_molecule_name=False,
    )
    check(
        "1.2 implicit modification follow-up",
        bool(r.get("is_implicit_follow_up") and r.get("follow_up_type") == "modification_request"),
        str(r),
    )

    r = detect_implicit_follow_up(
        "compare it with the ethyl version",
        has_active_molecule=True,
        has_explicit_molecule_name=False,
    )
    check(
        "1.3 implicit comparison follow-up",
        bool(r.get("is_implicit_follow_up") and r.get("follow_up_type") == "comparison_request"),
        str(r),
    )

    r = detect_implicit_follow_up(
        "benzene homo lumo",
        has_active_molecule=True,
        has_explicit_molecule_name=True,
    )
    check("1.4 explicit molecule is not implicit follow-up", not bool(r.get("is_implicit_follow_up")), str(r))

    os.environ["QCVIZ_CONTEXT_TRACKING_ENABLED"] = "false"
    set_active_molecule(
        "p4-final-flag-off",
        {
            "canonical_name": "water",
            "smiles": "O",
            "source": "regression",
            "set_at_turn": 1,
        },
    )
    check("1.5 flag off no-op", get_active_molecule("p4-final-flag-off") is None)
    os.environ["QCVIZ_CONTEXT_TRACKING_ENABLED"] = "true"

    set_active_molecule(
        sid,
        {
            "canonical_name": "ethylbenzene",
            "smiles": "CCc1ccccc1",
            "source": "regression",
            "set_at_turn": 2,
        },
    )
    hist = get_molecule_history(sid)
    check("1.6 history tracking", bool(hist and hist[0].get("canonical_name") == "toluene"), str(hist))
    clear_active_molecule(sid)
    check("1.6b clear active molecule", get_active_molecule(sid) is None)


def phase2_modification() -> None:
    print("\n" + "=" * 72)
    print("PHASE 2: Modification lane")
    print("=" * 72)
    from qcviz_mcp.llm.normalizer import parse_modification_intent
    from qcviz_mcp.security import validate_modification_input
    from qcviz_mcp.services.ko_aliases import translate_substituent
    from qcviz_mcp.services.structure_intelligence import (
        _RDKIT_AVAILABLE,
        generate_modification_candidates,
    )

    r = parse_modification_intent("replace methyl with ethyl")
    check("2.1 swap parse", bool(r and r.get("from_group") == "methyl" and r.get("to_group") == "ethyl"), str(r))

    r = parse_modification_intent("add nitro group")
    check("2.2 addition parse", bool(r and r.get("from_group") == "hydrogen" and r.get("to_group") == "nitro"), str(r))

    r = parse_modification_intent("remove methyl group")
    check("2.3 removal parse", bool(r and r.get("from_group") == "methyl" and r.get("to_group") == "hydrogen"), str(r))

    r = parse_modification_intent("show me homo lumo of benzene")
    check("2.4 non-modification query returns None", r is None, str(r))

    check("2.5a substituent translation methyl", translate_substituent("methyl") == "methyl")
    check("2.5b substituent translation nitro", translate_substituent("nitro") == "nitro")

    check("2.6a RDKit available", bool(_RDKIT_AVAILABLE), "RDKit is required for this regression suite")
    if _RDKIT_AVAILABLE:
        cands = generate_modification_candidates("c1ccccc1", "hydrogen", "methyl")
        check("2.6b RDKit candidate generation", len(cands) >= 1, f"count={len(cands)}")
    else:
        check("2.6b RDKit candidate generation", False, "RDKit unavailable")

    expect_raises(
        "2.7 sanitization blocks injection",
        lambda: validate_modification_input("methyl; rm -rf /", "ethyl", "c1ccccc1"),
    )


def phase3_comparison() -> None:
    print("\n" + "=" * 72)
    print("PHASE 3: Comparison and delta")
    print("=" * 72)
    from qcviz_mcp.compute.pyscf_runner import compute_delta
    from qcviz_mcp.security import validate_comparison_input
    from qcviz_mcp.web.result_explainer import explain_comparison

    result_a = {
        "structure_name": "toluene",
        "total_energy_ev": -2080.5,
        "orbital_gap_ev": 5.2,
        "scf_converged": True,
        "n_atoms": 15,
    }
    result_b = {
        "structure_name": "ethylbenzene",
        "total_energy_ev": -2095.3,
        "orbital_gap_ev": 4.8,
        "scf_converged": True,
        "n_atoms": 18,
    }

    delta = compute_delta(result_a, result_b)
    check(
        "3.1 delta energy",
        delta.get("energy_delta_ev") is not None and float(delta["energy_delta_ev"]) < 0.0,
        str(delta.get("energy_delta_ev")),
    )
    check(
        "3.1b delta gap",
        delta.get("gap_delta_ev") is not None and float(delta["gap_delta_ev"]) < 0.0,
        str(delta.get("gap_delta_ev")),
    )
    check("3.1c both converged", bool(delta.get("both_converged")), str(delta.get("both_converged")))

    exp = explain_comparison(delta=delta, result_a=result_a, result_b=result_b)
    check("3.2 comparison explanation", "Comparison between" in str(exp.get("summary", "")), str(exp.get("summary", "")))

    expect_raises(
        "3.3 comparison sanitization empty input",
        lambda: validate_comparison_input("", "toluene"),
    )


def phase4_integration() -> None:
    print("\n" + "=" * 72)
    print("PHASE 4: Integration stability")
    print("=" * 72)
    import typing

    from qcviz_mcp.config import MODIFICATION_CONFIDENCE_THRESHOLD as CFG_MOD_THRESHOLD
    from qcviz_mcp.env_bootstrap import get_feature_flags
    from qcviz_mcp.errors import ComparisonError, ComparisonTimeoutError, ModificationError
    from qcviz_mcp.llm.providers import get_timeout_profile
    from qcviz_mcp.llm.routing_config import MODIFICATION_CONFIDENCE_THRESHOLD as ROUTE_MOD_THRESHOLD
    from qcviz_mcp.llm.schemas import ModificationIntent, PlannerLane
    from qcviz_mcp.observability import get_phase_summary, metrics, register_phase2_3_metrics
    from qcviz_mcp.web.advisor_flow import prepare_advisor_plan_from_geometry
    from qcviz_mcp.web.app import create_app

    app = create_app()
    check("4.1 create_app", app is not None)

    check(
        "4.2 error class imports",
        all(cls is not None for cls in (ModificationError, ComparisonError, ComparisonTimeoutError)),
    )

    register_phase2_3_metrics()
    metrics.increment("modification_lane_entered", 1)
    summary = get_phase_summary()
    check(
        "4.3 observability summary",
        int(summary.get("modification", {}).get("modification_lane_entered", 0)) >= 1,
        str(summary),
    )

    flags = get_feature_flags()
    required_keys = {
        "QCVIZ_CONTEXT_TRACKING_ENABLED",
        "QCVIZ_MODIFICATION_LANE_ENABLED",
        "QCVIZ_COMPARISON_ENABLED",
    }
    check("4.4 feature-flag registry", required_keys.issubset(set(flags.keys())), str(flags))

    check(
        "4.5 config single source for modification threshold",
        float(ROUTE_MOD_THRESHOLD) == float(CFG_MOD_THRESHOLD),
        f"routing={ROUTE_MOD_THRESHOLD} config={CFG_MOD_THRESHOLD}",
    )

    p = get_timeout_profile("modification_intent")
    check(
        "4.6 timeout profile modification_intent",
        float(p.get("timeout", -1)) == 15.0 and int(p.get("max_retries", -1)) == 1,
        str(p),
    )

    lane_values = set(typing.get_args(PlannerLane))
    check("4.7a planner lane includes modification", "modification_exploration" in lane_values, str(lane_values))
    mi = ModificationIntent(from_group="methyl", to_group="ethyl", confidence=0.8)
    check("4.7b ModificationIntent model", mi.from_group == "methyl" and mi.to_group == "ethyl")

    plan = prepare_advisor_plan_from_geometry(
        intent_name="single_point",
        xyz_text="3\n\nO 0 0 0\nH 0 0 1\nH 0 1 0\n",
        charge=0,
        spin=0,
        modification_context={
            "base_molecule": "toluene",
            "modified_molecule": "ethylbenzene",
            "from_group": "methyl",
            "to_group": "ethyl",
        },
        comparison_context={
            "mol_a": "toluene",
            "mol_b": "ethylbenzene",
            "delta": {"energy_delta_ev": -0.1, "gap_delta_ev": -0.2},
        },
    )
    check("4.8a advisor modification context propagation", isinstance(plan.get("modification"), dict), str(plan))
    check("4.8b advisor comparison context propagation", isinstance(plan.get("comparison"), dict), str(plan))


def phase_perf() -> None:
    print("\n" + "=" * 72)
    print("PERFORMANCE: Micro benchmarks")
    print("=" * 72)
    from qcviz_mcp.compute.pyscf_runner import compute_delta
    from qcviz_mcp.llm.normalizer import detect_implicit_follow_up, parse_modification_intent
    from qcviz_mcp.web.conversation_state import get_active_molecule, set_active_molecule

    t0 = time.perf_counter()
    for _ in range(1000):
        detect_implicit_follow_up(
            "what if we replace methyl with ethyl?",
            has_active_molecule=True,
            has_explicit_molecule_name=False,
        )
    dt = (time.perf_counter() - t0) * 1000.0 / 1000.0
    check("perf detect_implicit_follow_up < 5ms", dt < 5.0, f"{dt:.3f}ms")

    t0 = time.perf_counter()
    for _ in range(1000):
        parse_modification_intent("replace methyl with ethyl")
    dt = (time.perf_counter() - t0) * 1000.0 / 1000.0
    check("perf parse_modification_intent < 8ms", dt < 8.0, f"{dt:.3f}ms")

    a = {"structure_name": "a", "total_energy_ev": -10.0, "orbital_gap_ev": 5.0, "scf_converged": True, "n_atoms": 3}
    b = {"structure_name": "b", "total_energy_ev": -11.0, "orbital_gap_ev": 4.8, "scf_converged": True, "n_atoms": 4}
    t0 = time.perf_counter()
    for _ in range(1000):
        compute_delta(a, b)
    dt = (time.perf_counter() - t0) * 1000.0 / 1000.0
    check("perf compute_delta < 2ms", dt < 2.0, f"{dt:.3f}ms")

    t0 = time.perf_counter()
    for _ in range(1000):
        set_active_molecule(
            "perf-session",
            {"canonical_name": "methane", "smiles": "C", "source": "perf", "set_at_turn": 1},
        )
        get_active_molecule("perf-session")
    dt = (time.perf_counter() - t0) * 1000.0 / 1000.0
    check("perf set/get active_molecule < 2ms", dt < 2.0, f"{dt:.3f}ms")


def main() -> int:
    print("=" * 72)
    print("QCViz v04: Phase 1-4 Full Regression")
    print("=" * 72)
    print(f"Python: {sys.version.split()[0]}")
    print(f"Root:   {ROOT}")
    print(
        "Flags:  context=%s, modification=%s, comparison=%s"
        % (
            os.environ.get("QCVIZ_CONTEXT_TRACKING_ENABLED"),
            os.environ.get("QCVIZ_MODIFICATION_LANE_ENABLED"),
            os.environ.get("QCVIZ_COMPARISON_ENABLED"),
        )
    )

    for name, fn in [
        ("Phase 1", phase1_context),
        ("Phase 2", phase2_modification),
        ("Phase 3", phase3_comparison),
        ("Phase 4", phase4_integration),
        ("Perf", phase_perf),
    ]:
        try:
            fn()
        except Exception as exc:
            fail(f"{name} unexpected exception", exc)

    total = PASS + FAIL
    print("\n" + "=" * 72)
    print(f"RESULT: {PASS} passed / {FAIL} failed / {total} total checks")
    if FAIL == 0:
        print("STATUS: FULL REGRESSION PASSED")
        return 0
    print("STATUS: REGRESSION FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

