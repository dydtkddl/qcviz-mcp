# 기능기 치환 설계 가이드 검증 + 실행 코드

## Part 0. 설계 가이드 검증 결과

### ✅ 맞는 부분 (인정)

| # | 주장 | 검증 |
|---|------|------|
| 1 | 치환은 검색이 아니라 구조 편집 워크플로 | ✅ 정확. structure_intelligence.py가 이미 이 패러다임 |
| 2 | 의도 파싱에서 대상분자/제거기/추가기/위치 4슬롯 필요 | ✅ 정확. ModificationIntent(schemas.py)에 from_group, to_group, position_hint, base_molecule 이미 존재 |
| 3 | 다중 매칭 시 disambiguation 필요 | ✅ 정확. 현재 position_hint가 있지만 실제 site labeling은 미흡 |
| 4 | 치환 후 원본 vs 결과 비교 필수 | ✅ 정확. preview_property_delta()가 이미 존재 |
| 5 | 한글 기능기 별칭 사전 필요 | ✅ 정확. ko_aliases.py에 SUBSTITUENT_KO_TO_EN(55개)은 있지만, SMARTS 직결 매핑이 없음 |
| 6 | Reaction SMARTS가 aromatic 치환에 유용 | ✅ 부분 정확. _aromatic_hydrogen_reaction_candidates()가 이미 존재 |
| 7 | Sanitization/Kekulization 실패 대비 필요 | ✅ 정확 |

### ❌ 틀린 부분 (수정 필요)

| # | 주장 | 실제 |
|---|------|------|
| 1 | "기능기 치환 전용 도구가 전혀 없다" | ❌ **이미 존재**: identify_substituents(), swap_substituent(), generate_modification_candidates(), preview_property_delta() in structure_intelligence.py |
| 2 | "RDKitHandler에 구조 편집 메서드가 하나도 없다" | ❌ structure_intelligence.py가 별도 모듈로 이미 RDKit 편집 담당 |
| 3 | "backend/app/services/intelligence/tools/에 등록" | ❌ 이 리포는 MolChat이 아님. QCViz-MCP의 구조: src/qcviz_mcp/services/ + llm/pipeline lane 구조 |
| 4 | "도구 7개만 등록" | ❌ QCViz는 tool registry가 아니라 PlannerLane + grounding + execution 흐름 |
| 5 | "새 도구를 만들어야" | ⚠️ 과도. 기존 modification_exploration lane 강화가 우선 |
| 6 | "Pan et al. (2026)" 인용 | ❌ 1차 출처 검증 불가. 근거로 사용 부적절 |
| 7 | "RDKit 이슈 #8069, #3155" | ⚠️ 현상 자체는 알려져 있으나, 이슈 번호 정확성 미확인 |

### 🎯 실제 우선순위 (딥스캔 기반)

1. **normalizer.py의 한글 modification intent 정규식 보강** — 현재 4개 패턴만 있고 커버리지 부족
2. **structure_intelligence.py의 SUBSTITUENT_SMARTS 확장** — 현재 13개 → 30+개로
3. **fg_ko_smarts.json 신규 생성** — 한글 기능기명 → SMARTS 직결 매핑
4. **site labeling 개선** — 다중 매칭 시 사용자에게 의미있는 위치 설명 제공
5. **grounding_merge.py의 modification 분기 안정화** — active molecule 있을 때 semantic grounding 우회

---

## Part 1. 신규 파일: fg_ko_smarts.json

**위치**: `version04/src/qcviz_mcp/services/fg_ko_smarts.json`

이 파일은 한글 기능기명 → 영어명 → SMARTS 패턴을 직결 매핑합니다.
현재 ko_aliases.py의 SUBSTITUENT_KO_TO_EN(55개)은 이름 번역만 하고,
structure_intelligence.py의 SUBSTITUENT_SMARTS(13개)는 영어만 지원합니다.
이 두 개를 하나로 연결하는 브릿지 파일입니다.

```json
{
  "_meta": {
    "version": "1.0.0",
    "description": "한글 기능기명 → 영어 canonical → SMARTS 패턴 통합 사전",
    "usage": "structure_intelligence.py, normalizer.py에서 import하여 사용"
  },
  "functional_groups": [
    {
      "ko": ["수소", "하이드로겐", "H"],
      "en": "hydrogen",
      "smarts_pattern": "[H]",
      "smarts_replacement": "[H]",
      "category": "atom"
    },
    {
      "ko": ["메틸기", "메틸", "CH3"],
      "en": "methyl",
      "smarts_pattern": "[CH3]",
      "smarts_replacement": "[CH3]",
      "category": "alkyl"
    },
    {
      "ko": ["에틸기", "에틸", "C2H5"],
      "en": "ethyl",
      "smarts_pattern": "[CH2][CH3]",
      "smarts_replacement": "CC",
      "category": "alkyl"
    },
    {
      "ko": ["프로필기", "프로필", "n-프로필"],
      "en": "propyl",
      "smarts_pattern": "[CH2][CH2][CH3]",
      "smarts_replacement": "CCC",
      "category": "alkyl"
    },
    {
      "ko": ["이소프로필기", "이소프로필", "아이소프로필"],
      "en": "isopropyl",
      "smarts_pattern": "[CH]([CH3])[CH3]",
      "smarts_replacement": "C(C)C",
      "category": "alkyl"
    },
    {
      "ko": ["tert-부틸기", "터트부틸", "t-부틸"],
      "en": "tert-butyl",
      "smarts_pattern": "[CX4]([CH3])([CH3])[CH3]",
      "smarts_replacement": "C(C)(C)C",
      "category": "alkyl"
    },
    {
      "ko": ["하이드록시기", "하이드록실기", "수산기", "히드록시", "OH기"],
      "en": "hydroxy",
      "smarts_pattern": "[OX2H]",
      "smarts_replacement": "O",
      "category": "oxygen"
    },
    {
      "ko": ["메톡시기", "메톡시", "OCH3"],
      "en": "methoxy",
      "smarts_pattern": "[OX2][CH3]",
      "smarts_replacement": "OC",
      "category": "oxygen"
    },
    {
      "ko": ["카르복실기", "카르복시기", "COOH기", "카복실"],
      "en": "carboxyl",
      "smarts_pattern": "[CX3](=O)[OX2H1]",
      "smarts_replacement": "C(=O)O",
      "category": "oxygen"
    },
    {
      "ko": ["알데히드기", "알데하이드기", "포르밀기", "CHO기"],
      "en": "formyl",
      "smarts_pattern": "[CX3H1](=O)",
      "smarts_replacement": "C=O",
      "category": "oxygen"
    },
    {
      "ko": ["케톤기", "카르보닐기", "C=O기"],
      "en": "carbonyl",
      "smarts_pattern": "[#6][CX3](=O)[#6]",
      "smarts_replacement": "C(=O)",
      "category": "oxygen"
    },
    {
      "ko": ["아세틸기", "아세틸", "COCH3기"],
      "en": "acetyl",
      "smarts_pattern": "[CX3](=O)[CH3]",
      "smarts_replacement": "C(=O)C",
      "category": "oxygen"
    },
    {
      "ko": ["에스테르기", "에스터기", "COO기"],
      "en": "ester",
      "smarts_pattern": "[#6][CX3](=O)[OX2H0][#6]",
      "smarts_replacement": "C(=O)OC",
      "category": "oxygen"
    },
    {
      "ko": ["아미노기", "아민기", "1차아민", "NH2기"],
      "en": "amino",
      "smarts_pattern": "[NX3;H2;!$(NC=O)]",
      "smarts_replacement": "N",
      "category": "nitrogen"
    },
    {
      "ko": ["나이트로기", "니트로기", "NO2기"],
      "en": "nitro",
      "smarts_pattern": "[$([NX3](=O)=O),$([NX3+](=O)[O-])]",
      "smarts_replacement": "[N+](=O)[O-]",
      "category": "nitrogen"
    },
    {
      "ko": ["시아노기", "니트릴기", "CN기"],
      "en": "cyano",
      "smarts_pattern": "[CX2]#[NX1]",
      "smarts_replacement": "C#N",
      "category": "nitrogen"
    },
    {
      "ko": ["아마이드기", "아미드기", "CONH2기"],
      "en": "amide",
      "smarts_pattern": "[CX3](=O)[NX3H2]",
      "smarts_replacement": "C(=O)N",
      "category": "nitrogen"
    },
    {
      "ko": ["플루오로기", "플루오린", "불소기", "F기"],
      "en": "fluoro",
      "smarts_pattern": "[F]",
      "smarts_replacement": "F",
      "category": "halogen"
    },
    {
      "ko": ["클로로기", "클로린", "염소기", "Cl기"],
      "en": "chloro",
      "smarts_pattern": "[Cl]",
      "smarts_replacement": "Cl",
      "category": "halogen"
    },
    {
      "ko": ["브로모기", "브로민", "브롬기", "Br기"],
      "en": "bromo",
      "smarts_pattern": "[Br]",
      "smarts_replacement": "Br",
      "category": "halogen"
    },
    {
      "ko": ["아이오도기", "요오드기", "I기"],
      "en": "iodo",
      "smarts_pattern": "[I]",
      "smarts_replacement": "I",
      "category": "halogen"
    },
    {
      "ko": ["트리플루오로메틸기", "CF3기", "삼불화메틸"],
      "en": "trifluoromethyl",
      "smarts_pattern": "[CX4](F)(F)F",
      "smarts_replacement": "C(F)(F)F",
      "category": "halogen"
    },
    {
      "ko": ["티올기", "설프하이드릴기", "SH기", "머캅토기"],
      "en": "thiol",
      "smarts_pattern": "[#16X2H]",
      "smarts_replacement": "S",
      "category": "sulfur"
    },
    {
      "ko": ["설포닐기", "술포닐기", "SO2기"],
      "en": "sulfonyl",
      "smarts_pattern": "[#16X4](=[OX1])(=[OX1])",
      "smarts_replacement": "S(=O)(=O)",
      "category": "sulfur"
    },
    {
      "ko": ["페닐기", "벤젠기", "Ph기"],
      "en": "phenyl",
      "smarts_pattern": "c1ccccc1",
      "smarts_replacement": "c1ccccc1",
      "category": "aromatic"
    },
    {
      "ko": ["벤질기", "CH2Ph기"],
      "en": "benzyl",
      "smarts_pattern": "[CH2]c1ccccc1",
      "smarts_replacement": "Cc1ccccc1",
      "category": "aromatic"
    },
    {
      "ko": ["비닐기", "에테닐기", "CH=CH2기"],
      "en": "vinyl",
      "smarts_pattern": "[CH]=[CH2]",
      "smarts_replacement": "C=C",
      "category": "unsaturated"
    },
    {
      "ko": ["에틴일기", "아세틸렌기", "C≡CH기"],
      "en": "ethynyl",
      "smarts_pattern": "[CX2]#[CH]",
      "smarts_replacement": "C#C",
      "category": "unsaturated"
    },
    {
      "ko": ["포스포릴기", "인산기", "PO4기"],
      "en": "phosphoryl",
      "smarts_pattern": "[PX4](=O)([OX2])([OX2])[OX2]",
      "smarts_replacement": "P(=O)(O)(O)O",
      "category": "phosphorus"
    }
  ]
}
```

---

## Part 2. structure_intelligence.py 패치

### 2-A. SUBSTITUENT_SMARTS 확장 (기존 13개 → 29개)

**교체 대상**: `SUBSTITUENT_SMARTS = {` ... `}` 블록 전체

```python
# ── 기존 SUBSTITUENT_SMARTS 블록을 아래로 교체 ──────────────────────
import json
import pathlib

_FG_DICT_PATH = pathlib.Path(__file__).parent / "fg_ko_smarts.json"

def _load_fg_dictionary() -> dict[str, str]:
    """fg_ko_smarts.json에서 en → smarts_pattern 매핑 로드"""
    base = {
        "hydrogen": "[H]",
        "methyl": "[CH3]",
        "ethyl": "[CH2][CH3]",
        "propyl": "[CH2][CH2][CH3]",
        "isopropyl": "[CH]([CH3])[CH3]",
        "tert-butyl": "[CX4]([CH3])([CH3])[CH3]",
        "hydroxy": "[OX2H]",
        "methoxy": "[OX2][CH3]",
        "carboxyl": "[CX3](=O)[OX2H1]",
        "formyl": "[CX3H1](=O)",
        "acetyl": "[CX3](=O)[CH3]",
        "amino": "[NX3;H2;!$(NC=O)]",
        "nitro": "[$([NX3](=O)=O),$([NX3+](=O)[O-])]",
        "cyano": "[CX2]#[NX1]",
        "amide": "[CX3](=O)[NX3H2]",
        "fluoro": "[F]",
        "chloro": "[Cl]",
        "bromo": "[Br]",
        "iodo": "[I]",
        "trifluoromethyl": "[CX4](F)(F)F",
        "thiol": "[#16X2H]",
        "sulfonyl": "[#16X4](=[OX1])(=[OX1])",
        "phenyl": "c1ccccc1",
        "benzyl": "[CH2]c1ccccc1",
        "vinyl": "[CH]=[CH2]",
        "ethynyl": "[CX2]#[CH]",
        "ester": "[#6][CX3](=O)[OX2H0][#6]",
        "carbonyl": "[#6][CX3](=O)[#6]",
    }
    try:
        if _FG_DICT_PATH.exists():
            data = json.loads(_FG_DICT_PATH.read_text(encoding="utf-8"))
            for entry in data.get("functional_groups", []):
                en = entry.get("en", "")
                pat = entry.get("smarts_pattern", "")
                if en and pat:
                    base.setdefault(en, pat)
    except Exception:
        pass  # fallback to hardcoded
    return base

SUBSTITUENT_SMARTS: dict[str, str] = _load_fg_dictionary()
```

### 2-B. site labeling 함수 추가 (신규)

**위치**: `identify_substituents()` 함수 뒤에 추가

```python
def label_match_sites(
    smiles: str,
    group_name: str,
) -> list[dict]:
    """다중 매칭 시 각 위치를 사용자에게 의미있게 설명.
    
    Returns:
        [{"index": 0, "atom_indices": (3,), "label": "C3-OH (고리 내부)", 
          "neighbors": "C2, C4"}, ...]
    """
    if Chem is None:
        return []
    
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return []
    
    smarts_str = SUBSTITUENT_SMARTS.get(group_name.lower())
    if not smarts_str:
        return []
    
    pattern = Chem.MolFromSmarts(smarts_str)
    if pattern is None:
        return []
    
    matches = mol.GetSubstructMatches(pattern)
    if not matches:
        return []
    
    results = []
    for idx, match in enumerate(matches):
        anchor_idx = match[0]
        atom = mol.GetAtomWithIdx(anchor_idx)
        symbol = atom.GetSymbol()
        
        # 이웃 원자 정보
        neighbor_symbols = []
        for nbr in atom.GetNeighbors():
            nbr_sym = nbr.GetSymbol()
            nbr_idx = nbr.GetIdx()
            neighbor_symbols.append(f"{nbr_sym}{nbr_idx}")
        
        # 고리 내부인지 확인
        ring_info = mol.GetRingInfo()
        in_ring = ring_info.NumAtomRings(anchor_idx) > 0
        ring_label = "(고리 내부)" if in_ring else "(측쇄)"
        
        # 방향족 여부
        is_aromatic = atom.GetIsAromatic()
        arom_label = "[방향족]" if is_aromatic else ""
        
        label = (
            f"위치 {idx + 1}: {symbol}{anchor_idx}-{group_name} "
            f"{ring_label} {arom_label}".strip()
        )
        
        results.append({
            "index": idx,
            "atom_indices": tuple(match),
            "label": label,
            "neighbors": ", ".join(neighbor_symbols),
            "in_ring": in_ring,
            "is_aromatic": is_aromatic,
        })
    
    return results
```

### 2-C. generate_modification_candidates 보강 — replaceAll 옵션

**교체 대상**: `generate_modification_candidates()` 함수의 시그니처와 초반부

```python
def generate_modification_candidates(
    base_smiles: str,
    from_group: str,
    to_group: str,
    max_candidates: int = 5,
    replace_all: bool = False,      # 신규: 모든 매칭 위치 동시 치환
    target_position: int | None = None,  # 신규: 특정 위치만 치환
) -> list[dict]:
    """Phase 2 핵심: base_smiles + from_group + to_group → 후보 분자 리스트.
    
    Args:
        base_smiles: 원본 분자 SMILES
        from_group: 제거할 기능기 (영어 이름 또는 SMARTS)
        to_group: 추가할 기능기 (영어 이름 또는 SMARTS)
        max_candidates: 최대 후보 수
        replace_all: True이면 모든 매칭 위치를 한번에 치환
        target_position: 특정 매칭 인덱스만 치환 (0-based)
    
    Returns:
        [{"smiles": "...", "name": "...", "delta": {...}, "position": int}, ...]
    """
    if Chem is None:
        return []
    
    mol = Chem.MolFromSmiles(base_smiles)
    if mol is None:
        raise ModificationError(
            "유효하지 않은 SMILES입니다",
            base_smiles=base_smiles,
            from_group=from_group,
            to_group=to_group,
        )
    
    # SMARTS 패턴 해석: 이름이면 사전에서, 아니면 직접 SMARTS로
    from_smarts = SUBSTITUENT_SMARTS.get(from_group.lower(), from_group)
    to_smarts = SUBSTITUENT_SMARTS.get(to_group.lower(), to_group)
    
    from_pat = Chem.MolFromSmarts(from_smarts)
    if from_pat is None:
        raise ModificationError(
            f"'{from_group}' 패턴을 인식할 수 없습니다",
            base_smiles=base_smiles,
            from_group=from_group,
            to_group=to_group,
        )
    
    matches = mol.GetSubstructMatches(from_pat)
    if not matches:
        # 매칭 실패 — 존재하는 기능기 목록 제공
        existing = identify_substituents(base_smiles)
        existing_names = [s["group"] for s in existing.get("substituents", [])]
        raise ModificationError(
            f"이 분자에 '{from_group}' 기능기가 없습니다. "
            f"존재하는 기능기: {', '.join(existing_names) if existing_names else '없음'}",
            base_smiles=base_smiles,
            from_group=from_group,
            to_group=to_group,
        )
    
    candidates = []
    seen_smiles = set()
    
    if replace_all:
        # 모든 위치 동시 치환
        result = _try_substitute_all(mol, from_pat, to_smarts, base_smiles)
        if result and result not in seen_smiles:
            seen_smiles.add(result)
            delta = preview_property_delta(base_smiles, result)
            candidates.append({
                "smiles": result,
                "name": f"{from_group}→{to_group} (전체 {len(matches)}개소)",
                "delta": delta,
                "position": "all",
                "match_count": len(matches),
            })
    elif target_position is not None:
        # 특정 위치만
        if 0 <= target_position < len(matches):
            result = swap_substituent(base_smiles, from_group, to_group, target_position)
            if result and result not in seen_smiles:
                seen_smiles.add(result)
                delta = preview_property_delta(base_smiles, result)
                candidates.append({
                    "smiles": result,
                    "name": f"{from_group}→{to_group} (위치 {target_position + 1})",
                    "delta": delta,
                    "position": target_position,
                })
    else:
        # 기본: 각 위치별 후보 생성 (기존 로직 유지)
        for pos_idx in range(min(len(matches), max_candidates)):
            try:
                result = swap_substituent(base_smiles, from_group, to_group, pos_idx)
            except Exception:
                continue
            if result and result not in seen_smiles:
                seen_smiles.add(result)
                delta = preview_property_delta(base_smiles, result)
                candidates.append({
                    "smiles": result,
                    "name": f"{from_group}→{to_group} (위치 {pos_idx + 1}/{len(matches)})",
                    "delta": delta,
                    "position": pos_idx,
                })
    
    return candidates


def _try_substitute_all(
    mol,
    pattern,
    replacement_smarts: str,
    base_smiles: str,
) -> str | None:
    """모든 매칭 위치를 한번에 치환 (replaceAll)"""
    if Chem is None:
        return None
    try:
        repl_mol = Chem.MolFromSmiles(replacement_smarts)
        if repl_mol is None:
            repl_mol = Chem.MolFromSmarts(replacement_smarts)
        if repl_mol is None:
            return None
        
        result = AllChem.ReplaceSubstructs(mol, pattern, repl_mol, replaceAll=True)
        if not result:
            return None
        
        product = result[0]
        try:
            Chem.SanitizeMol(product)
        except Exception:
            try:
                Chem.SanitizeMol(product, sanitizeOps=Chem.SanitizeFlags.SANITIZE_ADJUSTHS)
            except Exception:
                return None
        
        smi = Chem.MolToSmiles(product)
        if _validate_smiles(smi):
            return smi
    except Exception:
        pass
    return None
```

### 2-D. 치환 결과 검증 함수 (신규)

**위치**: `preview_property_delta()` 뒤에 추가

```python
def validate_substitution_result(
    original_smiles: str,
    product_smiles: str,
    from_group: str,
    to_group: str,
) -> dict:
    """치환 결과의 화학적 유효성 검증.
    
    Returns:
        {"valid": bool, "checks": {...}, "warnings": [...]}
    """
    if Chem is None:
        return {"valid": False, "checks": {}, "warnings": ["RDKit 미설치"]}
    
    warnings = []
    checks = {}
    
    # 1. product SMILES 유효성
    product_mol = Chem.MolFromSmiles(product_smiles)
    checks["smiles_valid"] = product_mol is not None
    if not checks["smiles_valid"]:
        return {"valid": False, "checks": checks, "warnings": ["결과 SMILES 파싱 실패"]}
    
    original_mol = Chem.MolFromSmiles(original_smiles)
    if original_mol is None:
        return {"valid": False, "checks": checks, "warnings": ["원본 SMILES 파싱 실패"]}
    
    # 2. Tanimoto 유사도 (합리적 범위: 0.2~0.98)
    try:
        from rdkit.Chem import AllChem as _AC
        fp_orig = _AC.GetMorganFingerprintAsBitVect(original_mol, 2, nBits=2048)
        fp_prod = _AC.GetMorganFingerprintAsBitVect(product_mol, 2, nBits=2048)
        from rdkit import DataStructs
        similarity = DataStructs.TanimotoSimilarity(fp_orig, fp_prod)
        checks["tanimoto_similarity"] = round(similarity, 3)
        if similarity < 0.2:
            warnings.append(f"유사도가 매우 낮음({similarity:.2f}) — 치환이 과도할 수 있음")
        elif similarity > 0.98:
            warnings.append(f"유사도가 거의 동일({similarity:.2f}) — 치환이 반영되지 않았을 수 있음")
    except Exception as e:
        checks["tanimoto_similarity"] = None
        warnings.append(f"유사도 계산 실패: {e}")
    
    # 3. 제거 대상 기능기가 product에 없는지 확인
    from_smarts = SUBSTITUENT_SMARTS.get(from_group.lower(), from_group)
    from_pat = Chem.MolFromSmarts(from_smarts)
    if from_pat is not None:
        remaining = product_mol.GetSubstructMatches(from_pat)
        orig_matches = original_mol.GetSubstructMatches(from_pat)
        checks["from_group_removed"] = len(remaining) < len(orig_matches)
        if not checks["from_group_removed"]:
            warnings.append(f"'{from_group}'가 결과에 여전히 동일 수만큼 존재")
    
    # 4. 추가 대상 기능기가 product에 있는지 확인
    to_smarts = SUBSTITUENT_SMARTS.get(to_group.lower(), to_group)
    to_pat = Chem.MolFromSmarts(to_smarts)
    if to_pat is not None:
        new_matches = product_mol.GetSubstructMatches(to_pat)
        orig_to_matches = original_mol.GetSubstructMatches(to_pat)
        checks["to_group_added"] = len(new_matches) > len(orig_to_matches)
        if not checks["to_group_added"]:
            warnings.append(f"'{to_group}'가 결과에서 증가하지 않음")
    
    valid = checks.get("smiles_valid", False) and len(warnings) <= 1
    
    return {"valid": valid, "checks": checks, "warnings": warnings}
```

---

## Part 3. normalizer.py 패치 — 한글 modification intent 정규식 보강

**교체 대상**: 기존 `_MODIFICATION_SWAP_RE` ~ `_MODIFICATION_REMOVE_RE` 4개 패턴 블록

```python
# ── 한글 modification intent 정규식 (확장판) ──────────────────────
import re

# "메틸기를 에틸기로 바꿔" / "OH를 NH2로 치환해" / "아세틸기를 메틸기로 교체"
_MODIFICATION_SWAP_RE = re.compile(
    r"(?P<from>[가-힣A-Za-z0-9\-]+(?:기)?)"
    r"\s*[을를]\s*"
    r"(?P<to>[가-힣A-Za-z0-9\-]+(?:기)?)"
    r"\s*[으로]{1,2}\s*"
    r"(?:바꿔|바꾸|치환|교체|변경|대체|전환|교환|변환)"
    r"(?:줘|줄래|해줘|해|하자|할래|봐|보자)?",
    re.IGNORECASE,
)

# "replace methyl with ethyl" / "substitute OH for NH2" / "change acetyl to methyl"
_MODIFICATION_REPLACE_RE = re.compile(
    r"(?:replace|substitute|change|swap|switch|convert|exchange)"
    r"\s+(?P<from>[A-Za-z0-9\-]+(?:\s+group)?)"
    r"\s+(?:with|to|for|into|by)\s+"
    r"(?P<to>[A-Za-z0-9\-]+(?:\s+group)?)",
    re.IGNORECASE,
)

# "아미노기 추가" / "NH2 붙여줘" / "니트로기 도입"
_MODIFICATION_ADD_RE = re.compile(
    r"(?P<to>[가-힣A-Za-z0-9\-]+(?:기)?)"
    r"\s*(?:을|를)?\s*"
    r"(?:추가|첨가|부착|붙여|도입|넣어|달아|삽입)"
    r"(?:줘|줄래|해줘|해|하자|할래|봐|보자)?",
    re.IGNORECASE,
)

# "니트로기 제거" / "Cl 떼어줘" / "메틸기 빼줘"
_MODIFICATION_REMOVE_RE = re.compile(
    r"(?P<from>[가-힣A-Za-z0-9\-]+(?:기)?)"
    r"\s*(?:을|를)?\s*"
    r"(?:제거|삭제|떼어|빼|없애|떼줘|지워|탈리)"
    r"(?:줘|줄래|해줘|해|하자|할래|봐|보자)?",
    re.IGNORECASE,
)

# "메틸기를 에틸기로 만약 바꾸면 어떻게 될까" / "바꾸면 뭐가 달라져"
_MODIFICATION_CONDITIONAL_RE = re.compile(
    r"(?P<from>[가-힣A-Za-z0-9\-]+(?:기)?)"
    r"\s*[을를]\s*"
    r"(?P<to>[가-힣A-Za-z0-9\-]+(?:기)?)"
    r"\s*[으로]{1,2}\s*"
    r"(?:만약\s+)?(?:바꾸|치환|교체)"
    r"(?:면|하면)\s*"
    r"(?:어떻게|뭐가|어떤|무슨|무엇이)",
    re.IGNORECASE,
)

# "전부 다 바꿔" / "모든 OH를 F로 치환" 패턴 (replaceAll 감지)
_MODIFICATION_ALL_RE = re.compile(
    r"(?:전부|모든|모두|다|전체|싹다|죄다|일괄)"
    r".*?"
    r"(?:바꿔|치환|교체|변경|대체|replace|substitute)",
    re.IGNORECASE,
)


def parse_modification_intent(text: str) -> dict | None:
    """사용자 텍스트에서 modification intent 파싱.
    
    Returns:
        {"from_group": str, "to_group": str, "action": str, 
         "replace_all": bool, "raw_match": str} | None
    """
    # 한국어 치환기 이름 → 영어 정규화 (ko_aliases에서)
    from qcviz_mcp.services.ko_aliases import translate_substituent
    
    replace_all = bool(_MODIFICATION_ALL_RE.search(text))
    
    # 1. 교체 (A를 B로 바꿔)
    m = _MODIFICATION_SWAP_RE.search(text)
    if m:
        from_g = translate_substituent(m.group("from").strip())
        to_g = translate_substituent(m.group("to").strip())
        return {
            "from_group": _clean_group_name(from_g),
            "to_group": _clean_group_name(to_g),
            "action": "swap",
            "replace_all": replace_all,
            "raw_match": m.group(0),
        }
    
    # 2. 조건부 교체 (바꾸면 어떻게?)
    m = _MODIFICATION_CONDITIONAL_RE.search(text)
    if m:
        from_g = translate_substituent(m.group("from").strip())
        to_g = translate_substituent(m.group("to").strip())
        return {
            "from_group": _clean_group_name(from_g),
            "to_group": _clean_group_name(to_g),
            "action": "preview",
            "replace_all": replace_all,
            "raw_match": m.group(0),
        }
    
    # 3. 영어 replace 패턴
    m = _MODIFICATION_REPLACE_RE.search(text)
    if m:
        return {
            "from_group": _clean_group_name(m.group("from").strip()),
            "to_group": _clean_group_name(m.group("to").strip()),
            "action": "swap",
            "replace_all": replace_all,
            "raw_match": m.group(0),
        }
    
    # 4. 추가 (A 추가해줘)
    m = _MODIFICATION_ADD_RE.search(text)
    if m:
        to_g = translate_substituent(m.group("to").strip())
        return {
            "from_group": "hydrogen",  # H를 기능기로 치환 = 추가
            "to_group": _clean_group_name(to_g),
            "action": "add",
            "replace_all": replace_all,
            "raw_match": m.group(0),
        }
    
    # 5. 제거 (A 제거해줘)
    m = _MODIFICATION_REMOVE_RE.search(text)
    if m:
        from_g = translate_substituent(m.group("from").strip())
        return {
            "from_group": _clean_group_name(from_g),
            "to_group": "hydrogen",  # 기능기를 H로 = 제거
            "action": "remove",
            "replace_all": replace_all,
            "raw_match": m.group(0),
        }
    
    return None


def _clean_group_name(name: str) -> str:
    """기능기 이름 정규화: '기' 접미사 제거, 소문자화"""
    name = name.strip()
    if name.endswith("기") and len(name) > 1:
        name = name[:-1]
    # "group" 접미사 제거 (영어)
    if name.lower().endswith(" group"):
        name = name[:-6].strip()
    return name.lower()
```

---

## Part 4. grounding_merge.py 패치 — active molecule 보호

**교체 대상**: `grounding_merge()` 함수 내 `modification_exploration` 분기의 초반부

현재 문제: active molecule이 있는 상태에서 modification 요청 시, semantic grounding이
새 분자를 검색하러 가서 컨텍스트가 깨질 수 있음.

```python
# ── grounding_merge() 내 modification_exploration 분기 보강 ──────
# 기존 코드에서 lane == "modification_exploration" 분기 찾아서 아래로 교체

    if plan.lane == "modification_exploration":
        metrics.inc("grounding_modification_entered")
        
        # ★ active molecule이 이미 있으면 semantic grounding 건너뜀
        # modification은 "현재 분자"를 편집하는 것이므로 새 검색 불필요
        if (
            hasattr(plan, "modification_intent")
            and plan.modification_intent is not None
            and plan.modification_intent.base_molecule
        ):
            base_smiles = plan.modification_intent.base_molecule
            # synthetic candidate로 바로 진행
            from qcviz_mcp.llm.schemas import (
                GroundingCandidate,
                GroundingOutcome,
                ResolutionResult,
            )
            synthetic = GroundingCandidate(
                name=f"modification_base",
                smiles=base_smiles,
                source="context_active_molecule",
                confidence=0.95,
            )
            return GroundingOutcome(
                semantic_outcome="modification_candidates_ready",
                resolved_structure=ResolutionResult(
                    candidates=[synthetic],
                    primary=synthetic,
                    resolution_source="active_molecule",
                ),
                plan=plan,
                decision=None,
            )
        
        # active molecule 없으면 기존 로직 유지 (MolChat 검색 등)
        # ... (기존 코드 유지)
```

---

## Part 5. 요약 — 실제 필요 작업 목록

| # | 작업 | 파일 | 신규/패치 | 우선순위 |
|---|------|------|----------|---------|
| 1 | fg_ko_smarts.json 생성 | services/fg_ko_smarts.json | **신규** | P0 |
| 2 | SUBSTITUENT_SMARTS 확장 (13→29) | services/structure_intelligence.py | **패치** | P0 |
| 3 | label_match_sites() 추가 | services/structure_intelligence.py | **추가** | P0 |
| 4 | generate_modification_candidates() 보강 | services/structure_intelligence.py | **패치** | P0 |
| 5 | validate_substitution_result() 추가 | services/structure_intelligence.py | **추가** | P1 |
| 6 | 한글 modification intent 정규식 교체 | llm/normalizer.py | **패치** | P0 |
| 7 | grounding_merge modification 분기 보강 | llm/grounding_merge.py | **패치** | P1 |
| 8 | _try_substitute_all() 추가 | services/structure_intelligence.py | **추가** | P1 |

**설계 가이드에서 폐기할 부분**:
- "MolChat의 RDKitHandler에 메서드 추가" → QCViz의 structure_intelligence.py가 담당
- "intelligence/tools/에 substitution_tools.py 신규" → 기존 modification lane 활용
- "PromptBuilder 수정" → QCViz는 prompts.py + prompt_assets/ 구조
- "Pan et al. (2026)" 인용 → 검증 불가, 제거
- "RDKit 이슈 #8069, #3155" → 현상은 맞으나 이슈 번호 미확인, 일반론으로만 참조
