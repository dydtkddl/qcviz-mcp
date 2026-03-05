# Project Progress

## Phases Completed

### Phase α (MVP)

1. **Foundation**: `pyproject.toml`, CI/CD, BSD-3-Clause license.
2. **Core Backends**: 4 ABCs + BackendRegistry + PySCF/cclib/py3Dmol/ASE.
3. **MCP Integration**: FastMCP 3.x server, 6 LLM tools.
4. **Polish & Paper**: JOSS paper draft, examples, `claude_desktop_config.json`.

### Phase β (Cube→HTML)

5. `generate_cube`: PySCF cubegen → temp file → cube text string.
6. `render_orbital_from_cube`: dual isosurface HTML rendering.
7. E2E pipeline: `compute_ibo` → JSON with `visualization_html`.
8. Examples rewritten and verified on WSL2.

### Phase γ (Quality + Benchmarks)

9. **MCP Server Verification** (γ-1): FastMCP Client async test confirms 6 tools listed and `compute_ibo` callable via MCP protocol.
10. **Benchmark Suite** (γ-2): 10 molecules defined in `benchmark/molecules.py`, `run_benchmark.py` for console/JSON output, 20 parametrized tests.
11. **Coverage Expansion** (γ-3): Added `_parse_atom_spec` tests, DFT/B3LYP test, Boys localization test, ASE roundtrip, tool-level tests for all 6 tools, error handling test. Total: 40+ tests.
12. **Release Prep** (γ-4): CHANGELOG updated, `.gitignore` includes `benchmark/results/`.

## Current Metrics

| Item                    | Value                                 |
| ----------------------- | ------------------------------------- |
| Tests (Windows)         | 15 passed / 8 skipped                 |
| Tests (Linux, expected) | 40+ passed                            |
| Backends                | 4 fully operational                   |
| MCP Tools               | 6 registered, MCP Client verified     |
| Benchmark Molecules     | 10                                    |
| GitHub                  | https://github.com/dydtkddl/qcviz-mcp |
| JOSS Clock              | Started 2026-03-05                    |

## Action Items

- `[USER]` Run `pytest -v` on WSL2 → expect 40+ passed.
- `[USER]` Run `python -m benchmark.run_benchmark` → verify all 10 molecules.
- `[USER]` `git tag -a v0.1.0-alpha -m "v0.1.0-alpha"` + `git push origin v0.1.0-alpha`.
- `[USER]` Create GitHub Issues #1–5 for 6-month history.
