# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0-alpha] — 2026-03-05

### Added

- **PySCF 백엔드**: SCF, IAO, IBO 계산 (RHF/UHF/RKS/B3LYP/PBE0)
- **cclib 백엔드**: 16개 양자화학 프로그램 출력 파싱
- **py3Dmol 백엔드**: 분자 구조 + 오비탈 등치면 시각화
- **ASE 백엔드**: 구조 파일 포맷 변환
- **FastMCP 서버**: 6개 MCP 도구 등록 (`compute_ibo`, `visualize_orbital`, `parse_output`, `compute_partial_charges`, `convert_format`, `analyze_bonding`)
- XYZ 파일 포맷 자동 감지 및 PySCF 포맷 변환 (`_parse_atom_spec`)
- Löwdin 정규직교화 기반 IAO 부분 전하 계산
- Gaussian cube 포맷 생성 + py3Dmol 렌더링 파이프라인 (`generate_cube` → `render_orbital_from_cube`)
- `compute_ibo` 도구 E2E 파이프라인: SCF → IAO → IBO → Cube → HTML (JSON 반환)
- CI/CD: GitHub Actions (Linux full suite + Windows/macOS partial)
- 16+ 자동화 테스트 (PySCF 의존성 없는 환경에서 graceful skip)
- JOSS 논문 초안 (`paper/paper.md`) — JOSS 2025 필수 섹션 4개 포함
