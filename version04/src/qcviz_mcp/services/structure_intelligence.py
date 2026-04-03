"""RDKit-based structure intelligence helpers for modification exploration.

This module is intentionally safe to import even when RDKit is unavailable.
Public functions return empty results or ``None`` rather than raising.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
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
_FG_DICT_PATH = Path(__file__).with_name("fg_ko_smarts.json")

_FALLBACK_GROUP_DEFS: list[dict[str, Any]] = [
    {"en": "hydrogen", "smarts_pattern": "[H]", "smarts_replacement": "[H]", "ko": ["수소"]},
    {"en": "methyl", "smarts_pattern": "[CH3]", "smarts_replacement": "C", "ko": ["메틸", "메틸기"]},
    {"en": "ethyl", "smarts_pattern": "[CH2][CH3]", "smarts_replacement": "CC", "ko": ["에틸", "에틸기"]},
    {"en": "propyl", "smarts_pattern": "[CH2][CH2][CH3]", "smarts_replacement": "CCC", "ko": ["프로필", "프로필기"]},
    {"en": "isopropyl", "smarts_pattern": "[CH]([CH3])[CH3]", "smarts_replacement": "C(C)C", "ko": ["아이소프로필"]},
    {"en": "tert-butyl", "smarts_pattern": "[CX4]([CH3])([CH3])[CH3]", "smarts_replacement": "C(C)(C)C", "ko": ["터트부틸", "tert-부틸"]},
    {"en": "hydroxy", "smarts_pattern": "[OX2H]", "smarts_replacement": "O", "ko": ["하이드록시", "수산기"]},
    {"en": "methoxy", "smarts_pattern": "[OX2][CH3]", "smarts_replacement": "OC", "ko": ["메톡시"]},
    {"en": "carboxyl", "smarts_pattern": "[CX3](=O)[OX2H1]", "smarts_replacement": "C(=O)O", "ko": ["카복실", "카복실기"]},
    {"en": "formyl", "smarts_pattern": "[CX3H1](=O)", "smarts_replacement": "C=O", "ko": ["포밀", "알데하이드기"]},
    {"en": "carbonyl", "smarts_pattern": "[#6][CX3](=O)[#6]", "smarts_replacement": "C(=O)", "ko": ["카보닐", "케톤기"]},
    {"en": "acetyl", "smarts_pattern": "[CX3](=O)[CH3]", "smarts_replacement": "C(=O)C", "ko": ["아세틸", "아세틸기"]},
    {"en": "ester", "smarts_pattern": "[#6][CX3](=O)[OX2H0][#6]", "smarts_replacement": "C(=O)OC", "ko": ["에스터"]},
    {"en": "amino", "smarts_pattern": "[NX3;H2;!$(NC=O)]", "smarts_replacement": "N", "ko": ["아미노", "아미노기"]},
    {"en": "nitro", "smarts_pattern": "[$([NX3](=O)=O),$([NX3+](=O)[O-])]", "smarts_replacement": "[N+](=O)[O-]", "ko": ["니트로", "니트로기"]},
    {"en": "cyano", "smarts_pattern": "[CX2]#[NX1]", "smarts_replacement": "C#N", "ko": ["시아노", "사이아노"]},
    {"en": "amide", "smarts_pattern": "[CX3](=O)[NX3H2]", "smarts_replacement": "C(=O)N", "ko": ["아마이드"]},
    {"en": "fluoro", "smarts_pattern": "[F]", "smarts_replacement": "F", "ko": ["플루오로", "불소기"]},
    {"en": "chloro", "smarts_pattern": "[Cl]", "smarts_replacement": "Cl", "ko": ["클로로", "염소기"]},
    {"en": "bromo", "smarts_pattern": "[Br]", "smarts_replacement": "Br", "ko": ["브로모", "브롬기"]},
    {"en": "iodo", "smarts_pattern": "[I]", "smarts_replacement": "I", "ko": ["아이오도", "요오드기"]},
    {"en": "trifluoromethyl", "smarts_pattern": "[CX4](F)(F)F", "smarts_replacement": "C(F)(F)F", "ko": ["트리플루오로메틸", "CF3"]},
    {"en": "thiol", "smarts_pattern": "[#16X2H]", "smarts_replacement": "S", "ko": ["티올", "설파하이드릴"]},
    {"en": "sulfonyl", "smarts_pattern": "[#16X4](=[OX1])(=[OX1])", "smarts_replacement": "S(=O)(=O)", "ko": ["설포닐"]},
    {"en": "phenyl", "smarts_pattern": "c1ccccc1", "smarts_replacement": "c1ccccc1", "ko": ["페닐", "Ph"]},
    {"en": "benzyl", "smarts_pattern": "[CH2]c1ccccc1", "smarts_replacement": "Cc1ccccc1", "ko": ["벤질"]},
    {"en": "vinyl", "smarts_pattern": "[CH]=[CH2]", "smarts_replacement": "C=C", "ko": ["비닐"]},
    {"en": "ethynyl", "smarts_pattern": "[CX2]#[CH]", "smarts_replacement": "C#C", "ko": ["에티닐"]},
    {"en": "phosphoryl", "smarts_pattern": "[PX4](=O)([OX2])([OX2])[OX2]", "smarts_replacement": "P(=O)(O)(O)O", "ko": ["포스포릴", "인산기"]},
]


def _normalize_group_defs(raw_defs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in raw_defs:
        if not isinstance(row, dict):
            continue
        en = str(row.get("en") or "").strip().lower()
        smarts = str(row.get("smarts_pattern") or "").strip()
        replacement = str(row.get("smarts_replacement") or row.get("replacement_smiles") or "").strip()
        if not en or not smarts:
            continue
        if not replacement:
            replacement = "C"
        ko_aliases = [str(item).strip() for item in list(row.get("ko") or []) if str(item).strip()]
        normalized.append(
            {
                "en": en,
                "smarts_pattern": smarts,
                "smarts_replacement": replacement,
                "ko": ko_aliases,
                "category": str(row.get("category") or "").strip().lower() or "generic",
            }
        )
    return normalized


def _load_group_defs() -> list[dict[str, Any]]:
    fallback = _normalize_group_defs(_FALLBACK_GROUP_DEFS)
    try:
        if not _FG_DICT_PATH.exists():
            return fallback
        loaded = json.loads(_FG_DICT_PATH.read_text(encoding="utf-8"))
        fg_rows = loaded.get("functional_groups")
        if not isinstance(fg_rows, list):
            return fallback
        normalized = _normalize_group_defs(list(fg_rows))
        return normalized or fallback
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Failed to load %s: %s", _FG_DICT_PATH.name, exc)
        return fallback


_GROUP_DEFS = _load_group_defs()

SUBSTITUENT_SMARTS: dict[str, dict[str, Any]] = {
    row["en"]: {
        "smarts": row["smarts_pattern"],
        "replacement_smiles": row["smarts_replacement"],
        "display_name_ko": ", ".join(row.get("ko") or []),
        "display_name_en": row["en"],
        "category": row.get("category") or "generic",
    }
    for row in _GROUP_DEFS
}

_GROUP_KEY_TO_SMILES = {
    key: str(meta.get("replacement_smiles") or "C")
    for key, meta in SUBSTITUENT_SMARTS.items()
}


def _normalize_group_key(key: str) -> str:
    return str(key or "").strip().lower()


def _group_smarts(group_key: str) -> str:
    key = _normalize_group_key(group_key)
    if key not in SUBSTITUENT_SMARTS:
        return ""
    return str(SUBSTITUENT_SMARTS[key].get("smarts") or "").strip()


def _group_replacement_smiles(group_key: str) -> str:
    key = _normalize_group_key(group_key)
    return str(_GROUP_KEY_TO_SMILES.get(key) or "").strip()


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
    smiles = _group_replacement_smiles(key)
    return smiles or "C"


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
    if symbol == "I":
        return "iodo"
    return None


def _label_hydrogen_sites(mol: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    mol_h = Chem.AddHs(mol)
    for idx, atom in enumerate(mol_h.GetAtoms(), start=1):
        if atom.GetSymbol() != "H" or atom.GetDegree() != 1:
            continue
        parent = atom.GetNeighbors()[0]
        bond = atom.GetBonds()[0]
        out.append(
            {
                "position": idx,
                "atom_idx": atom.GetIdx(),
                "match_atom_indices": [atom.GetIdx()],
                "parent_atom_idx": parent.GetIdx(),
                "ring_member": bool(parent.IsInRing()),
                "position_description": f"hydrogen site {idx} (H atom {atom.GetIdx()})",
                "anchor_symbol": "H",
                "anchor_bond_type": str(bond.GetBondType()).split(".")[-1],
            }
        )
    return out


def label_match_sites(smiles: str, group_name: str) -> list[dict[str, Any]]:
    """Return match-site labels for a substituent SMARTS group."""
    if not _RDKIT_AVAILABLE:
        return []

    group_key = _normalize_group_key(group_name)
    if group_key not in SUBSTITUENT_SMARTS:
        return []

    mol = _validate_smiles(smiles)
    if mol is None:
        return []

    if group_key == "hydrogen":
        return _label_hydrogen_sites(mol)

    pattern_smarts = _group_smarts(group_key)
    pattern = Chem.MolFromSmarts(pattern_smarts) if pattern_smarts else None
    if pattern is None:
        return []

    out: list[dict[str, Any]] = []
    matches = list(mol.GetSubstructMatches(pattern, uniquify=True))
    for idx, match in enumerate(matches, start=1):
        if not match:
            continue
        anchor_idx = int(match[0])
        anchor_atom = mol.GetAtomWithIdx(anchor_idx)
        out.append(
            {
                "position": idx,
                "atom_idx": anchor_idx,
                "match_atom_indices": [int(atom_idx) for atom_idx in match],
                "parent_atom_idx": (
                    int(anchor_atom.GetNeighbors()[0].GetIdx())
                    if anchor_atom.GetNeighbors()
                    else None
                ),
                "ring_member": bool(anchor_atom.IsInRing()),
                "position_description": f"{group_key} site {idx} (atom {anchor_idx})",
                "anchor_symbol": str(anchor_atom.GetSymbol()),
                "anchor_bond_type": (
                    str(anchor_atom.GetBonds()[0].GetBondType()).split(".")[-1]
                    if anchor_atom.GetBonds()
                    else ""
                ),
            }
        )
    return out


def identify_substituents(smiles: str) -> list[dict[str, Any]]:
    """Identify replaceable substituent positions and annotate them."""
    if not _RDKIT_AVAILABLE:
        logger.warning("identify_substituents: RDKit not available")
        return []

    mol = _validate_smiles(smiles)
    if mol is None:
        return []

    results: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, tuple[int, ...]]] = set()

    for group_key in SUBSTITUENT_SMARTS.keys():
        for site in label_match_sites(smiles, group_key):
            match_ids = tuple(int(item) for item in list(site.get("match_atom_indices") or []))
            dedupe_key = (group_key, match_ids)
            if dedupe_key in seen_keys:
                continue
            seen_keys.add(dedupe_key)
            results.append(
                {
                    "atom_idx": int(site.get("atom_idx", -1)),
                    "current_group": group_key,
                    "symbol": str(site.get("anchor_symbol") or ""),
                    "bond_type": str(site.get("anchor_bond_type") or ""),
                    "ring_member": bool(site.get("ring_member", False)),
                    "parent_atom_idx": site.get("parent_atom_idx"),
                    "position": int(site.get("position", 0) or 0),
                    "match_atom_indices": list(site.get("match_atom_indices") or []),
                }
            )

    # Keep simple terminal-group heuristic too for robust fallback behavior.
    for atom in mol.GetAtoms():
        group_key = _terminal_group_key(atom)
        if not group_key:
            continue
        if atom.GetDegree() != 1:
            continue
        match_ids = (int(atom.GetIdx()),)
        dedupe_key = (group_key, match_ids)
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
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
                "position": 0,
                "match_atom_indices": [atom.GetIdx()],
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


def _replace_substructure(
    base_smiles: str,
    from_group: str,
    to_group: str,
    *,
    replace_all: bool,
) -> list[str]:
    base_mol = _validate_smiles(base_smiles)
    if base_mol is None:
        return []
    query_smarts = _group_smarts(from_group)
    replacement_smiles = _group_replacement_smiles(to_group)
    if not query_smarts or not replacement_smiles:
        return []
    query = Chem.MolFromSmarts(query_smarts)
    replacement = Chem.MolFromSmiles(replacement_smiles)
    if query is None or replacement is None:
        return []

    out: list[str] = []
    seen: set[str] = set()
    try:
        products = Chem.ReplaceSubstructs(base_mol, query, replacement, replaceAll=replace_all)
    except Exception:
        products = []
    for candidate in list(products or []):
        try:
            Chem.SanitizeMol(candidate)
            canonical = Chem.MolToSmiles(candidate, canonical=True)
        except Exception:
            continue
        if not canonical or canonical in seen:
            continue
        seen.add(canonical)
        out.append(canonical)
    return out


def _aromatic_hydrogen_reaction_candidates(
    base_smiles: str,
    to_group: str,
    *,
    max_candidates: int,
) -> list[str]:
    """Fallback aromatic C-H substitution using RDKit reaction SMARTS."""
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
    group_key = _normalize_group_key(new_group_key)
    if group_key not in SUBSTITUENT_SMARTS:
        logger.warning("swap_substituent: unknown substituent key %s", new_group_key)
        return None

    hydrogen_result = _swap_hydrogen_site(smiles, atom_idx, group_key)
    if hydrogen_result is not None:
        return hydrogen_result
    return _swap_terminal_group(smiles, atom_idx, group_key)


def _safe_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except Exception:
        return None


def _count_group_matches(mol: Any, group_key: str) -> int:
    if group_key == "hydrogen":
        mol_h = Chem.AddHs(mol)
        return sum(1 for atom in mol_h.GetAtoms() if atom.GetSymbol() == "H" and atom.GetDegree() == 1)
    query = Chem.MolFromSmarts(_group_smarts(group_key))
    if query is None:
        return 0
    return int(len(list(mol.GetSubstructMatches(query, uniquify=True))))


def validate_substitution_result(
    base_smiles: str,
    modified_smiles: str,
    from_group: str,
    to_group: str,
) -> dict[str, Any]:
    """Validate that substitution output is chemically usable and plausible."""
    out: dict[str, Any] = {
        "is_valid": False,
        "removed_group_absent": None,
        "added_group_present": None,
        "warnings": [],
    }
    base_mol = _validate_smiles(base_smiles)
    mod_mol = _validate_smiles(modified_smiles)
    if base_mol is None or mod_mol is None:
        out["warnings"].append("invalid_smiles_after_substitution")
        return out

    from_key = _normalize_group_key(from_group)
    to_key = _normalize_group_key(to_group)
    base_from_count = _count_group_matches(base_mol, from_key)
    mod_from_count = _count_group_matches(mod_mol, from_key)
    mod_to_count = _count_group_matches(mod_mol, to_key)

    if from_key == "hydrogen":
        removed_group_absent = None
    else:
        removed_group_absent = mod_from_count < base_from_count
    added_group_present = mod_to_count > 0

    out["removed_group_absent"] = removed_group_absent
    out["added_group_present"] = added_group_present
    out["heavy_atom_delta"] = int(mod_mol.GetNumHeavyAtoms() - base_mol.GetNumHeavyAtoms())
    out["is_valid"] = bool(added_group_present and (removed_group_absent is not False))

    if removed_group_absent is False:
        out["warnings"].append("from_group_still_present")
    if not added_group_present:
        out["warnings"].append("to_group_not_detected")
    if out["heavy_atom_delta"] > 20:
        out["warnings"].append("large_structural_jump")
    return out


def _candidate_position_indexes(
    total_sites: int,
    *,
    target_position: int | None,
    replace_all: bool,
    max_candidates: int,
) -> list[int]:
    if total_sites <= 0:
        return []
    if replace_all:
        return [0]
    if target_position is not None:
        index = max(1, int(target_position)) - 1
        if 0 <= index < total_sites:
            return [index]
        return []
    return list(range(min(total_sites, max(1, int(max_candidates)))))


def _replace_for_position(
    base_smiles: str,
    from_group: str,
    to_group: str,
    *,
    site_index: int,
    site_atom_idx: int | None,
) -> str | None:
    if from_group == "hydrogen":
        if site_atom_idx is not None and site_atom_idx >= 0:
            swapped = swap_substituent(base_smiles, int(site_atom_idx), to_group)
            if swapped:
                return swapped
        aromatic = _aromatic_hydrogen_reaction_candidates(
            base_smiles,
            to_group,
            max_candidates=max(1, site_index + 1),
        )
        if site_index < len(aromatic):
            return aromatic[site_index]
        if aromatic:
            return aromatic[0]
        return None

    substruct_candidates = _replace_substructure(
        base_smiles,
        from_group,
        to_group,
        replace_all=False,
    )
    if site_index < len(substruct_candidates):
        return substruct_candidates[site_index]
    if substruct_candidates:
        return substruct_candidates[0]

    # Final fallback for terminal-like positions.
    if site_atom_idx is not None and site_atom_idx >= 0:
        return swap_substituent(base_smiles, int(site_atom_idx), to_group)
    return None


def generate_modification_candidates(
    base_smiles: str,
    from_group: str,
    to_group: str,
    *,
    max_candidates: int = _DEFAULT_MAX_CANDIDATES,
    target_position: int | None = None,
    replace_all: bool = False,
) -> list[dict[str, Any]]:
    """Generate unique candidate molecules for substituent replacement."""
    if not _RDKIT_AVAILABLE:
        logger.warning("generate_modification_candidates: RDKit not available")
        return []

    from_key = _normalize_group_key(from_group)
    to_key = _normalize_group_key(to_group)
    if from_key not in SUBSTITUENT_SMARTS or to_key not in SUBSTITUENT_SMARTS:
        err = ModificationError(
            "Unknown substituent key",
            base_smiles=base_smiles,
            from_group=from_group,
            to_group=to_group,
        )
        logger.warning("generate_modification_candidates: %s", err)
        return []
    if from_key == to_key:
        return []
    if _validate_smiles(base_smiles) is None:
        return []

    candidates: list[dict[str, Any]] = []
    seen_smiles: set[str] = set()
    labeled_sites = label_match_sites(base_smiles, from_key)

    if replace_all:
        all_smiles: str | None = None
        if from_key != "hydrogen":
            replaced_all = _replace_substructure(base_smiles, from_key, to_key, replace_all=True)
            if replaced_all:
                all_smiles = replaced_all[0]
        canonical = _canonicalize_smiles(all_smiles or "")
        if canonical and canonical not in seen_smiles:
            validation = validate_substitution_result(base_smiles, canonical, from_key, to_key)
            if validation.get("is_valid"):
                seen_smiles.add(canonical)
                candidates.append(
                    {
                        "candidate_smiles": canonical,
                        "position_description": f"Replace all {from_key} groups with {to_key}",
                        "atom_idx": -1,
                        "site_index": 0,
                        "from_group": from_key,
                        "to_group": to_key,
                        "replace_all": True,
                        "target_position": None,
                        "property_delta": preview_property_delta(base_smiles, canonical),
                        "validation": validation,
                    }
                )

    if not replace_all:
        indexes = _candidate_position_indexes(
            len(labeled_sites),
            target_position=target_position,
            replace_all=False,
            max_candidates=max_candidates,
        )
        for index in indexes:
            site = labeled_sites[index]
            site_atom_idx = _safe_int(site.get("atom_idx"))
            candidate_smiles = _replace_for_position(
                base_smiles,
                from_key,
                to_key,
                site_index=index,
                site_atom_idx=site_atom_idx,
            )
            canonical = _canonicalize_smiles(candidate_smiles or "")
            if not canonical or canonical in seen_smiles:
                continue
            validation = validate_substitution_result(base_smiles, canonical, from_key, to_key)
            if not validation.get("is_valid"):
                continue
            seen_smiles.add(canonical)
            candidates.append(
                {
                    "candidate_smiles": canonical,
                    "position_description": str(site.get("position_description") or ""),
                    "atom_idx": int(site_atom_idx or -1),
                    "site_index": int(site.get("position", index + 1)),
                    "from_group": from_key,
                    "to_group": to_key,
                    "replace_all": False,
                    "target_position": int(site.get("position", index + 1)),
                    "property_delta": preview_property_delta(base_smiles, canonical),
                    "validation": validation,
                }
            )
            if len(candidates) >= max(1, int(max_candidates)):
                break

    if not candidates and from_key == "hydrogen" and to_key != "hydrogen":
        for idx, canonical in enumerate(
            _aromatic_hydrogen_reaction_candidates(
                base_smiles,
                to_key,
                max_candidates=max_candidates,
            ),
            start=1,
        ):
            if canonical in seen_smiles:
                continue
            validation = validate_substitution_result(base_smiles, canonical, from_key, to_key)
            if not validation.get("is_valid"):
                continue
            seen_smiles.add(canonical)
            candidates.append(
                {
                    "candidate_smiles": canonical,
                    "position_description": f"Replace aromatic hydrogen with {to_key} (site {idx})",
                    "atom_idx": -1,
                    "site_index": idx,
                    "from_group": from_key,
                    "to_group": to_key,
                    "replace_all": False,
                    "target_position": idx,
                    "property_delta": preview_property_delta(base_smiles, canonical),
                    "validation": validation,
                }
            )
            if len(candidates) >= max(1, int(max_candidates)):
                break

    logger.info(
        "generate_modification_candidates(%s, %s -> %s): %d candidates (replace_all=%s, target_position=%s)",
        base_smiles[:40],
        from_key,
        to_key,
        len(candidates),
        replace_all,
        target_position,
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
    "label_match_sites",
    "generate_modification_candidates",
    "validate_substitution_result",
    "preview_property_delta",
]
