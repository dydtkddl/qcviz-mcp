# Project Progress — v0.5.0-alpha

## Phase Summary

| Phase          | Content                                                         | Status |
| -------------- | --------------------------------------------------------------- | ------ |
| α MVP          | 4 backends, 6 MCP tools, E2E pipeline                           | ✅     |
| β Cube→HTML    | generate_cube, render_orbital_from_cube                         | ✅     |
| γ Quality      | 10-mol benchmark, MCP verification, 50 tests                    | ✅     |
| δ Audit        | Security patches, cc-pVDZ, paper draft, mkdocs                  | ✅     |
| ε Completion   | 6/6 tools functional, Molden export, IBO validation, JOSS paper | ✅     |
| **ζ 3대 한계** | **TM ECP fallback, UHF IBO, headless PNG**                      | **✅** |

## Current Metrics

| Item                    | Value                             |
| ----------------------- | --------------------------------- |
| Version                 | 0.5.0-alpha                       |
| Tests (Windows)         | 31 passed / 16 skipped / 0 failed |
| Tests (Linux, expected) | 110+ passed                       |
| MCP Tools               | 6/6 functional                    |
| Benchmark molecules     | 10 main + 2 UHF + 2 TM = 14       |
| JOSS Paper              | 6/6 sections, 0 TODO              |

## WSL2 전체 검증 + 릴리스

```bash
cd /mnt/d/20260305_양자화학시각화MCP서버구축
pytest -v
python -m benchmark.run_benchmark
git add -A && git commit -m "feat: Phase ζ v0.5.0-alpha"
git tag -a v0.5.0-alpha -m "v0.5.0-alpha: TM, UHF, PNG"
git push origin main --tags
```
