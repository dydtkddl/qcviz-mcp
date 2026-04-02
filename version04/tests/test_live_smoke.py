from __future__ import annotations

import os

import pytest
from dotenv import dotenv_values

from qcviz_mcp.services.gemini_agent import GeminiAgent
from qcviz_mcp.services.molchat_client import MolChatClient


def _load_gemini_key() -> str:
    key = str(os.getenv("GEMINI_API_KEY") or "").strip()
    if key:
        return key
    env_values = dotenv_values(".env")
    return str(env_values.get("GEMINI_API_KEY") or "").strip()


@pytest.mark.live
def test_live_gemini_planner_smoke() -> None:
    gemini_key = _load_gemini_key()
    assert gemini_key, "GEMINI_API_KEY must be configured (env or .env)."

    agent = GeminiAgent(api_key=gemini_key)
    result = agent.parse_sync("show HOMO for water")

    assert result is not None
    plan = result.to_plan_dict()
    assert plan["provider"] == "gemini"
    assert plan["job_type"] in {"orbital_preview", "analyze", "resolve_structure"}
    assert plan["confidence"] > 0


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_molchat_api_smoke() -> None:
    client = MolChatClient()
    try:
        resolved = await client.resolve(["water"])
        assert resolved
        assert resolved[0]["cid"]

        card = await client.get_card("water")
        assert card is not None
        smiles = card.get("canonical_smiles") or card.get("smiles")
        assert smiles

        sdf = await client.generate_3d_sdf(smiles)
        assert sdf
        assert "V2000" in sdf or "V3000" in sdf
    finally:
        await client.close()
