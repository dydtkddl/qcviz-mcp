# QCViz-MCP

![CI](https://github.com/user/qcviz-mcp/actions/workflows/ci.yml/badge.svg)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A Model Context Protocol (MCP) Server for Quantum Chemistry Visualization and Electronic Structure Analysis.

## 개요 (Overview)

QCViz-MCP는 LLM 클라이언트(Claude Desktop 둥)가 양자화학 계산, 파일 파싱, 그리고 오비탈 시각화를 자연어로 쉽게 수행할 수 있도록 해주는 MCP 서버입니다.

### 핵심 기능:

- **오비탈 분석**: PySCF를 활용한 IAO (Intrinsic Atomic Orbitals) 및 IBO (Intrinsic Bond Orbitals) 국소화 계산
- **결과 파싱**: cclib를 통해 ORCA, Gaussian 등 16개 양자화학 프로그램 출력 파싱
- **3D 시각화**: py3Dmol을 이용한 상호작용 가능한 3D 오비탈 등치면 렌더링
- **구조 조작**: ASE를 이용한 분자 구조 변환

## 빠른 시작 가이드 (Quick Start)

### 설치 방법 (conda 권장)

```bash
# conda 환경 생성 (PySCF는 conda-forge에서 설치 권장)
conda create -n qcviz python=3.11 -y
conda activate qcviz
conda install -c conda-forge pyscf -y

# 나머지 의존성 설치
pip install -e ".[viz,parse,structure]"
```

> **Windows 사용자**: PySCF는 Linux/macOS만 네이티브 지원합니다. Windows에서는 WSL2를 사용하세요.
> PySCF 없이도 파싱(`cclib`), 시각화(`py3Dmol`), 포맷 변환(`ASE`) 기능은 동작합니다:
> `pip install -e ".[dev-no-pyscf]"`

### 테스트 및 검증

```bash
pytest -v
python examples/01_water_ibo.py  # PySCF 필요
python examples/02_orca_parse_viz.py
```

## 아키텍처 다이어그램

QCViz-MCP 서버는 다양한 플러그인 형태의 백엔드와 연결되어 각 도구를 제공합니다.

```
MCP 클라이언트 (Claude Desktop)
       │
       ▼
[QCViz-MCP 서버 / Tools] ─┬─ compute_ibo
                          ├─ visualize_orbital
                          ├─ parse_output
                          ├─ compute_partial_charges
                          ├─ convert_format
                          └─ analyze_bonding
       │
       ▼
[백엔드 엔진] ─────────────┬─ PySCFBackend (계산, 분석)
                          ├─ CclibBackend (파싱)
                          ├─ Py3DmolBackend (시각화)
                          └─ ASEBackend (구조 조작)
```

## 라이선스

QCViz-MCP는 BSD-3-Clause 라이선스로 제공됩니다. 의존성 중 ASE는 LGPL 라이선스로 포함되어 있으나, QCViz-MCP는 이를 포함(distribute)하지 않고 참조(import)로만 사용합니다.
