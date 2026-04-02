"""RDKit-based molecular structure intelligence for modification exploration.

This module provides substituent identification, swapping, and candidate
generation for the ``modification_exploration`` lane in QCViz Phase 2.

All public functions degrade gracefully when RDKit is unavailable:
they return empty lists / None and log a warning.

Typical usage::

    from qcviz_mcp.services.structure_intelligence import (
        generate_modification_candidates,
    )
    candidates = generate_modification_candidates("CCNC", "methyl", "ethyl")
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── RDKit optional import (follows existing project pattern) ─────────
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors, RWMol, rdmolops
    _RDKIT_AVAILABLE = True
except Exception:  # pragma: no cover — RDKit is optional
    Chem = None  # type: ignore[assignment]
    AllChem = None  # type: ignore[assignment]
    Descriptors = None  # type: ignore[assignment]
    RWMol = None  # type: ignore[assignment]
    rdmolops = None  # type: ignore[assignment]
    _RDKIT_AVAILABLE = False
    logger.info("RDKit not available — structure_intelligence functions will return empty results")


# ── Constants ────────────────────────────────────────────────────────
_MAX_HEAVY_ATOMS = 200
_DEFAULT_MAX_CANDIDATES = 5

# Substituent SMARTS dictionary.
# Each entry: key → {smarts, display_name_ko, display_name_en}
SUBSTITUENT_SMARTS: Dict[str, Dict[str, str]] = {
    "hydrogen": {
        "smarts": "[H]",
        "display_name_ko": "수소",
        "display_name_en": "hydrogen",
    },
    "methyl": {
        "smarts": "[CH3]",
        "display_name_ko": "메틸기",
        "display_name_en": "methyl",
    },
    "ethyl": {
        "smarts": "[CH2][CH3]",
        "display_name_ko": "에틸기",
        "display_name_en": "ethyl",
    },
    "propyl": {
        "smarts": "[CH2][CH2][CH3]",
        "display_name_ko": "프로필기",
        "display_name_en": "propyl",
    },
    "hydroxy": {
        "smarts": "[OH]",
        "display_name_ko": "하이드록시기",
        "display_name_en": "hydroxy",
    },
    "amino": {
        "smarts": "[NH2]",
        "display_name_ko": "아미노기",
        "display_name_en": "amino",
    },
    "nitro": {
        "smarts": "[N+](=O)[O-]",
        "display_name_ko": "니트로기",
        "display_name_en": "nitro",
    },
    "fluoro": {
        "smarts": "[F]",
        "display_name_ko": "플루오로",
        "display_name_en": "fluoro",
    },
    "chloro": {
        "smarts": "[Cl]",
        "display_name_ko": "클로로",
        "display_name_en": "chloro",
    },
    "bromo": {
        "smarts": "[Br]",
        "display_name_ko": "브로모",
        "display_name_en": "bromo",
    },
    "cyano": {
        "smarts": "[C]#N",
        "display_name_ko": "시아노기",
        "display_name_en": "cyano",
    },
    "formyl": {
        "smarts": "[CH]=O",
        "display_name_ko": "포밀기",
        "display_name_en": "formyl",
    },
    "acetyl": {
        "smarts": "[C](=O)[CH3]",
        "display_name_ko": "아세틸기",
        "display_name_en": "acetyl",
    },
}

# Reverse lookup: SMILES fragment → group key (for identification)
_SMILES_TO_GROUP: Dict[str, str] = {}


def _ensure_smiles_to_group() -> None:
    """Build reverse lookup table on first use."""
    if _SMILES_TO_GROUP:
        return
    if not _RDKIT_AVAILABLE:
        return
    for key, info in SUBSTITUENT_SMARTS.items():
        try:
            mol = Chem.MolFromSmarts(info["smarts"])
            if mol is not None:
                _SMILES_TO_GROUP[Chem.MolToSmiles(mol)] = key
        except Exception:
            pass


# ── Safety helpers ───────────────────────────────────────────────────

def _validate_smiles(smiles: str) -> Optional[Any]:
    """Parse and validate a SMILES string.

    Args:
        smiles: SMILES string to validate.

    Returns:
        RDKit Mol object, or None if invalid or RDKit unavailable.
    """
    if not _RDKIT_AVAILABLE or not smiles:
        return None
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        Chem.SanitizeMol(mol)
        if mol.GetNumHeavyAtoms() > _MAX_HEAVY_ATOMS:
            logger.warning(
                "Molecule too large (%d heavy atoms > %d limit): %s",
                mol.GetNumHeavyAtoms(), _MAX_HEAVY_ATOMS, smiles[:60],
            )
            return None
        return mol
    except Exception as exc:
        logger.debug("SMILES validation failed for %r: %s", smiles[:60], exc)
        return None


def _compute_properties(mol: Any) -> Dict[str, float]:
    """Compute MW, LogP, TPSA for a molecule.

    Args:
        mol: RDKit Mol object.

    Returns:
        Dict with keys mw, logp, tpsa.
    """
    if not _RDKIT_AVAILABLE or mol is None:
        return {"mw": 0.0, "logp": 0.0, "tpsa": 0.0}
    try:
        return {
            "mw": Descriptors.ExactMolWt(mol),
            "logp": Descriptors.MolLogP(mol),
            "tpsa": Descriptors.TPSA(mol),
        }
    except Exception:
        return {"mw": 0.0, "logp": 0.0, "tpsa": 0.0}


# ── Public API ───────────────────────────────────────────────────────

def identify_substituents(smiles: str) -> List[Dict[str, Any]]:
    """Identify replaceable substituent positions in a molecule.

    Scans the molecule for terminal (degree-1) non-ring atoms that can
    be replaced with another functional group.

    Args:
        smiles: Canonical SMILES of the base molecule.

    Returns:
        List of dicts, each with:
            atom_idx (int): Atom index in the molecule.
            current_group (str): Best-guess group key from SUBSTITUENT_SMARTS.
            symbol (str): Atomic symbol at this position.
            bond_type (str): Bond type to parent ("SINGLE", "DOUBLE", etc.).
            ring_member (bool): Whether the atom is in a ring.

    # Test scenario: identify_substituents("CCNC")
    #   → should find H atoms and terminal CH3 groups
    """
    if not _RDKIT_AVAILABLE:
        logger.warning("identify_substituents: RDKit not available")
        return []

    mol = _validate_smiles(smiles)
    if mol is None:
        return []

    # Add explicit Hs to see terminal hydrogens
    mol_h = Chem.AddHs(mol)
    results: List[Dict[str, Any]] = []

    for atom in mol_h.GetAtoms():
        idx = atom.GetIdx()
        symbol = atom.GetSymbol()
        degree = atom.GetDegree()
        in_ring = atom.IsInRing()

        # Terminal atoms (degree 1) are candidate replacement sites
        if degree != 1:
            continue

        # Skip H atoms on aromatic carbons for cleaner results
        # (those are the main sites for substitution)
        bonds = atom.GetBonds()
        bond_type = "SINGLE"
        if bonds:
            bond_type = str(bonds[0].GetBondType()).split(".")[-1]

        # Guess current group
        current_group = "hydrogen" if symbol == "H" else symbol.lower()

        results.append({
            "atom_idx": idx,
            "current_group": current_group,
            "symbol": symbol,
            "bond_type": bond_type,
            "ring_member": in_ring,
        })

    logger.debug(
        "identify_substituents(%s): found %d positions", smiles[:40], len(results)
    )
    return results


def swap_substituent(
    smiles: str,
    atom_idx: int,
    new_group_key: str,
) -> Optional[str]:
    """Replace a substituent at a specific position.

    Args:
        smiles: Base molecule SMILES.
        atom_idx: Atom index to replace (in H-added molecule).
        new_group_key: Key from SUBSTITUENT_SMARTS for the new group.

    Returns:
        Canonical SMILES of the modified molecule, or None on failure.

    # Test scenario: swap_substituent("c1ccccc1", 6, "methyl")
    #   → should return toluene SMILES "Cc1ccccc1" (or equivalent)
    """
    if not _RDKIT_AVAILABLE:
        logger.warning("swap_substituent: RDKit not available")
        return None

    if new_group_key not in SUBSTITUENT_SMARTS:
        logger.warning("Unknown substituent key: %s", new_group_key)
        return None

    mol = _validate_smiles(smiles)
    if mol is None:
        return None

    try:
        mol_h = Chem.AddHs(mol)
        if atom_idx >= mol_h.GetNumAtoms():
            logger.debug("atom_idx %d out of range for %s", atom_idx, smiles[:40])
            return None

        target_atom = mol_h.GetAtomWithIdx(atom_idx)

        # Build the new group fragment
        new_smarts = SUBSTITUENT_SMARTS[new_group_key]["smarts"]

        # For simple single-atom replacements (H, F, Cl, Br)
        if new_group_key == "hydrogen":
            # "Replace with H" means just remove the atom if it's not H
            if target_atom.GetSymbol() == "H":
                return smiles  # Already H, no change
            # Remove the atom and add H
            rw = RWMol(mol_h)
            neighbors = [n.GetIdx() for n in target_atom.GetNeighbors()]
            if not neighbors:
                return None
            rw.RemoveAtom(atom_idx)
            try:
                Chem.SanitizeMol(rw)
                result = Chem.MolToSmiles(rw)
                return result if _validate_smiles(result) else None
            except Exception:
                return None

        # For replacing an H with a functional group
        if target_atom.GetSymbol() == "H":
            # Get the parent atom
            neighbors = [n.GetIdx() for n in target_atom.GetNeighbors()]
            if not neighbors:
                return None
            parent_idx = neighbors[0]

            # Remove the H
            rw = RWMol(mol_h)
            rw.RemoveAtom(atom_idx)

            # Parse the new group
            new_frag = Chem.MolFromSmiles(
                _group_key_to_smiles(new_group_key)
            )
            if new_frag is None:
                return None

            # Combine
            combo = Chem.CombineMols(rw.GetMol(), new_frag)
            rw2 = RWMol(combo)

            # The parent atom index might have shifted after removal
            # Adjust: if atom_idx < parent_idx, parent shifts down by 1
            adj_parent = parent_idx if atom_idx > parent_idx else parent_idx - 1

            # The first atom of the new fragment
            new_start = rw.GetNumAtoms()

            rw2.AddBond(adj_parent, new_start, Chem.BondType.SINGLE)

            try:
                Chem.SanitizeMol(rw2)
                result = Chem.MolToSmiles(rw2)
                # Validate the result
                if _validate_smiles(result) is not None:
                    return result
            except Exception:
                pass

        return None

    except Exception as exc:
        logger.debug("swap_substituent failed: %s", exc)
        return None


def _group_key_to_smiles(key: str) -> str:
    """Convert a substituent key to a connectable SMILES fragment.

    Args:
        key: Key from SUBSTITUENT_SMARTS.

    Returns:
        SMILES string suitable for fragment combination.
    """
    _simple_map = {
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
        "acetyl": "C(=O)C",
        "hydrogen": "[H]",
    }
    return _simple_map.get(key, "C")


def generate_modification_candidates(
    base_smiles: str,
    from_group: str,
    to_group: str,
    *,
    max_candidates: int = _DEFAULT_MAX_CANDIDATES,
) -> List[Dict[str, Any]]:
    """Generate modified molecule candidates by substituent replacement.

    Finds all positions where ``from_group`` can be replaced with
    ``to_group`` and returns up to ``max_candidates`` unique results
    with property delta previews.

    Args:
        base_smiles: SMILES of the starting molecule.
        from_group: Substituent key to replace (e.g. "hydrogen", "methyl").
        to_group: Substituent key for the replacement (e.g. "methyl", "ethyl").
        max_candidates: Maximum number of candidates to return.

    Returns:
        List of candidate dicts, each containing:
            candidate_smiles (str): SMILES of modified molecule.
            position_description (str): Human-readable position info.
            atom_idx (int): Original atom index that was replaced.
            from_group (str): Original substituent key.
            to_group (str): New substituent key.
            property_delta (dict): MW/LogP/TPSA deltas.

    # Test scenario: generate_modification_candidates("c1ccccc1", "hydrogen", "methyl")
    #   → should return toluene as a candidate with MW delta ~14
    """
    if not _RDKIT_AVAILABLE:
        logger.warning("generate_modification_candidates: RDKit not available")
        return []

    if from_group not in SUBSTITUENT_SMARTS or to_group not in SUBSTITUENT_SMARTS:
        logger.warning(
            "Unknown group key: from=%s to=%s", from_group, to_group
        )
        return []

    base_mol = _validate_smiles(base_smiles)
    if base_mol is None:
        return []

    # Identify positions with the from_group
    positions = identify_substituents(base_smiles)
    target_symbol = {
        "hydrogen": "H",
        "fluoro": "F",
        "chloro": "Cl",
        "bromo": "Br",
    }.get(from_group)

    candidates: List[Dict[str, Any]] = []
    seen_smiles: set = set()

    for pos in positions:
        # Filter to positions matching from_group
        if target_symbol and pos["symbol"] != target_symbol:
            continue
        if not target_symbol and pos["current_group"] != from_group:
            continue

        modified = swap_substituent(base_smiles, pos["atom_idx"], to_group)
        if modified is None:
            continue

        # Deduplicate by canonical SMILES
        try:
            canonical = Chem.MolToSmiles(Chem.MolFromSmiles(modified))
        except Exception:
            canonical = modified

        if canonical in seen_smiles:
            continue
        seen_smiles.add(canonical)

        # Compute property delta
        delta = preview_property_delta(base_smiles, canonical)

        from_name = SUBSTITUENT_SMARTS[from_group]["display_name_en"]
        to_name = SUBSTITUENT_SMARTS[to_group]["display_name_en"]

        candidates.append({
            "candidate_smiles": canonical,
            "position_description": (
                f"Replace {from_name} at position {pos['atom_idx']} "
                f"with {to_name}"
            ),
            "atom_idx": pos["atom_idx"],
            "from_group": from_group,
            "to_group": to_group,
            "property_delta": delta,
        })

        if len(candidates) >= max_candidates:
            break

    logger.info(
        "generate_modification_candidates(%s, %s→%s): %d candidates",
        base_smiles[:40], from_group, to_group, len(candidates),
    )
    return candidates


def preview_property_delta(
    base_smiles: str,
    modified_smiles: str,
) -> Dict[str, float]:
    """Compute property differences between two molecules.

    Args:
        base_smiles: Original molecule SMILES.
        modified_smiles: Modified molecule SMILES.

    Returns:
        Dict with mw_delta, logp_delta, tpsa_delta (floats).
        All zeros if computation fails.

    # Test scenario: preview_property_delta("c1ccccc1", "Cc1ccccc1")
    #   → mw_delta ≈ +14.0, logp_delta > 0
    """
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
