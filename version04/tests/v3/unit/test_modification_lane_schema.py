from __future__ import annotations

import importlib
import typing

import pytest

from qcviz_mcp.llm.normalizer import parse_modification_intent
from qcviz_mcp.llm.lane_lock import LaneLock
from qcviz_mcp.llm.schemas import (
    ExecutionAction,
    GroundingSemanticOutcome,
    ModificationIntent,
    PlanResult,
    PlannerLane,
)


def test_planner_lane_includes_modification_exploration():
    assert "modification_exploration" in typing.get_args(PlannerLane)


def test_modification_intent_model_normalizes_fields():
    intent = ModificationIntent(
        from_group=" methyl ",
        to_group="ethyl",
        from_group_ko="메틸",
        to_group_ko="에틸",
        position_hint=" para ",
        base_molecule_name="toluene",
        base_molecule_smiles="Cc1ccccc1",
        confidence=1.5,
    )

    assert intent.from_group == "methyl"
    assert intent.position_hint == "para"
    assert intent.confidence == 1.0


def test_plan_result_accepts_modification_lane_with_intent():
    result = PlanResult(
        lane="modification_exploration",
        confidence=0.82,
        reasoning="swap methyl to ethyl",
        modification_intent={
            "from_group": "methyl",
            "to_group": "ethyl",
            "confidence": 0.8,
        },
    )

    assert result.lane == "modification_exploration"
    assert result.modification_intent is not None
    assert result.modification_intent.from_group == "methyl"
    assert result.modification_intent.to_group == "ethyl"


def test_plan_result_rejects_modification_lane_without_intent():
    with pytest.raises(ValueError, match="modification_exploration lane requires modification_intent"):
        PlanResult(
            lane="modification_exploration",
            confidence=0.4,
            reasoning="missing modification intent",
        )


def test_grounding_semantic_outcome_and_execution_action_include_modification_values():
    assert "modification_candidates_ready" in typing.get_args(GroundingSemanticOutcome)
    assert "modification_preview" in typing.get_args(ExecutionAction)


def test_lane_lock_allows_modification():
    lock = LaneLock.from_lane("modification_exploration")
    assert lock.allows_modification() is True
    assert lock.allows_grounding() is False
    assert lock.allows_compute() is False


def test_routing_config_modification_defaults(monkeypatch):
    monkeypatch.delenv("QCVIZ_MODIFICATION_CONFIDENCE_THRESHOLD", raising=False)
    monkeypatch.delenv("QCVIZ_MODIFICATION_MAX_CANDIDATES", raising=False)

    import qcviz_mcp.llm.routing_config as routing_config

    reloaded = importlib.reload(routing_config)

    assert reloaded.MODIFICATION_CONFIDENCE_THRESHOLD == 0.60
    assert reloaded.MODIFICATION_MAX_CANDIDATES == 5


def test_parse_modification_intent_extracts_target_position():
    parsed = parse_modification_intent("replace nitro with amino at 2nd position")
    assert parsed is not None
    assert parsed["from_group"] == "nitro"
    assert parsed["to_group"] == "amino"
    assert parsed["target_position"] == 2
    assert parsed["replace_all"] is False


def test_parse_modification_intent_extracts_replace_all():
    parsed = parse_modification_intent("replace all hydroxy with methoxy")
    assert parsed is not None
    assert parsed["from_group"] == "hydroxy"
    assert parsed["to_group"] == "methoxy"
    assert parsed["replace_all"] is True
