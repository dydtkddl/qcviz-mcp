# Project Progress — v0.3.0-alpha

## Audit Response (18 Issues)

| #   | Issue                          | Status                                                     | Phase |
| --- | ------------------------------ | ---------------------------------------------------------- | ----- |
| 1   | Collaborative effort           | `[USER]` 외부 engagement 필요                              | —     |
| 2   | AI disclosure                  | ✅ paper.md에 전체 내용 작성                               | δ-8   |
| 3   | Research impact                | ✅ 초안 작성, `[TODO]` 마커 포함                           | δ-8   |
| 4   | cc-pVDZ benchmarks             | ✅ 10 molecules × 2 basis sets                             | δ-3   |
| 5   | UHF support                    | 🔶 O₂ 정의됨, PySCF UHF 분기 존재                          | δ-4   |
| 6   | parse_output path validation   | ✅ `_validate_file_path` 구현                              | δ-1   |
| 7   | Real QC output testing         | 🔶 WSL2에서 검증 필요                                      | δ-5   |
| 8   | Saddle point detection         | 🔶 `warnings` 키 추가, gradient 추출은 PySCF API 확인 필요 | δ-2   |
| 9   | Cube resolution 80             | ✅ 기본값 80³                                              | δ-2   |
| 10  | paper.md full content          | ✅ 7개 섹션 영문 작성 완료                                 | δ-8   |
| 11  | API documentation              | ✅ mkdocs.yml + 5 doc pages                                | δ-7   |
| 12  | cclib EOL monitoring           | ✅ 문서화                                                  | —     |
| 13  | Argonne comparison             | ✅ paper.md State of Field에 포함                          | δ-8   |
| 14  | analyze_bonding                | ✅ IBO 기여도 분석으로 업그레이드                          | δ-6   |
| 15  | convert_format path validation | ✅ `_validate_file_path` 적용                              | δ-1   |
| 16  | Playwright PNG export          | `[FUTURE]` Phase ε                                         | —     |
| 17  | Transition metal docs          | `[FUTURE]`                                                 | —     |
| 18  | Dockerfile                     | `[FUTURE]`                                                 | —     |

## Current Metrics

| Item                    | Value                     |
| ----------------------- | ------------------------- |
| Tests (Windows)         | 21 passed / 8 skipped     |
| Tests (Linux, expected) | 70+ passed                |
| Version                 | 0.3.0-alpha               |
| paper.md                | 7/7 JOSS sections written |
| References              | 11                        |
| Benchmark molecules     | 10 × 2 basis sets         |

## User Actions

1. WSL2: `pytest -v` → 70+ passed 확인
2. WSL2: `python -m benchmark.run_benchmark` → 20 runs
3. `git add -A && git commit -m "feat: Phase δ v0.3.0-alpha"`
4. `git tag -a v0.3.0-alpha && git push origin main --tags`
5. GitHub Issues 5개 생성 (6개월 이력)
6. 외부 engagement: PySCF Discussions, Reddit r/comp_chem
