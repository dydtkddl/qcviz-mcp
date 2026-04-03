"""Boundary-safe Korean molecule and substituent alias translation helpers."""

from __future__ import annotations

import re
from importlib import import_module
from typing import Dict, Optional

_SUBSCRIPT_MAP = str.maketrans(
    {
        "₀": "0",
        "₁": "1",
        "₂": "2",
        "₃": "3",
        "₄": "4",
        "₅": "5",
        "₆": "6",
        "₇": "7",
        "₈": "8",
        "₉": "9",
        "₋": "-",
        "⁻": "-",
        "−": "-",
        "–": "-",
        "—": "-",
        "‑": "-",
        "﹣": "-",
        "－": "-",
    }
)
_UNICODE_DASH_RE = re.compile(r"[−–—‑﹣－]")

_KO_BOUNDARY = r"[가-힣A-Za-z0-9]"
_KO_PARTICLE_SUFFIXES = tuple(
    sorted(
        (
            "에서",
            "으로",
            "로",
            "의",
            "을",
            "를",
            "은",
            "는",
            "이",
            "가",
            "에",
            "과",
            "와",
            "도",
            "만",
            "까지",
            "부터",
            "랑",
            "이랑",
        ),
        key=len,
        reverse=True,
    )
)
_KO_PARTICLE_PATTERN = "(?:" + "|".join(re.escape(item) for item in _KO_PARTICLE_SUFFIXES) + ")?"


def _normalize_formula_text(text: str) -> str:
    result = str(text or "").translate(_SUBSCRIPT_MAP)
    result = _UNICODE_DASH_RE.sub("-", result)
    result = re.sub(r"\s*/+\s*$", "", result).strip()
    return result


_KO_TO_EN_CACHE: Optional[Dict[str, str]] = None


def _load_ko_to_en() -> Dict[str, str]:
    global _KO_TO_EN_CACHE
    if _KO_TO_EN_CACHE is not None:
        return _KO_TO_EN_CACHE
    module = import_module("qcviz_mcp.llm.normalizer")
    _KO_TO_EN_CACHE = getattr(module, "KO_TO_EN", {})
    return _KO_TO_EN_CACHE


KO_TO_EN: Dict[str, str] = _load_ko_to_en()


def _alias_pattern(ko_name: str) -> re.Pattern[str]:
    escaped = re.escape(ko_name)
    return re.compile(
        rf"(?<!{_KO_BOUNDARY})({escaped}){_KO_PARTICLE_PATTERN}(?!{_KO_BOUNDARY})"
    )


SUBSTITUENT_KO_TO_EN: Dict[str, str] = {
    # Korean aliases
    "메틸": "methyl",
    "메틸기": "methyl",
    "에틸": "ethyl",
    "에틸기": "ethyl",
    "프로필": "propyl",
    "프로필기": "propyl",
    "부틸": "butyl",
    "부틸기": "butyl",
    "하이드록시": "hydroxy",
    "하이드록시기": "hydroxy",
    "아미노": "amino",
    "아미노기": "amino",
    "니트로": "nitro",
    "니트로기": "nitro",
    "시아노": "cyano",
    "시아노기": "cyano",
    "플루오로": "fluoro",
    "플루오로기": "fluoro",
    "클로로": "chloro",
    "클로로기": "chloro",
    "브로모": "bromo",
    "브로모기": "bromo",
    "아이오도": "iodo",
    "아이오도기": "iodo",
    "아이소프로필": "isopropyl",
    "이소프로필": "isopropyl",
    "아이소프로필기": "isopropyl",
    "터트부틸": "tert-butyl",
    "tert-부틸": "tert-butyl",
    "t-부틸": "tert-butyl",
    "페닐": "phenyl",
    "페닐기": "phenyl",
    "벤질": "benzyl",
    "벤질기": "benzyl",
    "카복실": "carboxyl",
    "카복실기": "carboxyl",
    "카보닐": "carbonyl",
    "카보닐기": "carbonyl",
    "에스터": "ester",
    "에스터기": "ester",
    "아마이드": "amide",
    "아마이드기": "amide",
    "포르밀": "formyl",
    "포르밀기": "formyl",
    "아세틸": "acetyl",
    "아세틸기": "acetyl",
    "메톡시": "methoxy",
    "에톡시": "ethoxy",
    "트리플루오로메틸": "trifluoromethyl",
    "트리플루오로메틸기": "trifluoromethyl",
    "cf3": "trifluoromethyl",
    "티올": "thiol",
    "티올기": "thiol",
    "설파하이드릴": "thiol",
    "설파하이드릴기": "thiol",
    "머캡토": "thiol",
    "설포닐": "sulfonyl",
    "설포닐기": "sulfonyl",
    "술포닐": "sulfonyl",
    "비닐": "vinyl",
    "비닐기": "vinyl",
    "에테닐": "vinyl",
    "에티닐": "ethynyl",
    "에티닐기": "ethynyl",
    "포스포릴": "phosphoryl",
    "포스포릴기": "phosphoryl",
    "인산기": "phosphoryl",
    "수소": "hydrogen",
    # English aliases
    "hydrogen": "hydrogen",
    "hydroxy": "hydroxy",
    "hydroxyl": "hydroxy",
    "amino": "amino",
    "nitro": "nitro",
    "cyano": "cyano",
    "fluoro": "fluoro",
    "chloro": "chloro",
    "bromo": "bromo",
    "iodo": "iodo",
    "formyl": "formyl",
    "acetyl": "acetyl",
    "phenyl": "phenyl",
    "vinyl": "vinyl",
    "methoxy": "methoxy",
    "ethoxy": "ethoxy",
    "methyl": "methyl",
    "ethyl": "ethyl",
    "propyl": "propyl",
    "butyl": "butyl",
    "isopropyl": "isopropyl",
    "tert-butyl": "tert-butyl",
    "carboxyl": "carboxyl",
    "carbonyl": "carbonyl",
    "ester": "ester",
    "amide": "amide",
    "benzyl": "benzyl",
    "trifluoromethyl": "trifluoromethyl",
    "thiol": "thiol",
    "sulfonyl": "sulfonyl",
    "vinyl": "vinyl",
    "ethynyl": "ethynyl",
    "phosphoryl": "phosphoryl",
}

_SUBSTITUENT_PARTICLES = tuple(
    sorted(
        (
            "기를",
            "기",
            "으로",
            "로",
            "에서",
            "에",
            "은",
            "는",
            "이",
            "가",
            "을",
            "를",
            "과",
            "와",
            "도",
            "만",
            "까지",
            "부터",
            "랑",
            "이랑",
        ),
        key=len,
        reverse=True,
    )
)


def _normalize_substituent(text: str) -> str:
    candidate = _normalize_formula_text(str(text or "")).strip().lower()
    candidate = re.sub(r"[\"'`\[\]{}()?,.!;:]+", "", candidate)
    candidate = re.sub(r"\s+", "", candidate)
    return candidate


def _strip_substituent_particles(text: str) -> str:
    value = _normalize_substituent(text)
    if not value:
        return ""
    changed = True
    while changed and value:
        changed = False
        for particle in _SUBSTITUENT_PARTICLES:
            if value.endswith(particle):
                value = value[: -len(particle)]
                changed = True
                break
    return value


def translate_substituent(text: str) -> Optional[str]:
    """Translate a Korean substituent name to the canonical group key."""
    cleaned = _strip_substituent_particles(text)
    if not cleaned:
        return None

    exact = SUBSTITUENT_KO_TO_EN.get(cleaned)
    if exact:
        return exact

    # Guard molecule names that belong to the molecule alias map.
    aliases = _load_ko_to_en()
    if cleaned in aliases:
        return None

    return None


def translate(text: str) -> str:
    """Translate Korean molecule aliases only when they appear as standalone names."""
    if not text or not text.strip():
        return text

    result = _normalize_formula_text(text.strip())
    for ko_name, en_name in sorted(_load_ko_to_en().items(), key=lambda item: len(item[0]), reverse=True):
        result = _alias_pattern(ko_name).sub(en_name, result)
    return result.strip()


def find_molecule_name(text: str) -> Optional[str]:
    """Return the English alias for a standalone Korean molecule mention."""
    if not text or not text.strip():
        return None

    cleaned = _normalize_formula_text(text.strip())
    for ko_name, en_name in sorted(_load_ko_to_en().items(), key=lambda item: len(item[0]), reverse=True):
        if _alias_pattern(ko_name).search(cleaned):
            return en_name
    return None
