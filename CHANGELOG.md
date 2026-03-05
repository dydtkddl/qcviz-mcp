# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0-alpha] — 2026-03-05

### Security

- **Path traversal prevention**: `parse_output` and `convert_format` now validate file paths against project directory whitelist
- **Input size limits**: `_validate_atom_spec` rejects molecules with >200 atoms

### Added

- **cc-pVDZ benchmarks**: All 10 molecules now tested with both STO-3G and cc-pVDZ basis sets
- **UHF molecule**: O₂ triplet added to benchmark definitions (spin=2)
- **analyze_bonding upgrade**: IBO contribution analysis with per-atom population breakdown (no longer stub)
- **API documentation**: mkdocs + mkdocstrings configuration with Material theme
- **JOSS paper**: Full draft with all 7 required sections (Summary, Statement of Need, State of the Field, Software Design, Research Impact, AI Disclosure)
- **Bibliography**: Expanded to 11 references (Argonne MCP, El Agente, Löwdin, Anthropic MCP)
- Security test suite (`test_security.py`): path traversal, atom limits
- MCP server async tests via FastMCP Client

### Changed

- Default cube resolution: 40³ → **80³** for publication-quality output
- `compute_ibo` tool adds `warnings` key to JSON response
- Version bumped to 0.3.0-alpha

## [0.2.0-alpha] — 2026-03-05

### Added

- Benchmark suite (10 molecules), parametrized tests, MCP server verification

## [0.1.0-alpha] — 2026-03-05

### Added

- Initial MVP: PySCF/cclib/py3Dmol/ASE backends, 6 MCP tools, E2E IBO→cube→HTML pipeline
