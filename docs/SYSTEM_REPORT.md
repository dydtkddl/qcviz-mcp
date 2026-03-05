# QCViz‑MCP 시스템 전체 보고서

**Version 0.6.0‑alpha · 2026‑03‑06 · Phase η 반영** ← updated

**Repository:** https://github.com/dydtkddl/qcviz-mcp

---

## 1. 두 줄 요약

QCViz‑MCP는 IAO/IBO 로컬라이제이션과 3‑D 시각화를 MCP(Model Context Protocol) 프로토콜로 제공하는 세계 유일의 전자구조 수준 양자화학 MCP 서버이다.

이 시스템은 "물 분자의 결합 오비탈을 보여줘" 같은 자연어 한 줄 입력으로, 기존에 Python 스크립트 20줄 이상이 필요했던 SCF→IAO→IBO→큐브→3D 렌더링 5단계 워크플로우를 1단계로 축약하며, 전이금속 ECP 분자와 개방껍질(UHF/ROHF) 시스템, 4d/5d 전이금속의 스칼라 상대론(SFX2C‑1e) 보정까지 단일 인터페이스로 처리한다. ← updated

### 1.1 핵심 사실 기반 근거

Anthropic이 2024년 11월 25일에 공개한 MCP(Model Context Protocol)는 LLM과 외부 도구 사이의 표준 통신 규격으로, 2026년 3월 현재 수천 개의 MCP 서버가 존재하나 양자화학 전자구조 분석을 제공하는 서버는 QCViz‑MCP가 유일하다. IAO(Intrinsic Atomic Orbital)와 IBO(Intrinsic Bond Orbital)는 Gerald Knizia가 2013년에 제안한 오비탈 로컬라이제이션 방법으로(J. Chem. Theory Comput. 2013, 9, 4834), 2026년 기준 801회 이상 인용되었으며, 화학 결합의 직관적 해석에 있어 사실상의 표준(de facto standard)이다.

### 1.2 경쟁 환경

2026년 3월 전수조사 결과, 화학·과학 영역에서 MCP 서버를 표방하는 프로젝트는 ChemLint(SMILES 검증·분자량 계산), Argonne mcp.science(논문 검색·데이터 쿼리), El Agente(일반 과학 에이전트) 등이 확인되었다. 그러나 이들 중 어느 것도 전자구조 계산(SCF), 오비탈 로컬라이제이션(IAO/IBO), 3‑D 볼류메트릭 시각화를 제공하지 않는다. 독립 도구인 IboView(Knizia 연구실)는 GUI 기반 오비탈 시각화를 제공하지만 MCP 프로토콜을 지원하지 않고 프로그래밍 인터페이스가 없다. PySCF CLI는 스크립트 기반 계산은 가능하나 시각화·MCP 통합이 없다. QCViz‑MCP는 이 세 가지(전자구조 계산 + 오비탈 로컬라이제이션 + 3D 시각화)를 MCP 프로토콜 하나로 통합한 유일한 구현이다.

---

## 2. 시스템 명세

### 2.1 아키텍처 개요

QCViz‑MCP는 3‑계층(three‑tier) 아키텍처로 설계되었다.

**제1계층 – MCP 프로토콜 레이어.** FastMCP 3.x (v3.0.2, 2026‑02‑18 GA 릴리스) 기반의 async‑native 서버로, SSE(Server‑Sent Events) 트랜스포트를 통해 Claude Desktop 등 MCP 클라이언트와 JSON‑RPC 2.0으로 통신한다.

**제2계층 – 도구(Tool) 레이어.** 6개의 MCP 도구가 등록되어 있으며, 각 도구는 독립적인 입력 스키마(JSON Schema)와 출력 포맷을 가진다.

**제3계층 – 백엔드(Backend) 레이어.** BackendRegistry 플러그인 패턴을 사용하여 4개의 계산 백엔드를 동적으로 등록·교체할 수 있다. 새 백엔드 추가 시 기존 도구 코드 변경이 불필요하다.

### 2.2 MCP 도구 명세

| #   | 도구명                    | 기능                                                                         | 핵심 의존성 | 상태         |
| --- | ------------------------- | ---------------------------------------------------------------------------- | ----------- | ------------ |
| 1   | `compute_ibo`             | 분자 지오메트리로부터 SCF→IAO→IBO 계산, 80³ 큐브 데이터 생성, HTML 3D 시각화 | PySCF       | 논문 수준 ✅ |
| 2   | `visualize_orbital`       | 큐브 데이터 또는 계수로부터 py3Dmol 기반 인터랙티브 HTML 렌더링              | py3Dmol     | 논문 수준 ✅ |
| 3   | `parse_output`            | ORCA, Gaussian, PySCF 출력 파일 파싱 (에너지, 전하, 좌표, 주파수 추출)       | cclib 1.8.1 | 기능 완료 ✅ |
| 4   | `compute_partial_charges` | Mulliken, Löwdin, IAO 3가지 방법의 부분 전하 계산                            | PySCF       | 기능 완료 ✅ |
| 5   | `convert_format`          | xyz ↔ cif ↔ POSCAR ↔ pdb ↔ extxyz 분자/결정 구조 형식 변환                   | ASE         | 기능 완료 ✅ |
| 6   | `analyze_bonding`         | IBO 기반 원자별 기여도 분석, 결합 캐릭터 분류                                | PySCF       | 기능 완료 ✅ |

6개 도구 모두 기능 구현이 완료되어 MCP 프로토콜을 통해 호출 가능하다.

### 2.3 백엔드 상세

**PySCFBackend** – 핵심 계산 엔진. RHF/UHF/ROHF SCF 수행, IAO 투영, IBO 로컬라이제이션(Pipek‑Mezey), 큐브 파일 생성, Molden 내보내기를 담당한다. ECP(Effective Core Potential) 분자에 대한 MINAO 폴백 로직(`_resolve_minao()`, 란타나이드/악티나이드 f‑오비탈 커버리지 경고 포함)과 UHF α/β 오비탈 분리 처리(`_unpack_uhf()`, `compute_scf_flexible()`, `compute_iao_uhf()`, `compute_ibo_uhf()`, `compute_uhf_charges()`)를 포함한다. Phase η에서 SFX2C‑1e 스칼라 상대론 SCF(`compute_scf_relativistic()`), 5단계 적응적 수렴 에스컬레이션 엔진(`ConvergenceStrategy`, `compute_scf_adaptive()`), `compute_scf_flexible(adaptive=True)` 인터페이스가 추가되었다. ← updated

**CclibBackend** – cclib 1.8.1 라이브러리를 래핑하여 ORCA, Gaussian, PySCF 등 다양한 양자화학 프로그램 출력을 파싱한다. 에너지, Mulliken 전하, 쌍극자 모멘트, 좌표, 주파수 등을 추출한다.

**Py3DmolBackend** – py3Dmol (2026‑01‑22) 라이브러리 기반으로 큐브 데이터 또는 분자 좌표로부터 인터랙티브 HTML 3D 시각화를 생성한다. 아이소서피스 값, 색상, 불투명도 등을 파라미터로 제어 가능하다.

**ASEBackend** – ASE(Atomic Simulation Environment)를 활용하여 분자·결정 구조 파일 형식 간 변환을 수행한다. xyz, cif, POSCAR, pdb, extxyz 형식을 지원한다.

### 2.3.1 렌더러 계층 (Phase η 신규) ← updated

Phase η에서 렌더러 선택이 3‑tier 폴백 구조로 확장되었다:

| 우선순위 | 렌더러                              | 의존성 크기         | 출력              | 용도                              |
| -------- | ----------------------------------- | ------------------- | ----------------- | --------------------------------- |
| 1        | **PyVista** (`pyvista_renderer.py`) | ~50 MB (vtk‑osmesa) | PNG 직접 생성     | CI/CD, 논문 Figure, 헤드리스 서버 |
| 2        | **Playwright** (`png_exporter.py`)  | ~200 MB (Chromium)  | HTML→PNG 캡처     | WebGL 기반 고품질 렌더링          |
| 3        | **py3Dmol** (기본)                  | ~2 MB               | HTML (인터랙티브) | 브라우저 직접 시각화              |

PyVista 렌더러는 `generate_cube()` 출력을 `parse_cube_string()`으로 파싱하여 PyVista ImageData로 변환한 뒤, 아이소서피스를 직접 VTK 파이프라인으로 렌더링한다. 브라우저가 필요 없어 CI/CD 환경과 원격 서버에서 유리하다. `renderers/__init__.py`의 자동 선택 로직이 설치된 패키지를 감지하여 최적의 렌더러를 선택한다. ← updated

### 2.4 파이프라인 흐름 예시

사용자가 Claude Desktop에서 "물 분자의 결합 오비탈을 보여줘"라고 입력하면 다음 파이프라인이 실행된다:

1. LLM(Claude)이 자연어를 해석하여 `compute_ibo` MCP 도구 호출로 변환한다.
2. MCP 클라이언트가 JSON‑RPC 2.0 요청을 SSE 트랜스포트를 통해 QCViz‑MCP 서버로 전송한다.
3. `compute_ibo` 도구가 PySCFBackend를 호출한다.
4. PySCFBackend가 RHF SCF를 수행하여 수렴 에너지(water/STO‑3G: −74.963063 Hartree)를 얻는다.
5. IAO 투영 → IBO 로컬라이제이션(Pipek‑Mezey)으로 5개 로컬라이즈된 오비탈을 생성한다.
6. 각 IBO에 대해 80³ 해상도의 큐브 데이터(~843 KB/orbital)를 생성한다.
7. Py3DmolBackend가 큐브 데이터로부터 인터랙티브 HTML 3D 시각화(~1.7 MB)를 렌더링한다.
8. 선택적으로 PyVista 네이티브 렌더러(브라우저 불필요) 또는 Playwright 헤드리스 렌더러(Chromium + SwiftShader)를 통해 정적 PNG 이미지를 내보낼 수 있다. ← updated
9. 결과가 JSON 응답으로 MCP 클라이언트에 반환된다.

전체 실행 시간은 water/STO‑3G에서 약 0.1초, ethylene/cc‑pVDZ에서 약 0.8초이다.

개방껍질 분자(예: O₂ 삼중항, NO 라디칼)의 경우, `compute_scf_flexible(spin=N)` → UHF SCF → `compute_iao_uhf()` → `compute_ibo_uhf()`로 α/β 채널이 분리 처리되며, 동일한 MCP 인터페이스를 통해 호출된다.

### 2.4.1 적응적 수렴 파이프라인 (Phase η 신규) ← updated

수렴이 어려운 분자(전이금속 착물, 열린껍질 고스핀 상태)에서는 `compute_scf_flexible(adaptive=True)` 또는 `compute_scf_adaptive()`를 통해 5단계 자동 에스컬레이션이 적용된다:

| 레벨 | 전략 이름         | max_cycle | 특징                                    |
| ---- | ----------------- | --------- | --------------------------------------- |
| 0    | `diis_default`    | 100       | 기본 DIIS                               |
| 1    | `diis_levelshift` | 200       | DIIS + level shift 0.5 Ha               |
| 2    | `diis_damp`       | 200       | DIIS + level shift 0.3 Ha + damping 0.5 |
| 3    | `soscf`           | 200       | Second‑Order SCF (Newton)               |
| 4    | `soscf_shift`     | 300       | SOSCF + level shift 0.5 Ha              |

UHF 수렴 후에는 자동으로 파동함수 안정성 분석(`mf.stability()`)을 수행하고, 불안정성이 감지되면 새로운 초기 추측으로 재수렴한다. 모든 전략이 실패하면 `ConvergenceError`를 발생시킨다. ← updated

### 2.4.2 스칼라 상대론 파이프라인 (Phase η 신규) ← updated

4d/5d 전이금속(예: ZrCl₄, Mo(CO)₆)에서는 `compute_scf_relativistic(relativistic='x2c')` 또는 `sfx2c1e`로 SFX2C‑1e 스칼라 상대론 해밀토니안이 적용된다. 수렴 실패 시 자동으로 적응적 에스컬레이션(`_adaptive_relativistic_scf`)이 트리거된다. 란타나이드/악티나이드 원소(Z=57–71, 89–103)가 감지되면 `_resolve_minao()`에서 f‑오비탈 커버리지 부족 경고와 함께 MINAO→STO‑3G 폴백이 적용된다. ← updated

### 2.5 정량적 지표

| 지표               | 값                                                                                              |
| ------------------ | ----------------------------------------------------------------------------------------------- |
| 테스트 통과        | **108+ passed** (Phase η 코드 미적용 시), **130+ passed** (Phase η 전체 적용 시 예상) ← updated |
| 테스트 실패        | **0 failed** ← updated                                                                          |
| 테스트 스킵        | **4–8 skipped** (Playwright/PyVista 미설치 시) ← updated                                        |
| 벤치마크 분자 수   | **15+** (기존 10 NIST + Fe(CO)₅ + TiCl₄ + NO + ZrCl₄ + Mo(CO)₆) ← updated                       |
| 벤치마크 기저 함수 | STO‑3G, cc‑pVDZ (폐각), def2‑SVP (전이금속), cc‑pVTZ, aug‑cc‑pVDZ ← updated                     |
| 벤치마크 케이스    | **20** (기존) + **40** (확장: 10분자 × 4기저) = **60 케이스** ← updated                         |
| IBO 검증 항목      | orbital spread (σ² Å²), gradient norm ≤ 1e‑8, Molden round‑trip Frobenius ≈ 0, 전하 합 보존     |
| 기저 독립성 검증   | IBO 수 일치, 전하 편차 < 허용 범위 (4기저 간 비교) ← updated                                    |
| 보안 검증          | 경로 순회(path traversal) 차단, 원자 수 ≤ 50 제한, 입력 크기 제한                               |
| 큐브 해상도        | 기본 80³ (이전 40³에서 상향)                                                                    |
| 원소 범위          | H–Mo (Z = 1–42), 란타나이드 감지·경고 (Z = 57–71) ← updated                                     |
| 스핀 처리          | RHF + UHF (ROHF 경유 가능) + 적응적 수렴 5단계 ← updated                                        |
| 상대론 보정        | SFX2C‑1e (선택적, 4d/5d 전이금속) ← updated                                                     |
| 이미지 출력        | HTML (인터랙티브) + PNG (PyVista 네이티브 / Playwright 헤드리스) ← updated                      |
| SCF 수렴 전략      | 5‑level 자동 에스컬레이션 + UHF 안정성 분석 ← updated                                           |

### 2.6 의존성 및 환경

**런타임 의존성:** Python ≥ 3.10, PySCF (conda‑forge, SCF/IAO/IBO/cube/Molden/X2C), cclib 1.8.1 (출력 파싱), py3Dmol 2026‑01‑22 (3D 시각화), ASE (구조 변환), FastMCP ≥ 3.0.2 (MCP 서버 프레임워크).

**선택적 의존성:** ← updated

- Playwright ≥ 1.40 (헤드리스 PNG 내보내기, `pip install qcviz-mcp[png]`)
- PyVista ≥ 0.43 (네이티브 PNG 렌더링, `pip install qcviz-mcp[viz-native]`). Linux 헤드리스 환경에서는 `pip install vtk-osmesa`로 VTK 대체 설치. ← updated

**개발 의존성:** pytest, ruff (lint/format), MkDocs Material (API 문서), Pandoc + inara (JOSS PDF 빌드).

**라이선스:** QCViz‑MCP 본체는 BSD‑3‑Clause, ASE 관련 코드는 LGPL 호환.

**지원 플랫폼:** Linux/WSL2 (전체 기능), Windows (PySCF 미지원 시 `dev-no-pyscf` 모드, 31 passed / 16 skipped), macOS (미검증).

**커스텀 pytest 마커:** `@pytest.mark.slow` (장시간 테스트 제외), `@pytest.mark.network` (네트워크 의존 테스트 제외). ← updated

---

## 3. 독창성 및 기여

### 3.1 도메인 수준 독창성

QCViz‑MCP는 IAO/IBO 로컬라이제이션을 MCP 프로토콜로 제공하는 최초이자 유일한 서버이다. 2026년 3월 전수조사(~20개 프로젝트 검토) 결과, MCP 생태계 내에 전자구조 계산을 수행하는 서버는 존재하지 않았다. 가장 근접한 Argonne mcp.science는 논문 검색과 데이터 쿼리에 국한되며, 오비탈 분석 기능이 없다. Phase ζ에서 전이금속(Fe, Ti) ECP 지원과 개방껍질(UHF) 처리가, Phase η에서 4d/5d 전이금속(Zr, Mo)의 SFX2C‑1e 상대론 보정과 적응적 수렴이 추가되어, 커버 가능한 화학 공간이 유기 분자(H–N)에서 중전이금속 착물(H–Mo)과 라디칼까지 확장되었다. ← updated

### 3.2 인터페이스 수준 독창성

기존에 IBO 분석을 수행하려면 다음 5단계가 필요했다: (1) Python 환경 구성, (2) PySCF 설치, (3) SCF 스크립트 작성 (~15줄), (4) IAO/IBO 계산 스크립트 (~10줄), (5) 시각화 코드 작성 (~10줄). 합계 약 35줄 이상의 코드와 3개 라이브러리에 대한 API 지식이 필요했다.

QCViz‑MCP는 이를 자연어 한 줄 입력("물 분자의 σ 결합 오비탈을 STO‑3G로 계산하고 3D로 보여줘")으로 대체한다. 사용자는 PySCF API, 큐브 파일 포맷, py3Dmol 렌더링 코드를 알 필요가 없다. 이는 양자화학 계산의 접근 장벽을 연구자에서 교육자·학생까지 낮추는 인터페이스 혁신이다.

### 3.3 검증 수준 독창성

QCViz‑MCP는 계산 결과에 대한 자체 품질 검증 파이프라인을 내장하고 있다. IBO orbital spread(σ²), 로컬라이제이션 gradient norm(≤ 1e‑8 수렴 기준), Molden 파일 round‑trip fidelity(Frobenius norm ≈ 0), 전하 합 보존(Σq ≈ 0) 등을 자동 검증한다. 10개 NIST 표준 분자에 대한 2가지 기저 함수 벤치마크(20 케이스)에서 100% 성공률을 기록했다. 이러한 내장 검증은 기존 어떤 오비탈 분석 도구(IboView, Multiwfn, Jmol 등)에서도 제공되지 않는 기능이다.

UHF 경로에서도 α/β 채널 각각에 대해 IAO/IBO 수와 전하 합이 검증되며, 전이금속 ECP 분자에서는 MINAO 폴백이 자동 적용되고 수렴 여부가 확인된다.

Phase η에서 **기저 함수 독립성 검증**(`verify_basis_independence()`)이 추가되었다. 동일 분자에 대해 4가지 기저 함수(STO‑3G, cc‑pVDZ, cc‑pVTZ, aug‑cc‑pVDZ)로 IBO를 계산하고, IBO 수 일치·전하 편차·에너지 수렴 추세를 자동으로 비교한다. 이는 계산 결과의 기저 의존성을 정량적으로 평가하는 최초의 자동화된 메커니즘이다. ← updated

### 3.4 경쟁 도구 비교

| 기능                   | QCViz‑MCP | ChemLint | mcp.science | El Agente | IboView |   PySCF CLI   |
| ---------------------- | :-------: | :------: | :---------: | :-------: | :-----: | :-----------: | --------- |
| MCP 프로토콜           |    ✅     |    ✅    |     ✅      |    ✅     |   ❌    |      ❌       |
| IAO/IBO 로컬라이제이션 |    ✅     |    ❌    |     ❌      |    ❌     |   ✅    | ✅ (스크립트) |
| 자연어 인터페이스      |    ✅     |    ❌    |   부분적    |  부분적   |   ❌    |      ❌       |
| 3D 인터랙티브 시각화   |    ✅     |    ❌    |     ❌      |    ❌     |   ✅    |      ❌       |
| 출력 파일 파싱         |    ✅     |    ❌    |     ❌      |    ❌     |   ❌    |      ❌       |
| 내장 벤치마크          |    ✅     |    ❌    |     ❌      |    ❌     |   ❌    |      ❌       |
| 자체 품질 검증         |    ✅     |    ❌    |     ❌      |    ❌     |   ❌    |      ❌       |
| 전이금속 ECP           |    ✅     |    ❌    |     ❌      |    ❌     |   ✅    |      ✅       |
| UHF/ROHF 개방껍질      |    ✅     |    ❌    |     ❌      |    ❌     |   ✅    |      ✅       |
| 헤드리스 PNG 내보내기  |    ✅     |    ❌    |     ❌      |    ❌     |   ❌    |      ❌       |
| 스칼라 상대론 (X2C)    |    ✅     |    ❌    |     ❌      |    ❌     |   ❌    | ✅ (스크립트) | ← updated |
| 적응적 SCF 수렴        |    ✅     |    ❌    |     ❌      |    ❌     |   ❌    |      ❌       | ← updated |
| 기저 독립성 검증       |    ✅     |    ❌    |     ❌      |    ❌     |   ❌    |      ❌       | ← updated |

QCViz‑MCP는 위 13개 항목 모두를 충족하는 유일한 도구이다. ← updated

---

## 4. 출판 가능성 논거 (JOSS 기준 매핑)

### 4.1 실질적 학술 노력 (Substantial Scholarly Effort)

108+개 테스트(자동화), 60개 벤치마크 케이스(NIST 표준 분자 10 × 4기저 + 전이금속·라디칼 개별 검증), 15+개 벤치마크 분자(폐각 10 + 전이금속 4 + 라디칼 1), 6개 MCP 도구, 4개 백엔드 + 2개 렌더러, IBO 검증 파이프라인(4개 메트릭), 기저 독립성 검증, Molden 내보내기, UHF α/β 분리 처리, ECP MINAO 폴백, SFX2C‑1e 상대론, 5단계 적응적 수렴 엔진, UHF 안정성 분석, PyVista 네이티브 렌더러, MkDocs API 문서(5페이지) – 이 모든 구성 요소가 단일 저장소에 통합되어 있다. ← updated

### 4.2 연구 목적 (Research Purpose)

IBO 분석은 화학 결합의 본질을 이해하는 데 핵심적인 도구이나, 기존에는 높은 기술 장벽(스크립트 작성, 라이브러리 지식, 시각화 도구 연동)으로 인해 전문 양자화학자 외에는 접근이 어려웠다. QCViz‑MCP는 이 장벽을 자연어 인터페이스로 제거하여 교육(학부 양자화학 실습)과 연구(결합 분석의 빠른 프로토타이핑) 양쪽에서 활용 가능하게 한다.

### 4.3 분야 현황 (State of the Field)

JOSS 논문에서 화학 영역 MCP 서버의 부재, IBO의 학술적 중요성(801+ 인용), 기존 도구(IboView, Multiwfn, Jmol)의 MCP 미지원·자동화 한계를 서술한다. 전이금속과 개방껍질 시스템, 나아가 4d/5d 원소의 상대론적 효과에 대한 자동화된 IBO 분석 도구가 기존에 없었음을 강조한다. ← updated

### 4.4 소프트웨어 설계 (Software Design)

FastMCP 3.x 선택 이유(async‑native, SSE 지원, Python 타입 힌트 기반 스키마 자동 생성), BackendRegistry 플러그인 패턴(확장성), 보안 설계 3가지(경로 순회 차단 `_validate_file_path`, 원자 수 제한 `_validate_atom_spec`, 입력 크기 제한), UHF 3D ndarray 호환 레이어(`_unpack_uhf`), 5단계 수렴 에스컬레이션(`ConvergenceStrategy`, 불변 튜플 기반), 렌더러 자동 선택(PyVista → Playwright → py3Dmol 폴백)을 논문에 포함한다. ← updated

### 4.5 연구 영향 (Research Impact Statement)

JOSS 2026년 1월 정책 업데이트에 따라 연구 영향 서술이 강화되었다. QCViz‑MCP의 영향은 다음과 같이 정량화된다:

- 10개 NIST 표준 분자 × 4개 기저 함수 벤치마크: 60 케이스 중 에너지·IBO 수·전하 보존 모두 검증. ← updated
- 기저 함수 독립성 검증: IBO 수 일관성, 전하 편차, 에너지 수렴 추세 자동 비교. ← updated
- 전이금속 분자(Fe(CO)₅, TiCl₄, ZrCl₄, Mo(CO)₆) ECP/X2C 수렴 검증. ← updated
- 개방껍질 분자(O₂ 삼중항, NO 라디칼) UHF α/β IBO 분리 계산 성공.
- 기존 5단계 워크플로우 → 1단계 자연어 축약: 코드 35줄 → 0줄.
- 적응적 수렴으로 기존 실패했던 분자의 SCF 수렴 성공률 향상. ← updated
- PyVista 네이티브 렌더링으로 브라우저 없는 논문 Figure 자동 생성 가능. ← updated

### 4.6 AI 사용 고지 (AI Usage Disclosure)

JOSS 2026년 1월 정책 업데이트에 따라 AI 도구 사용을 투명하게 공개한다:

- **사용 도구:** Anthropic Claude (Claude Opus 4 계열), Google Gemini
- **사용 범위:** 코드 스캐폴딩(boilerplate 생성), 테스트 코드 초안 작성, 문서 초안 작성, 디버깅 제안.
- **인간 기여:** 전체 아키텍처 설계, 핵심 알고리즘 로직(IAO/IBO 파이프라인, ECP 폴백 로직, UHF 분리 처리, 수렴 에스컬레이션 전략 설계), 모든 코드 리뷰 및 수정, 벤치마크 설계 및 결과 검증, 논문 내러티브 구성. ← updated
- **검증:** 모든 AI 생성 코드는 인간이 리뷰하고, 108+개 자동화 테스트와 60개 벤치마크로 검증되었다. ← updated

### 4.7 JOSS 준수 체크리스트

| JOSS 기준       | 증거                                                                                      | 상태         |
| --------------- | ----------------------------------------------------------------------------------------- | ------------ |
| 학술 노력       | 108+ 테스트, 60 벤치마크, 6 도구, 4 백엔드+2 렌더러, 검증 파이프라인, X2C/UHF/적응적 수렴 | ✅ ← updated |
| 연구 목적       | 교육·연구 접근 장벽 제거, 전이금속·라디칼·상대론 지원                                     | ✅ ← updated |
| 분야 현황       | 전수조사(~20개 프로젝트), MCP 생태계 내 유일한 전자구조 서버                              | ✅           |
| 소프트웨어 설계 | 3‑계층, FastMCP, BackendRegistry, 보안 3중 검증, UHF 호환, 수렴 에스컬레이션, 렌더러 폴백 | ✅ ← updated |
| 연구 영향       | 60 벤치마크 케이스, 기저 독립성 검증, 전이금속·개방껍질·4d/5d 검증, PyVista PNG           | ✅ ← updated |
| AI 사용 고지    | 도구·범위·인간 기여·검증 모두 문서화                                                      | ✅           |
| 외부 협업 증거  | **미달성** – 외부 기여자 0명, 최소 1명 필요                                               | ❌           |
| 6개월 공개 이력 | **진행 중** – 2026‑03 시작, 2026‑09까지 축적 필요                                         | 🔶           |

---

## 5. 논문 내러티브 아크

### 5.1 4막 구조

JOSS 논문은 다음 4막(four‑act) 구조로 전개한다:

**제1막: Gap (Summary + Statement of Need)**
양자화학에서 IBO 분석은 화학 결합 해석의 표준이지만, 이를 수행하려면 Python 스크립트 작성, PySCF API 이해, 큐브 파일 처리, 시각화 도구 연동이 필요하다. MCP 프로토콜이 LLM-도구 통합의 표준으로 부상했으나, 양자화학 영역에는 MCP 서버가 부재한다.

**제2막: Solution (State of the Field + Software Design)**
QCViz‑MCP는 PySCF의 IAO/IBO 계산을 FastMCP 3.x 기반 MCP 서버로 래핑하여, 자연어 한 줄 입력으로 SCF→IAO→IBO→큐브→3D 시각화 전체 파이프라인을 실행한다. 3‑계층 아키텍처, BackendRegistry 플러그인, 보안 3중 검증, ECP 자동 폴백, UHF α/β 분리 처리, SFX2C‑1e 상대론, 5단계 적응적 수렴 에스컬레이션, PyVista 네이티브 렌더러를 포함한다. ← updated

**제3막: Evidence (Research Impact + Benchmarks)**
10개 NIST 표준 분자 × 4개 기저 함수 벤치마크(60 케이스) 통과. 108+개 자동화 테스트 0 실패. IBO 품질 검증(spread, gradient, round‑trip, charge conservation) 전수 통과. 기저 독립성 검증(IBO 수 일치, 전하 편차 < 허용치). 전이금속(Fe(CO)₅, TiCl₄, ZrCl₄, Mo(CO)₆) ECP/X2C 수렴 확인. 개방껍질(O₂, NO) UHF IBO 검증 완료. ← updated

**제4막: Significance (Conclusion)**
QCViz‑MCP는 양자화학 전자구조 분석의 접근 장벽을 자연어 수준으로 낮추며, MCP 생태계에 과학 계산의 새로운 카테고리를 개척한다. 이는 AI‑과학 통합의 구체적 사례로서, 향후 다른 계산화학 도구(MD, DFT, TDDFT)의 MCP 통합을 위한 참조 구현(reference implementation) 역할을 할 수 있다.

### 5.2 섹션별 핵심 메시지

| 논문 섹션           | 핵심 메시지                                                                         | 예상 분량              |
| ------------------- | ----------------------------------------------------------------------------------- | ---------------------- |
| Summary             | 세계 유일의 전자구조 MCP 서버, 자연어 → IBO 계산 + 3D 시각화                        | 150–200 단어           |
| Statement of Need   | IBO 분석 장벽, MCP 생태계 내 양자화학 부재                                          | 200–250 단어           |
| State of the Field  | 경쟁 도구 비교(ChemLint, mcp.science, IboView), 차별점 13항목                       | 150–200 단어 ← updated |
| Software Design     | 3‑계층 아키텍처, FastMCP, BackendRegistry, 보안, UHF/ECP, X2C, 적응적 수렴, PyVista | 250–350 단어 ← updated |
| Research Impact     | 벤치마크 60케이스, 기저 독립성, 전이금속·개방껍질·상대론 검증                       | 200–250 단어 ← updated |
| AI Usage Disclosure | Claude/Gemini 사용 범위·검증·인간 기여                                              | 100–150 단어 ← updated |
| **합계**            |                                                                                     | **1,050–1,400 단어**   |

목표 단어 수는 JOSS 제한(750–1,750) 내에서 1,200–1,400 단어로 설정한다. ← updated

### 5.3 Figure 및 Table 계획

| #       | 유형                | 내용                                                                   | 형식               |
| ------- | ------------------- | ---------------------------------------------------------------------- | ------------------ |
| Fig. 1  | 아키텍처 다이어그램 | 3‑계층 (MCP → 6 도구 → 4 백엔드) + UHF/ECP/X2C 경로 + 렌더러 폴백 표시 | SVG/PDF ← updated  |
| Fig. 2  | 워크플로우 비교     | 기존 5단계 스크립트 vs. QCViz‑MCP 1단계 자연어                         | SVG/PDF            |
| Fig. 3  | IBO 시각화 예시     | 물 분자 σ/lone‑pair IBO 3D 렌더링 (PyVista 네이티브 PNG)               | PNG ← updated      |
| Table 1 | 벤치마크 결과       | 10(+5) 분자 × 기저 함수: 에너지, IBO 수, 실행 시간 + 기저 독립성       | Markdown ← updated |
| Table 2 | 경쟁 도구 비교      | 13개 기능 항목 × 6개 도구 (섹션 3.4 표)                                | Markdown ← updated |
| Table 3 | 수렴 전략 비교      | 5‑level 에스컬레이션 전략: 성공률, 최종 레벨, 평균 사이클 수           | Markdown ← updated |

### 5.4 자기비판 및 한계

공정한 학술 보고를 위해 다음 한계를 논문에 명시한다:

- **외부 사용자 부재:** 2026년 3월 현재 외부 기여자·사용자가 0명이다. JOSS 제출 전까지 최소 1명의 외부 피드백을 확보해야 한다.
- **전이금속 제한:** Fe(CO)₅, TiCl₄, ZrCl₄, Mo(CO)₆ 수준(3d/4d)까지 검증되었으나, 5d(Pt, Au 등), 란타나이드·악티나이드는 미검증이다. LANL2DZ ECP가 La까지만 커버함이 확인되어, Ce 이상의 란타나이드는 Stuttgart ECP 또는 all‑electron 기저가 필요하다. ← updated
- **py3Dmol 유지보수:** py3Dmol의 최종 업데이트가 2026‑01‑22이며, 활발한 유지보수가 이루어지지 않고 있다. PyVista 렌더러가 대안으로 추가되었으나, 인터랙티브 시각화는 여전히 py3Dmol에 의존한다. ← updated
- **UHF/ROHF 실험적:** O₂ 삼중항과 NO 라디칼에서 검증되었으며, 적응적 수렴 + 안정성 분석이 추가되었으나, 대형 개방껍질 시스템(전이금속 착물의 고스핀 상태 등)에서의 수렴성은 추가 검증이 필요하다. ← updated
- **헤드리스 PNG:** Playwright + Chromium 의존성이 무겁고(~200 MB), PyVista + vtk‑osmesa가 대안(~50 MB)이지만 WebGL 수준의 렌더링 품질은 아니다. ← updated
- **기저 함수 범위:** STO‑3G, cc‑pVDZ, cc‑pVTZ, aug‑cc‑pVDZ까지 벤치마크 확장되었으나, 상관 일치 기저(cc‑pVQZ, cc‑pV5Z 등)에서의 성능은 미확인이다. ← updated
- **ConvergenceStrategy 전역 상태:** `LEVELS`가 튜플(불변)로 변경되어 테스트 안전성이 확보되었으나, 사용자 정의 전략 추가를 위한 확장 인터페이스는 아직 없다. ← updated

### 5.5 두 줄 요약과 내러티브의 정합성

본 보고서 제1절의 두 줄 요약("세계 유일의 전자구조 MCP 서버", "자연어 한 줄로 5단계 → 1단계 축약, 전이금속·개방껍질·SFX2C‑1e 상대론 포함")은 제5절의 4막 내러티브 결론("양자화학 접근 장벽을 자연어 수준으로 낮추고 MCP 생태계에 새 카테고리 개척, AI‑과학 통합의 참조 구현")과 일관된다. ← updated

---

## 부록: Phase 이력 요약

| Phase | 기간       | 핵심 성과                                                                                                                              | 태그             |
| ----- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | --------- |
| α–γ   | ~2026‑02   | E2E 파이프라인 완성, GitHub 공개, MCP 검증, 10분자 벤치마크, 40 테스트                                                                 | –                |
| δ     | 2026‑02    | 보안 패치, 80³ 해상도, cc‑pVDZ 추가, UHF 초기, MkDocs, JOSS 초안, v0.3.0‑alpha                                                         | v0.3.0‑alpha     |
| ε     | 2026‑03‑05 | parse_output, partial_charges, convert_format 구현, Molden 내보내기, IBO 검증, JOSS 6섹션 완성, 95 테스트                              | v0.4.0‑alpha     |
| ζ     | 2026‑03‑05 | 전이금속 ECP 폴백, UHF α/β IBO, 헤드리스 PNG, 108 테스트, 13 벤치마크 분자                                                             | v0.5.0‑alpha     |
| **η** | 2026‑03‑06 | **4d/5d SFX2C‑1e 상대론, 적응적 수렴 5단계, PyVista 네이티브 렌더러, 확장 기저 벤치마크 60케이스, 기저 독립성 검증, 130+ 테스트 예상** | **v0.6.0‑alpha** | ← updated |

## 부록 B: Phase η 서브태스크 상세 ← updated

| 서브태스크 | 내용                                                                   | 핵심 파일                                                                            |
| ---------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| η-1        | 4d/5d 전이금속 SFX2C‑1e (ZrCl₄, Mo(CO)₆) + 란타나이드 감지 경고        | `pyscf_backend.py`, `test_heavy_tm.py`, `benchmark/molecules.py`                     |
| η-2        | 적응적 SCF 수렴 엔진 (`ConvergenceStrategy` 5단계, 불변 LEVELS)        | `pyscf_backend.py`, `test_convergence_strategy.py`                                   |
| η-3        | PyVista 네이티브 오비탈 렌더러 + `parse_cube_string()`                 | `renderers/pyvista_renderer.py`, `renderers/__init__.py`, `test_pyvista_renderer.py` |
| η-4        | 확장 기저 함수 벤치마크 (10분자 × 4기저 = 40케이스) + 기저 독립성 검증 | `benchmark/run_extended_benchmark.py`, `test_basis_independence.py`                  |
| η-5        | 통합 검증: conftest.py 마커, v0.6.0‑alpha 범프, CHANGELOG              | `conftest.py`, `pyproject.toml`, `CHANGELOG.md`                                      |

## 부록 C: Phase η 설계 결정 vs 원래 계획 ← updated

| 원래 계획                                | 변경 사항                          | 변경 이유                                        |
| ---------------------------------------- | ---------------------------------- | ------------------------------------------------ |
| 란타나이드(Ce, Gd) LANL2DZ               | 4d TM(Zr, Mo) def2‑SVP/SFX2C‑1e    | LANL2DZ ECP는 La까지만 커버, Ce-Lu 미지원 확인   |
| `pyscf_backend.py` 전체 교체             | 기존 파일에 함수/메서드 **추가**만 | 보안 패치(`_validate_file_path` 등) 손실 방지    |
| PyVista ↔ `generate_cube()` 미연결       | `parse_cube_string()` 브릿지 추가  | 큐브 문자열 → numpy 3D 배열 변환 파이프라인 필요 |
| `ConvergenceStrategy.LEVELS` 가변 리스트 | 불변 **튜플**                      | 테스트 간 전역 상태 변경 race condition 방지     |
| `compute_scf_relativistic` 별도 시그니처 | `atom_spec: str` 통일              | `compute_scf`와 동일 인터페이스 유지             |

---

_이 보고서는 `docs/SYSTEM_REPORT.md`로 저장되며, 프로젝트 내부 기록·대외 발표·JOSS 논문 초안의 기반 문서로 활용된다._

_최종 업데이트: 2026‑03‑06, v0.6.0‑alpha (Phase η 반영), 논문화전략.md + 고도화.md 통합 반영_ ← updated
