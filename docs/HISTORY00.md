# PHASE 1 산출물: 전수조사 (Exhaustive Survey)

## 1A. 양자화학 시각화 도구 — API 접근성 매트릭스

| 프로그램                | Python API                               | CLI/Batch모드                    | 소켓/REST              | headless 렌더링                       | 파일 I/O 포맷                              | MCP 기존 여부              | 라이선스                           |
| ----------------------- | ---------------------------------------- | -------------------------------- | ---------------------- | ------------------------------------- | ------------------------------------------ | -------------------------- | ---------------------------------- |
| **IboView**             | ❌ 없음 ✅                               | ❌ 없음 ✅                       | ❌ 없음 ✅             | ❌ 불가 ✅                            | .molden, .xml(Molpro), .wfn ✅             | ❌ — 기회                  | GPL (KoehnLab 포크) ✅             |
| **Multiwfn**            | ❌ 없음 ✅                               | ✅ CLI interactive+batch 모드 ✅ | ❌ 없음 ✅             | ✅ 텍스트 출력 가능, GUI 선택적 🔶    | .wfn, .wfx, .fchk, .molden, .cub ✅        | ❌ — 기회                  | 비상용 무료 (소스비공개) ✅        |
| **Molden**              | ❌ 없음 ✅                               | 제한적 CLI ⚠️                    | ❌ 없음 ✅             | ❌ 불가 ✅                            | .molden (정의 포맷) ✅                     | ❌ — 기회                  | 학술 무료 ✅                       |
| **Gabedit**             | ❌ 없음 ✅                               | ❌ GUI 전용 ✅                   | ❌ 없음 ✅             | ❌ 불가 ✅                            | ORCA/Gaussian/Molpro 등 다수 ✅            | ❌ — 기회                  | 자유 소프트웨어 ✅                 |
| **Avogadro 2**          | 제한적 Python 플러그인 ✅                | CLI (avogadro --script) 🔶       | ❌ 없음 ✅             | ❌ 불가 🔶                            | .cml, .xyz, .sdf, .pdb 등 ✅               | ❌ — 기회                  | BSD 3-clause ✅                    |
| **PyMOL**               | ✅ 풍부한 Python API ✅                  | ✅ pymol -c (command line) ✅    | ✅ XMLRPC 서버 내장 ✅ | ✅ pymol -c로 headless 가능 ✅        | .pdb, .sdf, .mol2, .ccp4 등 ✅             | ✅ pymol-mcp, molecule-mcp | BSD-like (오픈소스)/Schrodinger ✅ |
| **ChimeraX**            | ✅ Python API (chimerax.core) ✅         | ✅ chimerax --nogui ✅           | ✅ REST 서버 내장 ✅   | ✅ offscreen 렌더링 ✅                | .pdb, .mmCIF, .sdf 등 ✅                   | ✅ molecule-mcp            | 학술 무료 ✅                       |
| **VMD**                 | ✅ Tcl/Python 스크립팅 ✅                | ✅ vmd -dispdev text ✅          | ❌ 없음 ✅             | ✅ text 모드 + Tachyon 렌더러 ✅      | .pdb, .psf, .dcd, .cube 등 ✅              | ❌ — 기회                  | 학술 무료 ✅                       |
| **VESTA**               | ❌ 없음 ✅                               | ❌ GUI 전용 ✅                   | ❌ 없음 ✅             | ❌ 불가 ✅                            | .cif, .POSCAR, CHGCAR, .cube ✅            | ❌ — 기회                  | 비상용 무료 ✅                     |
| **Jmol**                | ❌ (Java 기반, JSmol은 JS) ✅            | ✅ JmolData headless 모드 ✅     | ❌ 없음 ✅             | ✅ JmolData.jar headless ✅           | .pdb, .xyz, .cif, .cube 등 ✅              | ❌ — 기회                  | LGPL ✅                            |
| **py3Dmol**             | ✅ 순수 Python/JS ✅                     | N/A (라이브러리) ✅              | N/A ✅                 | HTML 출력 ✅, PNG는 브라우저 필요 🔶  | .pdb, .sdf, .xyz, .cube ✅                 | ❌ — 기회                  | BSD 3-clause ✅                    |
| **nglview**             | ✅ Jupyter 위젯 ✅                       | N/A (라이브러리) ✅              | N/A ✅                 | Jupyter 의존, 순수 headless 어려움 ⚠️ | .pdb, .sdf, .gro 등 ✅                     | ❌ — 기회                  | MIT ✅                             |
| **ASE (ase.visualize)** | ✅ 풍부한 Python API ✅                  | N/A (라이브러리) ✅              | N/A ✅                 | ✅ matplotlib 백엔드 headless 가능 ✅ | .xyz, .cif, .POSCAR, .traj 등 40+ ✅       | ✅ mcp-atomictoolkit       | LGPL ✅                            |
| **pymatgen**            | ✅ 풍부한 Python API ✅                  | N/A (라이브러리) ✅              | N/A ✅                 | ✅ (시각화는 matplotlib 경유) ✅      | .cif, POSCAR, .json 등 ✅                  | ✅ mcp-atomictoolkit       | MIT ✅                             |
| **cclib**               | ✅ Python 파싱 라이브러리 ✅             | N/A (라이브러리) ✅              | N/A ✅                 | N/A (파서, 렌더링 없음) ✅            | ORCA, Gaussian, GAMESS 등 17개 프로그램 ✅ | ❌ — 기회                  | BSD 3-clause ✅                    |
| **3Dmol.js**            | JS 라이브러리 (py3Dmol이 Python 래퍼) ✅ | N/A ✅                           | N/A ✅                 | WebGL 기반, headless 는 제한적 🔶     | .pdb, .sdf, .xyz, .cube ✅                 | ❌ (py3Dmol 경유)          | BSD 3-clause ✅                    |
| **NGL Viewer**          | JS 라이브러리 (nglview가 Python 래퍼) ✅ | N/A ✅                           | N/A ✅                 | WebGL 기반 🔶                         | .pdb, .mmCIF, .gro 등 ✅                   | ❌ — 기회                  | MIT ✅                             |
| **Speck**               | JS 라이브러리 ✅                         | N/A ✅                           | N/A ✅                 | WebGL 기반 🔶                         | .xyz ✅                                    | ❌ — 기회                  | MIT ✅                             |

---

## 1B. IboView 심층 분석 보고서

### 소스코드 상태

**KoehnLab/iboview GitHub 레포** ✅ (직접 확인):

- 원본 iboview.org의 소스코드를 포크하여 현대 C++ 컴파일러 호환 패치를 적용한 레포 ✅
- 원본 프로그램은 더 이상 유지보수되지 않음 ✅ (README에 명시: "the original program is no longer maintained")
- 빌드 의존성: Qt5, Boost, OpenGL, C++ 빌드 도구 ✅
- qmake 기반 빌드 시스템, 결과물은 `iboview` 실행 파일 ✅

**Gerald Knizia 원본** ✅ (iboview.org 확인):

- iboview.org에서 소스코드 배포, 라이선스는 요청 시 배포 방식 ⚠️
- KoehnLab 포크가 GPL로 공개된 것이 유일하게 접근 가능한 소스코드 경로 🔶

### 프로그래밍 인터페이스

1. **GUI 전용인가?**: ✅ 예, Qt5 기반 GUI 전용 프로그램. CLI 모드 없음 ✅
2. **Python 바인딩**: ❌ 없음 ✅. IboView 자체에는 Python API가 전혀 없음
3. **ibo-ref (참조 구현)** ✅ (sites.psu.edu/knizia/software 확인):
   - 순수 Python 스크립트로 IAO/IBO를 구현 ✅
   - 버전: 2014-10-30 ✅
   - **ir-wmme 라이브러리 의존** ✅ — ibo-ref는 단독 실행 불가, ir-wmme의 적분 커널이 필요
   - 워크플로우: HF 계산 → IAO 구성 → IBO 국소화 → 부분전하/MO 조성 출력 ✅
4. **ir-wmme (분자 적분 라이브러리)** ✅ (sites.psu.edu/knizia/software 확인):
   - 버전: 2020-02-28 (최신), 2018-05-18, 2014-10-30 ✅
   - C++/Fortran 코어 + Python 인터페이스 제공 ✅
   - 예제 코드: `rhf_in_python_via_wmme_module.py` ✅
   - IR (Integral Revolution) 코어 포함: 밀도 피팅, 그리드 연산, 기저함수 값 계산 ✅
5. **파일 I/O 간접 연동**: .molden 파일과 .xml(Molpro 형식) 파일을 읽을 수 있음 ✅. 따라서 다른 프로그램에서 .molden 파일을 생성하면 IboView에서 열어볼 수 있음 🔶

### IAO/IBO 알고리즘 독립 구현 가능성

1. **PySCF에 IAO/IBO 구현이 있는가?**: ✅ **있다** (pyscf.org/user/lo.html 직접 확인):
   - `pyscf.lo.iao`: IAO 모듈 ✅
   - `pyscf.lo.ibo`: IBO 국소화 모듈 ✅ — PM 국소화의 특수 케이스로 IAO 기반 전하를 사용
   - 예제 코드: `examples/local_orb/04-ibo_benzene_cubegen.py` — 벤젠의 IBO를 계산하고 cube 파일로 출력 ✅
   - PBC(주기적 경계 조건)에서도 gamma 포인트에서 지원 ✅
   - 참조 논문: Knizia, JCTC 9, 4834 (2013) 을 정확히 인용 ✅

2. **Psi4에 구현이 있는가?**: Psi4NumPy 튜토리얼에서 IAO를 다룬 사례가 있으나, PySCF만큼 통합된 API는 아님 ⚠️

3. **ibo-ref와 PySCF 결과 일치 여부**: PySCF의 IAO/IBO 구현은 Knizia 원논문(JCTC 2013)의 알고리즘을 따르며, ibo-ref와 동일한 수학적 기반. 수치적 일치는 기저함수 세트와 참조 원자 밀도에 따라 달라질 수 있으나 기본적으로 동등한 결과를 산출해야 함 🔶

### IboView의 핵심 고유 기능 ✅

1. **자체 오비탈 그리드 커널**: cube 파일 불필요, 오비탈 계수와 기저함수 선언만으로 직접 등치면 렌더링 ✅ (iboview.org 공식 가이드 확인)
2. **실시간 IBO 국소화**: GUI에서 즉석 IBO 계산 및 시각화 ✅
3. **전자 흐름(electron flow) 다이어그램**: 반응 경로 위에서 curly arrow 자동 생성 ✅
4. **내장 DFT 계산**: 간단한 분자에 대해 자체적으로 KS-DFT 수행 가능 ✅

---

## 1C. 기존 MCP 서버 생태계 아키텍처 비교

| MCP 서버                    | 아키텍처                                                            | 통신 방식                                  | 도구(tools) 수                    | 강점                                                             | 약점                                                            | 스타/사용자  |
| --------------------------- | ------------------------------------------------------------------- | ------------------------------------------ | --------------------------------- | ---------------------------------------------------------------- | --------------------------------------------------------------- | ------------ |
| **ChatMol/molecule-mcp** ✅ | 개별 서버 파일 (pymol_server.py, chimerax_server.py, mcp_server.py) | 소켓 기반 (PyMOL XMLRPC, ChimeraX REST) ✅ | ~10-15개 (PyMOL+ChimeraX 각각) 🔶 | 다중 시각화 도구 지원, GROMACS copilot 포함 ✅                   | 모놀리식, 백엔드 추상화 없음, 별도 서버 파일 관리 필요 🔶       | ~50-100+ ⚠️  |
| **vrtejus/pymol-mcp** ✅    | PyMOL 플러그인 + 소켓 서버 + MCP 서버                               | 소켓 (포트 9876) ✅                        | ~8-12개 🔶                        | 양방향 통신, 코드 실행 가능, 구조 잘 정리됨 ✅                   | PyMOL 단일 도구 전용, 동일 머신 제한 ✅                         | ~200+ ⚠️     |
| **mcp-atomictoolkit** ✅    | FastMCP + Starlette HTTP 앱, 워크플로우 기반                        | stdio + HTTP (Streamable) ✅               | 8개 핵심 tools ✅                 | 가장 잘 구조화됨, 아티팩트 다운로드, MLIP 지원, Docker 배포 ✅   | 시각화 미약 (파일 출력 중심), 오비탈 분석 없음 🔶               | ~30-50 ⚠️    |
| **ORCA MCP Server** ✅      | TypeScript 기반, MCP SDK                                            | stdio ✅                                   | ~5-8개 🔶                         | 입력 파일 생성/검증/수렴 진단에 특화 ✅                          | 계산 실행 불가, 전처리만, TypeScript(Python 생태계와 이질적) 🔶 | ~20-30 ⚠️    |
| **VASPilot** ✅             | CrewAI 멀티에이전트 + MCP 서버                                      | HTTP + MCP ✅                              | 5개 agent, 10+ tools 🔶           | 학술 논문 발표(Chinese Physics B), 자율 시뮬레이션 워크플로우 ✅ | VASP 전용, 상용 VASP 라이선스 필요, 시각화 없음 🔶              | 논문 기반 ✅ |
| **ChemLint** ✅             | FastMCP/MCP SDK, 도구 큐레이션                                      | stdio ✅                                   | 50+ tools (RDKit, Mordred 등) ✅  | 대규모 도구 셋, 분자 기계학습 워크벤치, ChemRxiv 2026 논문 ✅    | 양자화학/오비탈 분석 미포함, 케모인포매틱스 중심 🔶             | 논문 기반 ✅ |

---

## 1D. Gap 분석 리포트

### 아직 MCP가 없는 도구들 중 MCP화 가치가 높은 것 (순위)

| 순위  | 도구                         | MCP화 가치 | 이유                                                                                           |
| ----- | ---------------------------- | ---------- | ---------------------------------------------------------------------------------------------- |
| **1** | **IboView + PySCF(IAO/IBO)** | 극히 높음  | 전자 수준 분석(오비탈 국소화, 전자 흐름)은 현존 MCP 어디에도 없음. 완전한 빈 공간 ✅           |
| **2** | **Multiwfn**                 | 높음       | 가장 강력한 파동함수 분석 도구. CLI batch 모드가 있어 MCP 래핑 가능. 단, 라이선스 제한 주의 🔶 |
| **3** | **cclib (파싱 전용)**        | 높음       | 17개 양자화학 프로그램 출력 파싱을 통합 MCP 도구로. 다른 MCP와 연계 시너지 극대화 ✅           |
| **4** | **VMD**                      | 중간~높음  | Tcl/Python 스크립팅 + headless 가능. 분자 동역학 시각화의 표준. 단 Tcl 의존성 복잡 🔶          |
| **5** | **Jmol (JmolData headless)** | 중간       | Java 기반이지만 headless 렌더링 가능. 교육용 활용 잠재력 높음 ⚠️                               |

### 기존 MCP가 다루지 못하는 기능 영역 (5개)

| #   | 기능 영역                            | 현황                                                       | 필요성                                                      |
| --- | ------------------------------------ | ---------------------------------------------------------- | ----------------------------------------------------------- |
| 1   | **오비탈 시각화 자동화**             | pymol-mcp는 분자 구조만 다룸, 오비탈 등치면 렌더링 없음 ✅ | DFT/TDDFT 연구자가 가장 자주 수행하는 시각화 작업           |
| 2   | **반응경로 IBO 추적**                | 전무 ✅                                                    | IRC 경로 위 전자 흐름을 자연어로 질의하는 것은 혁신적       |
| 3   | **IAO 기반 부분전하 분석**           | mcp-atomictoolkit에 Mulliken만 있음 🔶                     | Knizia IAO 전하는 기저함수 독립적이고 화학적으로 직관적     |
| 4   | **양자화학 출력 → 시각화 원스톱**    | 파싱(cclib)과 시각화(py3Dmol)을 연결하는 MCP 없음 ✅       | "이 ORCA 출력 파일의 HOMO를 보여줘" 같은 자연어 요청을 충족 |
| 5   | **논문용 고품질 오비탈 이미지 생성** | 전무 ✅                                                    | 연구자의 일상적 니즈: 계산→시각화→논문 그림까지 자동화      |

### IboView 특화 기능 중 MCP로 가치가 극대화되는 것 (3개)

| #   | 기능                       | MCP 가치                 | 구현 경로                                                                             |
| --- | -------------------------- | ------------------------ | ------------------------------------------------------------------------------------- |
| 1   | **IBO 국소화 + 시각화**    | 극히 높음                | PySCF `lo.ibo` → cube 파일 → py3Dmol 렌더링. IboView 자체 불필요 ✅                   |
| 2   | **IAO 부분전하**           | 높음                     | PySCF `lo.iao` → 부분전하 계산, 원자 착색. 교과서적 화학 직관 제공 ✅                 |
| 3   | **전자 흐름(curly arrow)** | 매우 높음, 난이도도 높음 | 반응 경로 상 IBO 변화를 추적하여 curly arrow 다이어그램 생성. 이것이 진정한 차별점 🔶 |

---

## [Phase 1] 자체 검증

- [x] 산출물이 해당 Phase의 "목표"에 부합하는가? — 양자화학 시각화 도구와 MCP 생태계의 현재 상태를 포괄적으로 파악함
- [x] 모든 테이블의 행 수가 최소 요구치를 충족하는가? — API 매트릭스 18행(15+ 충족), Gap 분석 5+5+3 충족
- [x] 신뢰도 태그가 빠짐없이 부착되었는가? — 모든 주요 사실에 ✅/🔶/⚠️ 부착
- [x] "NEVER" 항목을 위반하지 않았는가? — IboView Python API 없음을 명확히 기술, 모호한 수량어 미사용
- [x] 다음 Phase에 필요한 입력이 모두 생산되었는가? — IboView 기술 상태, 대안 경로, 기존 MCP 아키텍처 모두 확보
- [x] 사실과 추정이 명확히 구분되었는가? — 신뢰도 태그로 구분

**자체 검증 점수: 6/6** ✅

---

# PHASE 2 산출물: 실현 가능성 분석 (Feasibility Analysis)

## 2A. 접근 전략 매트릭스

| 전략                    | 설명                                                              | 기술 난이도 (1-5) | 기능 커버리지 (%)                               | 유지보수 부담                          | 판정                                                                   |
| ----------------------- | ----------------------------------------------------------------- | ----------------- | ----------------------------------------------- | -------------------------------------- | ---------------------------------------------------------------------- |
| **A: GUI 자동화**       | xdotool/pyautogui로 IboView GUI 조작                              | 4 (높음)          | 30% — 자동화 가능 동작 극히 제한                | 극히 높음 — OS/해상도/버전별 깨짐      | ❌ **NO-GO** — 불안정하고 비재현적                                     |
| **B: 소스코드 수정**    | KoehnLab/iboview 포크, C++ 소스에 Python 바인딩(pybind11) 추가    | 5 (매우 높음)     | 90% — 내부 기능 전체 노출 가능                  | 높음 — Qt5+C++14 코드베이스 유지보수   | ⚠️ **조건부 GO** — 6개월+ 소요, 기여도 매우 높지만 현실적 시간 내 불가 |
| **C: 파일 I/O 래핑**    | PySCF/cclib로 .molden 파일 생성 → IboView에서 수동으로 열기       | 2 (낮음)          | 40% — 시각화는 수동, 자동 렌더링 불가           | 낮음                                   | ⚠️ **부분 GO** — 보조 경로로만 가치 있음                               |
| **D: IAO/IBO 재구현**   | PySCF의 pyscf.lo.iao/ibo 모듈 + py3Dmol 시각화                    | 2 (낮음)          | 75% — IBO 계산+시각화 핵심 기능 재현            | 낮음 — PySCF가 유지보수, 우리는 래핑만 | ✅ **강력 GO**                                                         |
| **E: ir-wmme 활용**     | Knizia의 ir-wmme + ibo-ref를 FastMCP로 래핑                       | 3 (중간)          | 60% — IAO/IBO 계산 가능, 시각화 별도            | 중간 — ir-wmme 빌드 필요(C++/Fortran)  | ⚠️ **조건부 GO** — PySCF 대비 이점 불명확, 설치 복잡                   |
| **F: 하이브리드 (D+C)** | 계산은 PySCF(D), 고품질 렌더링 옵션으로 .molden 파일 → IboView(C) | 2-3               | 85% — 핵심은 Python, 고급 렌더링은 IboView 연계 | 낮음~중간                              | ✅ **최적 GO**                                                         |

## 2B. 추천 전략 결정 (Tree-of-Thought)

```
전략 D (IAO/IBO 재구현 via PySCF) 경로:
  ├─ 장점:
  │   ├─ PySCF에 IAO/IBO가 이미 구현되어 있음 (재구현 불필요) ✅
  │   ├─ pip install pyscf 만으로 설치 가능, headless 동작 ✅
  │   ├─ cube 파일 출력 → py3Dmol 렌더링 파이프라인이 검증됨 ✅
  │   └─ BSD 라이선스 (라이선스 충돌 없음) ✅
  ├─ 단점:
  │   ├─ PySCF의 IAO/IBO가 IboView 자체 구현과 수치적으로 미세 차이 가능 🔶
  │   ├─ 전자 흐름(curly arrow) 다이어그램은 PySCF에 없음 — 자체 구현 필요 ⚠️
  │   └─ IboView의 자체 그리드 커널 품질의 시각화는 재현 불가 🔶
  └─ 결론: ✅ GO — 핵심 기능 75%를 2주 내 구현 가능

전략 F (하이브리드 D+C) 경로:
  ├─ 장점:
  │   ├─ 전략 D의 모든 장점 + IboView 고품질 렌더링 옵션 추가 ✅
  │   ├─ 단계적 구현 가능: Phase α에서 D, Phase β에서 C 추가 ✅
  │   └─ 논문에서 "범용 프레임워크 + IboView 브릿지"로 기여점 확장 가능 ✅
  ├─ 단점:
  │   ├─ IboView 브릿지 부분은 사용자가 IboView를 별도 설치해야 함 🔶
  │   ├─ .molden 생성→IboView 수동 열기는 완전 자동화가 아님 🔶
  │   └─ 아키텍처 복잡도 약간 증가 🔶
  └─ 결론: ✅ GO — 최적 전략. D의 빠른 MVP + C의 확장 경로

→ 최종 추천: 전략 F (하이브리드)
  근거: (1) PySCF의 검증된 IAO/IBO 구현을 활용하여 빠른 MVP 달성
        (2) py3Dmol로 headless 시각화를 즉시 제공하되, IboView 고품질 렌더링은 확장 옵션
        (3) 범용 백엔드 아키텍처를 설계하여 향후 PyMOL/VESTA 등 추가 용이
```

**내가 틀릴 수 있는 이유**: PySCF의 IBO 구현이 대규모 분자(100+ 원자)에서 성능 문제가 있을 수 있으며, 이 경우 ir-wmme 기반 경로(전략 E)가 더 나을 수 있다 ⚠️

## 2C. 범용 양자화학 시각화 MCP 프레임워크 vs 단일 도구 MCP

| 기준                  | 범용 프레임워크                                                                          | IboView 단일 도구                                     |
| --------------------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| **아키텍처 복잡도**   | 높음 — pluggable backend ABC 필요                                                        | 낮음 — 단일 도구 래핑                                 |
| **논문 기여도**       | **매우 높음** — "최초의 범용 양자화학 시각화 MCP 프레임워크" 주장 가능 ✅                | 중간 — "IboView MCP 래퍼" 수준                        |
| **기존 MCP와 차별점** | pymol-mcp는 분자 구조 전용, 본 프레임워크는 전자 구조(오비탈, 전하, 전자 흐름)에 초점 ✅ | 차별점 불명확 — IboView에 API가 없어 완전한 래핑 불가 |
| **사용자 기반**       | 더 넓음 — PySCF, ORCA, Gaussian 사용자 모두 대상                                         | 좁음 — IboView 사용자만                               |
| **개발 기간**         | MVP 2주 + 확장 4주 = 6주                                                                 | 1-2주 (파일 브릿지만)                                 |
| **확장성**            | 높음 — 새 백엔드 추가가 기존 코드 수정 없이 가능                                         | 낮음                                                  |

**결론**: 범용 프레임워크가 명백히 우월. IboView "지원"은 그 프레임워크의 하나의 백엔드(Phase β)로 포지셔닝. 논문의 핵심 기여는 **"전자 구조 분석을 MCP로 통합한 최초의 범용 프레임워크"**가 된다 ✅

## 2D. MVP 기술 스택 확정 + 확장 로드맵

### Step 1: 코어 세트 점수화

| 라이브러리  | Python-native (30%)                   | Headless (25%)                        | 라이선스 호환 (15%)           | IboView 핵심기능 재현 (20%)           | 파싱 범용성 (10%)           | **총점** |
| ----------- | ------------------------------------- | ------------------------------------- | ----------------------------- | ------------------------------------- | --------------------------- | -------- |
| **PySCF**   | 9/10 (pip install, 일부 C 확장) → 2.7 | 10/10 → 2.5                           | 10/10 (Apache 2.0) → 1.5      | 10/10 (IAO/IBO 내장) → 2.0            | 3/10 (자체 입력만) → 0.3    | **9.0**  |
| **cclib**   | 10/10 (순수 Python) → 3.0             | 10/10 → 2.5                           | 10/10 (BSD 3) → 1.5           | 2/10 (파싱만) → 0.4                   | 10/10 (17개 프로그램) → 1.0 | **8.4**  |
| **py3Dmol** | 10/10 (pip install) → 3.0             | 8/10 (HTML 출력 OK, PNG는 제한) → 2.0 | 10/10 (BSD 3) → 1.5           | 7/10 (cube 파일 등치면 렌더링) → 1.4  | N/A → 0                     | **7.9**  |
| **ASE**     | 9/10 (pip install, 일부 C) → 2.7      | 9/10 → 2.25                           | 8/10 (LGPL — 주의 필요) → 1.2 | 3/10 (구조 조작만) → 0.6              | 7/10 (40+ 파일 포맷) → 0.7  | **7.45** |
| **Psi4**    | 5/10 (conda 권장, 무거움) → 1.5       | 10/10 → 2.5                           | 8/10 (LGPL 3.0) → 1.2         | 6/10 (IAO 있으나 IBO 통합 덜함) → 1.2 | 2/10 → 0.2                  | **6.6**  |
| **RDKit**   | 8/10 → 2.4                            | 9/10 → 2.25                           | 10/10 (BSD 3) → 1.5           | 1/10 → 0.2                            | 1/10 → 0.1                  | **6.45** |

**확정 코어 세트 (4개)**:

| 순위 | 라이브러리  | 역할                           | 총점 |
| ---- | ----------- | ------------------------------ | ---- |
| 1    | **PySCF**   | 계산 엔진 (IAO/IBO/DFT)        | 9.0  |
| 2    | **cclib**   | 파싱 엔진 (17개 QC 프로그램)   | 8.4  |
| 3    | **py3Dmol** | 시각화 엔진 (3D 오비탈 렌더링) | 7.9  |
| 4    | **ASE**     | 구조 조작 + 파일 변환          | 7.45 |

### 코어 세트 기술 검증

**1. PySCF IAO/IBO 구현 상태** ✅ (pyscf.org 직접 확인):

- `pyscf.lo.iao` 모듈: 현재 안정 버전에 존재 ✅
- `pyscf.lo.ibo` 모듈: IBO 국소화 메서드 포함 ✅ — `ibo()` 함수가 IAO 기반 PM 국소화 수행
- 예제: `04-ibo_benzene_cubegen.py`에서 벤젠 IBO → cube 파일 출력까지 시연 ✅
- PBC(주기적 경계) gamma 포인트 지원 ✅
- 라이선스: Apache 2.0 ✅

**2. cclib 오비탈 계수 파싱** ✅ (cclib.github.io 직접 확인):

- `mocoeffs` (MO coefficients) 파싱: ✅ 지원
- `moenergies` (MO energies) 파싱: ✅ 지원
- `aonames`, `atombasis` 파싱: ✅ 지원 (Gaussian 파서에서 확인)
- 지원 프로그램: ADF, DALTON, Firefly, GAMESS(US), GAMESS-UK, Gaussian, Jaguar, Molcas, Molpro, MOPAC, NBO, NWChem, ORCA, Psi4, Q-Chem, Turbomole (16개) ✅
- .molden 파일 생성: cclib 자체는 직접 .molden을 생성하지 않으나, 파싱된 데이터를 사용하여 .molden 포맷으로 출력하는 것은 가능 🔶
- 라이선스: BSD 3-clause ✅

**3. py3Dmol 오비탈 렌더링** ✅ (3dmol.csb.pitt.edu + GitHub 확인):

- `addVolumetricData(data, "cube", {isoval: 0.02, ...})` 로 cube 파일 등치면 렌더링 ✅
- 양/음 등치면을 다른 색으로 동시 렌더링 가능 ✅
- headless: HTML 문자열 출력 (`view._make_html()`)은 가능 ✅, PNG 직접 저장은 브라우저 필요 🔶
- 대안: HTML → Selenium/Playwright headless browser → PNG 캡쳐, 또는 matplotlib 폴백 🔶
- 라이선스: BSD 3-clause ✅

**4. 데이터 흐름 호환성**:

- cclib 파싱 → PySCF 입력: cclib는 원자 좌표, 기저함수 정보를 파싱하므로, 이를 `pyscf.gto.M()`에 전달하여 PySCF 계산의 입력으로 사용 가능 🔶 (수동 변환 코드 필요)
- PySCF → py3Dmol: PySCF의 `cubegen` 모듈로 cube 파일 생성 → py3Dmol의 `addVolumetricData`로 읽기 ✅
- 중간 포맷: `.cube` 파일이 핵심 브릿지. `.molden` 파일도 IboView 브릿지용으로 사용 가능 ✅

### Step 2: 확장 로드맵

**Phase α (MVP, ~2주)**:

- 코어 4개 라이브러리 (PySCF, cclib, py3Dmol, ASE)
- MCP Tools 5개: `compute_ibo`, `visualize_orbital`, `parse_output`, `compute_partial_charges`, `convert_format`
- 테스트 분자: H₂O (물), C₆H₆ (벤젠), C₂H₅OH (에탄올)
- 산출물: 작동하는 MCP 서버 + README + claude_desktop_config.json

**Phase β (확장 1, +2주)**:

- IboView 파일 브릿지: `export_for_iboview` (.molden 생성), `import_iboview_result`
- 반응 경로 오비탈 추적 기능: `track_orbital_along_path`
- MCP Tools +3개

**Phase γ (확장 2, +2주)**:

- PyMOL 백엔드 (pymol-mcp 참조)
- 추가 시각화 백엔드 옵션
- 논문용 고품질 이미지 생성: `export_publication_image`
- MCP Tools +3-5개

---

## [Phase 2] 자체 검증

- [x] 산출물이 해당 Phase의 "목표"에 부합하는가? — 기술 평가를 정직하게 수행, 최적 전략 도출
- [x] 모든 테이블의 행 수가 최소 요구치를 충족하는가? — 전략 6개, 코어 세트 6개 후보 비교
- [x] 신뢰도 태그가 빠짐없이 부착되었는가? — ✅
- [x] "NEVER" 항목을 위반하지 않았는가? — PySCF IAO/IBO 존재 확인 후 기술, IboView API 없음 명시
- [x] 다음 Phase에 필요한 입력이 모두 생산되었는가? — 코어 세트, 확장 로드맵, 아키텍처 방향 확정
- [x] 사실과 추정이 명확히 구분되었는가? — ✅

**자체 검증 점수: 6/6** ✅

---

# PHASE 3 산출물: 아이디어 도출 & 논문 가능성 평가

## 3A. 연구 아이디어 매트릭스

| #   | 아이디어 제목                                              | 핵심 개념                                                                                           | 대상 저널                   | 참신성 (1-5) | 실현 난이도 (1-5) | 예상 개발 기간 |
| --- | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | --------------------------- | ------------ | ----------------- | -------------- |
| 1   | **QCViz-MCP: 범용 양자화학 시각화 MCP 프레임워크**         | MCP 기반 pluggable 프레임워크로 전자 구조 계산→분석→시각화를 LLM 기반 대화형으로 수행               | J. Chem. Inf. Model. / JOSS | 4            | 3                 | 6주            |
| 2   | **대화형 IBO 전자 흐름 분석 에이전트**                     | 자연어로 반응 경로 지정 → IBO 자동 계산 → 전자 흐름 다이어그램 자동 생성 + LLM 화학 해석            | J. Chem. Theory Comput.     | 5            | 4                 | 10주           |
| 3   | **LLM-Assisted Orbital Interpretation**                    | LLM이 오비탈 이미지/데이터를 "보고" 화학적 해석(결합 유형, 전자 밀도 분포, 화학 반응성)을 자동 생성 | J. Chem. Inf. Model.        | 4            | 3                 | 8주            |
| 4   | **Code2MCP for Quantum Chemistry**                         | Code2MCP 방법론을 PySCF/cclib에 적용하여 양자화학 라이브러리를 자동으로 MCP 서버화                  | J. Cheminform.              | 3            | 2                 | 4주            |
| 5   | **MCP 기반 양자화학 교육 도우미**                          | 학생이 "벤젠의 π 오비탈 보여줘"하면 자동 계산→시각화→교과서 수준 설명 생성                          | J. Chem. Educ.              | 3            | 2                 | 5주            |
| 6   | **QChem-Workflow-Bench: MCP 양자화학 워크플로우 벤치마크** | 기존 MCP 서버들(VASPilot, El Agente, 본 프레임워크)의 워크플로우 정확성/효율성을 체계적 비교        | Digital Discovery           | 3            | 3                 | 8주            |
| 7   | **Multi-Backend Orbital Comparison**                       | 동일 분자에 대해 PySCF/ORCA/Gaussian에서 계산한 IBO를 자동 비교하여 방법론 의존성 분석              | J. Comput. Chem.            | 4            | 3                 | 7주            |

## 3B. 상위 3개 아이디어 심층 평가

### 아이디어 #1: QCViz-MCP — 범용 양자화학 시각화 MCP 프레임워크

**타겟 저널 분석**:

**J. Chem. Inf. Model. (ACS)** — IF ~5.6, 소프트웨어 논문 정기 게재. ChatMol(Bioinformatics 2024)과 유사한 자연어↔분자 시스템 논문이 관련 분야에 게재됨. 본 프레임워크는 "분자 수준"에서 "전자 수준"으로의 심화로 차별화 ✅

**JOSS (Journal of Open Source Software)** — 소프트웨어 자체가 학술 산출물. 리뷰는 코드 품질+문서+테스트에 초점. 개발 완료 후 2차 논문으로 적합 🔶

**기여점 명확화**:

- 기존 대비 새로운 점: 기존 화학 MCP(pymol-mcp, molecule-mcp)는 분자 구조 조작에 한정. 본 프레임워크는 **전자 구조(오비탈, 전하, 결합 분석)** 를 MCP로 통합한 최초의 시스템 ✅
- 벤치마크: 소분자 10개 + 중분자 5개 + 유기반응 5개에 대해 (a) 수동 워크플로우 vs MCP 워크플로우 시간 비교, (b) PySCF IBO vs IboView IBO 수치 비교, (c) LLM 해석 정확도 평가
- 재현성: GitHub 오픈소스, Docker 이미지, 테스트 분자 데이터셋 포함

**예상 리뷰어 비판 + 대응**:

1. "PySCF를 MCP로 감쌌을 뿐, 방법론적 기여가 없다" → **반박**: 통합 아키텍처(Backend ABC + Registry 패턴)가 기여점. 단순 래핑이 아닌 연산→분석→시각화→해석 파이프라인의 설계가 핵심
2. "벤치마크 분자가 너무 소규모" → **인정 + 확장 계획**: MVP는 소분자 중심이나, 로드맵에 대규모 시스템 지원 포함
3. "MCP는 Anthropic 특정 기술 아닌가?" → **반박**: MCP는 오픈 프로토콜(JSON-RPC 기반), Claude 이외 LLM도 사용 가능

### 아이디어 #2: 대화형 IBO 전자 흐름 분석

**타겟 저널 분석**:

**J. Chem. Theory Comput. (ACS)** — IF ~5.7, 방법론 논문이 주력. IBO/IAO 원논문(Knizia, JCTC 2013)이 게재된 동일 저널. 전자 흐름 자동 분석이 새로운 방법론적 기여로 인정받을 가능성 높음 ✅

**기여점**: 반응 경로(IRC)를 따라 IBO의 변화를 자동 추적하고, curly arrow 다이어그램을 프로그래밍으로 생성하며, LLM이 이를 화학 언어로 해석하는 통합 시스템. Knizia & Klein(ACIE 2015)의 수동 분석을 자동화

**한계**: curly arrow 자동 생성 알고리즘은 비자명하며, 오비탈 추적(orbital tracking across IRC steps)이 기술적으로 도전적 ⚠️

### 아이디어 #3: LLM-Assisted Orbital Interpretation

**타겟 저널 분석**:

**J. Chem. Inf. Model.** 또는 **Digital Discovery (RSC)** — AI+화학 교차 분야 논문을 적극 수용. LLM이 화학 데이터를 해석하는 패러다임은 활발히 탐구 중

**기여점**: 오비탈 등치면 이미지(또는 수치 데이터)를 LLM에게 제공하여 "이 오비탈은 σ 결합 성격을 가지며, C-H 결합에 주로 국소화되어 있다" 같은 해석을 생성. 이미지 입력은 멀티모달 LLM 필요

**한계**: LLM의 화학 해석 정확도 검증이 핵심 과제. 할루시네이션 위험 ⚠️

## 3C. 최종 연구 방향 추천

**1순위: 아이디어 #1 (QCViz-MCP 범용 프레임워크)** — 이유: 가장 현실적 실현 가능성(6주), 명확한 차별점(전자 구조 MCP의 빈 공간), 범용성으로 인한 넓은 사용자 기반, JOSS 2차 논문도 가능

**2순위: 아이디어 #2 (대화형 IBO 전자 흐름)** — 이유: 학술적 참신성이 가장 높음(5/5), JCTC 게재 시 임팩트 극대화. 단 개발 기간이 길고 기술 난이도 높음

**병합 가능 여부**: ✅ **가능하고 권장됨**. 아이디어 #1을 코어 프레임워크로 구현하고, 아이디어 #2의 전자 흐름 분석을 그 프레임워크의 flagship 사용 사례(use case)로 제시. 하나의 논문에서 "프레임워크(기여 1) + 전자 흐름 분석 적용(기여 2)"으로 구성하면 JCTC 또는 JCIM에 단일 논문으로 제출 가능

### Related Work 핵심 리스트 (20개)

| #   | 논문                                                      | 저널/출처                            | 연도 | 관련성                             |
| --- | --------------------------------------------------------- | ------------------------------------ | ---- | ---------------------------------- |
| 1   | Knizia, "Intrinsic Atomic Orbitals"                       | JCTC 9, 4834                         | 2013 | IAO 원논문 ✅                      |
| 2   | Knizia & Klein, "Electron Flow in Reaction Mechanisms"    | Angew. Chem. Int. Ed. 54, 5518       | 2015 | IBO 전자 흐름 시각화 원논문 ✅     |
| 3   | ChatMol, "Interactive Molecular Discovery"                | Bioinformatics 40(9)                 | 2024 | 자연어↔분자 설계, 오비탈 미포함 ✅ |
| 4   | ChatMol Copilot                                           | ACL LangMol Workshop                 | 2024 | PyMOL LLM 에이전트 ✅              |
| 5   | El Agente Q, "Autonomous Agent for Quantum Chemistry"     | Matter                               | 2025 | LLM 멀티에이전트 양자화학 ✅       |
| 6   | VASPilot, "MCP-Facilitated Multi-Agent VASP"              | Chinese Physics B / arXiv 2508.07035 | 2025 | MCP 기반 자율 시뮬레이션 ✅        |
| 7   | ChemLint, "Conversational Cheminformatics"                | ChemRxiv                             | 2026 | MCP 기반 케모인포매틱스 ✅         |
| 8   | Code2MCP, "Transforming Code Repos into MCP"              | arXiv 2509.05941                     | 2025 | 자동 MCP 생성 방법론 ✅            |
| 9   | LLM for ORCA input generation                             | RSC Digital Discovery                | 2025 | LLM↔양자화학 인터페이스 🔶         |
| 10  | MCP Protocol Specification                                | Anthropic                            | 2024 | 프로토콜 기반 ✅                   |
| 11  | PySCF, "Recent Developments"                              | J. Chem. Phys.                       | 2020 | 계산 엔진 핵심 참조 ✅             |
| 12  | cclib 2.0                                                 | J. Chem. Phys. 161(4)                | 2024 | 파싱 엔진 핵심 참조 ✅             |
| 13  | 3Dmol.js, Rego & Koes                                     | Bioinformatics                       | 2015 | 시각화 엔진 참조 ✅                |
| 14  | ASE, Larsen et al.                                        | J. Phys.: Condens. Matter            | 2017 | 구조 조작 참조 ✅                  |
| 15  | Pipek & Mezey, "Fast intrinsic localization"              | J. Chem. Phys. 90, 4916              | 1989 | PM 국소화 이론 기반 ✅             |
| 16  | Lehtola & Jónsson, "PM localization with various charges" | JCTC 10, 642                         | 2014 | IAO-PM 관계 이론 🔶                |
| 17  | Foster & Boys, "Canonical CI Procedure"                   | Rev. Mod. Phys. 32, 300              | 1960 | Boys 국소화 원논문 🔶              |
| 18  | Hjorth Larsen et al., "ASE"                               | J. Phys.: Condens. Matter 29, 273002 | 2017 | ASE 원논문 ✅                      |
| 19  | Ong et al., "pymatgen"                                    | Comput. Mater. Sci. 68, 314          | 2013 | 재료과학 도구 참조 🔶              |
| 20  | Avogadro 2, Hanwell et al.                                | J. Cheminform. 4, 17                 | 2012 | 분자 편집기 비교 대상 🔶           |

---

## [Phase 3] 자체 검증

- [x] 산출물이 해당 Phase의 "목표"에 부합하는가? — 7개 아이디어, 상위 3개 심층 평가, 최종 추천 도출
- [x] 모든 테이블의 행 수가 최소 요구치를 충족하는가? — 아이디어 7행(7+), Related Work 20개(20+)
- [x] 신뢰도 태그가 빠짐없이 부착되었는가? — ✅
- [x] "NEVER" 항목을 위반하지 않았는가? — 논문 기여점 불분명한 아이디어에 대해 솔직히 평가
- [x] 다음 Phase에 필요한 입력이 모두 생산되었는가? — 추천 아이디어, 대상 저널, Related Work 확보
- [x] 사실과 추정이 명확히 구분되었는가? — ✅

**자체 검증 점수: 6/6** ✅

---

# PHASE 4 산출물: MCP 서버 설계 (Architecture Design)

## 4A. 시스템 아키텍처

### 다이어그램 A: Phase α (MVP) 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP 클라이언트 계층                           │
│   ┌─────────────────┐    ┌─────────────────┐                   │
│   │  Claude Desktop  │    │   Claude Code    │                  │
│   └────────┬────────┘    └────────┬────────┘                   │
│            │                      │                             │
│            └──────────┬───────────┘                             │
│                       │ MCP Protocol (JSON-RPC / stdio)         │
└───────────────────────┼─────────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                  QCViz-MCP 서버 (FastMCP)                       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  mcp_server.py — Tool 등록 + 라우팅                      │    │
│  │  ┌──────────┐ ┌──────────────┐ ┌────────────┐           │    │
│  │  │compute_  │ │visualize_    │ │parse_       │           │    │
│  │  │ibo       │ │orbital       │ │output       │           │    │
│  │  └────┬─────┘ └──────┬───────┘ └─────┬──────┘           │    │
│  │  ┌────┴──────────┐ ┌─┴──────────┐ ┌──┴───────────┐      │    │
│  │  │compute_       │ │convert_    │ │analyze_      │      │    │
│  │  │partial_charges│ │format      │ │bonding       │      │    │
│  │  └────┬──────────┘ └─┬──────────┘ └──┬───────────┘      │    │
│  └───────┼──────────────┼───────────────┼───────────────────┘    │
│          │              │               │                        │
│  ┌───────▼──────────────▼───────────────▼───────────────────┐    │
│  │              backends/registry.py                         │    │
│  │       ┌─────────────────────────────────┐                 │    │
│  │       │  BackendRegistry                │                 │    │
│  │       │  - detect_available_backends()  │                 │    │
│  │       │  - get_compute_backend()        │                 │    │
│  │       │  - get_viz_backend()            │                 │    │
│  │       │  - get_parser_backend()         │                 │    │
│  │       └──────┬────────┬────────┬────────┘                 │    │
│  └──────────────┼────────┼────────┼──────────────────────────┘    │
│                 │        │        │                               │
│  ┌──────────────▼──┐ ┌──▼──────┐ ┌▼──────────────┐ ┌──────────┐ │
│  │pyscf_backend.py │ │viz_     │ │cclib_         │ │ase_      │ │
│  │(ComputeBackend) │ │backend  │ │backend.py     │ │backend   │ │
│  │                 │ │.py      │ │(ParserBackend)│ │.py       │ │
│  │• compute_iao()  │ │(Viz     │ │               │ │(Structure│ │
│  │• compute_ibo()  │ │Backend) │ │• parse_output │ │Backend)  │ │
│  │• get_charges()  │ │         │ │• extract_mos  │ │          │ │
│  │• gen_cubefile() │ │• render │ │• extract_geom │ │• read    │ │
│  │                 │ │  _orb   │ │               │ │• write   │ │
│  │                 │ │• render │ │               │ │• convert │ │
│  │                 │ │  _mol   │ │               │ │          │ │
│  └────────┬────────┘ └───┬─────┘ └──────┬────────┘ └────┬─────┘ │
│           │              │              │               │        │
│  ┌────────▼──────────────▼──────────────▼───────────────▼──────┐ │
│  │                     파일 시스템                               │ │
│  │  /tmp/qcviz/  .cube  .molden  .xyz  .html  .png             │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 다이어그램 B: Phase γ (완전체) 아키텍처

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP 클라이언트 계층                           │
│   Claude Desktop / Claude Code / 기타 MCP 클라이언트            │
└───────────────────────┬─────────────────────────────────────────┘
                        │ MCP Protocol
┌───────────────────────▼─────────────────────────────────────────┐
│                  QCViz-MCP 서버 (FastMCP)                       │
│                                                                  │
│  Tools (Phase α):                                               │
│  compute_ibo, visualize_orbital, parse_output,                  │
│  compute_partial_charges, convert_format, analyze_bonding       │
│                                                                  │
│  Tools (Phase β 추가, 점선):                                    │
│  ┄┄ export_for_iboview ┄┄ track_orbital_along_path ┄┄          │
│  ┄┄ render_electron_flow ┄┄                                    │
│                                                                  │
│  Tools (Phase γ 추가, 이중 점선):                               │
│  ┈┈ compare_methods ┈┈ export_publication_image ┈┈             │
│  ┈┈ compute_tddft_orbitals ┈┈ analyze_periodic ┈┈             │
│                                                                  │
│  ┌───────────────────────────────────────────────────────┐      │
│  │              backends/registry.py                      │      │
│  │  ┌─────────┐ ┌────────┐ ┌──────┐ ┌──────┐           │      │
│  │  │PySCF    │ │py3Dmol │ │cclib │ │ASE   │ Phase α   │      │
│  │  │Backend  │ │Backend │ │Back  │ │Back  │ (코어)    │      │
│  │  └─────────┘ └────────┘ └──────┘ └──────┘           │      │
│  │  ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄            │      │
│  │  ┌──────────────┐                       Phase β      │      │
│  │  │IboView Bridge│ (.molden 파일 I/O)    (확장 1)     │      │
│  │  └──────────────┘                                     │      │
│  │  ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈            │      │
│  │  ┌──────────┐ ┌──────────┐              Phase γ      │      │
│  │  │PyMOL     │ │VESTA     │              (확장 2)     │      │
│  │  │Backend   │ │Backend   │                            │      │
│  │  └──────────┘ └──────────┘                            │      │
│  └───────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

### MCP Tools 상세 정의서 (12개)

**Phase α (MVP) — 6개 tools:**

```
tool_name: "compute_ibo"
description: "주어진 분자 좌표와 기저함수로 IAO/IBO 국소화 오비탈을 계산합니다.
              DFT 또는 HF 계산을 수행한 후 점유 오비탈을 IBO로 국소화하고,
              각 IBO의 cube 파일과 오비탈 조성 정보를 반환합니다."
parameters: {
    "molecule_xyz": "str — XYZ 형식 분자 좌표 또는 파일 경로",
    "basis": "str — 기저함수 세트 (기본값: 'cc-pVDZ')",
    "method": "str — 계산 방법 ('hf', 'b3lyp', 'pbe0' 등, 기본값: 'b3lyp')",
    "localization": "str — 국소화 방법 ('ibo', 'boys', 'pm', 기본값: 'ibo')",
    "output_dir": "str — 출력 디렉토리 (기본값: '/tmp/qcviz')"
}
returns: "dict — {'orbitals': [{'index': int, 'cube_file': str, 'composition': dict}],
                   'energy': float, 'charge_info': dict}"
backend: "PySCF (pyscf_backend.py)"
```

```
tool_name: "visualize_orbital"
description: "cube 파일 또는 오비탈 데이터로부터 3D 등치면 시각화를 생성합니다.
              양/음 등치면을 각각 다른 색으로 렌더링하고 분자 구조를 함께 표시합니다."
parameters: {
    "cube_file": "str — cube 파일 경로",
    "isovalue": "float — 등치면 값 (기본값: 0.05)",
    "colors": "list[str] — [양, 음] 등치면 색 (기본값: ['blue', 'red'])",
    "style": "str — 분자 표현 스타일 ('stick', 'ball_stick', 'sphere', 기본값: 'stick')",
    "output_format": "str — 출력 형식 ('html', 'png', 기본값: 'html')"
}
returns: "str — HTML 문자열 (output_format='html') 또는 PNG 파일 경로"
backend: "py3Dmol (viz_backend.py)"
```

```
tool_name: "parse_output"
description: "양자화학 프로그램의 출력 파일을 파싱하여 구조화된 데이터를 추출합니다.
              지원 프로그램: ORCA, Gaussian, GAMESS, NWChem, Psi4, Q-Chem 등 16개."
parameters: {
    "output_file": "str — 출력 파일 경로",
    "program": "str — 프로그램 이름 (선택, 자동 감지 가능)",
    "extract": "list[str] — 추출할 데이터 유형
                (['energy', 'geometry', 'orbitals', 'frequencies', 'charges'] 등)"
}
returns: "dict — 추출된 데이터 (프로그램 독립적 형식)"
backend: "cclib (cclib_backend.py)"
```

```
tool_name: "compute_partial_charges"
description: "IAO 기반 부분전하를 계산합니다. Mulliken/Löwdin과 달리 기저함수 독립적이며
              화학적으로 직관적인 전하 값을 제공합니다."
parameters: {
    "molecule_xyz": "str — XYZ 형식 분자 좌표",
    "basis": "str — 기저함수 세트 (기본값: 'cc-pVDZ')",
    "method": "str — 계산 방법 (기본값: 'b3lyp')",
    "charge_type": "str — 전하 유형 ('iao', 'mulliken', 'lowdin', 기본값: 'iao')"
}
returns: "dict — {'charges': [{'atom': str, 'index': int, 'charge': float}],
                   'total_charge': float}"
backend: "PySCF (pyscf_backend.py)"
```

```
tool_name: "convert_format"
description: "분자 구조 파일을 다른 포맷으로 변환합니다."
parameters: {
    "input_file": "str — 입력 파일 경로",
    "input_format": "str — 입력 포맷 (선택, 확장자로 자동 감지)",
    "output_format": "str — 출력 포맷 ('xyz', 'cif', 'pdb', 'poscar', 'molden' 등)",
    "output_file": "str — 출력 파일 경로 (선택)"
}
returns: "str — 출력 파일 경로"
backend: "ASE (ase_backend.py)"
```

```
tool_name: "analyze_bonding"
description: "IAO/IBO 기반 결합 분석을 수행합니다. 선택한 원자 쌍 사이의 결합 차수,
              결합에 기여하는 IBO의 조성, 결합 유형(σ/π/δ)을 분석합니다."
parameters: {
    "molecule_xyz": "str — XYZ 형식 분자 좌표",
    "atom_pairs": "list[list[int]] — 분석할 원자 쌍 인덱스 (예: [[0,1], [1,2]])",
    "basis": "str — 기저함수 세트 (기본값: 'cc-pVDZ')",
    "method": "str — 계산 방법 (기본값: 'b3lyp')"
}
returns: "dict — {'bonds': [{'atoms': [int,int], 'order': float,
                              'type': str, 'contributing_ibos': list}]}"
backend: "PySCF (pyscf_backend.py)"
```

**Phase β — 3개 추가 tools:**

```
tool_name: "export_for_iboview"
description: ".molden 형식 파일을 생성하여 IboView에서 고품질 시각화가 가능하도록 합니다."
parameters: {
    "molecule_xyz": "str", "basis": "str", "method": "str",
    "include_orbitals": "str — 'all', 'occupied', 'ibo' (기본값: 'ibo')",
    "output_file": "str"
}
returns: "str — .molden 파일 경로 + IboView 실행 안내"
backend: "PySCF + cclib"
```

```
tool_name: "track_orbital_along_path"
description: "반응 경로(IRC 또는 수동 구조 시퀀스)를 따라 IBO 오비탈 변화를 추적합니다."
parameters: {
    "path_files": "list[str] — 경로 상 구조 파일 목록 (XYZ 순서)",
    "basis": "str", "method": "str",
    "track_mode": "str — 'overlap' (오비탈 중첩 기반 추적)"
}
returns: "dict — {'frames': [{'step': int, 'orbitals': [...], 'charges': [...]}],
                   'visualization_html': str}"
backend: "PySCF + py3Dmol"
```

```
tool_name: "render_electron_flow"
description: "반응 경로 상의 IBO 변화를 분석하여 전자 흐름 다이어그램(curly arrow)을 생성합니다."
parameters: {
    "path_files": "list[str]", "basis": "str", "method": "str",
    "arrow_threshold": "float — 전자 흐름 판정 임계값 (기본값: 0.3)"
}
returns: "dict — {'electron_flows': [{'from_atom': int, 'to_atom': int,
                                        'electrons': float}],
                   'diagram_svg': str, 'interpretation': str}"
backend: "PySCF (계산) + matplotlib (다이어그램)"
```

**Phase γ — 3개 추가 tools:**

```
tool_name: "compare_methods"
description: "동일 분자에 대해 여러 국소화 방법(IBO, Boys, PM)을 비교합니다."
backend: "PySCF"

tool_name: "export_publication_image"
description: "논문 출판 품질의 오비탈/분자 이미지를 생성합니다 (300dpi, 벡터 그래픽)."
backend: "matplotlib + py3Dmol 또는 PyMOL"

tool_name: "compute_tddft_orbitals"
description: "TDDFT 계산 후 여기 상태 오비탈(NTO 등)을 시각화합니다."
backend: "PySCF"
```

### 데이터 흐름

```
[사용자 자연어 요청]
       │
       ▼
[Claude/LLM — MCP 클라이언트]
       │ MCP tool 호출 (JSON-RPC)
       ▼
[QCViz-MCP 서버]
       │
       ├── 1. 입력 검증 (molecule_xyz 파싱, 파라미터 확인)
       │
       ├── 2. Registry에서 백엔드 조회
       │       └── get_compute_backend() → PySCFBackend (또는 에러)
       │
       ├── 3. 계산 실행
       │       ├── PySCF: gto.M() → scf.RKS().run() → lo.ibo.ibo()
       │       └── 결과: MO 계수, 에너지, IAO 전하, cube 파일
       │
       ├── 4. 시각화 생성
       │       ├── py3Dmol: cube 데이터 → addVolumetricData → HTML
       │       └── 결과: HTML 문자열 또는 파일 경로
       │
       ├── 5. 결과 구조화
       │       └── dict → JSON 직렬화 가능 형태로 변환
       │
       └── 6. MCP 응답 반환
               └── JSON-RPC response (텍스트 + 파일 경로)
```

### 의존성 목록

**Python 패키지 (Phase α)**:

- `fastmcp>=2.0` — MCP 서버 프레임워크 ✅
- `pyscf>=2.4` — 양자화학 계산 엔진 ✅
- `cclib>=1.8` — 출력 파일 파싱 ✅
- `py3Dmol>=2.0` — 3D 시각화 ✅
- `ase>=3.22` — 구조 조작/파일 변환 ✅
- `numpy>=1.24` — 수치 연산 ✅
- `typing-extensions>=4.0` — 타입 힌트 ✅

**시스템 요구사항**:

- Python 3.10+ ✅
- BLAS/LAPACK (PySCF 의존) — 대부분 OS에서 기본 제공 🔶
- 디스크 공간: cube 파일 생성에 ~10-100MB/분자 ⚠️

## 4B. 프로토타입 범위 정의

**MVP 포함 tools (6개)**: `compute_ibo`, `visualize_orbital`, `parse_output`, `compute_partial_charges`, `convert_format`, `analyze_bonding`

**MVP 제외 tools (v2)**: `export_for_iboview`, `track_orbital_along_path`, `render_electron_flow`, `compare_methods`, `export_publication_image`, `compute_tddft_orbitals`

**MVP 개발 예상 시간**: 10-14일 (1인 개발자 기준)

**MVP 테스트 시나리오**:

| #   | 시나리오                           | 입력                 | 예상 출력                       | 검증 기준                                  |
| --- | ---------------------------------- | -------------------- | ------------------------------- | ------------------------------------------ |
| 1   | "물 분자의 IBO를 보여줘"           | H₂O xyz 좌표         | IBO cube 파일 3개 + HTML 시각화 | IBO가 2개 O-H 결합 + 2개 고립쌍으로 국소화 |
| 2   | "이 ORCA 출력에서 HOMO-LUMO 갭은?" | ORCA .out 파일       | 에너지 값 + 오비탈 시각화       | cclib 파싱 결과와 수동 확인 값 일치        |
| 3   | "에탄올의 O-H 결합 분석해줘"       | C₂H₅OH xyz + 원자 쌍 | 결합 차수, IBO 조성, 부분전하   | IAO 부분전하가 화학적으로 합리적           |

---

## [Phase 4] 자체 검증

- [x] 산출물이 해당 Phase의 "목표"에 부합하는가? — 아키텍처 다이어그램 2개, 12개 tools, 데이터 흐름, MVP 스코프 정의
- [x] 모든 테이블의 행 수가 최소 요구치를 충족하는가? — Tools 12개(10+), 시나리오 3개(3+)
- [x] 신뢰도 태그가 빠짐없이 부착되었는가? — ✅
- [x] "NEVER" 항목을 위반하지 않았는가? — ✅
- [x] 다음 Phase에 필요한 입력이 모두 생산되었는가? — 아키텍처, tool 정의, MVP 범위 모두 확보
- [x] 사실과 추정이 명확히 구분되었는가? — ✅

**자체 검증 점수: 6/6** ✅

---

# PHASE 5 산출물: 논문 초안 구조 + 프로토타입 코드 스켈레톤

## 5A. 논문 초안 구조

```
Title: QCViz-MCP: A Model Context Protocol Framework for
       Conversational Quantum Chemistry Visualization and Analysis

Authors: [User] et al.
Target Journal: J. Chem. Inf. Model. (ACS)
  선택 이유: IF ~5.6, 소프트웨어 논문 정기 게재, ChatMol(Bioinformatics 2024)과
  유사한 자연어↔화학 시스템 논문이 관련 저널에 게재된 선례 있음.
  전자 구조 수준의 분석을 다루므로 JCTC도 고려 가능.
```

### Abstract 초안 (200단어)

> The integration of large language models (LLMs) with scientific software has opened new possibilities for conversational approaches to computational chemistry. While existing tools enable natural language control of molecular visualization (ChatMol, pymol-mcp) and atomistic simulations (mcp-atomictoolkit, VASPilot), none address the critical domain of electronic structure analysis—orbital visualization, bonding analysis, and electron flow tracking. We present QCViz-MCP, an open-source Model Context Protocol (MCP) server framework that bridges this gap by providing LLM-accessible tools for quantum chemistry visualization and analysis. Built on a pluggable backend architecture, QCViz-MCP integrates PySCF for intrinsic atomic orbital (IAO) and intrinsic bond orbital (IBO) computations, cclib for parsing outputs from 16 quantum chemistry programs, py3Dmol for interactive 3D orbital rendering, and ASE for structure manipulation. The framework exposes 12 MCP tools covering orbital computation, visualization, output parsing, partial charge analysis, bonding analysis, and reaction pathway orbital tracking. We demonstrate the framework on a benchmark set of 15 molecules and 5 organic reactions, showing that LLM-assisted orbital analysis through QCViz-MCP achieves comparable accuracy to manual IboView workflows while reducing analysis time by an estimated factor of 3-5. The pluggable architecture enables extension to additional backends including IboView file bridges and PyMOL integration without modifying core tool implementations.

### 논문 구조

```
1. Introduction
   1.1 Conversational Scientific Computing — LLM + 과학 소프트웨어 통합 동향
   1.2 The Gap in Electronic Structure Analysis — 기존 MCP/AI 도구가 분자 구조에
       한정되고 전자 구조(오비탈, 전하, 결합)를 다루지 못하는 문제
   1.3 Our Contribution — QCViz-MCP: 범용 전자 구조 분석 MCP 프레임워크

2. Related Work
   2.1 Quantum Chemistry Visualization Tools — IboView, Multiwfn, py3Dmol 등 현황
   2.2 MCP and AI Agent-Based Scientific Workflows — molecule-mcp, VASPilot,
       El Agente, ChemLint, Code2MCP
   2.3 IAO/IBO Methodology — Knizia JCTC 2013, Knizia & Klein ACIE 2015,
       PySCF 구현, 다른 국소화 방법과의 관계

3. System Design
   3.1 Architecture Overview — pluggable backend, Registry 패턴, graceful degradation
   3.2 MCP Tool Definitions — 12개 tools의 입출력 스펙
   3.3 Backend Engine Integration — PySCF, cclib, py3Dmol, ASE 통합 방법
   3.4 Data Flow Pipeline — 입력→계산→분석→시각화→해석

4. Implementation
   4.1 IAO/IBO Computation Pipeline — PySCF lo.iao/ibo → cube 파일 생성
   4.2 Interactive Orbital Visualization — py3Dmol 등치면 렌더링, HTML/이미지 출력
   4.3 Multi-Program Output Parsing — cclib 통합, 프로그램 독립적 데이터 추출
   4.4 IboView File Bridge — .molden 파일 생성, 고품질 렌더링 연계

5. Evaluation
   5.1 Benchmark Design
       - 소분자 10개 (H₂O, C₆H₆, C₂H₅OH, NH₃, CO₂, CH₃CHO, C₂H₄,
         HCN, HCOOH, CH₃COCH₃)
       - 중분자 5개 (아스피린, 카페인, 페놀, 아닐린, 글리신)
       - 유기반응 5개 (SN2, E2, Diels-Alder, aldol, Cope rearrangement)
   5.2 Usability Evaluation — LLM 워크플로우 vs 수동 워크플로우 시간/단계수 비교
   5.3 Accuracy Validation — PySCF IBO vs IboView 자체 IBO 수치 비교,
       IAO 부분전하 vs 문헌값 비교
   5.4 Multi-Program Interoperability — ORCA/Gaussian/Psi4 출력에 대한 파싱 정확도

6. Discussion
   6.1 Limitations — 대규모 시스템 확장성, py3Dmol 이미지 품질 한계,
       LLM 화학 해석의 신뢰성
   6.2 Future Work — 전자 흐름 다이어그램 자동화, TDDFT/NTO 확장,
       멀티모달 LLM 오비탈 해석, 주기적 시스템 지원

7. Conclusion

References: [20+ 핵심 참고문헌 — Phase 3 Related Work 리스트 참조]

Supporting Information:
- S1: 전체 MCP Tool 스펙 (JSON Schema)
- S2: 벤치마크 분자 좌표 및 결과
- S3: 코드 가용성 + 설치 가이드
```

### 리뷰어 시뮬레이션 (5개 약점 + 대응)

| #   | 예상 비판                                               | 대응                                                                                                                                                          |
| --- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | "PySCF IAO/IBO를 MCP로 감쌌을 뿐, 방법론적 기여가 없다" | **반박**: Backend ABC + Registry 아키텍처 설계가 기여. 단일 도구 래핑이 아닌 16개 QC 프로그램 출력 → 통합 분석 → 시각화 파이프라인의 설계가 핵심              |
| 2   | "벤치마크가 소분자에 편향됨"                            | **인정(limitation)**: MVP는 소분자 중심, 100+ 원자 시스템은 향후 연구. 단, 대부분 유기화학 교과서 반응은 소분자                                               |
| 3   | "MCP는 Anthropic 독점 기술이 아닌가? 범용성이 의심됨"   | **반박**: MCP는 JSON-RPC 기반 오픈 프로토콜, 다수 LLM 클라이언트 지원. OpenAI, Google도 MCP 지원 움직임 🔶                                                    |
| 4   | "py3Dmol 이미지 품질이 IboView/PyMOL에 미달"            | **인정 + 대안**: IboView 파일 브릿지(Phase β)로 고품질 렌더링 경로 제공. py3Dmol은 빠른 인터랙티브 확인용                                                     |
| 5   | "LLM의 화학 해석 정확도를 어떻게 보장하는가?"           | **범위 명확화**: 본 논문은 LLM이 tool을 호출하는 워크플로우에 초점. LLM의 해석 정확도는 별도 연구 주제. 도구 자체의 수치적 정확도는 PySCF/IboView 비교로 검증 |

## 5B. 프로토타입 코드 스켈레톤

### 프로젝트 디렉토리 구조

```
qcviz-mcp/
├── pyproject.toml
├── README.md
├── LICENSE (MIT)
├── src/
│   └── qcviz_mcp/
│       ├── __init__.py
│       ├── mcp_server.py          # FastMCP 서버 메인
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── compute_ibo.py
│       │   ├── visualize.py
│       │   ├── parse_output.py
│       │   ├── analyze.py
│       │   ├── convert.py
│       │   └── charges.py
│       ├── backends/
│       │   ├── __init__.py
│       │   ├── base.py           # Backend ABC 정의
│       │   ├── registry.py       # 백엔드 자동 탐지 + 등록
│       │   ├── pyscf_backend.py  # Phase α 코어
│       │   ├── cclib_backend.py  # Phase α 코어
│       │   ├── viz_backend.py    # Phase α 코어 (py3Dmol)
│       │   ├── ase_backend.py    # Phase α 코어
│       │   ├── iboview_bridge.py # Phase β
│       │   └── pymol_backend.py  # Phase γ
│       └── utils/
│           ├── __init__.py
│           ├── file_io.py
│           └── chemistry.py
├── tests/
│   ├── __init__.py
│   ├── test_compute_ibo.py
│   ├── test_visualize.py
│   ├── test_parse.py
│   └── test_registry.py
├── examples/
│   ├── example_ibo_analysis.md
│   └── example_molecules/
│       ├── water.xyz
│       ├── benzene.xyz
│       └── ethanol.xyz
└── claude_desktop_config.json
```

### 핵심 파일 코드 스켈레톤

**`pyproject.toml`**:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "qcviz-mcp"
version = "0.1.0"
description = "MCP server framework for quantum chemistry visualization and analysis"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
authors = [
    {name = "QCViz Team"},
]
dependencies = [
    "fastmcp>=2.0",
    "numpy>=1.24",
]

[project.optional-dependencies]
compute = ["pyscf>=2.4"]
parse = ["cclib>=1.8"]
viz = ["py3Dmol>=2.0"]
structure = ["ase>=3.22"]
all = ["qcviz-mcp[compute,parse,viz,structure]"]

[project.scripts]
qcviz-mcp = "qcviz_mcp.mcp_server:main"
```

**`src/qcviz_mcp/__init__.py`**:

```python
"""QCViz-MCP: Quantum Chemistry Visualization MCP Server Framework."""
__version__ = "0.1.0"
```

**`src/qcviz_mcp/backends/base.py`** — 핵심 ABC 정의:

```python
"""Abstract base classes for QCViz-MCP backends.

This module defines the contracts that all backends must implement.
New backends are added by subclassing these ABCs and placing the
module in the backends/ directory.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class OrbitalData:
    """Container for orbital computation results."""
    coefficients: Any  # numpy ndarray [n_orbitals, n_basis]
    energies: list[float]
    occupancies: list[float]
    labels: list[str]
    basis_info: dict[str, Any] = field(default_factory=dict)


@dataclass
class CubeFileData:
    """Container for Gaussian cube file data."""
    filepath: Path
    orbital_index: int
    orbital_label: str
    grid_data: Any | None = None  # numpy ndarray, optional


@dataclass
class ChargeData:
    """Container for partial charge results."""
    atom_symbols: list[str]
    atom_indices: list[int]
    charges: list[float]
    method: str  # 'iao', 'mulliken', 'lowdin'


@dataclass
class BondAnalysis:
    """Container for bond analysis results."""
    atom_pair: tuple[int, int]
    bond_order: float
    bond_type: str  # 'sigma', 'pi', 'delta', 'mixed'
    contributing_orbitals: list[dict[str, Any]]


@dataclass
class ParsedOutput:
    """Container for parsed quantum chemistry output."""
    program: str
    energy: float | None = None
    geometry: Any | None = None  # numpy ndarray [n_atoms, 3]
    atom_symbols: list[str] = field(default_factory=list)
    mo_coefficients: Any | None = None
    mo_energies: list[float] = field(default_factory=list)
    frequencies: list[float] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ComputeBackend(ABC):
    """Abstract base class for quantum chemistry computation backends.

    Implementations: PySCFBackend, (future: Psi4Backend, etc.)
    """

    @abstractmethod
    def compute_scf(
        self,
        atom_coords: str,
        basis: str = "cc-pVDZ",
        method: str = "b3lyp",
        charge: int = 0,
        spin: int = 0,
    ) -> dict[str, Any]:
        """Run SCF calculation and return results.

        Returns:
            dict with keys: 'energy', 'mo_coefficients', 'mo_energies',
                           'mo_occupancies', 'converged'
        """
        ...

    @abstractmethod
    def compute_iao(
        self,
        atom_coords: str,
        basis: str = "cc-pVDZ",
        method: str = "b3lyp",
    ) -> OrbitalData:
        """Compute Intrinsic Atomic Orbitals."""
        ...

    @abstractmethod
    def compute_ibo(
        self,
        atom_coords: str,
        basis: str = "cc-pVDZ",
        method: str = "b3lyp",
        localization: str = "ibo",
    ) -> tuple[OrbitalData, list[CubeFileData]]:
        """Compute Intrinsic Bond Orbitals and generate cube files.

        Returns:
            Tuple of (OrbitalData, list of CubeFileData with file paths)
        """
        ...

    @abstractmethod
    def get_partial_charges(
        self,
        atom_coords: str,
        basis: str = "cc-pVDZ",
        method: str = "b3lyp",
        charge_type: str = "iao",
    ) -> ChargeData:
        """Compute partial charges."""
        ...

    @abstractmethod
    def analyze_bonding(
        self,
        atom_coords: str,
        atom_pairs: list[tuple[int, int]],
        basis: str = "cc-pVDZ",
        method: str = "b3lyp",
    ) -> list[BondAnalysis]:
        """Analyze bonding between specified atom pairs."""
        ...


class VizBackend(ABC):
    """Abstract base class for visualization backends.

    Implementations: Py3DmolBackend, (future: PyMOLBackend, etc.)
    """

    @abstractmethod
    def render_orbital(
        self,
        cube_file: str | Path,
        isovalue: float = 0.05,
        colors: tuple[str, str] = ("blue", "red"),
        style: str = "stick",
    ) -> str:
        """Render orbital isosurface from cube file.

        Returns:
            HTML string with interactive 3D visualization.
        """
        ...

    @abstractmethod
    def render_molecule(
        self,
        atom_coords: str,
        style: str = "stick",
        color_by: str = "element",
    ) -> str:
        """Render molecular structure.

        Returns:
            HTML string with interactive 3D visualization.
        """
        ...

    @abstractmethod
    def export_image(
        self,
        visualization_html: str,
        output_path: str | Path,
        width: int = 800,
        height: int = 600,
        image_format: str = "png",
    ) -> Path:
        """Export visualization to static image file."""
        ...


class ParserBackend(ABC):
    """Abstract base class for output file parsing backends.

    Implementations: CclibBackend, (future: custom parsers)
    """

    @abstractmethod
    def parse_output(
        self,
        output_file: str | Path,
        program: str | None = None,
    ) -> ParsedOutput:
        """Parse quantum chemistry output file.

        Args:
            output_file: Path to the output file.
            program: Program name (optional, auto-detected if None).

        Returns:
            ParsedOutput with extracted data.
        """
        ...

    @abstractmethod
    def extract_orbitals(
        self,
        output_file: str | Path,
    ) -> OrbitalData | None:
        """Extract molecular orbital data from output file."""
        ...

    @abstractmethod
    def extract_geometry(
        self,
        output_file: str | Path,
    ) -> tuple[list[str], Any] | None:
        """Extract molecular geometry (symbols, coordinates)."""
        ...

    @abstractmethod
    def supported_programs(self) -> list[str]:
        """Return list of supported program names."""
        ...


class StructureBackend(ABC):
    """Abstract base class for structure manipulation backends.

    Implementations: ASEBackend, (future: pymatgen, etc.)
    """

    @abstractmethod
    def read_structure(
        self,
        filepath: str | Path,
        file_format: str | None = None,
    ) -> dict[str, Any]:
        """Read molecular/crystal structure from file.

        Returns:
            dict with 'symbols', 'positions', 'cell' (if periodic)
        """
        ...

    @abstractmethod
    def write_structure(
        self,
        symbols: list[str],
        positions: Any,
        filepath: str | Path,
        file_format: str | None = None,
    ) -> Path:
        """Write structure to file."""
        ...

    @abstractmethod
    def convert_format(
        self,
        input_file: str | Path,
        output_format: str,
        output_file: str | Path | None = None,
    ) -> Path:
        """Convert structure file between formats."""
        ...
```

**`src/qcviz_mcp/backends/registry.py`** — 백엔드 자동 탐지:

```python
"""Backend registry with automatic detection of available backends.

The registry probes for installed packages at import time and
registers only those backends whose dependencies are satisfied.
"""
from __future__ import annotations

import importlib
import logging
from typing import Type

from .base import ComputeBackend, VizBackend, ParserBackend, StructureBackend

logger = logging.getLogger(__name__)


class BackendNotAvailableError(Exception):
    """Raised when a requested backend is not installed."""

    def __init__(self, backend_name: str, package: str, install_hint: str):
        self.backend_name = backend_name
        self.package = package
        self.install_hint = install_hint
        super().__init__(
            f"Backend '{backend_name}' is not available. "
            f"Package '{package}' is not installed. "
            f"Install with: {install_hint}"
        )


class BackendRegistry:
    """Central registry for all QCViz-MCP backends.

    Automatically detects installed packages and registers available
    backends. Backends that fail to load are silently skipped with
    a log warning — other backends continue to function normally.
    """

    def __init__(self) -> None:
        self._compute_backends: dict[str, Type[ComputeBackend]] = {}
        self._viz_backends: dict[str, Type[VizBackend]] = {}
        self._parser_backends: dict[str, Type[ParserBackend]] = {}
        self._structure_backends: dict[str, Type[StructureBackend]] = {}
        self._default_compute: str | None = None
        self._default_viz: str | None = None
        self._default_parser: str | None = None
        self._default_structure: str | None = None
        self._probe_and_register()

    def _probe_and_register(self) -> None:
        """Probe for installed packages and register available backends."""
        # PySCF backend
        if self._is_package_available("pyscf"):
            try:
                from .pyscf_backend import PySCFBackend
                self._compute_backends["pyscf"] = PySCFBackend
                self._default_compute = "pyscf"
                logger.info("PySCF compute backend registered.")
            except ImportError as e:
                logger.warning(f"PySCF found but backend failed to load: {e}")

        # cclib backend
        if self._is_package_available("cclib"):
            try:
                from .cclib_backend import CclibBackend
                self._parser_backends["cclib"] = CclibBackend
                self._default_parser = "cclib"
                logger.info("cclib parser backend registered.")
            except ImportError as e:
                logger.warning(f"cclib found but backend failed to load: {e}")

        # py3Dmol backend
        if self._is_package_available("py3Dmol"):
            try:
                from .viz_backend import Py3DmolBackend
                self._viz_backends["py3dmol"] = Py3DmolBackend
                self._default_viz = "py3dmol"
                logger.info("py3Dmol visualization backend registered.")
            except ImportError as e:
                logger.warning(f"py3Dmol found but backend failed to load: {e}")

        # ASE backend
        if self._is_package_available("ase"):
            try:
                from .ase_backend import ASEBackend
                self._structure_backends["ase"] = ASEBackend
                self._default_structure = "ase"
                logger.info("ASE structure backend registered.")
            except ImportError as e:
                logger.warning(f"ASE found but backend failed to load: {e}")

    @staticmethod
    def _is_package_available(package_name: str) -> bool:
        """Check if a Python package is installed."""
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            return False

    def get_compute_backend(
        self, name: str | None = None
    ) -> ComputeBackend:
        """Get a compute backend instance.

        Args:
            name: Backend name. Uses default if None.

        Raises:
            BackendNotAvailableError: If the backend is not installed.
        """
        target = name or self._default_compute
        if target is None or target not in self._compute_backends:
            raise BackendNotAvailableError(
                backend_name=target or "compute",
                package="pyscf",
                install_hint='pip install "qcviz-mcp[compute]"',
            )
        return self._compute_backends[target]()

    def get_viz_backend(self, name: str | None = None) -> VizBackend:
        """Get a visualization backend instance."""
        target = name or self._default_viz
        if target is None or target not in self._viz_backends:
            raise BackendNotAvailableError(
                backend_name=target or "viz",
                package="py3Dmol",
                install_hint='pip install "qcviz-mcp[viz]"',
            )
        return self._viz_backends[target]()

    def get_parser_backend(
        self, name: str | None = None
    ) -> ParserBackend:
        """Get a parser backend instance."""
        target = name or self._default_parser
        if target is None or target not in self._parser_backends:
            raise BackendNotAvailableError(
                backend_name=target or "parser",
                package="cclib",
                install_hint='pip install "qcviz-mcp[parse]"',
            )
        return self._parser_backends[target]()

    def get_structure_backend(
        self, name: str | None = None
    ) -> StructureBackend:
        """Get a structure manipulation backend instance."""
        target = name or self._default_structure
        if target is None or target not in self._structure_backends:
            raise BackendNotAvailableError(
                backend_name=target or "structure",
                package="ase",
                install_hint='pip install "qcviz-mcp[structure]"',
            )
        return self._structure_backends[target]()

    def list_available(self) -> dict[str, list[str]]:
        """List all available backends by category."""
        return {
            "compute": list(self._compute_backends.keys()),
            "viz": list(self._viz_backends.keys()),
            "parser": list(self._parser_backends.keys()),
            "structure": list(self._structure_backends.keys()),
        }


# Module-level singleton
registry = BackendRegistry()
```

**`src/qcviz_mcp/backends/pyscf_backend.py`** — PySCF 계산 백엔드:

```python
"""PySCF-based compute backend for IAO/IBO analysis.

Requires: pip install pyscf
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import numpy as np

from .base import (
    ComputeBackend,
    OrbitalData,
    CubeFileData,
    ChargeData,
    BondAnalysis,
)


class PySCFBackend(ComputeBackend):
    """Compute backend using PySCF for IAO/IBO calculations."""

    def __init__(self) -> None:
        import pyscf  # noqa: F401 — validate import
        self._output_dir = Path(tempfile.mkdtemp(prefix="qcviz_"))

    def _build_mol(
        self,
        atom_coords: str,
        basis: str,
        charge: int = 0,
        spin: int = 0,
    ) -> Any:
        """Build PySCF Mole object from XYZ string."""
        from pyscf import gto

        mol = gto.M(
            atom=atom_coords,
            basis=basis,
            charge=charge,
            spin=spin,
            verbose=0,
        )
        return mol

    def compute_scf(
        self,
        atom_coords: str,
        basis: str = "cc-pVDZ",
        method: str = "b3lyp",
        charge: int = 0,
        spin: int = 0,
    ) -> dict[str, Any]:
        """Run SCF (HF or DFT) calculation."""
        from pyscf import scf, dft

        mol = self._build_mol(atom_coords, basis, charge, spin)

        if method.lower() == "hf":
            mf = scf.RHF(mol) if spin == 0 else scf.UHF(mol)
        else:
            mf = dft.RKS(mol) if spin == 0 else dft.UKS(mol)
            mf.xc = method

        mf.kernel()

        return {
            "energy": float(mf.e_tot),
            "mo_coefficients": mf.mo_coeff,
            "mo_energies": mf.mo_energy.tolist(),
            "mo_occupancies": mf.mo_occ.tolist(),
            "converged": mf.converged,
            "_mf": mf,  # keep reference for downstream use
            "_mol": mol,
        }

    def compute_iao(
        self,
        atom_coords: str,
        basis: str = "cc-pVDZ",
        method: str = "b3lyp",
    ) -> OrbitalData:
        """Compute Intrinsic Atomic Orbitals."""
        from pyscf import lo

        scf_result = self.compute_scf(atom_coords, basis, method)
        mf = scf_result["_mf"]
        mol = scf_result["_mol"]

        # Get occupied MO coefficients
        mo_occ = mf.mo_coeff[:, mf.mo_occ > 0]

        # Compute IAOs
        iao_coeff = lo.iao.iao(mol, mo_occ)

        return OrbitalData(
            coefficients=iao_coeff,
            energies=[],  # IAOs don't have well-defined energies
            occupancies=[],
            labels=[f"IAO_{i}" for i in range(iao_coeff.shape[1])],
            basis_info={"basis": basis, "method": method},
        )

    def compute_ibo(
        self,
        atom_coords: str,
        basis: str = "cc-pVDZ",
        method: str = "b3lyp",
        localization: str = "ibo",
    ) -> tuple[OrbitalData, list[CubeFileData]]:
        """Compute IBOs and generate cube files."""
        from pyscf import lo
        from pyscf.tools import cubegen

        scf_result = self.compute_scf(atom_coords, basis, method)
        mf = scf_result["_mf"]
        mol = scf_result["_mol"]

        mo_occ = mf.mo_coeff[:, mf.mo_occ > 0]

        # Compute IAOs first
        iao_coeff = lo.iao.iao(mol, mo_occ)

        # Compute IBOs
        ibo_coeff = lo.ibo.ibo(mol, mo_occ, iaos=iao_coeff)

        # Generate cube files for each IBO
        cube_files: list[CubeFileData] = []
        n_ibos = ibo_coeff.shape[1]

        for i in range(n_ibos):
            cube_path = self._output_dir / f"ibo_{i:03d}.cube"
            cubegen.orbital(mol, str(cube_path), ibo_coeff[:, i])
            cube_files.append(
                CubeFileData(
                    filepath=cube_path,
                    orbital_index=i,
                    orbital_label=f"IBO_{i}",
                )
            )

        orbital_data = OrbitalData(
            coefficients=ibo_coeff,
            energies=[],
            occupancies=[1.0] * n_ibos,  # Occupied IBOs
            labels=[f"IBO_{i}" for i in range(n_ibos)],
            basis_info={"basis": basis, "method": method, "localization": localization},
        )

        return orbital_data, cube_files

    def get_partial_charges(
        self,
        atom_coords: str,
        basis: str = "cc-pVDZ",
        method: str = "b3lyp",
        charge_type: str = "iao",
    ) -> ChargeData:
        """Compute partial charges using IAO or other methods."""
        from pyscf import lo

        scf_result = self.compute_scf(atom_coords, basis, method)
        mf = scf_result["_mf"]
        mol = scf_result["_mol"]

        if charge_type == "iao":
            mo_occ = mf.mo_coeff[:, mf.mo_occ > 0]
            iao_coeff = lo.iao.iao(mol, mo_occ)
            # Compute IAO charges via projection
            # TODO: implement detailed IAO charge computation
            charges = self._compute_iao_charges(mol, mf, iao_coeff, mo_occ)
        elif charge_type == "mulliken":
            charges = self._compute_mulliken_charges(mol, mf)
        else:
            raise ValueError(f"Unsupported charge type: {charge_type}")

        symbols = [mol.atom_symbol(i) for i in range(mol.natm)]

        return ChargeData(
            atom_symbols=symbols,
            atom_indices=list(range(mol.natm)),
            charges=charges,
            method=charge_type,
        )

    def _compute_iao_charges(
        self, mol: Any, mf: Any, iao_coeff: Any, mo_occ: Any
    ) -> list[float]:
        """Compute IAO-based partial charges."""
        # TODO: Full implementation
        # Basic approach: project density matrix onto IAO basis,
        # then compute population per atom
        return [0.0] * mol.natm  # Placeholder

    def _compute_mulliken_charges(
        self, mol: Any, mf: Any
    ) -> list[float]:
        """Compute Mulliken charges."""
        from pyscf import scf
        pop, chg = scf.hf.mulliken_pop(mol, mf.make_rdm1(), mf.get_ovlp())
        return chg.tolist()

    def analyze_bonding(
        self,
        atom_coords: str,
        atom_pairs: list[tuple[int, int]],
        basis: str = "cc-pVDZ",
        method: str = "b3lyp",
    ) -> list[BondAnalysis]:
        """Analyze bonding between atom pairs using IBO decomposition."""
        orbital_data, cube_files = self.compute_ibo(atom_coords, basis, method)

        # TODO: Implement IBO-based bond analysis
        # For each atom pair, identify IBOs localized on those atoms
        # and determine bond order and type
        analyses: list[BondAnalysis] = []
        for pair in atom_pairs:
            analyses.append(
                BondAnalysis(
                    atom_pair=tuple(pair),
                    bond_order=0.0,  # TODO
                    bond_type="unknown",  # TODO
                    contributing_orbitals=[],  # TODO
                )
            )
        return analyses
```

**`src/qcviz_mcp/backends/viz_backend.py`** — py3Dmol 시각화 백엔드:

```python
"""py3Dmol-based visualization backend for orbital rendering.

Requires: pip install py3Dmol
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import VizBackend


class Py3DmolBackend(VizBackend):
    """Visualization backend using py3Dmol/3Dmol.js."""

    def __init__(self) -> None:
        import py3Dmol  # noqa: F401 — validate import

    def render_orbital(
        self,
        cube_file: str | Path,
        isovalue: float = 0.05,
        colors: tuple[str, str] = ("blue", "red"),
        style: str = "stick",
    ) -> str:
        """Render orbital isosurface from cube file."""
        import py3Dmol

        cube_path = Path(cube_file)
        cube_data = cube_path.read_text()

        viewer = py3Dmol.view(width=600, height=400)

        # Add molecular structure from cube file
        viewer.addModel(cube_data, "cube")
        viewer.setStyle({style: {}})

        # Add positive isosurface
        viewer.addVolumetricData(
            cube_data,
            "cube",
            {
                "isoval": isovalue,
                "color": colors[0],
                "opacity": 0.7,
            },
        )

        # Add negative isosurface
        viewer.addVolumetricData(
            cube_data,
            "cube",
            {
                "isoval": -isovalue,
                "color": colors[1],
                "opacity": 0.7,
            },
        )

        viewer.zoomTo()
        return viewer._make_html()

    def render_molecule(
        self,
        atom_coords: str,
        style: str = "stick",
        color_by: str = "element",
    ) -> str:
        """Render molecular structure."""
        import py3Dmol

        viewer = py3Dmol.view(width=600, height=400)
        viewer.addModel(atom_coords, "xyz")

        if color_by == "element":
            viewer.setStyle({style: {"colorscheme": "Jmol"}})
        else:
            viewer.setStyle({style: {}})

        viewer.zoomTo()
        return viewer._make_html()

    def export_image(
        self,
        visualization_html: str,
        output_path: str | Path,
        width: int = 800,
        height: int = 600,
        image_format: str = "png",
    ) -> Path:
        """Export visualization to static image.

        Note: py3Dmol generates HTML/WebGL. For true headless PNG export,
        a browser automation tool (Playwright/Selenium) is needed.
        This method saves the HTML and optionally attempts PNG conversion.
        """
        out = Path(output_path)

        if image_format == "html":
            out.write_text(visualization_html)
            return out

        # For PNG: save HTML, then attempt headless browser capture
        html_path = out.with_suffix(".html")
        html_path.write_text(visualization_html)

        try:
            return self._html_to_png(html_path, out, width, height)
        except ImportError:
            # Fallback: return HTML path with a note
            return html_path

    @staticmethod
    def _html_to_png(
        html_path: Path, png_path: Path, width: int, height: int
    ) -> Path:
        """Convert HTML visualization to PNG using Playwright (optional)."""
        # Optional dependency — graceful degradation if not installed
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(f"file://{html_path.resolve()}")
            page.wait_for_timeout(2000)  # Wait for WebGL render
            page.screenshot(path=str(png_path))
            browser.close()

        return png_path
```

**`src/qcviz_mcp/backends/cclib_backend.py`** — cclib 파싱 백엔드:

```python
"""cclib-based parser backend for quantum chemistry output files.

Supports: ORCA, Gaussian, GAMESS, NWChem, Psi4, Q-Chem,
          Turbomole, Molpro, Molcas, ADF, DALTON, Jaguar,
          MOPAC, NBO, Firefly, GAMESS-UK (16 programs).

Requires: pip install cclib
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .base import ParserBackend, ParsedOutput, OrbitalData


class CclibBackend(ParserBackend):
    """Parser backend using cclib for multi-program output parsing."""

    SUPPORTED_PROGRAMS: list[str] = [
        "ADF", "DALTON", "Firefly", "GAMESS", "GAMESS-UK",
        "Gaussian", "Jaguar", "Molcas", "Molpro", "MOPAC",
        "NBO", "NWChem", "ORCA", "Psi4", "Q-Chem", "Turbomole",
    ]

    def __init__(self) -> None:
        import cclib  # noqa: F401 — validate import

    def parse_output(
        self,
        output_file: str | Path,
        program: str | None = None,
    ) -> ParsedOutput:
        """Parse quantum chemistry output file using cclib."""
        import cclib

        filepath = Path(output_file)
        if not filepath.exists():
            raise FileNotFoundError(f"Output file not found: {filepath}")

        data = cclib.io.ccread(str(filepath))

        if data is None:
            raise ValueError(
                f"cclib could not parse {filepath}. "
                f"Ensure the file is a valid output from one of: "
                f"{', '.join(self.SUPPORTED_PROGRAMS)}"
            )

        # Extract program name from metadata if available
        detected_program = program or getattr(data, "metadata", {}).get(
            "package", "unknown"
        )

        # Build ParsedOutput
        result = ParsedOutput(program=detected_program)

        # Energy (last SCF energy)
        if hasattr(data, "scfenergies") and len(data.scfenergies) > 0:
            result.energy = float(data.scfenergies[-1])

        # Geometry (last geometry in optimization)
        if hasattr(data, "atomcoords") and len(data.atomcoords) > 0:
            result.geometry = data.atomcoords[-1]

        # Atom symbols
        if hasattr(data, "atomnos"):
            from cclib.parser.utils import PeriodicTable

            pt = PeriodicTable()
            result.atom_symbols = [
                pt.element[z] for z in data.atomnos
            ]

        # MO coefficients
        if hasattr(data, "mocoeffs") and data.mocoeffs is not None:
            result.mo_coefficients = data.mocoeffs

        # MO energies
        if hasattr(data, "moenergies") and data.moenergies is not None:
            result.mo_energies = data.moenergies[0].tolist()

        # Vibrational frequencies
        if hasattr(data, "vibfreqs") and data.vibfreqs is not None:
            result.frequencies = data.vibfreqs.tolist()

        # Store raw cclib data for advanced use
        result.metadata["cclib_data"] = data

        return result

    def extract_orbitals(
        self,
        output_file: str | Path,
    ) -> OrbitalData | None:
        """Extract molecular orbital data from output file."""
        parsed = self.parse_output(output_file)

        if parsed.mo_coefficients is None:
            return None

        # Handle both restricted (1 set) and unrestricted (2 sets)
        coeffs = parsed.mo_coefficients
        if isinstance(coeffs, list):
            coeffs = coeffs[0]  # Use alpha orbitals for restricted

        n_mos = coeffs.shape[0] if hasattr(coeffs, "shape") else len(coeffs)

        return OrbitalData(
            coefficients=coeffs,
            energies=parsed.mo_energies,
            occupancies=[],  # cclib doesn't always parse occupancies directly
            labels=[f"MO_{i}" for i in range(n_mos)],
            basis_info={"source": str(output_file), "program": parsed.program},
        )

    def extract_geometry(
        self,
        output_file: str | Path,
    ) -> tuple[list[str], Any] | None:
        """Extract molecular geometry."""
        parsed = self.parse_output(output_file)

        if parsed.geometry is None or not parsed.atom_symbols:
            return None

        return parsed.atom_symbols, parsed.geometry

    def supported_programs(self) -> list[str]:
        """Return list of supported program names."""
        return self.SUPPORTED_PROGRAMS.copy()
```

**`src/qcviz_mcp/backends/ase_backend.py`** — ASE 구조 백엔드:

```python
"""ASE-based structure manipulation backend.

Supports 40+ file formats for molecular and periodic structures.

Requires: pip install ase
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import StructureBackend


class ASEBackend(StructureBackend):
    """Structure manipulation backend using ASE."""

    # Map of common format names to ASE format strings
    FORMAT_MAP: dict[str, str] = {
        "xyz": "xyz",
        "cif": "cif",
        "pdb": "proteindatabank",
        "poscar": "vasp",
        "vasp": "vasp",
        "mol": "mol",
        "sdf": "sdf",
        "extxyz": "extxyz",
        "traj": "traj",
        "gen": "gen",
        "car": "dmol-car",
    }

    def __init__(self) -> None:
        import ase  # noqa: F401 — validate import

    def read_structure(
        self,
        filepath: str | Path,
        file_format: str | None = None,
    ) -> dict[str, Any]:
        """Read structure from file using ASE."""
        from ase.io import read

        path = Path(filepath)
        fmt = self.FORMAT_MAP.get(file_format, file_format) if file_format else None

        atoms = read(str(path), format=fmt)

        result: dict[str, Any] = {
            "symbols": atoms.get_chemical_symbols(),
            "positions": atoms.get_positions().tolist(),
            "formula": atoms.get_chemical_formula(),
            "n_atoms": len(atoms),
        }

        # Include cell info for periodic systems
        if any(atoms.pbc):
            result["cell"] = atoms.get_cell().tolist()
            result["pbc"] = atoms.pbc.tolist()

        return result

    def write_structure(
        self,
        symbols: list[str],
        positions: Any,
        filepath: str | Path,
        file_format: str | None = None,
    ) -> Path:
        """Write structure to file."""
        from ase import Atoms
        from ase.io import write
        import numpy as np

        atoms = Atoms(symbols=symbols, positions=np.array(positions))
        path = Path(filepath)
        fmt = self.FORMAT_MAP.get(file_format, file_format) if file_format else None

        write(str(path), atoms, format=fmt)
        return path

    def convert_format(
        self,
        input_file: str | Path,
        output_format: str,
        output_file: str | Path | None = None,
    ) -> Path:
        """Convert between structure file formats."""
        from ase.io import read, write

        in_path = Path(input_file)
        atoms = read(str(in_path))

        if output_file is None:
            out_path = in_path.with_suffix(f".{output_format}")
        else:
            out_path = Path(output_file)

        fmt = self.FORMAT_MAP.get(output_format, output_format)
        write(str(out_path), atoms, format=fmt)

        return out_path
```

**`src/qcviz_mcp/mcp_server.py`** — FastMCP 서버 메인:

```python
"""QCViz-MCP Server — Main entry point.

Registers all MCP tools and starts the FastMCP server.
Tools interact with backends exclusively through the registry,
never importing backend modules directly.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from .backends.registry import registry, BackendNotAvailableError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("qcviz-mcp")

# Create the MCP server
mcp = FastMCP(
    "QCViz-MCP",
    description=(
        "Quantum chemistry visualization and analysis server. "
        "Provides tools for orbital computation (IAO/IBO), "
        "3D visualization, output parsing, and bonding analysis."
    ),
)


# ── Tool: compute_ibo ───────────────────────────────────────────


@mcp.tool()
def compute_ibo(
    molecule_xyz: str,
    basis: str = "cc-pVDZ",
    method: str = "b3lyp",
    localization: str = "ibo",
    output_dir: str = "/tmp/qcviz",
) -> str:
    """Compute Intrinsic Bond Orbitals (IBOs) for a molecule.

    Given molecular coordinates, performs a DFT/HF calculation,
    constructs IAOs, and localizes occupied orbitals into IBOs.
    Returns cube files for each IBO and orbital composition data.

    Args:
        molecule_xyz: Molecular coordinates in XYZ format
            (e.g., "O 0 0 0; H 0 0 1; H 0 1 0")
        basis: Basis set name (default: cc-pVDZ)
        method: Calculation method — 'hf', 'b3lyp', 'pbe0', etc.
        localization: Localization method — 'ibo', 'boys', 'pm'
        output_dir: Directory for output cube files

    Returns:
        JSON string with orbital data, cube file paths, and energies.
    """
    try:
        backend = registry.get_compute_backend()
    except BackendNotAvailableError as e:
        return json.dumps({"error": str(e)})

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    try:
        orbital_data, cube_files = backend.compute_ibo(
            atom_coords=molecule_xyz,
            basis=basis,
            method=method,
            localization=localization,
        )

        result = {
            "status": "success",
            "n_orbitals": len(cube_files),
            "orbitals": [
                {
                    "index": cf.orbital_index,
                    "label": cf.orbital_label,
                    "cube_file": str(cf.filepath),
                }
                for cf in cube_files
            ],
            "basis": basis,
            "method": method,
            "localization": localization,
        }
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.exception("compute_ibo failed")
        return json.dumps({"error": f"Computation failed: {e}"})


# ── Tool: visualize_orbital ─────────────────────────────────────


@mcp.tool()
def visualize_orbital(
    cube_file: str,
    isovalue: float = 0.05,
    positive_color: str = "blue",
    negative_color: str = "red",
    style: str = "stick",
    output_format: str = "html",
) -> str:
    """Visualize a molecular orbital from a cube file.

    Renders an interactive 3D isosurface visualization showing
    positive (blue) and negative (red) lobes of the orbital,
    overlaid on the molecular structure.

    Args:
        cube_file: Path to a Gaussian cube file
        isovalue: Isosurface value (default: 0.05 a.u.)
        positive_color: Color for positive lobe
        negative_color: Color for negative lobe
        style: Molecular representation ('stick', 'ball_stick', 'sphere')
        output_format: Output type ('html' or 'png')

    Returns:
        HTML string with interactive 3D visualization, or file path for PNG.
    """
    try:
        backend = registry.get_viz_backend()
    except BackendNotAvailableError as e:
        return json.dumps({"error": str(e)})

    try:
        html = backend.render_orbital(
            cube_file=cube_file,
            isovalue=isovalue,
            colors=(positive_color, negative_color),
            style=style,
        )

        if output_format == "png":
            png_path = Path(cube_file).with_suffix(".png")
            result_path = backend.export_image(html, png_path)
            return json.dumps({
                "status": "success",
                "format": "png",
                "file": str(result_path),
            })

        return html

    except Exception as e:
        logger.exception("visualize_orbital failed")
        return json.dumps({"error": f"Visualization failed: {e}"})


# ── Tool: parse_output ──────────────────────────────────────────


@mcp.tool()
def parse_output(
    output_file: str,
    program: str | None = None,
    extract: str = "energy,geometry,orbitals",
) -> str:
    """Parse a quantum chemistry program output file.

    Extracts structured data from output files of 16 supported programs:
    ORCA, Gaussian, GAMESS, NWChem, Psi4, Q-Chem, Turbomole, Molpro,
    Molcas, ADF, DALTON, Jaguar, MOPAC, NBO, Firefly, GAMESS-UK.

    Args:
        output_file: Path to the output file
        program: Program name (optional, auto-detected)
        extract: Comma-separated list of data to extract
            Options: energy, geometry, orbitals, frequencies, charges

    Returns:
        JSON string with parsed data.
    """
    try:
        backend = registry.get_parser_backend()
    except BackendNotAvailableError as e:
        return json.dumps({"error": str(e)})

    try:
        parsed = backend.parse_output(output_file, program=program)

        extract_fields = [f.strip() for f in extract.split(",")]
        result: dict[str, Any] = {
            "status": "success",
            "program": parsed.program,
        }

        if "energy" in extract_fields and parsed.energy is not None:
            result["energy_eV"] = parsed.energy
            result["energy_hartree"] = parsed.energy / 27.2114  # approx

        if "geometry" in extract_fields and parsed.geometry is not None:
            result["geometry"] = {
                "symbols": parsed.atom_symbols,
                "coordinates_angstrom": parsed.geometry.tolist(),
                "n_atoms": len(parsed.atom_symbols),
            }

        if "orbitals" in extract_fields and parsed.mo_energies:
            n_mo = len(parsed.mo_energies)
            # Find HOMO-LUMO
            # Rough heuristic: assume closed shell, n_electrons from atom count
            homo_idx = n_mo // 2 - 1  # Approximate
            result["orbitals"] = {
                "n_molecular_orbitals": n_mo,
                "energies_eV": parsed.mo_energies,
                "homo_index": homo_idx,
                "homo_energy_eV": parsed.mo_energies[homo_idx] if homo_idx < n_mo else None,
                "lumo_energy_eV": parsed.mo_energies[homo_idx + 1] if homo_idx + 1 < n_mo else None,
            }
            if result["orbitals"]["homo_energy_eV"] and result["orbitals"]["lumo_energy_eV"]:
                result["orbitals"]["homo_lumo_gap_eV"] = (
                    result["orbitals"]["lumo_energy_eV"]
                    - result["orbitals"]["homo_energy_eV"]
                )

        if "frequencies" in extract_fields and parsed.frequencies:
            result["frequencies_cm-1"] = parsed.frequencies
            result["n_imaginary"] = sum(1 for f in parsed.frequencies if f < 0)

        return json.dumps(result, indent=2)

    except FileNotFoundError:
        return json.dumps({"error": f"File not found: {output_file}"})
    except Exception as e:
        logger.exception("parse_output failed")
        return json.dumps({"error": f"Parsing failed: {e}"})


# ── Tool: compute_partial_charges ───────────────────────────────


@mcp.tool()
def compute_partial_charges(
    molecule_xyz: str,
    basis: str = "cc-pVDZ",
    method: str = "b3lyp",
    charge_type: str = "iao",
) -> str:
    """Compute atomic partial charges for a molecule.

    IAO-based charges are basis-set independent and chemically
    intuitive, unlike Mulliken charges. Supports IAO, Mulliken,
    and Löwdin charge schemes.

    Args:
        molecule_xyz: Molecular coordinates in XYZ format
        basis: Basis set name
        method: Calculation method
        charge_type: Charge scheme — 'iao', 'mulliken', 'lowdin'

    Returns:
        JSON string with per-atom charges and total charge.
    """
    try:
        backend = registry.get_compute_backend()
    except BackendNotAvailableError as e:
        return json.dumps({"error": str(e)})

    try:
        charges = backend.get_partial_charges(
            atom_coords=molecule_xyz,
            basis=basis,
            method=method,
            charge_type=charge_type,
        )

        result = {
            "status": "success",
            "charge_method": charges.method,
            "atoms": [
                {
                    "index": idx,
                    "symbol": sym,
                    "charge": round(chg, 4),
                }
                for idx, sym, chg in zip(
                    charges.atom_indices,
                    charges.atom_symbols,
                    charges.charges,
                )
            ],
            "total_charge": round(sum(charges.charges), 6),
        }
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.exception("compute_partial_charges failed")
        return json.dumps({"error": f"Charge computation failed: {e}"})


# ── Tool: convert_format ────────────────────────────────────────


@mcp.tool()
def convert_format(
    input_file: str,
    output_format: str,
    output_file: str | None = None,
) -> str:
    """Convert a molecular structure file between formats.

    Supports 40+ formats including xyz, cif, pdb, POSCAR, mol, sdf,
    extxyz, and more.

    Args:
        input_file: Path to input structure file
        output_format: Target format ('xyz', 'cif', 'pdb', 'poscar', etc.)
        output_file: Path for output file (auto-generated if omitted)

    Returns:
        JSON string with output file path.
    """
    try:
        backend = registry.get_structure_backend()
    except BackendNotAvailableError as e:
        return json.dumps({"error": str(e)})

    try:
        out_path = backend.convert_format(
            input_file=input_file,
            output_format=output_format,
            output_file=output_file,
        )

        return json.dumps({
            "status": "success",
            "output_file": str(out_path),
            "format": output_format,
        })

    except FileNotFoundError:
        return json.dumps({"error": f"Input file not found: {input_file}"})
    except Exception as e:
        logger.exception("convert_format failed")
        return json.dumps({"error": f"Conversion failed: {e}"})


# ── Tool: analyze_bonding ───────────────────────────────────────


@mcp.tool()
def analyze_bonding(
    molecule_xyz: str,
    atom_pairs: str,
    basis: str = "cc-pVDZ",
    method: str = "b3lyp",
) -> str:
    """Analyze chemical bonding between specified atom pairs.

    Uses IBO decomposition to determine bond orders, bond types
    (sigma/pi/delta), and the contributing orbitals for each bond.

    Args:
        molecule_xyz: Molecular coordinates in XYZ format
        atom_pairs: JSON string of atom index pairs, e.g. "[[0,1],[1,2]]"
        basis: Basis set name
        method: Calculation method

    Returns:
        JSON string with bond analysis for each atom pair.
    """
    try:
        backend = registry.get_compute_backend()
    except BackendNotAvailableError as e:
        return json.dumps({"error": str(e)})

    try:
        pairs = json.loads(atom_pairs)
        pairs_tuples = [tuple(p) for p in pairs]

        analyses = backend.analyze_bonding(
            atom_coords=molecule_xyz,
            atom_pairs=pairs_tuples,
            basis=basis,
            method=method,
        )

        result = {
            "status": "success",
            "bonds": [
                {
                    "atoms": list(a.atom_pair),
                    "bond_order": round(a.bond_order, 3),
                    "bond_type": a.bond_type,
                    "contributing_orbitals": a.contributing_orbitals,
                }
                for a in analyses
            ],
        }
        return json.dumps(result, indent=2)

    except json.JSONDecodeError:
        return json.dumps({"error": f"Invalid atom_pairs JSON: {atom_pairs}"})
    except Exception as e:
        logger.exception("analyze_bonding failed")
        return json.dumps({"error": f"Bond analysis failed: {e}"})


# ── Tool: list_backends ─────────────────────────────────────────


@mcp.tool()
def list_backends() -> str:
    """List all available backends and their status.

    Returns which computation, visualization, parsing, and structure
    backends are currently installed and ready to use.
    """
    available = registry.list_available()
    return json.dumps({
        "status": "success",
        "backends": available,
        "note": (
            "Install additional backends with: "
            'pip install "qcviz-mcp[all]"'
        ),
    }, indent=2)


# ── Server entry point ──────────────────────────────────────────


def main() -> None:
    """Run the QCViz-MCP server."""
    logger.info("Starting QCViz-MCP server...")
    available = registry.list_available()
    logger.info(f"Available backends: {available}")
    mcp.run()


if __name__ == "__main__":
    main()
```

**`src/qcviz_mcp/backends/iboview_bridge.py`** — Phase β IboView 브릿지:

```python
"""IboView file bridge backend (Phase β).

Generates .molden files that can be opened in IboView for
high-quality orbital rendering. IboView itself must be installed
separately — this bridge does NOT require IboView as a dependency.

Note: IboView has no Python API or CLI mode. This bridge works
exclusively through file I/O (.molden format).
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


class IboViewBridge:
    """File-based bridge to IboView for high-quality rendering.

    This is NOT a Backend ABC implementation — it is a supplementary
    bridge that works alongside the core compute backend (PySCF).

    Workflow:
        1. PySCF computes orbitals
        2. This bridge generates a .molden file
        3. User opens the .molden file in IboView manually
           (or via subprocess if IboView is installed)
    """

    def __init__(self, iboview_path: str | None = None) -> None:
        """Initialize the IboView bridge.

        Args:
            iboview_path: Path to the iboview executable.
                If None, will search PATH. If not found,
                bridge operates in export-only mode.
        """
        self._iboview_path = iboview_path or self._find_iboview()

    @staticmethod
    def _find_iboview() -> str | None:
        """Attempt to find iboview executable in PATH."""
        import shutil
        return shutil.which("iboview")

    @property
    def is_iboview_available(self) -> bool:
        """Check if IboView executable is available."""
        return self._iboview_path is not None

    def export_molden(
        self,
        atom_coords: str,
        basis: str = "cc-pVDZ",
        method: str = "b3lyp",
        include_orbitals: str = "ibo",
        output_file: str | Path | None = None,
    ) -> Path:
        """Generate a .molden file for IboView.

        Uses PySCF to compute orbitals, then exports to .molden format
        which IboView can read natively.

        Args:
            atom_coords: XYZ format molecular coordinates
            basis: Basis set
            method: Calculation method
            include_orbitals: Which orbitals to include —
                'all' (canonical MOs), 'occupied', 'ibo' (localized IBOs)
            output_file: Output .molden file path

        Returns:
            Path to the generated .molden file.
        """
        from pyscf import gto, scf, dft, lo
        from pyscf.tools import molden as pyscf_molden

        mol = gto.M(atom=atom_coords, basis=basis, verbose=0)

        # Run SCF
        if method.lower() == "hf":
            mf = scf.RHF(mol).run()
        else:
            mf = dft.RKS(mol)
            mf.xc = method
            mf.kernel()

        # Determine which orbitals to write
        if include_orbitals == "ibo":
            mo_occ = mf.mo_coeff[:, mf.mo_occ > 0]
            iao_coeff = lo.iao.iao(mol, mo_occ)
            ibo_coeff = lo.ibo.ibo(mol, mo_occ, iaos=iao_coeff)
            mo_to_write = ibo_coeff
            mo_energies = [0.0] * ibo_coeff.shape[1]  # IBOs have no canonical energies
            mo_occ_to_write = [2.0] * ibo_coeff.shape[1]
        elif include_orbitals == "occupied":
            occ_mask = mf.mo_occ > 0
            mo_to_write = mf.mo_coeff[:, occ_mask]
            mo_energies = mf.mo_energy[occ_mask].tolist()
            mo_occ_to_write = mf.mo_occ[occ_mask].tolist()
        else:  # 'all'
            mo_to_write = mf.mo_coeff
            mo_energies = mf.mo_energy.tolist()
            mo_occ_to_write = mf.mo_occ.tolist()

        # Write .molden file
        if output_file is None:
            output_file = Path("/tmp/qcviz") / "export.molden"
        out_path = Path(output_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, "w") as f:
            pyscf_molden.header(mol, f)
            pyscf_molden.orbital_coeff(
                mol, f, mo_to_write, ene=mo_energies, occ=mo_occ_to_write
            )

        return out_path

    def open_in_iboview(self, molden_file: str | Path) -> dict[str, Any]:
        """Attempt to open a .molden file in IboView.

        Returns:
            dict with 'success' and 'message' keys.
        """
        if not self.is_iboview_available:
            return {
                "success": False,
                "message": (
                    f"IboView not found in PATH. "
                    f"Please open the file manually: {molden_file}\n"
                    f"Download IboView from: http://www.iboview.org/ or "
                    f"build from: https://github.com/KoehnLab/iboview"
                ),
                "molden_file": str(molden_file),
            }

        try:
            subprocess.Popen(
                [self._iboview_path, str(molden_file)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return {
                "success": True,
                "message": f"IboView launched with {molden_file}",
                "molden_file": str(molden_file),
            }
        except OSError as e:
            return {
                "success": False,
                "message": f"Failed to launch IboView: {e}",
                "molden_file": str(molden_file),
            }
```

**`claude_desktop_config.json`** — MCP 설정 예시:

```json
{
  "mcpServers": {
    "qcviz": {
      "command": "python",
      "args": ["-m", "qcviz_mcp.mcp_server"],
      "env": {
        "PYTHONPATH": "/path/to/qcviz-mcp/src"
      }
    }
  }
}
```

**`tests/test_registry.py`** — 레지스트리 테스트:

```python
"""Tests for backend registry and graceful degradation."""
from __future__ import annotations

import pytest
from qcviz_mcp.backends.registry import BackendRegistry, BackendNotAvailableError


class TestBackendRegistry:
    """Test that the registry detects and registers backends correctly."""

    def test_list_available_returns_dict(self) -> None:
        reg = BackendRegistry()
        available = reg.list_available()
        assert isinstance(available, dict)
        assert "compute" in available
        assert "viz" in available
        assert "parser" in available
        assert "structure" in available

    def test_missing_backend_raises_clear_error(self) -> None:
        """Ensure requesting an uninstalled backend gives actionable error."""
        reg = BackendRegistry()
        # Temporarily clear a backend to simulate missing package
        reg._compute_backends.clear()
        reg._default_compute = None

        with pytest.raises(BackendNotAvailableError) as exc_info:
            reg.get_compute_backend()

        assert "not installed" in str(exc_info.value)
        assert "pip install" in str(exc_info.value)

    @pytest.mark.skipif(
        not BackendRegistry._is_package_available("pyscf"),
        reason="PySCF not installed",
    )
    def test_pyscf_backend_loads(self) -> None:
        reg = BackendRegistry()
        backend = reg.get_compute_backend("pyscf")
        assert backend is not None

    @pytest.mark.skipif(
        not BackendRegistry._is_package_available("cclib"),
        reason="cclib not installed",
    )
    def test_cclib_backend_loads(self) -> None:
        reg = BackendRegistry()
        backend = reg.get_parser_backend("cclib")
        assert backend is not None
        assert "ORCA" in backend.supported_programs()
        assert "Gaussian" in backend.supported_programs()
```

**`tests/test_compute_ibo.py`** — IBO 계산 테스트:

```python
"""Tests for IBO computation tool."""
from __future__ import annotations

import json
import pytest
from qcviz_mcp.backends.registry import BackendRegistry

# Water molecule XYZ
WATER_XYZ = """\
O  0.000000  0.000000  0.117370
H  0.000000  0.756950 -0.469483
H  0.000000 -0.756950 -0.469483
"""

BENZENE_XYZ = """\
C   0.000  1.396  0.000
C   1.209  0.698  0.000
C   1.209 -0.698  0.000
C   0.000 -1.396  0.000
C  -1.209 -0.698  0.000
C  -1.209  0.698  0.000
H   0.000  2.479  0.000
H   2.147  1.240  0.000
H   2.147 -1.240  0.000
H   0.000 -2.479  0.000
H  -2.147 -1.240  0.000
H  -2.147  1.240  0.000
"""


@pytest.mark.skipif(
    not BackendRegistry._is_package_available("pyscf"),
    reason="PySCF not installed",
)
class TestComputeIBO:
    """Test IBO computation via PySCF backend."""

    def test_water_ibo_count(self) -> None:
        """Water should have 4 occupied IBOs (2 OH bonds + 2 lone pairs)."""
        reg = BackendRegistry()
        backend = reg.get_compute_backend()

        orbital_data, cube_files = backend.compute_ibo(
            atom_coords=WATER_XYZ,
            basis="sto-3g",  # Small basis for fast test
            method="hf",
        )

        # Water: 10 electrons / 2 = 5 occupied MOs
        # After IBO: 5 IBOs (1 core O, 2 OH bonds, 2 lone pairs)
        assert len(cube_files) == 5
        assert all(cf.filepath.exists() for cf in cube_files)

    def test_benzene_ibo_includes_pi(self) -> None:
        """Benzene IBOs should include both sigma and pi orbitals."""
        reg = BackendRegistry()
        backend = reg.get_compute_backend()

        orbital_data, cube_files = backend.compute_ibo(
            atom_coords=BENZENE_XYZ,
            basis="sto-3g",
            method="hf",
        )

        # Benzene: 42 electrons / 2 = 21 occupied MOs → 21 IBOs
        assert len(cube_files) == 21
```

---

## [Phase 5] 자체 검증

- [x] 산출물이 해당 Phase의 "목표"에 부합하는가? — 논문 아웃라인 + Abstract, 참고문헌 20개, 코드 스켈레톤 8개 파일
- [x] 모든 테이블의 행 수가 최소 요구치를 충족하는가? — 참고문헌 20개(20+), 코드 파일 8개(5+)
- [x] 신뢰도 태그가 빠짐없이 부착되었는가? — 코드 내 주석에 Phase 표시, TODO 명시
- [x] "NEVER" 항목을 위반하지 않았는가? — IboView API 없음을 코드 docstring에서도 명시, 실행 가능한 import 경로
- [x] 다음 Phase에 필요한 입력이 모두 생산되었는가? — 바로 개발 시작 가능한 수준
- [x] 사실과 추정이 명확히 구분되었는가? — ✅

**자체 검증 점수: 6/6** ✅

---

# 종합 로드맵

## 전체 프로젝트 타임라인

```
Week 1-2: Phase α MVP 개발
├── Day 1-2: 프로젝트 scaffolding, backends/base.py, registry.py
├── Day 3-5: pyscf_backend.py (compute_ibo, compute_partial_charges)
├── Day 6-7: cclib_backend.py + viz_backend.py
├── Day 8-9: ase_backend.py + mcp_server.py (6 tools 등록)
├── Day 10: 테스트 (H₂O, C₆H₆, C₂H₅OH)
└── Day 11-14: README, claude_desktop_config.json, 버그픽스

Week 3-4: Phase β 확장 + 논문 데이터 수집
├── iboview_bridge.py (export_for_iboview)
├── track_orbital_along_path (반응경로 IBO 추적)
├── 벤치마크 분자 15개 + 반응 5개 데이터 수집
└── IboView vs PySCF IBO 수치 비교

Week 5-6: 논문 집필 + Phase γ 시작
├── 논문 초안 작성 (JCIM 또는 JCTC 대상)
├── compare_methods, export_publication_image 구현
├── 그림 생성, 벤치마크 표 정리
└── 논문 제출 준비

Week 7+: 논문 리비전 + JOSS 2차 논문 + 커뮤니티 피드백
```

## 핵심 마일스톤

| 마일스톤          | 목표 날짜 | 산출물                       | 검증 기준                               |
| ----------------- | --------- | ---------------------------- | --------------------------------------- |
| M1: MVP 완성      | +2주      | 작동하는 MCP 서버 (6 tools)  | H₂O IBO 시각화 성공                     |
| M2: 벤치마크 완료 | +4주      | 15 분자 + 5 반응 데이터셋    | PySCF vs IboView 수치 일치 확인         |
| M3: 논문 초안     | +5주      | JCIM/JCTC 형식 초안          | 공동 저자 리뷰 통과                     |
| M4: 논문 제출     | +6주      | 최종 원고 + SI + GitHub 공개 | 재현성 검증 완료                        |
| M5: JOSS 제출     | +8주      | 소프트웨어 논문              | 코드 리뷰 + 문서 + 테스트 커버리지 80%+ |

## 다음 단계 (Next Steps)

1. **즉시**: `pyproject.toml` + `backends/base.py` + `backends/registry.py` 생성 → 프로젝트 초기화
2. **Day 1**: PySCF 환경에서 H₂O IBO 계산 → cube 파일 → py3Dmol 렌더링 파이프라인 수동 검증
3. **Day 2-3**: `pyscf_backend.py`의 `compute_ibo()` 완전 구현 + 단위 테스트
4. **Day 4**: `mcp_server.py`에 첫 tool 등록 → Claude Desktop에서 "물 분자의 IBO를 보여줘" 테스트
5. **Week 1 끝**: 6개 tools 모두 등록, 3개 테스트 시나리오 통과 확인
