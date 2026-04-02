"""RDKit-based structure intelligence helpers for modification exploration.

This module is intentionally safe to import even when RDKit is unavailable.
Public functions return empty results or ``None`` rather than raising.
"""

from __future__ import annotations

import logging
from typing import Any

from qcviz_mcp.errors import ModificationError, StructureIntelligenceError

logger = logging.getLogger(__name__)

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors, RWMol

    _RDKIT_AVAILABLE = True
except Exception:  # pragma: no cover - RDKit is optional
    Chem = None  # type: ignore[assignment]
    AllChem = None  # type: ignore[assignment]
    Descriptors = None  # type: ignore[assignment]
    RWMol = None  # type: ignore[assignment]
    _RDKIT_AVAILABLE = False
    logger.info("RDKit not available; structure_intelligence will return empty results")


_MAX_HEAVY_ATOMS = 200
_DEFAULT_MAX_CANDIDATES = 5

SUBSTITUENT_SMARTS: dict[str, dict[str, str]] = {
    "hydrogen": {"smarts": "[H]", "display_name_ko": "hydrogen", "display_name_en": "hydrogen"},
    "methyl": {"smarts": "[CH3]", "display_name_ko": "methyl", "display_name_en": "methyl"},
    "ethyl": {"smarts": "[CH2][CH3]", "display_name_ko": "ethyl", "display_name_en": "ethyl"},
    "propyl": {"smarts": "[CH2][CH2][CH3]", "display_name_ko": "propyl", "display_name_en": "propyl"},
    "hydroxy": {"smarts": "[OH]", "display_name_ko": "hydroxy", "display_name_en": "hydroxy"},
    "amino": {"smarts": "[NH2]", "display_name_ko": "amino", "display_name_en": "amino"},
    "nitro": {"smarts": "[N+](=O)[O-]", "display_name_ko": "nitro", "display_name_en": "nitro"},
    "fluoro": {"smarts": "[F]", "display_name_ko": "fluoro", "display_name_en": "fluoro"},
    "chloro": {"smarts": "[Cl]", "display_name_ko": "chloro", "display_name_en": "chloro"},
    "bromo": {"smarts": "[Br]", "display_name_ko": "bromo", "display_name_en": "bromo"},
    "cyano": {"smarts": "[C]#N", "display_name_ko": "cyano", "display_name_en": "cyano"},
    "formyl": {"smarts": "[CH]=O", "display_name_ko": "formyl", "display_name_en": "formyl"},
    "acetyl": {"smarts": "[C](=O)[CH3]", "display_name_ko": "acetyl", "display_name_en": "acetyl"},
}

_GROUP_KEY_TO_SMILES = {
    "hydrogen": "[H]",
    "methyl": "C",
    "ethyl": "CC",
    "propyl": "CCC",
    "hydroxy": "O",
    "amino": "N",
    "nitro": "[N+](=O)[O-]",
    "fluoro": "F",
    "chloro": "Cl",
    "bromo": "Br",
    "cyano": "C#N",
    "formyl": "C=O",
    "acetyl": "CC=O",
}


def _validate_smiles(smiles: str) -> Any | None:
    if not _RDKIT_AVAILABLE or not smiles:
        return None
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        Chem.SanitizeMol(mol)
        if mol.GetNumHeavyAtoms() > _MAX_HEAVY_ATOMS:
            logger.warning(
                "structure_intelligence skipped molecule with %d heavy atoms (limit=%d)",
                mol.GetNumHeavyAtoms(),
                _MAX_HEAVY_ATOMS,
            )
            return None
        return mol
    except Exception as exc:
        err = StructureIntelligenceError(
            "Invalid SMILES for structure_intelligence",
            smiles_preview=smiles[:60],
            cause=str(exc),
        )
        logger.debug("%s", err)
        return None


def _canonicalize_smiles(smiles: str) -> str | None:
    mol = _validate_smiles(smiles)
    if mol is None:
        return None
    try:
        return Chem.MolToSmiles(mol, canonical=True)
    except Exception:
        return None


def _compute_properties(mol: Any | None) -> dict[str, float]:
    if not _RDKIT_AVAILABLE or mol is None:
        return {"mw": 0.0, "logp": 0.0, "tpsa": 0.0}
    try:
        return {
            "mw": float(Descriptors.ExactMolWt(mol)),
            "logp": float(Descriptors.MolLogP(mol)),
            "tpsa": float(Descriptors.TPSA(mol)),
        }
    except Exception:
        return {"mw": 0.0, "logp": 0.0, "tpsa": 0.0}


def _group_key_to_smiles(key: str) -> str:
    return _GROUP_KEY_TO_SMILES.get(key, "C")


def _terminal_group_key(atom: Any) -> str | None:
    symbol = atom.GetSymbol()
    total_h = atom.GetTotalNumHs()
    if symbol == "C" and atom.GetDegree() == 1 and total_h >= 3:
        return "methyl"
    if symbol == "O" and atom.GetDegree() == 1 and total_h >= 1:
        return "hydroxy"
    if symbol == "N" and atom.GetDegree() == 1 and total_h >= 1:
        return "amino"
    if symbol == "F":
        return "fluoro"
    if symbol == "Cl":
        return "chloro"
    if symbol == "Br":
        return "bromo"
    return None


def identify_substituents(smiles: str) -> list[dict[str, Any]]:
    """Identify replaceable hydrogen and terminal substituent positions."""
    if not _RDKIT_AVAILABLE:
        logger.warning("identify_substituents: RDKit not available")
        return []

    mol = _validate_smiles(smiles)
    if mol is None:
        return []

    results: list[dict[str, Any]] = []

    mol_h = Chem.AddHs(mol)
    for atom in mol_h.GetAtoms():
        if atom.GetSymbol() != "H" or atom.GetDegree() != 1:
            continue
        parent = atom.GetNeighbors()[0]
        bond = atom.GetBonds()[0]
        results.append(
            {
                "atom_idx": atom.GetIdx(),
                "current_group": "hydrogen",
                "symbol": "H",
                "bond_type": str(bond.GetBondType()).split(".")[-1],
                "ring_member": bool(parent.IsInRing()),
                "parent_atom_idx": parent.GetIdx(),
            }
        )

    for atom in mol.GetAtoms():
        group_key = _terminal_group_key(atom)
        if not group_key:
            continue
        if atom.GetDegree() != 1:
            continue
        parent = atom.GetNeighbors()[0]
        bond = atom.GetBonds()[0]
        results.append(
            {
                "atom_idx": atom.GetIdx(),
                "current_group": group_key,
                "symbol": atom.GetSymbol(),
                "bond_type": str(bond.GetBondType()).split(".")[-1],
                "ring_member": bool(atom.IsInRing()),
                "parent_atom_idx": parent.GetIdx(),
            }
        )

    logger.debug("identify_substituents(%s) -> %d positions", smiles[:40], len(results))
    return results


def _attach_fragment(parent_mol: Any, parent_idx: int, fragment_smiles: str) -> str | None:
    fragment = Chem.MolFromSmiles(fragment_smiles) if _RDKIT_AVAILABLE else None
    if fragment is None:
        return None
    try:
        combo = Chem.CombineMols(parent_mol, fragment)
        rw = RWMol(combo)
        fragment_start = parent_mol.GetNumAtoms()
        rw.AddBond(parent_idx, fragment_start, Chem.BondType.SINGLE)
        result = rw.GetMol()
        Chem.SanitizeMol(result)
        return Chem.MolToSmiles(result, canonical=True)
    except Exception as exc:
        logger.debug("Failed to attach fragment %s at atom %s: %s", fragment_smiles, parent_idx, exc)
        return None


def _swap_hydrogen_site(smiles: str, atom_idx: int, new_group_key: str) -> str | None:
    mol = _validate_smiles(smiles)
    if mol is None:
        return None
    mol_h = Chem.AddHs(mol)
    if atom_idx < 0 or atom_idx >= mol_h.GetNumAtoms():
        return None

    target = mol_h.GetAtomWithIdx(atom_idx)
    if target.GetSymbol() != "H" or target.GetDegree() != 1:
        return None

    parent_idx = target.GetNeighbors()[0].GetIdx()
    rw = RWMol(mol_h)
    rw.RemoveAtom(atom_idx)
    base = rw.GetMol()
    try:
        Chem.SanitizeMol(base)
    except Exception:
        return None

    if new_group_key == "hydrogen":
        return Chem.MolToSmiles(Chem.RemoveHs(base), canonical=True)

    adjusted_parent_idx = parent_idx if atom_idx > parent_idx else parent_idx - 1
    return _attach_fragment(base, adjusted_parent_idx, _group_key_to_smiles(new_group_key))


def _swap_terminal_group(smiles: str, atom_idx: int, new_group_key: str) -> str | None:
    mol = _validate_smiles(smiles)
    if mol is None or atom_idx < 0 or atom_idx >= mol.GetNumAtoms():
        return None

    target = mol.GetAtomWithIdx(atom_idx)
    if target.GetDegree() != 1:
        return None
    parent_idx = target.GetNeighbors()[0].GetIdx()

    rw = RWMol(mol)
    rw.RemoveAtom(atom_idx)
    base = rw.GetMol()
    try:
        Chem.SanitizeMol(base)
    except Exception:
        return None

    adjusted_parent_idx = parent_idx if atom_idx > parent_idx else parent_idx - 1
    if new_group_key == "hydrogen":
        return Chem.MolToSmiles(base, canonical=True)
    return _attach_fragment(base, adjusted_parent_idx, _group_key_to_smiles(new_group_key))


def _aromatic_hydrogen_reaction_candidates(
    base_smiles: str,
    to_group: str,
    *,
    max_candidates: int,
) -> list[str]:
    """Fallback aromatic C-H substitution using RDKit reaction SMARTS.

    This path is robust for aromatic systems (e.g., benzene -> toluene) where
    explicit H atom editing can fail sanitization after atom index shifts.
    """
    if not _RDKIT_AVAILABLE or to_group == "hydrogen":
        return []

    base_mol = _validate_smiles(base_smiles)
    fragment = _group_key_to_smiles(to_group)
    if base_mol is None or not fragment:
        return []

    try:
        rxn = AllChem.ReactionFromSmarts(f"[cH:1]>>[c:1]{fragment}")
    except Exception:
        return []
    if rxn is None:
        return []

    out: list[str] = []
    seen: set[str] = set()
    try:
        product_sets = rxn.RunReactants((base_mol,))
    except Exception:
        return []

    for product_tuple in product_sets:
        if not product_tuple:
            continue
        candidate = product_tuple[0]
        try:
            Chem.SanitizeMol(candidate)
            canonical = Chem.MolToSmiles(candidate, canonical=True)
        except Exception:
            continue
        if canonical and canonical not in seen:
            seen.add(canonical)
            out.append(canonical)
        if len(out) >= max(1, int(max_candidates)):
            break

    return out


def swap_substituent(smiles: str, atom_idx: int, new_group_key: str) -> str | None:
    """Replace a substituent at a specific hydrogen or terminal-group position."""
    if not _RDKIT_AVAILABLE:
        logger.warning("swap_substituent: RDKit not available")
        return None
    if new_group_key not in SUBSTITUENT_SMARTS:
        logger.warning("swap_substituent: unknown substituent key %s", new_group_key)
        return None

    hydrogen_result = _swap_hydrogen_site(smiles, atom_idx, new_group_key)
    if hydrogen_result is not None:
        return hydrogen_result
    return _swap_terminal_group(smiles, atom_idx, new_group_key)


def generate_modification_candidates(
    base_smiles: str,
    from_group: str,
    to_group: str,
    *,
    max_candidates: int = _DEFAULT_MAX_CANDIDATES,
) -> list[dict[str, Any]]:
    """Generate unique candidate molecules for a simple substituent swap."""
    if not _RDKIT_AVAILABLE:
        logger.warning("generate_modification_candidates: RDKit not available")
        return []
    if from_group not in SUBSTITUENT_SMARTS or to_group not in SUBSTITUENT_SMARTS:
        err = ModificationError(
            "Unknown substituent key",
            base_smiles=base_smiles,
            from_group=from_group,
            to_group=to_group,
        )
        logger.warning("generate_modification_candidates: %s", err)
        return []
    if _validate_smiles(base_smiles) is None:
        return []

    candidates: list[dict[str, Any]] = []
    seen_smiles: set[str] = set()

    for site in identify_substituents(base_smiles):
        if site.get("current_group") != from_group:
            continue
        candidate_smiles = swap_substituent(base_smiles, int(site["atom_idx"]), to_group)
        canonical = _canonicalize_smiles(candidate_smiles or "")
        if not canonical or canonical in seen_smiles:
            continue
        seen_smiles.add(canonical)
        candidates.append(
            {
                "candidate_smiles": canonical,
                "position_description": (
                    f"Replace {from_group} at atom {site['atom_idx']} with {to_group}"
                ),
                "atom_idx": int(site["atom_idx"]),
                "from_group": from_group,
                "to_group": to_group,
                "property_delta": preview_property_delta(base_smiles, canonical),
            }
        )
        if len(candidates) >= max_candidates:
            break

    if not candidates and from_group == "hydrogen" and to_group != "hydrogen":
        for canonical in _aromatic_hydrogen_reaction_candidates(
            base_smiles,
            to_group,
            max_candidates=max_candidates,
        ):
            if canonical in seen_smiles:
                continue
            seen_smiles.add(canonical)
            candidates.append(
                {
                    "candidate_smiles": canonical,
                    "position_description": (
                        f"Replace aromatic hydrogen with {to_group}"
                    ),
                    "atom_idx": -1,
                    "from_group": from_group,
                    "to_group": to_group,
                    "property_delta": preview_property_delta(base_smiles, canonical),
                }
            )
            if len(candidates) >= max_candidates:
                break

    logger.info(
        "generate_modification_candidates(%s, %s -> %s): %d candidates",
        base_smiles[:40],
        from_group,
        to_group,
        len(candidates),
    )
    return candidates


def preview_property_delta(base_smiles: str, modified_smiles: str) -> dict[str, float]:
    """Compute simple property deltas between base and modified molecules."""
    if not _RDKIT_AVAILABLE:
        return {"mw_delta": 0.0, "logp_delta": 0.0, "tpsa_delta": 0.0}

    base_mol = _validate_smiles(base_smiles)
    mod_mol = _validate_smiles(modified_smiles)
    if base_mol is None or mod_mol is None:
        return {"mw_delta": 0.0, "logp_delta": 0.0, "tpsa_delta": 0.0}

    base_props = _compute_properties(base_mol)
    mod_props = _compute_properties(mod_mol)
    return {
        "mw_delta": round(mod_props["mw"] - base_props["mw"], 2),
        "logp_delta": round(mod_props["logp"] - base_props["logp"], 2),
        "tpsa_delta": round(mod_props["tpsa"] - base_props["tpsa"], 2),
    }


__all__ = [
    "_RDKIT_AVAILABLE",
    "SUBSTITUENT_SMARTS",
    "identify_substituents",
    "swap_substituent",
    "generate_modification_candidates",
    "preview_property_delta",
]
