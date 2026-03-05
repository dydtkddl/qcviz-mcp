# Project Progress — v0.4.0-alpha

## Phase Summary

| Phase        | Content                                                         | Status |
| ------------ | --------------------------------------------------------------- | ------ |
| α MVP        | 4 backends, 6 MCP tools, E2E pipeline                           | ✅     |
| β Cube→HTML  | generate_cube, render_orbital_from_cube                         | ✅     |
| γ Quality    | 10-mol benchmark, MCP verification, 50 tests                    | ✅     |
| δ Audit      | Security patches, cc-pVDZ, paper draft, mkdocs                  | ✅     |
| ε Completion | 6/6 tools functional, Molden export, IBO validation, JOSS paper | ✅     |

## Current Metrics

| Item                    | Value                                |
| ----------------------- | ------------------------------------ |
| Version                 | 0.4.0-alpha                          |
| Tests (Windows)         | 27 passed / 12 skipped               |
| Tests (Linux, expected) | 90+ passed                           |
| MCP Tools               | 6/6 functional                       |
| Benchmark               | 10 molecules × 2 basis sets          |
| JOSS Paper              | 6/6 sections, 0 TODO, 11 references  |
| Molden Export           | IboView compatible                   |
| IBO Validation          | spread, roundtrip, charge comparison |

## User Actions

```bash
# WSL2 전체 검증
cd /mnt/d/20260305_양자화학시각화MCP서버구축
pytest -v
python -m benchmark.run_benchmark
git add -A && git commit -m "feat: Phase ε v0.4.0-alpha"
git tag -a v0.4.0-alpha -m "v0.4.0-alpha: 6/6 tools, Molden, IBO validation, JOSS paper"
git push origin main --tags
```
