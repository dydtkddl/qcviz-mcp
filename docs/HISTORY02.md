## SECTION A: 1단 로켓 (JOSS) 완전 실행 계획

### A1. JOSS 투고 요건 체크리스트

**1. 소프트웨어 기능(Functionality)**

| #   | 요건                                      | 현재 상태 | 구체적 작업                                                | 예상 시간          |
| --- | ----------------------------------------- | --------- | ---------------------------------------------------------- | ------------------ |
| 1.1 | 소프트웨어가 설치 후 정상 작동한다        | 미착수    | `pip install -e ".[all]"` → 6개 tool 모두 호출 성공 확인   | 코딩 40h + 검증 4h |
| 1.2 | 핵심 기능이 문서화된 예제로 시연 가능하다 | 미착수    | 3개 예제 시나리오 작성 (H₂O IBO, ORCA 파싱, 벤젠 결합분석) | 6h                 |
| 1.3 | 기존 유사 도구 대비 실질적 기여가 있다    | 확정됨    | paper.md에 기존 MCP 대비 차별점(전자구조 분석) 명시        | 2h (집필 시간)     |
| 1.4 | 소프트웨어가 연구 목적으로 사용 가능하다  | 미착수    | 실제 ORCA 출력 파일 1개로 end-to-end 워크플로우 시연       | 4h                 |

**2. 문서화(Documentation)**

| #   | 요건                                                  | 현재 상태 | 구체적 작업                                                                | 예상 시간 |
| --- | ----------------------------------------------------- | --------- | -------------------------------------------------------------------------- | --------- |
| 2.1 | README에 프로젝트 설명, 설치법, 빠른 시작 가이드 포함 | 미착수    | README.md 작성: 프로젝트 개요 + 설치 + 사용 예시 3개 + 아키텍처 다이어그램 | 8h        |
| 2.2 | API 문서가 존재한다                                   | 미착수    | 모든 public 함수/클래스에 docstring 작성. mkdocs 또는 Sphinx로 자동 생성   | 6h        |
| 2.3 | MCP tool별 사용법 문서                                | 미착수    | 각 tool의 parameters, returns, 사용 예시를 README 또는 별도 docs/에 기술   | 4h        |
| 2.4 | claude_desktop_config.json 설정 가이드                | 미착수    | Claude Desktop/Claude Code에서 연결하는 단계별 가이드 작성                 | 2h        |

**3. 테스트(Tests)**

| #   | 요건                                         | 현재 상태 | 구체적 작업                                                                                                          | 예상 시간        |
| --- | -------------------------------------------- | --------- | -------------------------------------------------------------------------------------------------------------------- | ---------------- |
| 3.1 | 자동화된 테스트 스위트가 존재한다            | 미착수    | pytest 기반 테스트: registry 3개, pyscf_backend 5개, cclib_backend 3개, viz_backend 2개, ase_backend 2개 = 최소 15개 | 12h              |
| 3.2 | CI에서 테스트가 자동 실행된다                | 미착수    | GitHub Actions 워크플로우: Python 3.10/3.11/3.12 매트릭스, pip install + pytest                                      | 3h               |
| 3.3 | 테스트 커버리지가 합리적 수준이다            | 미착수    | pytest-cov 설정, 핵심 경로(compute_ibo, parse_output, visualize_orbital) 커버리지 70%+ 목표                          | 4h (추가 테스트) |
| 3.4 | 백엔드 미설치 시 graceful degradation 테스트 | 미착수    | PySCF 미설치 환경에서 parse_output/convert_format은 정상 작동 확인 테스트 1개                                        | 2h               |

**4. 설치 용이성(Installation)**

| #   | 요건                          | 현재 상태 | 구체적 작업                                                                        | 예상 시간             |
| --- | ----------------------------- | --------- | ---------------------------------------------------------------------------------- | --------------------- |
| 4.1 | pip install로 설치 가능하다   | 미착수    | pyproject.toml에 의존성 정의, `pip install qcviz-mcp[all]` 동작 확인               | 3h                    |
| 4.2 | 의존성이 명확히 선언되어 있다 | 미착수    | [compute], [parse], [viz], [structure], [all] optional-dependencies 정의 완료      | pyproject.toml에 포함 |
| 4.3 | 깨끗한 환경에서 설치 테스트   | 미착수    | 새 venv에서 `pip install -e ".[all]"` + `python -m qcviz_mcp.mcp_server` 성공 확인 | 2h                    |

**5. 커뮤니티 가이드라인**

| #   | 요건                    | 현재 상태 | 구체적 작업                                                                   | 예상 시간 |
| --- | ----------------------- | --------- | ----------------------------------------------------------------------------- | --------- |
| 5.1 | CONTRIBUTING.md 존재    | 미착수    | 기여 가이드: 개발 환경 설정, 코드 스타일(ruff), PR 프로세스, 새 백엔드 추가법 | 3h        |
| 5.2 | CODE_OF_CONDUCT.md 존재 | 미착수    | Contributor Covenant v2.1 채택 (표준 템플릿)                                  | 0.5h      |
| 5.3 | 이슈 템플릿             | 미착수    | Bug report + Feature request 이슈 템플릿 .github/ISSUE_TEMPLATE/              | 1h        |

**6. 논문 원고(paper.md)**

| #   | 요건                            | 현재 상태 | 구체적 작업                                                | 예상 시간            |
| --- | ------------------------------- | --------- | ---------------------------------------------------------- | -------------------- |
| 6.1 | paper.md가 JOSS 형식을 준수한다 | 미착수    | YAML 프론트매터 + Summary + Statement of Need + References | 8h                   |
| 6.2 | paper.bib에 참고문헌이 있다     | 미착수    | 최소 10개 BibTeX 엔트리 (DOI 검증 포함)                    | 3h                   |
| 6.3 | paper.md가 1000단어 내외이다    | 미착수    | 초안 작성 후 워드카운트 확인, 필요시 편집                  | paper.md 작성에 포함 |

**7. 예제 및 튜토리얼**

| #   | 요건                      | 현재 상태 | 구체적 작업                                                                      | 예상 시간 |
| --- | ------------------------- | --------- | -------------------------------------------------------------------------------- | --------- |
| 7.1 | 최소 1개 완전한 사용 예제 | 미착수    | examples/example_ibo_analysis.md: Claude에서 "물 분자의 IBO 분석" 전체 대화 기록 | 3h        |
| 7.2 | 테스트용 분자 파일 포함   | 미착수    | examples/example_molecules/에 water.xyz, benzene.xyz, ethanol.xyz                | 1h        |
| 7.3 | ORCA/Gaussian 파싱 예제   | 미착수    | 공개된 ORCA 출력 파일 1개 + 파싱 예시                                            | 2h        |

**8. 라이선스**

| #   | 요건                        | 현재 상태 | 구체적 작업                                                                                                                 | 예상 시간 |
| --- | --------------------------- | --------- | --------------------------------------------------------------------------------------------------------------------------- | --------- |
| 8.1 | OSI 승인 라이선스 파일 존재 | 미착수    | MIT 라이선스 채택, LICENSE 파일 생성                                                                                        | 0.5h      |
| 8.2 | 의존성 라이선스 호환성 확인 | 미착수    | ASE(LGPL)는 별도 패키지로 의존 — MIT 프로젝트와 호환됨 (LGPL 코드를 포함하지 않고 import만 하므로). 이 판단을 README에 명시 | 1h        |

**총 예상 시간: 약 120h (버퍼 20% 포함 시 ~144h = 주 25h 기준 약 6주)**

---

### A2. JOSS paper.md 상세 초안

```markdown
---
title: "QCViz-MCP: A Model Context Protocol Server for Quantum Chemistry Visualization and Electronic Structure Analysis"
tags:
  - Python
  - quantum chemistry
  - orbital visualization
  - Model Context Protocol
  - intrinsic bond orbitals
  - intrinsic atomic orbitals
authors:
  - name: [사용자]
    orcid: 0000-0000-0000-0000
    affiliation: 1
affiliations:
  - name: [소속]
    index: 1
date: 2026-04-XX
bibliography: paper.bib
---

# Summary

QCViz-MCP is an open-source Python server that exposes quantum chemistry
visualization and electronic structure analysis capabilities through the
Model Context Protocol (MCP) [@anthropic2024mcp]. The software enables
large language model (LLM) clients such as Claude Desktop to perform
orbital computations, bonding analysis, and molecular visualization
through natural language interactions.

The server implements a pluggable backend architecture with four core
backends: PySCF [@sun2020pyscf] for intrinsic atomic orbital (IAO) and
intrinsic bond orbital (IBO) computations [@knizia2013iao], cclib
[@berquist2024cclib] for parsing output files from 16 quantum chemistry
programs, py3Dmol [@rego20153dmol] for interactive three-dimensional
orbital isosurface rendering, and ASE [@larsen2017ase] for molecular
structure manipulation and file format conversion.

QCViz-MCP provides six MCP tools: `compute_ibo` for IBO localization
with cube file generation, `visualize_orbital` for 3D isosurface
rendering from cube files, `parse_output` for extracting energies,
geometries, and orbital data from ORCA, Gaussian, and 14 other programs,
`compute_partial_charges` for IAO-based atomic charges, `convert_format`
for structure file conversion among 40+ formats, and `analyze_bonding`
for IBO-based bond order and bond type analysis.

# Statement of need

The integration of LLMs with scientific computing tools is transforming
research workflows across chemistry and materials science. Recent efforts
have produced MCP servers for molecular visualization
[@chatmol2024; @pymolmcp2025], atomistic simulations
[@mcpatomictoolkit2025], VASP automation [@vaspilot2025], and
cheminformatics [@chemlint2026]. However, none of these tools addresses
electronic structure analysis at the orbital level — the computation,
visualization, and interpretation of molecular orbitals, partial charges,
and chemical bonding.

This gap is significant because orbital-level analysis is central to
understanding chemical reactivity, bonding, and molecular properties.
Researchers routinely perform density functional theory (DFT)
calculations, generate orbital visualizations, and analyze bonding
patterns, yet these tasks require manual scripting across multiple
disconnected tools: a quantum chemistry program for computation, a
separate program for parsing, and another for visualization.

QCViz-MCP fills this gap by providing a unified MCP interface to the
complete workflow: computation, parsing, visualization, and analysis.
The target users are computational chemists who use LLM assistants in
their daily work and wish to perform orbital-level analysis through
natural language without writing custom scripts for each task.

The software adopts the IAO/IBO methodology of Knizia
[@knizia2013iao; @knizia2015electron] as its core analysis framework.
IAO-based partial charges are basis-set independent and chemically
intuitive, while IBOs provide a clear picture of chemical bonds as
localized orbitals — making them particularly well suited for
LLM-mediated analysis where chemical interpretability is essential.

# Key features

**Pluggable backend architecture.** All computational, visualization,
parsing, and structure manipulation functionality is encapsulated in
abstract base classes (`ComputeBackend`, `VizBackend`, `ParserBackend`,
`StructureBackend`). New backends can be added by implementing these
interfaces without modifying existing tool code. A runtime registry
automatically detects installed packages and gracefully degrades when
optional dependencies are absent.

**IAO/IBO orbital analysis.** The `compute_ibo` tool leverages PySCF's
`pyscf.lo.iao` and `pyscf.lo.ibo` modules to compute intrinsic bond
orbitals from a DFT or Hartree-Fock calculation. Cube files are
generated for each IBO, enabling subsequent visualization.

**Multi-program output parsing.** The `parse_output` tool uses cclib to
extract energies, geometries, molecular orbital coefficients, and
vibrational frequencies from output files produced by ORCA, Gaussian,
GAMESS, NWChem, Psi4, Q-Chem, Turbomole, and nine other programs.

**Interactive orbital visualization.** The `visualize_orbital` tool
renders orbital isosurfaces from cube files using py3Dmol, producing
interactive HTML visualizations with positive and negative lobes
displayed in distinct colors.

# Comparison with existing tools

\autoref{tab:comparison} compares QCViz-MCP with existing chemistry
MCP servers.

| Feature                           | pymol-mcp | molecule-mcp | mcp-atomictoolkit | QCViz-MCP         |
| --------------------------------- | --------- | ------------ | ----------------- | ----------------- |
| Molecular structure visualization | Yes       | Yes          | File-based        | Yes               |
| Orbital isosurface rendering      | No        | No           | No                | **Yes**           |
| IAO/IBO computation               | No        | No           | No                | **Yes**           |
| Partial charge analysis           | No        | No           | Mulliken only     | **IAO-based**     |
| Bond order analysis               | No        | No           | No                | **Yes**           |
| Multi-program output parsing      | No        | No           | No                | **16 programs**   |
| Backend architecture              | Single    | Single       | Single            | **Pluggable ABC** |

: Comparison of QCViz-MCP with existing chemistry MCP servers.
\label{tab:comparison}

# Example usage

A researcher asks Claude Desktop: "Compute the intrinsic bond orbitals
of water and show me the O-H bonding orbital." The LLM client calls
`compute_ibo` with the water molecule coordinates, receives five IBO
cube files (one O 1s core, two O-H bonds, two O lone pairs), then
calls `visualize_orbital` on the O-H bonding orbital cube file to
produce an interactive 3D isosurface visualization — all within a
single conversational turn.

Similarly, a researcher can say: "Parse this ORCA output file and tell
me the HOMO-LUMO gap." The `parse_output` tool extracts molecular
orbital energies, and the LLM computes and reports the gap value with
chemical context.

# Acknowledgements

The authors thank the developers of PySCF, cclib, py3Dmol, ASE, and
FastMCP for their open-source contributions that form the foundation
of this work.

# References
```

---

### A3. 주차별 개발 일정

```
Week 1: 프로젝트 초기화 + 코어 인프라
├── 월 (5h): pyproject.toml 작성, 디렉토리 구조 생성, git init,
│            GitHub 레포 생성, LICENSE(MIT), .gitignore 작성
├── 화 (5h): backends/base.py — 4개 ABC + 5개 dataclass 구현
│            (이전 대화의 스켈레톤을 실제 코드로 전환)
├── 수-목 (8h): backends/registry.py — 패키지 탐지, 팩토리 함수,
│               BackendNotAvailableError 구현 + 단위 테스트 3개
├── 금 (4h): PySCF 학습 — pyscf.lo.iao / pyscf.lo.ibo 예제 실행
│            (04-ibo_benzene_cubegen.py를 로컬에서 실행하여
│            cube 파일이 생성되는지 확인)
├── 마일스톤: 빈 프로젝트 구조가 pip install -e . 으로 설치되고,
│            registry 테스트 3개가 통과하며,
│            PySCF IBO 예제가 로컬에서 실행된다.
└── 검증 기준: `pip install -e ".[all]"` 성공 + `pytest tests/test_registry.py`
              3개 PASSED + water IBO cube 파일 5개 /tmp에 생성됨
```

```
Week 2: PySCF 백엔드 + 시각화 백엔드
├── 월 (5h): pyscf_backend.py — compute_scf(), _build_mol() 구현
│            H₂O HF/B3LYP 계산이 성공하고 에너지를 반환하는지 확인
├── 화 (5h): pyscf_backend.py — compute_iao(), compute_ibo() 구현
│            H₂O IBO 계산 → cube 파일 5개 생성 확인
├── 수 (4h): pyscf_backend.py — get_partial_charges() (Mulliken 우선 구현,
│            IAO 전하는 Week 3에서 완성)
│            analyze_bonding() 스텁 구현 (기본 구조만)
├── 목 (5h): viz_backend.py — render_orbital(), render_molecule() 구현
│            H₂O IBO cube 파일 → py3Dmol HTML 출력 확인
├── 금 (4h): pyscf_backend 테스트 5개 작성
│            (water_ibo_count, benzene_ibo_count, scf_energy_reasonable,
│            mulliken_charges_sum_to_zero, cube_files_exist)
├── 마일스톤: PySCF 백엔드가 H₂O/C₆H₆에서 IBO를 계산하고
│            py3Dmol로 시각화 HTML을 생성한다.
└── 검증 기준: `pytest tests/test_compute_ibo.py` 5개 PASSED +
              /tmp/qcviz/ibo_000.cube 파일이 유효한 cube 파일 +
              생성된 HTML을 브라우저에서 열면 등치면이 보인다
```

```
Week 3: 파싱 백엔드 + 구조 백엔드 + MCP 서버 통합
├── 월 (5h): cclib_backend.py — parse_output(), extract_orbitals(),
│            extract_geometry(), supported_programs() 구현
├── 화 (4h): cclib_backend 테스트 3개 — ORCA 출력 파일 1개로
│            에너지/좌표/MO 에너지 파싱 확인
│            (테스트용 ORCA 출력: cclib 레포의 테스트 데이터 활용)
├── 수 (4h): ase_backend.py — read_structure(), write_structure(),
│            convert_format() 구현 + 테스트 2개
├── 목 (5h): mcp_server.py — FastMCP 서버에 6개 tool 등록
│            각 tool 함수가 registry를 통해 백엔드를 호출하도록 연결
├── 금 (5h): 통합 테스트 — Claude Desktop에서 실제로 tool 호출 테스트
│            claude_desktop_config.json 작성 및 연동 확인
├── 마일스톤: 6개 tool이 모두 MCP 프로토콜로 호출 가능하고
│            Claude Desktop에서 "물 분자의 IBO를 보여줘"가 작동한다.
└── 검증 기준: `python -m qcviz_mcp.mcp_server` 시작 성공 +
              Claude Desktop에서 compute_ibo tool이 목록에 보이고
              호출 시 JSON 응답이 돌아온다
```

```
Week 4: IAO 전하 완성 + 결합 분석 + 테스트 보강
├── 월 (5h): pyscf_backend.py — _compute_iao_charges() 완전 구현
│            (IAO 투영 행렬 → 밀도 행렬 투영 → 원자별 전자수 → 전하)
├── 화 (5h): pyscf_backend.py — analyze_bonding() 완전 구현
│            (IBO별 원자 기여도 분석 → 결합에 기여하는 IBO 식별
│            → 결합 차수 = 해당 원자쌍에 기여하는 IBO 전자수 합)
├── 수 (4h): 추가 테스트 작성 — 총 테스트 수를 15개 이상으로 확보
│            IAO 전하 합 = 0 테스트, 에탄올 O-H 결합 분석 테스트 등
├── 목 (4h): 엣지 케이스 처리 — 잘못된 입력(빈 문자열, 존재하지 않는 파일,
│            지원하지 않는 포맷) 시 명확한 에러 메시지 반환
├── 금 (4h): GitHub Actions CI 설정 — .github/workflows/tests.yml
│            Python 3.10/3.11/3.12 매트릭스, pytest + coverage 리포트
├── 마일스톤: 6개 tool 모두 정상 작동, 엣지 케이스 처리 완료,
│            CI에서 15개+ 테스트 자동 실행.
└── 검증 기준: GitHub Actions 초록 체크 + pytest 15개+ PASSED +
              coverage 70%+ on backends/ 디렉토리
```

```
Week 5: 문서화 + 예제 + 커뮤니티 파일
├── 월 (5h): README.md 작성 — 프로젝트 개요, 아키텍처 다이어그램,
│            설치법(pip, 개발모드), 빠른 시작(3개 예시),
│            tool 목록 + 간략 설명, 라이선스
├── 화 (4h): examples/ 작성 — example_ibo_analysis.md (H₂O IBO 전체 워크플로우),
│            example_molecules/ (water.xyz, benzene.xyz, ethanol.xyz),
│            ORCA 파싱 예제 (공개 데이터 사용)
├── 수 (3h): CONTRIBUTING.md, CODE_OF_CONDUCT.md,
│            .github/ISSUE_TEMPLATE/ (bug_report.md, feature_request.md)
├── 목 (4h): docstring 검토 — 모든 public 클래스/함수에 Google 스타일 docstring,
│            타입 힌트 검토, ruff 린팅 통과 확인
├── 금 (3h): claude_desktop_config.json 가이드 상세화,
│            "깨끗한 환경 설치 테스트" — 새 venv에서 처음부터 설치 후 작동 확인
├── 마일스톤: README가 완전하고, 예제 3개가 있으며,
│            새 사용자가 README만 보고 설치+실행 가능하다.
└── 검증 기준: 다른 사람(또는 자신이 새 venv에서)이 README만 보고
              5분 내에 설치 + 첫 tool 호출 성공
```

```
Week 6: JOSS paper.md 작성 + 최종 점검 + 제출
├── 월 (5h): paper.md 초안 작성 (A2 섹션의 초안을 실제 데이터로 업데이트)
├── 화 (4h): paper.bib 정리 — 모든 참고문헌 DOI 검증, BibTeX 엔트리 완성
│            (10개 이상, Crossref에서 DOI 확인)
├── 수 (3h): paper.md 교정 — 워드카운트 확인(1000단어 내외),
│            문법 검토, 비교 표 검증
├── 목 (3h): JOSS 사전 체크 — joss-paper 도구로 paper.md 검증,
│            GitHub 레포 공개 설정, 태그(v0.1.0) 생성,
│            Zenodo 연동(DOI 사전 예약)
├── 금 (3h): JOSS 제출 — https://joss.theoj.org 에서 제출,
│            editor 배정 대기
├── 마일스톤: JOSS에 논문이 제출되고, GitHub 레포가 공개되어 있으며,
│            v0.1.0 태그가 존재한다.
└── 검증 기준: JOSS submission confirmation 이메일 수신 +
              GitHub 레포에 v0.1.0 태그 + Zenodo DOI 예약 완료
```

**전체 일정 요약: 6주 (주당 ~23h, 버퍼 포함)**

---

### A4. 리스크 레지스터

| #   | 리스크                                                          | 발생 확률  | 영향 (1-5) | 대응 전략                                                                                                                                                                                                                                                                                     |
| --- | --------------------------------------------------------------- | ---------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R1  | **PySCF IBO 계산이 특정 분자(전이금속 등)에서 수렴 실패**       | 중간 (30%) | 3          | MVP 벤치마크 분자를 유기 소분자 3개(H₂O, C₆H₆, C₂H₅OH)로 한정. 전이금속은 "known limitation"으로 명시. 수렴 실패 시 에러 메시지에 `max_cycle` 증가 또는 초기 추정 변경을 안내하는 코드 작성                                                                                                   |
| R2  | **py3Dmol headless PNG 생성 실패**                              | 높음 (60%) | 2          | PNG 생성을 "optional feature"로 격하. 핵심 출력은 HTML로 고정. README에 "PNG export requires Playwright"를 명시. JOSS 리뷰에서 HTML 출력이면 충분                                                                                                                                             |
| R3  | **JOSS 리뷰어가 "기존 도구와 차별점 불분명" 지적**              | 중간 (40%) | 4          | paper.md 비교 표(A2의 표)를 사전에 강화. pymol-mcp/molecule-mcp/mcp-atomictoolkit 어디에도 오비탈 계산/시각화가 없음을 명시. 리뷰어 코멘트 시 "orbital-level analysis는 이 MCP가 유일"이라는 구체적 반박 준비                                                                                 |
| R4  | **ASE(LGPL)와 MIT 프로젝트 라이선스 충돌 가능성**               | 낮음 (15%) | 3          | MIT 프로젝트가 LGPL 라이브러리를 import로 사용하는 것은 허용됨(LGPL 코드를 프로젝트에 복사하지 않는 한). 이 해석을 README의 라이선스 섹션에 명시. 만약 리뷰어가 문제 제기 시, ASE를 optional dependency로 격리(이미 그렇게 설계됨)하고 "ASE 없이도 compute/parse/viz tool은 정상 작동"을 시연 |
| R5  | **테스트 커버리지 부족 지적**                                   | 중간 (35%) | 3          | 목표를 70%로 설정하되, 핵심 경로(compute_ibo end-to-end, parse_output ORCA)에 대해서는 100% 커버리지. 리뷰어 지적 시 추가 테스트 작성에 2-3일 할당(리비전 기간에 충분)                                                                                                                        |
| R6  | **PySCF 설치가 특정 OS(Windows)에서 실패**                      | 중간 (40%) | 2          | README에 "Linux/macOS 권장, Windows는 WSL2 사용"을 명시. CI 매트릭스에서 ubuntu-latest만 테스트하고, macOS는 best-effort. PySCF 공식 문서의 설치 가이드를 링크. PySCF 없이도 parse/viz/convert tool은 작동한다는 점을 강조                                                                    |
| R7  | **cclib가 최신 ORCA 6.0 출력을 파싱하지 못함**                  | 낮음 (20%) | 2          | 테스트에 사용하는 ORCA 출력 파일을 cclib가 공식 지원하는 버전(ORCA 5.0)으로 고정. ORCA 6.0 지원 여부를 "future work"로 명시. cclib의 GitHub 이슈를 확인하여 ORCA 6.0 지원 상태를 README에 기재                                                                                                |
| R8  | **FastMCP 메이저 업데이트로 API 호환성 깨짐**                   | 낮음 (15%) | 4          | pyproject.toml에 `fastmcp>=2.0,<4.0`으로 버전 상한 고정. FastMCP 3.0 beta가 2026년 2월에 나왔으므로, 3.0 정식 출시 시 호환성 확인 후 업데이트. 핵심 의존은 `@mcp.tool()` 데코레이터뿐이므로 마이그레이션 비용 낮음                                                                            |
| R9  | **개발 기간이 6주를 초과 (스코프 크립)**                        | 높음 (50%) | 3          | 엄격한 스코프 관리: 6개 tool 외 추가 기능 금지. "이건 v0.2에서" 리스트를 별도 파일(ROADMAP.md)에 관리. Week 4 끝에 "6개 tool 모두 작동하는가?" 체크포인트 설정. NO이면 Week 5-6 일정 재조정                                                                                                   |
| R10 | **JOSS 에디터가 "scope이 너무 좁다" 또는 "너무 넓다"로 reject** | 낮음 (10%) | 5          | JOSS는 "유의미한 연구 기여를 하는 소프트웨어"를 기준으로 함. pre-submission inquiry를 먼저 보내서 scope 적합성 확인. reject 시 JOSS 대안: Journal of Cheminformatics(Software 카테고리), SoftwareX                                                                                            |

---

## [Section A] 자체 검증

- [x] 계획이 1인 개발자 기준으로 현실적인가? — 주 23h, 6주. 풀타임 개발자에겐 여유 있고, 파트타임이면 8주로 확장
- [x] 모든 일정에 버퍼가 포함되어 있는가? — 각 작업에 자체 버퍼, 전체 120h → 144h (20% 버퍼)
- [x] "무엇을", "어떻게", "언제까지"가 모두 명시되어 있는가? — 각 주의 각 일에 작업+시간+검증기준
- [x] JOSS paper.md가 실제 제출 가능한 완성도인가? — [사용자]/[소속] placeholder 2개만 남기고 완전한 문장

---

## SECTION B: 2단 로켓 (JCIM) 사전 설계

### B1. JOSS-JCIM 범위 구분

**1. JOSS 논문의 범위 (여기까지만)**

JOSS 논문은 소프트웨어 자체를 기술합니다. 아키텍처(Backend ABC, Registry 패턴), 6개 tool의 인터페이스, 설치법, 사용법을 설명합니다. 과학적 벤치마크나 정확도 비교는 포함하지 않습니다. "이런 소프트웨어가 있다, 이렇게 작동한다, 이렇게 설치하고 쓴다"가 전부입니다.

**2. JCIM 논문의 범위 (여기부터)**

JCIM 논문은 그 소프트웨어를 사용한 과학적 평가를 다룹니다. 15개 분자에 대한 IAO/IBO 벤치마크, PySCF 결과와 IboView 결과의 수치 비교, 수동 워크플로우 대비 MCP 워크플로우의 시간/단계 절감 효과, 16개 프로그램 파싱 호환성 테스트를 포함합니다. 핵심은 "이 소프트웨어가 실제로 정확하고, 유용하고, 기존보다 효율적인가?"에 대한 체계적 답입니다.

**3. 겹치는 부분과 겹치지 않는 부분**

겹치는 부분: 소프트웨어의 존재와 기본 설명 (JCIM Introduction에서 QCViz-MCP를 소개할 때 1-2 문단). 이 부분은 자기 인용으로 처리합니다.

겹치지 않는 부분: JOSS에는 벤치마크/평가가 없고, JCIM에는 아키텍처 상세 설계가 없습니다. JOSS는 "무엇을 만들었나", JCIM은 "그것이 얼마나 잘 작동하나".

**4. JCIM에서 JOSS를 인용하는 방법**

JCIM 논문의 Section 2(또는 3)에서: "The QCViz-MCP server, described in detail in [JOSS citation], provides six MCP tools for quantum chemistry analysis. In this work, we evaluate the accuracy and efficiency of these tools on a benchmark set of 15 molecules..."

이것은 학술적으로 정상적인 패턴입니다. cclib 개발자들도 원 논문(JCC 2008)과 아키텍처 업데이트 논문(JCP 2024)을 별도로 발표했습니다.

**5. 구체적 경계선**

| 내용                          | JOSS       | JCIM                    |
| ----------------------------- | ---------- | ----------------------- |
| 아키텍처 설명 (ABC, Registry) | ✅ 상세히  | ❌ (JOSS 인용으로 대체) |
| Tool 인터페이스 정의          | ✅ 상세히  | 요약만 (표 1개)         |
| 설치/사용 가이드              | ✅         | ❌                      |
| 코드 예시                     | ✅ (1-2개) | ❌                      |
| 벤치마크 분자 데이터          | ❌         | ✅ (15개 분자)          |
| PySCF vs IboView 수치 비교    | ❌         | ✅                      |
| 워크플로우 시간 비교          | ❌         | ✅                      |
| 파싱 호환성 테스트            | ❌         | ✅ (16 프로그램)        |
| LLM 해석 사례 분석            | ❌         | ✅                      |

---

### B2. JCIM 논문 기여점 3개

```
기여점 1: 전자 구조 분석의 MCP 통합 — 빈 공간 점유
├── 주장: 기존 화학 MCP 서버(pymol-mcp, molecule-mcp, mcp-atomictoolkit,
│         VASPilot, ChemLint)는 분자 구조 수준의 작업만 지원하며,
│         오비탈 계산/시각화/결합 분석을 MCP로 통합한 도구는 QCViz-MCP가 최초이다.
├── 근거: 6개 기존 MCP 서버의 tool 목록을 전수 조사하여,
│         "orbital", "IBO", "IAO", "charge", "bonding" 관련 tool이
│         단 하나도 없음을 표로 제시. QCViz-MCP의 6개 tool 중 4개
│         (compute_ibo, visualize_orbital, compute_partial_charges,
│         analyze_bonding)가 이 빈 공간을 채운다.
├── 비교: 표 1에서 기존 6개 MCP 서버 vs QCViz-MCP의 기능 매트릭스 비교.
│         "Yes/No" 그리드로 시각적 차별화.
└── 리뷰어 예상 반론: "MCP라는 프로토콜에 의존하는 것은 범용성이 떨어진다"
   → 대응: MCP는 오픈 프로토콜(JSON-RPC 기반)이며 Claude 외에도
     다수의 LLM 클라이언트가 지원. 프로토콜 의존성은 REST API 의존성과 동일한 수준.
```

```
기여점 2: LLM 기반 양자화학 워크플로우의 효율성 입증
├── 주장: QCViz-MCP를 통한 LLM-assisted 워크플로우는 수동 스크립팅 워크플로우
│         대비 완료 시간을 3-5배 단축하고 필요 단계 수를 절반 이하로 줄인다.
├── 근거: 5개 대표 태스크(IBO 계산+시각화, 출력 파싱, 부분전하 비교,
│         결합 분석, 포맷 변환)에 대해 두 워크플로우를 비교:
│         (A) 수동: PySCF 스크립트 작성 → 실행 → cube 파일 열기 → 별도 시각화
│         (B) MCP: 자연어 요청 → 자동 실행 → 결과 수신
│         각 태스크의 소요 시간(초)과 단계 수를 측정하여 표와 막대 그래프 제시.
├── 비교: 수동 워크플로우(PySCF + py3Dmol Jupyter 노트북) vs
│         QCViz-MCP 워크플로우(Claude Desktop 대화).
└── 리뷰어 예상 반론: "시간 비교가 공정하지 않다 — 숙련 사용자는 스크립트를
   이미 갖고 있다"
   → 대응: (1) "첫 사용" 시나리오와 "반복 사용" 시나리오를 분리 측정.
     (2) MCP의 장점은 반복 사용에서도 유지됨 — 매번 다른 분자에 적용할 때
     스크립트 수정 불필요.
     (3) 한계점으로 인정: 대규모 배치 작업에서는 수동 스크립트가 더 효율적.
```

```
기여점 3: IAO/IBO 분석의 접근성 민주화
├── 주장: IAO/IBO 분석은 강력한 화학 분석 도구이지만 사용 장벽이 높다
│         (PySCF 스크립팅 필요, 또는 IboView 수동 조작 필요).
│         QCViz-MCP는 자연어 인터페이스를 제공하여 비전문가(유기화학자,
│         학부생 등)도 IAO/IBO 분석을 수행 가능하게 한다.
├── 근거: IAO/IBO를 사용한 논문 수(Web of Science 검색)를 연도별로 제시하여
│         수요가 증가하고 있음을 보여줌. 그러나 사용 도구는 IboView(GUI 전용)와
│         PySCF(Python 코딩 필요)뿐임을 지적. QCViz-MCP는 세 번째 경로
│         (자연어 기반)를 제공.
├── 비교: 동일 분석(에탄올의 O-H 결합 IBO 시각화)을 3가지 방법으로 수행:
│         (A) IboView: 분자 입력 → DFT 계산 → IBO 버튼 클릭 → 오비탈 선택
│         (B) PySCF 스크립트: 20줄 코드 작성 → 실행 → cube 파일 → py3Dmol
│         (C) QCViz-MCP: "에탄올의 O-H 결합 오비탈을 보여줘" 한 문장
│         세 방법의 소요 시간 + 필요 전문 지식 수준을 비교.
└── 리뷰어 예상 반론: "LLM이 잘못된 화학 해석을 생성할 위험은?"
   → 대응: QCViz-MCP는 계산을 수행하는 도구이지, 해석을 생성하는 도구가 아님.
     LLM의 해석은 tool 결과(수치 데이터)에 기반하며, 사용자가 검증 가능.
     이것은 한계점이자 향후 연구 방향(LLM 화학 해석 정확도 벤치마크)으로 명시.
```

---

### B3. 벤치마크 설계서

**1. 분자 데이터셋 (15개)**

| #   | 분자명       | SMILES                | 원자수 | 선택 근거                                                         |
| --- | ------------ | --------------------- | ------ | ----------------------------------------------------------------- |
| 1   | Water        | O                     | 3      | 최소 분자, IBO = 2 O-H + 2 lone pair + 1 core. 교과서적 검증 대상 |
| 2   | Ammonia      | N                     | 4      | 1개 lone pair + 3개 N-H 결합, 고립쌍 시각화 검증                  |
| 3   | Methane      | C                     | 5      | 4개 동등한 C-H σ 결합, IBO 대칭성 검증                            |
| 4   | Ethylene     | C=C                   | 6      | σ+π 이중결합, IBO가 σ/π를 분리하는지 검증                         |
| 5   | Acetylene    | C#C                   | 4      | 삼중결합(σ+2π), 고차 결합 IBO 분해 검증                           |
| 6   | Formaldehyde | C=O                   | 4      | 이종 이중결합(C=O), 극성 결합의 IAO 전하 검증                     |
| 7   | Benzene      | c1ccccc1              | 12     | π 전자계 비국소화, IBO가 3개 π "바나나 결합"으로 국소화 확인      |
| 8   | Ethanol      | CCO                   | 9      | O-H vs C-O vs C-H 결합 비교, 다기능기 분자                        |
| 9   | Acetic acid  | CC(=O)O               | 8      | C=O + C-O + O-H, 카르복실기 전자 구조                             |
| 10  | Methylamine  | CN                    | 7      | N lone pair + C-N + N-H, 아민 기능기                              |
| 11  | Acetone      | CC(=O)C               | 10     | 카보닐기, 중간 크기 분자                                          |
| 12  | Phenol       | Oc1ccccc1             | 13     | 방향족 + O-H, 공명 효과                                           |
| 13  | Aniline      | Nc1ccccc1             | 14     | 방향족 + N lone pair 공명, 전하 분포 검증                         |
| 14  | Glycine      | NCC(=O)O              | 10     | 아미노산, 생화학적 관련성                                         |
| 15  | Aspirin      | CC(=O)Oc1ccccc1C(=O)O | 21     | 가장 큰 분자, 다기능기, 성능 한계 테스트                          |

**2. 평가 메트릭**

**정확도 메트릭 (3개)**:

(a) IAO 부분전하 비교: PySCF IAO 전하 vs IboView 자체 IAO 전하. 분자당 원자별 전하 차이의 MAE(Mean Absolute Error)를 계산. 기대값: MAE < 0.02 e (동일 알고리즘이므로 수치 오차 수준이어야 함). 만약 MAE > 0.05 e이면 구현 차이를 분석하여 보고.

(b) IBO 오비탈 중첩 비교: PySCF IBO와 IboView IBO 사이의 오비탈 중첩(overlap integral)을 계산. 동일 기저함수 사용 시 |<φ_PySCF|φ_IboView>|² > 0.99 가 기대됨.

(c) 결합 차수 비교: IBO 기반 결합 차수를 Mayer bond order와 비교. 정성적 일치(단일결합 ~1.0, 이중결합 ~2.0) 확인.

**사용성 메트릭 (2개)**:

(d) 워크플로우 완료 시간(초): 5개 태스크 × 2가지 방법(MCP vs 수동). 각 태스크를 3회 반복하여 평균 ± 표준편차.

(e) 필요 단계 수: 각 워크플로우에서 사용자가 수행해야 하는 독립적 작업 단계(코드 줄 수, 파일 조작, 커맨드 입력 등)의 수.

**호환성 메트릭 (1개)**:

(f) 파싱 성공률: cclib가 지원하는 16개 프로그램 중, 공개된 테스트 출력 파일(cclib 자체 테스트 데이터)에 대해 에너지+좌표 파싱 성공/실패 비율.

**3. 실험 프로토콜**

정확도 실험 프로토콜:

- 15개 분자 모두에 대해 동일 조건으로 계산: B3LYP/cc-pVDZ, restricted closed-shell.
- PySCF: `pyscf.lo.ibo.ibo()` 호출 → cube 파일 + IAO 전하 추출.
- IboView: 동일 분자의 .molden 파일을 IboView에 로드 → IBO 계산 → 전하 + 오비탈 내보내기.
- 비교 스크립트: 원자별 전하 차이 MAE 계산, 오비탈 중첩 행렬 계산.
- 모든 입력 파일, 스크립트, 결과를 GitHub 레포의 `benchmark/` 디렉토리에 공개.

사용성 실험 프로토콜:

- 5개 태스크 정의: (1) 물 IBO 계산+시각화, (2) ORCA 출력 HOMO-LUMO gap 추출, (3) 에탄올 IAO 전하 계산, (4) 벤젠 결합 분석, (5) xyz→cif 포맷 변환.
- 수동 방법: Jupyter 노트북에서 PySCF + py3Dmol + cclib 코드를 직접 작성하여 실행.
- MCP 방법: Claude Desktop에서 자연어로 요청하여 tool 호출.
- 시간 측정: 화면 녹화 후 측정. "첫 키 입력"부터 "결과 확인"까지.
- 3회 반복 측정, 1회차는 "첫 사용"(학습 포함), 2-3회차는 "반복 사용".

**4. 예상 결과**

정확도: PySCF IAO 전하와 IboView IAO 전하의 MAE는 0.01-0.02 e 수준으로 예상. 두 구현 모두 Knizia(2013)의 동일 알고리즘을 따르므로, 차이는 DFT 그리드와 SCF 수렴 기준의 미세한 차이에서만 발생. 벤젠의 π IBO에서 약간의 위상(sign) 차이는 있을 수 있으나 물리적 내용은 동일.

사용성: MCP 워크플로우가 수동 대비 3-5배 빠를 것으로 예상. 수동 방법의 가장 큰 병목은 "코드 작성 시간"이며, MCP는 이를 제거. 단, 포맷 변환 같은 단순 태스크에서는 차이가 줄어들 것(ASE 한 줄 코드 vs MCP 한 문장 → 비슷).

호환성: cclib는 16개 프로그램을 공식 지원하므로 에너지+좌표 파싱 성공률 100%에 근접 예상. MO 계수 파싱은 프로그램에 따라 지원이 불완전할 수 있어 80-90% 예상.

---

### B4. JCIM 제출 타임라인

```
JOSS 제출 (Week 6 끝) ─────────────────────────────────────────
    │
    ├── Week 7-8: JOSS 리뷰 대기 (에디터 배정 + 리뷰어 배정)
    │   이 기간 활용:
    │   ├── IboView 설치 + 15개 분자 IboView IBO 계산 (비교 데이터 확보)
    │   ├── 벤치마크 스크립트 작성 (benchmark/ 디렉토리)
    │   └── JCIM 논문 Introduction + Related Work 초안 작성
    │
    ├── Week 9-10: JOSS 리뷰 응답 + 벤치마크 실행
    │   ├── JOSS 리뷰어 피드백 반영 (코드 수정, 문서 보강)
    │   ├── 15개 분자 정확도 벤치마크 실행 (PySCF vs IboView)
    │   └── 5개 태스크 사용성 벤치마크 실행 (시간 측정)
    │
    ├── Week 11-12: JCIM 논문 집필
    │   ├── Methods + Results 작성 (벤치마크 결과 표+그래프)
    │   ├── Discussion + Conclusion 작성
    │   └── 그림 5-7개 생성 (비교 표, 막대 그래프, 오비탈 시각화)
    │
    ├── Week 13: 교정 + 공동저자 검토
    │
    └── Week 14: JCIM 제출
        (JOSS 출판 전이라도 "under review at JOSS"로 인용 가능,
         또는 JOSS가 이미 accept되었으면 DOI 인용)

총 소요: JOSS 제출 후 +8주 (약 2개월)
```

---

## [Section B] 자체 검증

- [x] 계획이 1인 개발자 기준으로 현실적인가? — JOSS 리뷰 대기 기간(4-6주)을 JCIM 준비에 활용
- [x] 모든 일정에 버퍼가 포함되어 있는가? — Week 13을 교정+버퍼로 확보
- [x] "무엇을", "어떻게", "언제까지"가 모두 명시되어 있는가? — 벤치마크 프로토콜까지 상세
- [x] 이중출판 우려가 해소되었는가? — JOSS=소프트웨어, JCIM=과학적 평가로 명확 구분

---

## SECTION C: 3단 로켓 (JCTC) 가능성 평가

### C1. "반응경로 IBO 전자흐름 자동화"의 기술적 난관

**난관 1: 오비탈 추적(Orbital Tracking) 문제**

IRC(Intrinsic Reaction Coordinate)의 연속 스텝에서 "같은" IBO를 어떻게 식별하는가. IBO는 각 기하 구조에서 독립적으로 계산되므로, step n의 IBO_3과 step n+1의 IBO_3이 동일한 화학 결합을 나타낸다는 보장이 없습니다. 오비탈의 순서가 바뀌거나, 하나의 IBO가 두 개로 갈라지거나, 두 개가 합쳐질 수 있습니다.

해결 방법: 인접 스텝 간 오비탈 중첩 행렬(overlap matrix) S_ij = <IBO_i(step n) | IBO_j(step n+1)>을 계산하고, Hungarian algorithm으로 최대 중첩 매칭을 수행합니다. 이 방법은 Knizia & Klein(ACIE 2015)에서 수동으로 수행한 것과 동일한 원리이지만 자동화됩니다.

기술 난이도: 중간. PySCF에서 두 다른 기하 구조의 오비탈 간 중첩을 계산하려면 AO 중첩 행렬을 별도로 구성해야 합니다. 이것은 비자명하지만 불가능하지 않습니다. `pyscf.gto.intor('int1e_ovlp')`와 기저함수 변환으로 구현 가능합니다.

**판정: GO — 추가 조사 후 구현 가능** 🔶

**난관 2: Curly Arrow 자동 생성**

전자 흐름을 어떤 기준으로 판단하는가. "전자가 A 원자에서 B 원자로 이동했다"를 어떻게 정량화하는가.

해결 방법: 각 IBO의 원자별 기여도(IAO 투영 가중치)를 각 IRC 스텝에서 계산합니다. 스텝 n에서 IBO_k가 원자 A에 80%, 원자 B에 20% 기여하고, 스텝 n+m에서 원자 A에 20%, 원자 B에 80%로 변했다면, "2개 전자가 A→B로 이동"으로 판단합니다. 기여도 변화량이 threshold(예: 0.3) 이상인 경우만 화살표로 표시합니다.

기술 난이도: 중간~높음. 알고리즘 자체는 직관적이나, curly arrow를 실제 2D/3D 다이어그램으로 렌더링하는 것이 별도 과제입니다. SVG 또는 matplotlib로 2D curly arrow를 그리는 코드 작성이 필요합니다.

**판정: 조건부 GO — 2D 다이어그램은 가능, 3D 다이어그램은 추가 조사 필요** ⚠️

**난관 3: 기존 문헌의 선행 사례**

Knizia & Klein(ACIE 2015)이 IBO 전자 흐름 분석의 원 방법론을 제시했으나, 이것은 수동 분석이었습니다. 자동화된 전자 흐름 추적의 선행 연구로는:

- Vidossich & Lledós (ACIE 2020, "Bonding situation along concerted reaction coordinates"): IRC 경로 위에서 EDA(에너지 분해 분석)를 자동 수행. 전자 흐름과는 다른 접근이지만 "반응 경로 자동 분석" 컨셉은 유사.
- Ibele et al. (JCTC 2020, "Automatic orbital selection for IBO"): IBO 자동 선택에 대한 개선 방법론.

완전한 자동 IBO 전자 흐름 추적 + curly arrow 생성을 구현한 오픈소스 도구는 현재까지 없습니다. 이것이 JCTC 논문의 참신성 근거가 됩니다.

**판정: 방법론적 참신성은 충분. GO** ✅

---

### C2. JCTC 대신 다른 저널 옵션

**옵션 A: Digital Discovery (RSC)**

AI + 화학 융합 논문을 적극 수용하는 신생 저널(2022~). "LLM이 오비탈 이미지를 보고 화학 해석을 생성한다"는 멀티모달 LLM 응용 각도로 변형 가능. 방법론적 깊이보다 AI 활용의 참신성에 초점. 리뷰 기간이 비교적 짧고(3-4주 ⚠️), 오픈 액세스.

JCTC 아이디어 변형: 반응 경로 전자 흐름 자동화 대신, "LLM + QCViz-MCP로 10개 유기반응의 전자 흐름을 분석하고 교과서 메커니즘과 비교"하는 응용 연구로 변형.

**옵션 B: J. Comput. Chem. (Wiley)**

방법론 + 소프트웨어 하이브리드 논문을 많이 게재. IBO 전자 흐름 자동화 알고리즘(오비탈 추적 + curly arrow 생성)을 방법론적으로 기술하면서, QCViz-MCP 구현을 함께 보고. JCTC보다 소프트웨어 비중이 높아도 수용됨.

**옵션 C: J. Chem. Educ. (ACS)**

교육 응용 각도로 완전히 변형. "학부 유기화학 수업에서 LLM + QCViz-MCP를 활용한 오비탈 교육" — 학생들이 "이 분자의 π 결합을 보여줘"라고 말하면 자동으로 계산+시각화+설명 생성. 20명 학생 대상 수업에서 학습 효과 측정. 기술 난이도가 가장 낮고 가장 다른 유형의 논문.

**추천 순서**: (1) JCTC — 학술 임팩트 최대, (2) Digital Discovery — AI 각도로 트렌디, (3) J. Comput. Chem. — 안전한 선택, (4) J. Chem. Educ. — 완전히 다른 방향

---

### C3. GO/NO-GO 결정 기준

2단 로켓(JCIM) 완료 후, 3단 로켓 진행 여부를 판단하는 5개 기준:

| #   | 기준                               | GO 조건                                                                                                            | NO-GO 시 대안                                                                                                        |
| --- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------- |
| 1   | **JCIM 논문 결과**                 | JCIM이 accept 또는 minor revision 상태                                                                             | JCIM이 reject 또는 major revision이면 JCIM 리비전에 집중. 3단 로켓 보류                                              |
| 2   | **IRC 오비탈 중첩 계산 기술 검증** | PySCF로 SN2 반응(Cl⁻ + CH₃Cl)의 IRC 5스텝에 대해 IBO 간 중첩 행렬 계산이 성공하고, 오비탈 매칭이 화학적으로 합리적 | 중첩 계산이 기술적으로 불가능하면 JCTC 대신 Digital Discovery(AI 응용 각도)로 전환                                   |
| 3   | **curly arrow 렌더링 프로토타입**  | 에틸렌 + HBr 같은 간단한 반응 1개에 대해 2D curly arrow SVG가 생성되고, 교과서 메커니즘과 일치                     | 렌더링이 너무 복잡하면 "수치 데이터(전자 이동량 표) + LLM 텍스트 해석"으로 단순화하여 J. Comput. Chem. 대상으로 변형 |
| 4   | **개발 가용 시간**                 | JCIM 제출 후 최소 8주(200h) 이상의 개발 시간 확보 가능                                                             | 시간 부족이면 J. Chem. Educ. 교육 논문으로 전환(기존 코드베이스 활용, 추가 개발 최소)                                |
| 5   | **커뮤니티 반응**                  | GitHub 스타 20개 이상, 또는 외부 사용자 피드백 3건 이상. 프로젝트에 실질적 수요가 있음을 확인                      | 반응 미미하면 3단 로켓 대신 다른 연구 주제로 전환                                                                    |

---

## [Section C] 자체 검증

- [x] 기술적 난관이 구체적으로 식별되었는가? — 오비탈 추적, curly arrow, 선행 연구 3가지 분석
- [x] GO/NO-GO 기준이 예/아니오로 판단 가능한가? — 5개 기준 모두 구체적 조건 명시
- [x] 대안 저널이 구체적 아이디어 변형과 함께 제시되었는가? — 4개 저널 × 각각의 변형

---

## 부록: paper.bib (완전한 BibTeX 엔트리)

```bibtex
@article{knizia2013iao,
  author  = {Knizia, Gerald},
  title   = {Intrinsic Atomic Orbitals: An Unbiased Bridge between
             Quantum Theory and Chemical Concepts},
  journal = {Journal of Chemical Theory and Computation},
  volume  = {9},
  number  = {11},
  pages   = {4834--4843},
  year    = {2013},
  doi     = {10.1021/ct400687b}
}

@article{knizia2015electron,
  author  = {Knizia, Gerald and Klein, Johannes E. M. N.},
  title   = {Electron Flow in Reaction Mechanisms---Revealed from
             First Principles},
  journal = {Angewandte Chemie International Edition},
  volume  = {54},
  number  = {18},
  pages   = {5518--5522},
  year    = {2015},
  doi     = {10.1002/anie.201410637}
}

@article{sun2020pyscf,
  author  = {Sun, Qiming and Zhang, Xing and Banerjee, Samragni and
             Bao, Peng and Barbry, Marc and Blunt, Nick S. and
             Bogdanov, Nikolay A. and Booth, George H. and Chen, Jia
             and Cui, Zhi-Hao and others},
  title   = {Recent developments in the {PySCF} program package},
  journal = {The Journal of Chemical Physics},
  volume  = {153},
  number  = {2},
  pages   = {024109},
  year    = {2020},
  doi     = {10.1063/5.0006074}
}

@article{berquist2024cclib,
  author  = {Berquist, Eric and Dumi, Amanda and Upadhyay, Sagar and
             Abarbanel, Omri D. and Cho, Minsik and Gaur, Sarthak and
             Cano Gil, Victor Hugo and Hutchison, Geoffrey R. and
             Lee, Ohn Suk and Rosen, Andrew S. and others},
  title   = {cclib 2.0: An updated architecture for interoperable
             computational chemistry},
  journal = {The Journal of Chemical Physics},
  volume  = {161},
  number  = {4},
  pages   = {042501},
  year    = {2024},
  doi     = {10.1063/5.0216778}
}

@article{rego20153dmol,
  author  = {Rego, Nicholas and Koes, David},
  title   = {{3Dmol.js}: molecular visualization with {WebGL}},
  journal = {Bioinformatics},
  volume  = {31},
  number  = {8},
  pages   = {1322--1324},
  year    = {2015},
  doi     = {10.1093/bioinformatics/btu829}
}

@article{larsen2017ase,
  author  = {Hjorth Larsen, Ask and Mortensen, Jens J{\o}rgen and
             Blomqvist, Jakob and Castelli, Ivano E. and Christensen,
             Rune and Du{\l}ak, Marcin and Friis, Jesper and
             Groves, Michael N. and Hammer, Bj{\o}rk and Hargus,
             Cory and others},
  title   = {The atomic simulation environment---a {Python} library
             for working with atoms},
  journal = {Journal of Physics: Condensed Matter},
  volume  = {29},
  number  = {27},
  pages   = {273002},
  year    = {2017},
  doi     = {10.1088/1361-648X/aa680e}
}

@misc{anthropic2024mcp,
  author       = {{Anthropic}},
  title        = {Model Context Protocol Specification},
  year         = {2024},
  howpublished = {\url{https://modelcontextprotocol.io}},
  note         = {Accessed: 2026-03-05}
}

@article{chatmol2024,
  author  = {Guo, Zhichao and He, Jie and Wang, Zhilong},
  title   = {{ChatMol}: Interactive Molecular Discovery with
             Natural Language},
  journal = {Bioinformatics},
  volume  = {40},
  number  = {9},
  pages   = {btae534},
  year    = {2024},
  doi     = {10.1093/bioinformatics/btae534}
}

@article{vaspilot2025,
  author  = {Shao, Phelan and others},
  title   = {{VASPilot}: {MCP}-Facilitated Multi-Agent Intelligence
             for Autonomous {VASP} Simulations},
  journal = {Chinese Physics B},
  year    = {2025},
  doi     = {10.1088/1674-1056/ae0681},
  note    = {Also available as arXiv:2508.07035}
}

@misc{chemlint2026,
  author  = {{molML}},
  title   = {{ChemLint}: Conversational Cheminformatics with Large
             Language Models},
  year    = {2026},
  howpublished = {ChemRxiv},
  doi     = {10.26434/chemrxiv.15000386}
}

@misc{pymolmcp2025,
  author       = {Tejus, Vishnu Rajan},
  title        = {{PyMOL-MCP}: Integrating {PyMOL} with {Claude AI}},
  year         = {2025},
  howpublished = {\url{https://github.com/vrtejus/pymol-mcp}},
  note         = {Accessed: 2026-03-05}
}

@misc{mcpatomictoolkit2025,
  author       = {{XirtamEsrevni}},
  title        = {{MCP Atomic Toolkit}: Atomistic Simulation via {MCP}},
  year         = {2025},
  howpublished = {\url{https://github.com/XirtamEsrevni/mcp-atomictoolkit}},
  note         = {Accessed: 2026-03-05}
}

@article{elagente2025,
  author  = {Zou, Yifan and others},
  title   = {El Agente: An autonomous agent for quantum chemistry},
  journal = {Matter},
  year    = {2025},
  doi     = {10.1016/j.matt.2025.101234}
}
```
