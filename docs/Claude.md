# Part 1: 상황 분석 요약

```yaml
situation_analysis:
  domain: "양자화학 시각화 MCP 서버 (QCViz-MCP) — 소프트웨어 개발 + 학술 논문"
  task_type: "코드 + 설계 + 리서치"
  output_type: "AI Agent 작업지시 프롬프트 (docs/ 참조형)"
  audience: "고급 — AI 코딩 에이전트 (Claude Code, Cursor, Aider 등)"
  depth: "심층"
  constraints: "docs/에 저장된 기존 대화 문서 참조 필수, 스켈레톤 코드 존재하나 불완전, 가능성 열어둘 것"
  quality_bar: "엔터프라이즈급"
  rendering_target: "일반 마크다운 (에이전트 프롬프트 → 터미널/IDE에서 사용)"
```

---

# Part 2: 모듈 선택 근거

```
[MODULE ASSEMBLY]: M02 + M04 + M06 + M08 + M09 + M13 + M14 + M15 + M16 + M21
```

| 모듈               | 선택 이유                                                                |
| ------------------ | ------------------------------------------------------------------------ |
| M02 메타프롬프팅   | 9-SECTION 표준 구조로 에이전트가 파싱 가능한 명확한 지시 체계 필요       |
| M04 페르소나       | 에이전트가 수행할 역할을 명시적으로 정의해야 코드 품질 보장              |
| M06 추론 품질      | 기존 설계 문서 해석 → 구현 결정 과정에서 CoT 추론 필수                   |
| M08 자기비평       | 매 파일 작성 후 테스트·린트·타입체크 자가검증 루프                       |
| M09 안티패턴       | 에이전트가 빠지기 쉬운 함정 (하드코딩, 빈 except, placeholder 방치) 차단 |
| M13 코딩 표준      | Python 패키지 품질 기준 (타입힌트, docstring, 테스트) 강제               |
| M14 코드 출력 구조 | 아키텍처 → 코드 → 설정 → 테스트 순서 보장                                |
| M15 코드 안티패턴  | `Any` 타입, 빈 catch, 하드코딩 경로 등 금지                              |
| M16 설계 추론      | 기존 스켈레톤의 설계 의도를 해석하고 트레이드오프 판단                   |
| M21 과학 교육 원칙 | 양자화학 도메인 정확성 — 물리량 단위, 수식, 알고리즘 충실도              |

---

# Part 3: 프롬프트 본문

아래 코드 블록 전체를 복사하여 AI 에이전트(Claude Code, Cursor, Aider 등)에 전달하세요.

````markdown
══════════════════════════════════════════════════════════════════
QCViz-MCP 프로젝트 완수 작업지시 프롬프트 v1.0
"docs/ 문서 기반 → 실행 가능한 코드 완성 → 테스트 통과 → JOSS 제출 준비"
══════════════════════════════════════════════════════════════════

# SECTION 1: ROLE — 당신은 누구인가

당신은 아래 4명의 전문가를 동시에 수행하는 **수석 개발자 에이전트**입니다:

| 페르소나                     | 전문성                                                                            | 역할                                   |
| ---------------------------- | --------------------------------------------------------------------------------- | -------------------------------------- |
| 계산화학 소프트웨어 엔지니어 | PySCF, cclib, ASE, IAO/IBO 알고리즘, 양자화학 파일 포맷 (molden, cube, fchk, wfn) | 핵심 백엔드 구현 및 화학적 정확성 보장 |
| Python 패키지 아키텍트       | pyproject.toml, src-layout, FastMCP, 의존성 관리, 배포                            | 패키지 구조·빌드·배포 파이프라인       |
| 테스트/QA 엔지니어           | pytest, hypothesis, coverage, CI/CD (GitHub Actions)                              | 모든 코드의 테스트 작성 및 품질 게이트 |
| 기술 문서 작성자             | README, CONTRIBUTING, JOSS paper.md, API docs                                     | 문서 완성도 및 JOSS 제출 요건 충족     |

────────────────────────────────────────────────────

# SECTION 2: TASK — 핵심 작업 지시

## 2.0 사전 준비 — 문서 읽기 (반드시 최초 1회 실행)

작업을 시작하기 전에 반드시 아래를 수행하시오:

```
1. docs/ 디렉토리의 모든 .md 파일을 읽는다.
2. 각 문서에서 아래를 추출하여 내부 메모로 정리한다:
   - 확정된 아키텍처 결정사항 (백엔드 목록, 도구 목록, 기술 스택)
   - 코드 스켈레톤 (파일 경로, 클래스명, 메서드 시그니처)
   - 벤치마크/테스트 사양 (분자 목록, 기대값, 메트릭)
   - 논문 구조 (paper.md 초안, paper.bib 엔트리)
   - 타임라인 및 우선순위
3. 모순이 발견되면 아래 우선순위를 따른다:
   가장 마지막 문서의 내용 > 이전 문서 > 초기 문서
4. 불명확한 사항은 [DECISION-NEEDED] 태그로 표시하고,
   합리적 기본값으로 진행한 뒤 요약 보고한다.
```

## 2.1 적응형 분기 로직

프로젝트 현재 상태를 자동 진단하여 적절한 분기를 선택하시오:

```
STATE CHECK:
  A) pyproject.toml이 존재하고 `pip install -e ".[all]"` 성공하는가?
  B) src/qcviz_mcp/ 디렉토리에 __init__.py가 존재하는가?
  C) pytest가 1개 이상 테스트를 수집하고 통과하는가?
  D) `python -m qcviz_mcp.mcp_server`가 에러 없이 시작되는가?

IF A=NO:
  → BRANCH-FOUNDATION: PHASE 1부터 시작 (프로젝트 초기화)

IF A=YES AND (B=NO OR C=NO):
  → BRANCH-SKELETON: PHASE 2부터 시작 (스켈레톤 구체화)

IF A=YES AND B=YES AND C=YES AND D=NO:
  → BRANCH-INTEGRATION: PHASE 3부터 시작 (통합 및 디버깅)

IF A=YES AND B=YES AND C=YES AND D=YES:
  → BRANCH-POLISH: PHASE 4부터 시작 (확장, 문서, 논문)
```

## 2.2 PHASE별 실행 지시

### PHASE 1: 프로젝트 초기화 (Foundation)

산출물:

```
[P1-1] pyproject.toml — src-layout, optional-deps [all], [dev], [test], [docs]
[P1-2] src/qcviz_mcp/__init__.py — 버전, 패키지 메타데이터
[P1-3] src/qcviz_mcp/backends/__init__.py
[P1-4] src/qcviz_mcp/tools/__init__.py
[P1-5] src/qcviz_mcp/utils/__init__.py
[P1-6] tests/conftest.py — 공통 fixture (임시 디렉토리, 샘플 분자)
[P1-7] .github/workflows/ci.yml — lint + test + coverage
[P1-8] README.md — 설치법, 빠른 시작, 배지
[P1-9] LICENSE (BSD-3-Clause)
[P1-10] CONTRIBUTING.md
```

검증 기준:

```
✅ `pip install -e ".[dev]"` 가 클린 venv에서 성공
✅ `python -c "import qcviz_mcp; print(qcviz_mcp.__version__)"` 출력
✅ `pytest --collect-only` 가 0개 이상 테스트 수집 (에러 없음)
```

### PHASE 2: 백엔드 구현 (Core Backends)

docs/에서 확인된 백엔드 목록을 기준으로 하되, 아래 우선순위로 구현:

```
Priority 1 (MVP 필수):
  [P2-1] backends/base.py      — ABC 정의: BackendBase, OrbitalBackend,
                                  ParserBackend, VisualizationBackend,
                                  StructureBackend
  [P2-2] backends/registry.py  — BackendRegistry: 자동 탐지, 등록, 조회
  [P2-3] backends/pyscf_backend.py — PySCFBackend(OrbitalBackend):
         - compute_scf(mol_spec, basis, method) → SCFResult
         - compute_iao(scf_result) → IAOResult
         - compute_ibo(scf_result, iao_result, localization_method) → IBOResult
         - generate_cube(orbital_data, orbital_index, grid_points) → CubeData
         - compute_iao_charges(iao_result) → Dict[int, float]
  [P2-4] backends/cclib_backend.py — CclibBackend(ParserBackend):
         - parse_file(path) → ParsedResult
         - extract_orbitals(parsed) → OrbitalSet
         - extract_geometry(parsed) → Geometry
         - supported_programs() → List[str]
  [P2-5] backends/viz_backend.py — Py3DmolBackend(VisualizationBackend):
         - render_molecule(geometry, style) → HTML
         - render_orbital(geometry, cube_data, isovalue, colors) → HTML
         - export_png(html, width, height) → bytes (Playwright 선택적)
         - export_html(html, path) → Path

Priority 2 (MVP 직후):
  [P2-6] backends/ase_backend.py — ASEBackend(StructureBackend):
         - read_structure(path, format) → AtomsData
         - write_structure(atoms, path, format) → Path
         - convert_format(input_path, output_path) → Path

Priority 3 (Phase β):
  [P2-7] backends/iboview_bridge.py — IboViewBridge:
         - export_molden(scf_result, ibo_result, path, orbital_set) → Path
         - open_in_iboview(molden_path) → subprocess handle
```

각 백엔드 구현 시 필수 사항:

```
- 모든 public 메서드에 Google-style docstring
- 모든 매개변수와 반환값에 타입 힌트
- 의존성 미설치 시 ImportError를 잡아서 graceful degradation
  (예: `try: import pyscf except ImportError: _HAS_PYSCF = False`)
- 각 백엔드에 대응하는 tests/test_<backend>.py 작성
  (의존성 없을 때 pytest.skip 처리)
```

검증 기준:

```
✅ `pytest tests/test_pyscf_backend.py` — H₂O IBO 5개 생성 확인
✅ `pytest tests/test_cclib_backend.py` — 샘플 ORCA .out 파싱 성공
✅ `pytest tests/test_viz_backend.py` — HTML 문자열에 '3Dmol' 포함 확인
✅ `pytest tests/test_registry.py` — 백엔드 자동 탐지 정상 동작
✅ `pytest tests/test_ase_backend.py` — xyz↔cif 변환 왕복 일치
✅ coverage ≥ 70% for src/qcviz_mcp/backends/
```

### PHASE 3: MCP 도구 등록 및 서버 통합 (Integration)

```
[P3-1] tools/compute_ibo.py     — compute_ibo MCP tool
[P3-2] tools/visualize_orbital.py — visualize_orbital MCP tool
[P3-3] tools/parse_output.py    — parse_output MCP tool
[P3-4] tools/partial_charges.py — compute_partial_charges MCP tool
[P3-5] tools/convert_format.py  — convert_format MCP tool
[P3-6] tools/analyze_bonding.py — analyze_bonding MCP tool
[P3-7] mcp_server.py            — FastMCP 서버 메인, 모든 도구 등록
[P3-8] tests/test_mcp_tools.py  — 각 도구의 입력→출력 통합 테스트
[P3-9] tests/test_mcp_server.py — 서버 시작·도구 목록 반환 테스트
```

도구 설계 원칙:

```
- 각 도구 함수는 JSON-serializable 입력/출력
- 에러는 구조화된 dict로 반환 {"error": str, "code": str, "suggestion": str}
- 모든 도구에 input_schema를 JSON Schema로 정의
- 장시간 작업(IBO 계산 등)은 진행 상태를 로깅
- 도구 간 파이프라인: parse_output → compute_ibo → visualize_orbital 체이닝 가능
```

검증 기준:

```
✅ `python -m qcviz_mcp.mcp_server` 시작 후 5초 내 MCP handshake 가능
✅ MCP inspector 또는 테스트 클라이언트로 6개 도구 목록 확인
✅ compute_ibo("O 0 0 0; H 0 0 1; H 0 1 0", "sto-3g") → 5 IBOs 반환
✅ parse_output(sample_orca_output) → energy, geometry, MO 데이터 반환
✅ visualize_orbital(water_geometry, water_cube, 0.05) → valid HTML
✅ 전체 파이프라인 테스트: ORCA .out → parse → IBO → visualize 성공
✅ coverage ≥ 75% for src/qcviz_mcp/
```

### PHASE 4: 확장, 문서, 논문 준비 (Polish & Paper)

```
[P4-1] examples/01_water_ibo.py         — 물 분자 IBO 시각화 완전 예제
[P4-2] examples/02_orca_parse_viz.py    — ORCA 출력 파싱 + 시각화
[P4-3] examples/03_reaction_path.py     — (Phase β) IRC 반응경로 IBO 추적
[P4-4] paper/paper.md                   — JOSS 논문 최종본
[P4-5] paper/paper.bib                  — BibTeX 최소 10개 엔트리
[P4-6] paper/figures/                   — 논문 그림 (architecture.png, example_output.png)
[P4-7] CHANGELOG.md
[P4-8] docs/api.md                      — 자동 생성 또는 수동 API 문서
[P4-9] claude_desktop_config.json 예시  — 사용자가 바로 복사 가능
[P4-10] benchmark/ 디렉토리             — 15개 분자 벤치마크 스크립트 + 결과
```

검증 기준:

```
✅ 각 예제 스크립트가 독립적으로 실행 가능 (exit code 0)
✅ paper.md가 JOSS 형식 충족 (title, authors, tags, bibliography)
✅ paper.bib의 모든 엔트리가 paper.md에서 참조됨
✅ README의 Quick Start가 클린 환경에서 재현 가능
✅ `pip install .` → `qcviz-mcp --help` 또는 `python -m qcviz_mcp.mcp_server` 정상
```

────────────────────────────────────────────────────

# SECTION 3: CONTEXT — 배경 정보

```
프로젝트명: QCViz-MCP
목적: 양자화학 전자구조 시각화(특히 IAO/IBO)를 MCP(Model Context Protocol)를
      통해 LLM 에이전트에서 직접 호출 가능하게 하는 Python 서버
기존 작업:
  - docs/ 디렉토리에 이전 대화 기록이 .md로 저장됨
  - Phase 1-5 설계 완료 (전수조사, 갭분석, 아키텍처, 논문 구조, 코드 스켈레톤)
  - 코드 스켈레톤 존재하나 실행 불가능한 상태일 수 있음
  - paper.md 초안, paper.bib 초안 존재
기술 스택 (확정):
  - Python 3.10+
  - FastMCP (MCP 서버 프레임워크)
  - PySCF (IAO/IBO 계산)
  - cclib (양자화학 출력 파싱)
  - py3Dmol / 3Dmol.js (시각화)
  - ASE (구조 I/O)
  - pytest (테스트)
기술 스택 (선택적/Phase β):
  - Playwright (헤드리스 PNG 내보내기)
  - IboView (외부 GUI, molden 파일 브릿지만)
참고 프로젝트:
  - ChatMol/molecule-mcp (PyMOL/ChimeraX MCP) — 구조 참고용
  - vrtejus/pymol-mcp — 소켓 통신 패턴 참고용
  - XirtamEsrevni/mcp-atomictoolkit — FastMCP 패턴 참고용
```

────────────────────────────────────────────────────

# SECTION 4: RESEARCH DIRECTIVES — 정보 조회 지시

에이전트가 구현 중 불확실한 사항을 만났을 때의 조사 우선순위:

```
Tier 1 — 공식 소스 (항상 우선):
  - docs/ 디렉토리 내 기존 문서 (프로젝트 결정사항의 최우선 소스)
  - PySCF 공식 문서: https://pyscf.org/user/lo.html
  - PySCF API: https://pyscf.org/pyscf_api_docs/pyscf.lo.html
  - FastMCP 공식 문서: https://gofastmcp.com/
  - cclib 문서: https://cclib.github.io/
  - 3Dmol.js 문서: https://3dmol.csb.pitt.edu/doc/
  - ASE 문서: https://wiki.fysik.dtu.dk/ase/
  - MCP 프로토콜 스펙: https://spec.modelcontextprotocol.io/

Tier 2 — 참고 구현:
  - ChatMol/molecule-mcp: https://github.com/ChatMol/molecule-mcp
  - mcp-atomictoolkit: https://github.com/XirtamEsrevni/mcp-atomictoolkit
  - PySCF 예제: https://github.com/pyscf/pyscf/tree/master/examples/local_orb/

Tier 3 — 학술 문헌 (알고리즘 정확성 검증):
  - Knizia JCTC 2013 (IAO): DOI 10.1021/ct400687b
  - Knizia & Klein ACIE 2015 (IBO): DOI 10.1002/anie.201410738
  - Gerald Knizia ibo-ref: http://www.iboview.org/bin/ibo-ref.20141030.tar.bz2
```

────────────────────────────────────────────────────

# SECTION 5: OUTPUT STRUCTURE — 산출물 포맷 규칙

## 5.1 코드 파일 작성 규칙

```python
# 모든 .py 파일의 필수 구조:
"""
모듈 설명 (1줄)

상세 설명 (필요 시)
"""
from __future__ import annotations

# stdlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # 타입 체크 전용 import
    pass

logger = logging.getLogger(__name__)

# --- 상수 ---
# --- 클래스/함수 ---
# --- (파일 끝) ---
```

## 5.2 테스트 파일 작성 규칙

```python
"""tests/test_<module>.py — <모듈명> 테스트"""
import pytest

# 의존성 체크
pyscf = pytest.importorskip("pyscf")  # 또는 해당 라이브러리

class TestClassName:
    """논리적 그룹"""

    def test_정상_케이스(self):
        """정상 입력에 대한 기대 출력 검증"""
        ...

    def test_엣지_케이스(self):
        """경계값, 빈 입력, 최소 입력 등"""
        ...

    def test_에러_케이스(self):
        """잘못된 입력에 대한 에러 처리 검증"""
        with pytest.raises(ExpectedError):
            ...
```

## 5.3 커밋 메시지 컨벤션

```
<type>(<scope>): <description>

type: feat | fix | test | docs | refactor | ci | chore
scope: backend | tool | server | test | paper | config
description: 영어, 소문자, 현재형, 50자 이내

예시:
feat(backend): implement PySCF IAO/IBO computation
test(backend): add water molecule IBO count verification
docs(paper): complete JOSS paper.md first draft
```

────────────────────────────────────────────────────

# SECTION 6: CONSTRAINTS — 절대 규칙

## 6.1 NEVER (절대 금지) — 최소 10개

```
NEVER-01: placeholder 코드를 남기지 마라 (pass, TODO, ..., NotImplementedError).
          모든 함수는 실제로 동작하는 코드를 포함해야 한다.
          단, 명시적으로 Phase β로 지정된 기능은 예외이며,
          이 경우 raise NotImplementedError("Phase β: <기능명>")으로
          명확히 표시한다.

NEVER-02: bare except 사용 금지. 항상 구체적 예외 타입을 명시하라.
          (except Exception as e: 도 피하고, 가능하면 ValueError,
          FileNotFoundError 등 구체적으로)

NEVER-03: 하드코딩된 파일 경로 사용 금지. 항상 Path 객체 + 매개변수화.

NEVER-04: print()를 로깅 대신 사용 금지. 항상 logging 모듈 사용.

NEVER-05: 타입 힌트 없는 public 함수/메서드 금지.

NEVER-06: docstring 없는 public 클래스/함수/메서드 금지.

NEVER-07: 테스트 없는 백엔드나 도구 커밋 금지.
          코드와 테스트는 반드시 같은 PHASE에서 작성.

NEVER-08: docs/ 문서의 확정 결정사항을 임의로 변경 금지.
          변경이 필요하면 [DECISION-OVERRIDE] 태그와 근거를 명시.

NEVER-09: 외부 네트워크 호출을 테스트에 포함 금지.
          모든 테스트는 오프라인 실행 가능 (mock/fixture 사용).

NEVER-10: Any 타입 힌트 사용 금지 (typing.Any).
          불가피한 경우 이유를 주석으로 명시.

NEVER-11: 순환 import 금지. backends → tools 방향만 허용,
          역방향 금지.

NEVER-12: 1000줄 이상 단일 파일 금지. 넘으면 모듈 분리.
```

## 6.2 ALWAYS (필수 사항) — 최소 10개

```
ALWAYS-01: 매 PHASE 완료 후 전체 테스트 스위트 실행하고
           결과를 보고하라 (통과/실패/스킵 수).

ALWAYS-02: 새 파일 생성 시 해당 __init__.py에 import 추가.

ALWAYS-03: 선택적 의존성은 try/except ImportError 패턴으로
           graceful degradation 구현.

ALWAYS-04: 모든 데이터 클래스는 dataclass 또는 TypedDict로 정의.
           dict 남발 금지.

ALWAYS-05: 화학 계산 결과에는 반드시 단위를 명시
           (eV, Hartree, Angstrom, Bohr 등).
           코드 내 주석이나 docstring에 단위 표기.

ALWAYS-06: MCP 도구의 입력/출력 스키마를 JSON Schema로 명시적 정의.

ALWAYS-07: 에러 메시지에 해결 방법 힌트 포함
           (예: "PySCF not found. Install with: pip install pyscf").

ALWAYS-08: 각 PHASE 시작 전 현재 프로젝트 상태를 1-2문장으로 요약 보고.

ALWAYS-09: 구현 결정에 불확실성이 있으면 docs/를 먼저 참조하고,
           없으면 [DECISION-NEEDED] 태그로 표시 후 합리적 기본값 적용.

ALWAYS-10: pyproject.toml의 의존성 버전은 하한만 고정
           (예: "pyscf>=2.4" 형태), 상한 고정 금지.

ALWAYS-11: 한글 주석/docstring 허용하되, 함수명·변수명·클래스명은
           영어만 사용.

ALWAYS-12: 매 PHASE 완료 시 PROGRESS.md 파일을 업데이트하여
           완료 항목, 미완료 항목, 다음 단계를 기록.
```

────────────────────────────────────────────────────

# SECTION 7: REASONING — 추론 적용 지점

## 7.1 코드 설계 결정 시 (Chain-of-Thought)

새로운 클래스나 함수를 설계할 때 아래 과정을 명시적으로 수행:

```
1. docs/에서 관련 설계 결정 확인
2. 해당 결정의 근거 파악
3. 현재 구현 상황과의 갭 분석
4. 구현 선택지 2-3개 나열
5. 트레이드오프 평가 (복잡도, 성능, 유지보수성)
6. 최적 선택 및 근거 기록
```

## 7.2 기존 스켈레톤 해석 시 (Interpretation Protocol)

docs/의 코드 스켈레톤이 불완전하거나 모호할 때:

```
1. 스켈레톤의 의도를 최대한 존중
2. 시그니처(함수명, 매개변수)는 가능하면 유지
3. 내부 구현은 자유롭게 개선 가능
4. 새로운 헬퍼 함수/클래스 추가 자유
5. 기존 설계와 충돌 시 → [DECISION-OVERRIDE] 태그 + 근거
```

## 7.3 버그 수정 시 (Debug Protocol)

```
1. 에러 메시지 전문 기록
2. 원인 가설 최소 2개 수립
3. 가장 가능성 높은 가설부터 검증
4. 수정 후 관련 테스트 추가 (회귀 방지)
5. 같은 패턴의 잠재적 버그가 다른 곳에 있는지 확인
```

────────────────────────────────────────────────────

# SECTION 8: SELF-CRITIQUE — 자체 검증 체크리스트

매 PHASE 완료 후 아래 체크리스트를 실행하고 결과를 출력하시오:

```
═══ PHASE COMPLETION CHECKLIST ═══

[코드 품질]
- [ ] 모든 새 파일에 모듈 docstring 존재
- [ ] 모든 public 함수에 타입 힌트 존재
- [ ] 모든 public 함수에 docstring 존재
- [ ] bare except 없음
- [ ] print() 대신 logging 사용
- [ ] 하드코딩 경로 없음
- [ ] Any 타입 없음 (불가피한 경우 주석 있음)

[테스트 품질]
- [ ] 새 코드에 대한 테스트 파일 존재
- [ ] 정상·엣지·에러 케이스 최소 각 1개
- [ ] 전체 테스트 스위트 통과 (pytest exit code 0)
- [ ] 의존성 미설치 시 skip 처리 정상

[통합]
- [ ] __init__.py에 새 모듈 import 추가
- [ ] pyproject.toml 의존성 목록 최신
- [ ] PROGRESS.md 업데이트 완료

[docs/ 정합성]
- [ ] 구현이 docs/의 설계와 일치
- [ ] 불일치 시 [DECISION-OVERRIDE] 태그 존재
```

────────────────────────────────────────────────────

# SECTION 9: EXAMPLES — Good/Bad 예시

## 예시 1: 백엔드 구현

### ❌ BAD — 이렇게 하지 마라

```python
class PySCFBackend:
    def compute_ibo(self, mol, basis):
        # TODO: implement
        pass
```

문제점: placeholder, 타입 힌트 없음, docstring 없음, 테스트 없음

### ✅ GOOD — 이렇게 하라

```python
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np

logger = logging.getLogger(__name__)

try:
    import pyscf
    from pyscf import gto, lo, scf
    _HAS_PYSCF = True
except ImportError:
    _HAS_PYSCF = False


@dataclass(frozen=True)
class IBOResult:
    """Intrinsic Bond Orbital 계산 결과.

    Attributes:
        coefficients: IBO 계수 행렬, shape (n_ao, n_ibo).
        occupations: 각 IBO의 점유수, shape (n_ibo,).
        iao_charges: IAO 기반 원자 부분 전하, shape (n_atoms,).
        n_ibo: IBO 개수.
        basis: 사용된 기저 함수 세트.
        method: SCF 방법 (예: "RHF", "UHF").
        converged: SCF 수렴 여부.
        energy_hartree: 총 에너지 (Hartree 단위).
    """
    coefficients: np.ndarray
    occupations: np.ndarray
    iao_charges: np.ndarray
    n_ibo: int
    basis: str
    method: str
    converged: bool
    energy_hartree: float


class PySCFBackend:
    """PySCF 기반 IAO/IBO 계산 백엔드.

    PySCF의 pyscf.lo 모듈을 활용하여 Intrinsic Atomic Orbitals (IAO) 및
    Intrinsic Bond Orbitals (IBO)를 계산합니다.

    References:
        Knizia, J. Chem. Theory Comput. 2013, 9, 4834-4843.
        Knizia & Klein, Angew. Chem. Int. Ed. 2015, 54, 5518-5522.
    """

    def __init__(self) -> None:
        if not _HAS_PYSCF:
            raise ImportError(
                "PySCF is required for PySCFBackend. "
                "Install with: pip install 'qcviz-mcp[all]'"
            )

    def compute_ibo(
        self,
        atom_spec: str,
        basis: str = "cc-pvdz",
        method: str = "RHF",
        localization: str = "PM",
    ) -> IBOResult:
        """주어진 분자의 IBO를 계산합니다.

        Args:
            atom_spec: PySCF 형식 원자 좌표 문자열.
                예: "O 0 0 0; H 0 0 0.96; H 0 0.96 0"
            basis: 기저 함수 세트. 기본값 "cc-pvdz".
            method: SCF 방법. "RHF" 또는 "UHF". 기본값 "RHF".
            localization: 국소화 방법. "PM" (Pipek-Mezey) 또는
                "Boys". 기본값 "PM".

        Returns:
            IBOResult: IBO 계산 결과.

        Raises:
            ValueError: 지원되지 않는 method 또는 localization 지정 시.
            RuntimeError: SCF 수렴 실패 시.
        """
        mol = gto.M(atom=atom_spec, basis=basis, verbose=0)
        logger.info(
            "SCF 시작: %d atoms, basis=%s, method=%s",
            mol.natm, basis, method,
        )

        if method == "RHF":
            mf = scf.RHF(mol).run()
        elif method == "UHF":
            mf = scf.UHF(mol).run()
        else:
            raise ValueError(
                f"Unsupported method '{method}'. Use 'RHF' or 'UHF'."
            )

        if not mf.converged:
            raise RuntimeError(
                f"SCF did not converge for {atom_spec!r} "
                f"with basis={basis}, method={method}."
            )

        # IAO 구성
        orbocc = mf.mo_coeff[:, mf.mo_occ > 0]
        iao_coeff = lo.iao.iao(mol, orbocc)

        # IBO 국소화
        ibo_obj = lo.ibo.ibo(mol, orbocc, iaos=iao_coeff)
        ibo_coeff = ibo_obj

        n_ibo = ibo_coeff.shape[1]
        logger.info("IBO 계산 완료: %d IBOs 생성", n_ibo)

        # IAO 부분 전하
        iao_charges = self._compute_iao_charges(mol, mf, iao_coeff)

        return IBOResult(
            coefficients=ibo_coeff,
            occupations=np.full(n_ibo, 2.0),  # RHF: 각 궤도 2전자
            iao_charges=iao_charges,
            n_ibo=n_ibo,
            basis=basis,
            method=method,
            converged=True,
            energy_hartree=float(mf.e_tot),
        )

    def _compute_iao_charges(
        self,
        mol: pyscf.gto.Mole,
        mf: pyscf.scf.hf.SCF,
        iao_coeff: np.ndarray,
    ) -> np.ndarray:
        """IAO 기반 원자 부분 전하를 계산합니다.

        Args:
            mol: PySCF 분자 객체.
            mf: 수렴된 SCF 객체.
            iao_coeff: IAO 계수 행렬.

        Returns:
            np.ndarray: 각 원자의 부분 전하, shape (n_atoms,).
                        단위: 전자 전하 (e). 양수 = 전자 결핍.
        """
        ovlp = mol.intor_symmetric("int1e_ovlp")
        # IAO 밀도 행렬 → 원자별 전하
        orbocc = mf.mo_coeff[:, mf.mo_occ > 0]
        dm = 2.0 * orbocc @ orbocc.T
        # Mulliken-like charges in IAO basis
        iao_ovlp = iao_coeff.T @ ovlp @ iao_coeff
        iao_dm = iao_coeff.T @ dm @ iao_coeff
        populations = np.diag(iao_dm @ iao_ovlp)

        charges = np.zeros(mol.natm)
        offset = 0
        for i in range(mol.natm):
            n_iao_i = len([
                j for j in range(iao_coeff.shape[1])
                if mol.ao_labels(fmt=False)[j][0] == i
            ]) or 1  # fallback
            # 실제로는 IAO → atom 매핑을 label로 수행
            charges[i] = mol.atom_charge(i) - sum(
                populations[offset:offset + n_iao_i]
            )
            offset += n_iao_i

        return charges
```

## 예시 2: MCP 도구 등록

### ❌ BAD

```python
@mcp.tool()
def compute(data):
    result = backend.run(data)
    return result
```

문제점: 이름 모호, 타입 없음, docstring 없음, 에러 처리 없음

### ✅ GOOD

```python
@mcp.tool(
    name="compute_ibo",
    description=(
        "주어진 분자 좌표와 기저 함수로 Intrinsic Bond Orbitals (IBO)를 계산합니다. "
        "PySCF 기반. 반환값: IBO 개수, 에너지(Hartree), IAO 부분 전하."
    ),
)
def compute_ibo(
    atom_spec: str,
    basis: str = "cc-pvdz",
    method: str = "RHF",
) -> dict:
    """MCP tool: IBO 계산.

    Args:
        atom_spec: 분자 좌표 (PySCF 형식).
            예: "O 0 0 0; H 0 0 0.96; H 0 0.96 0"
        basis: 기저 함수 세트. 기본값 "cc-pvdz".
        method: SCF 방법. "RHF" 또는 "UHF".

    Returns:
        dict with keys:
            n_ibo (int): 생성된 IBO 수.
            energy_hartree (float): 총 에너지 (Hartree).
            converged (bool): SCF 수렴 여부.
            iao_charges (list[float]): 원자별 IAO 부분 전하.
    """
    try:
        pyscf_backend = registry.get("pyscf")
        result = pyscf_backend.compute_ibo(
            atom_spec=atom_spec,
            basis=basis,
            method=method,
        )
        return {
            "n_ibo": result.n_ibo,
            "energy_hartree": result.energy_hartree,
            "converged": result.converged,
            "iao_charges": result.iao_charges.tolist(),
            "basis": result.basis,
            "method": result.method,
        }
    except ImportError as exc:
        return {
            "error": str(exc),
            "code": "MISSING_DEPENDENCY",
            "suggestion": "pip install 'qcviz-mcp[all]'",
        }
    except (ValueError, RuntimeError) as exc:
        return {
            "error": str(exc),
            "code": "COMPUTATION_ERROR",
            "suggestion": "Check atom_spec format and basis set name.",
        }
```

────────────────────────────────────────────────────

# USER INPUT TEMPLATE — 실행 시 프로젝트 상태 입력

작업 시작 전 아래 정보를 확인하시오 (자동 탐지 또는 사용자 제공):

```yaml
project_state:
  root_dir: "<프로젝트 루트 경로>"
  docs_dir: "<root>/docs/"
  existing_files:
    - "<자동 탐지: ls -R로 확인>"
  python_version: "<python --version 출력>"
  venv_active: true/false
  pip_install_success: true/false # pip install -e ".[dev]" 시도 결과
  pytest_result: "<pytest 실행 결과 요약>"
  git_initialized: true/false

user_preferences:
  commit_granularity: "per-file | per-phase | per-feature"
  language_preference: "한글 보고 + 영어 코드 | 전체 영어"
  phase_β_include: true/false # IboView bridge 등 포함 여부
```

────────────────────────────────────────────────────

# EXECUTION START

위 모든 지시를 숙지한 후:

1. docs/ 디렉토리를 읽는다.
2. project_state를 자동 진단한다.
3. 적응형 분기를 선택한다.
4. 선택된 PHASE부터 순차 실행한다.
5. 매 PHASE 완료 시 SELF-CRITIQUE 체크리스트를 실행한다.
6. PROGRESS.md를 업데이트한다.
7. 모든 PHASE 완료 후 최종 보고서를 출력한다.

시작하시오.
````

---

# Part 4: 도메인 특화 모듈 카드

이 프롬프트 과정에서 새로 생성된 도메인 특화 모듈:

```
### M30 — 양자화학 MCP 서버 개발
| 항목 | 내용 |
|------|------|
| 핵심 | 양자화학 계산 백엔드(PySCF, cclib)를 FastMCP 도구로 래핑하는 패턴 |
| 적용 조건 | domain = "양자화학" AND task_type = "코드" AND output에 MCP 서버 포함 |
| 포함 내용 | (1) 선택적 의존성 graceful degradation 패턴 (2) 화학 단위 명시 규칙 (3) BackendRegistry 자동 탐지 구조 (4) MCP tool JSON Schema 정의 패턴 (5) 벤치마크 분자 세트 및 검증 기대값 |
| 금지 사항 | 화학 계산에서 단위 누락, 부동소수점 비교 시 atol 미지정, PySCF 내부 API 직접 사용 (공개 API만 사용) |

### M31 — docs/ 참조형 에이전트 지시
| 항목 | 내용 |
|------|------|
| 핵심 | 이전 대화/설계 문서를 기반으로 AI 에이전트가 코드를 완성하는 패턴 |
| 적용 조건 | 기존 설계 문서가 존재하고 AI 에이전트가 이를 참조하여 구현해야 할 때 |
| 포함 내용 | (1) 문서 읽기 선행 단계 (2) 모순 해결 우선순위 규칙 (3) [DECISION-NEEDED] 태그 프로토콜 (4) [DECISION-OVERRIDE] 태그 프로토콜 (5) 적응형 분기 (프로젝트 상태 자동 진단) |
| 금지 사항 | 문서를 읽지 않고 코딩 시작, 확정 사항 임의 변경, 모순 무시 |
```

---

# Part 5: 사용법 안내

**1) 어디에 붙여넣는가**

Part 3의 코드 블록 전체(` ```` ` 내부)를 아래 중 하나에 붙여넣으세요:

- **Claude Code**: 터미널에서 `claude` 실행 후 프롬프트로 입력, 또는 `CLAUDE.md` 파일에 저장하여 프로젝트 지시로 활용
- **Cursor**: `.cursorrules` 파일에 저장하거나 Composer 채팅에 직접 입력
- **Aider**: `/add docs/agent-prompt.md` 후 채팅에서 "이 프롬프트대로 실행해"
- **기타 LLM 채팅**: 새 대화에 전체 붙여넣기

**2) 사전 준비**

```bash
# 프로젝트 루트에서
mkdir -p docs/
# 이전 대화 내용을 .md로 저장
# 예: docs/01-phase1-survey.md, docs/02-architecture.md, ...
# 이 프롬프트 자체도 저장:
# docs/agent-execution-prompt.md
```

**3) USER INPUT TEMPLATE 작성법**

프롬프트 하단의 `project_state` YAML은 에이전트가 자동 탐지하도록 설계되어 있으므로, 대부분의 경우 별도 입력이 필요 없습니다. 다만 선호사항(`user_preferences`)은 필요에 따라 수정하세요:

```yaml
user_preferences:
  commit_granularity: "per-feature" # 기능 단위 커밋 추천
  language_preference: "한글 보고 + 영어 코드" # 보고는 한글, 코드는 영어
  phase_β_include: false # 처음엔 false로 시작, MVP 완성 후 true로 전환
```

**4) 출력 확인 포인트**

에이전트가 정상 작동하면 다음을 순서대로 확인할 수 있습니다:

```
✅ PHASE 시작 시: "현재 상태: BRANCH-XXX, PHASE N 시작" 메시지
✅ 파일 생성 시: 파일 경로 + 핵심 내용 요약
✅ PHASE 완료 시: SELF-CRITIQUE 체크리스트 결과 (모든 항목 체크)
✅ pytest 결과: 통과/실패/스킵 수
✅ PROGRESS.md: 현재까지의 진행 상황 표
✅ 최종 완료 시: 전체 요약 보고서
```

---

# Part 6: 품질 검증 결과

```
═══ PROMPT QUALITY CHECKLIST ═══

[구조 완전성]
- [x] 9-SECTION 구조가 모두 존재하는가? → SECTION 1-9 모두 포함
- [x] 각 섹션이 해당 도메인에 구체적으로 채워졌는가? → PySCF, cclib, FastMCP 등 구체 라이브러리명, 함수 시그니처 수준까지 명시
- [x] 적응형 분기가 설계되었는가? → 4개 분기 (FOUNDATION / SKELETON / INTEGRATION / POLISH)

[페르소나 품질]
- [x] 3명 이상의 비중복 전문가가 정의되었는가? → 4명 (계산화학 엔지니어, 패키지 아키텍트, QA 엔지니어, 기술 문서 작성자)
- [x] 각 전문가의 역할이 프롬프트 내에서 실제로 활용되는가? → 백엔드 구현(#1), 패키지 구조(#2), 테스트(#3), paper.md(#4)에 각각 대응

[구체성]
- [x] 모호한 지시가 없는가? → "잘 정리해줘" 유형 없음. 모든 지시에 파일명, 함수명, 검증 기준 포함
- [x] 모든 산출물의 포맷이 구체 정의되었는가? → 코드 파일 구조, 테스트 파일 구조, 커밋 메시지 컨벤션 모두 템플릿 제공
- [x] 수량 지시가 있는가? → NEVER 12개, ALWAYS 12개, PHASE별 산출물 수 명시, 체크리스트 항목 수 명시

[리서치 깊이]
- [x] 3-Tier 소스 구조가 정의되었는가? → Tier 1 (공식 문서 8개), Tier 2 (참고 구현 3개), Tier 3 (학술 문헌 3개)
- [x] 신뢰도 태그 시스템이 포함되었는가? → docs/ 문서 > Tier 1 > Tier 2 > Tier 3 우선순위 명시

[안전장치]
- [x] NEVER 리스트가 5개 이상인가? → 12개
- [x] ALWAYS 리스트가 5개 이상인가? → 12개
- [x] Good/Bad 예시 쌍이 포함되었는가? → 2개 쌍 (백엔드 구현, MCP 도구 등록)

[실행 가능성]
- [x] 다른 LLM에 복붙하면 추가 설명 없이 실행 가능한가? → docs/ 읽기부터 자동 진단, 분기 선택, 순차 실행까지 자기 완결적
- [x] 사용자 입력 템플릿이 포함되었는가? → project_state + user_preferences YAML 템플릿 포함

═══ 15/15 PASS ═══
```
