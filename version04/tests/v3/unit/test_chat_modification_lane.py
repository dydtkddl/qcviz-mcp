from __future__ import annotations

import pytest

from qcviz_mcp.llm.routing_config import MODIFICATION_MAX_CANDIDATES
from qcviz_mcp.llm.schemas import ModificationIntent
from qcviz_mcp.services import structure_intelligence
from qcviz_mcp.web.routes import chat as chat_route


def test_extract_modification_request_state_uses_plan_context_when_session_has_no_active_molecule(monkeypatch):
    monkeypatch.setattr(chat_route, "get_active_molecule", lambda session_id, manager=None: None)

    active_molecule, modification_intent = chat_route._extract_modification_request_state(
        "session-1",
        {
            "planner_lane": "modification_exploration",
            "context_molecule_name": "benzene",
            "context_molecule_smiles": "c1ccccc1",
            "modification_intent": ModificationIntent(
                from_group="hydrogen",
                to_group="methyl",
                confidence=0.82,
            ),
        },
    )

    assert active_molecule["canonical_name"] == "benzene"
    assert active_molecule["smiles"] == "c1ccccc1"
    assert modification_intent["from_group"] == "hydrogen"
    assert modification_intent["to_group"] == "methyl"


@pytest.mark.asyncio
async def test_handle_modification_exploration_sends_candidate_event(monkeypatch):
    captured: list[tuple[str, dict]] = []

    async def _fake_ws_send(websocket, event_type: str, **payload):
        captured.append((event_type, payload))

    def _fake_generate(base_smiles: str, from_group: str, to_group: str, *, max_candidates: int):
        assert base_smiles == "c1ccccc1"
        assert from_group == "hydrogen"
        assert to_group == "methyl"
        assert max_candidates == MODIFICATION_MAX_CANDIDATES
        return [
            {
                "candidate_smiles": "Cc1ccccc1",
                "position_description": "Replace hydrogen at atom 0 with methyl",
                "atom_idx": 0,
                "from_group": from_group,
                "to_group": to_group,
                "property_delta": {"mw_delta": 14.03, "logp_delta": 0.5, "tpsa_delta": 0.0},
            }
        ]

    monkeypatch.setattr(chat_route, "_ws_send", _fake_ws_send)
    monkeypatch.setattr(structure_intelligence, "_RDKIT_AVAILABLE", True)
    monkeypatch.setattr(structure_intelligence, "generate_modification_candidates", _fake_generate)

    await chat_route._handle_modification_exploration(
        object(),
        session_id="session-1",
        plan={"planner_lane": "modification_exploration"},
        active_molecule={"canonical_name": "benzene", "smiles": "c1ccccc1"},
        modification_intent={"from_group": "hydrogen", "to_group": "methyl"},
        turn_id="turn-1",
    )

    assert captured
    event_type, payload = captured[0]
    assert event_type == "modification_candidates"
    assert payload["base_molecule"]["name"] == "benzene"
    assert payload["from_group"] == "hydrogen"
    assert payload["to_group"] == "methyl"
    assert payload["plan"]["planner_lane"] == "modification_exploration"
    assert payload["candidates"][0]["candidate_smiles"] == "Cc1ccccc1"
