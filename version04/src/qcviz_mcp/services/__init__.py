"""QCViz-MCP services package exports."""

from __future__ import annotations

from .gemini_agent import GeminiAgent, GeminiResult
from .ion_pair_handler import ION_ALIASES, IonPairResult, is_ion_pair, resolve_ion_pair
from .molchat_client import MolChatClient
from .pubchem_client import PubChemClient
from .sdf_converter import merge_sdfs, sdf_to_atoms_list, sdf_to_xyz
from .structure_resolver import StructureResolver, StructureResult

try:
    from . import structure_intelligence
except ImportError:
    structure_intelligence = None  # type: ignore[assignment]

__all__ = [
    "sdf_to_xyz",
    "merge_sdfs",
    "sdf_to_atoms_list",
    "MolChatClient",
    "PubChemClient",
    "IonPairResult",
    "ION_ALIASES",
    "is_ion_pair",
    "resolve_ion_pair",
    "StructureResolver",
    "StructureResult",
    "GeminiAgent",
    "GeminiResult",
    "structure_intelligence",
]


def __getattr__(name: str):
    if name in {
        "KO_TO_EN",
        "translate",
        "find_molecule_name",
        "translate_substituent",
        "SUBSTITUENT_KO_TO_EN",
    }:
        from . import ko_aliases

        return getattr(ko_aliases, name)
    raise AttributeError(name)
