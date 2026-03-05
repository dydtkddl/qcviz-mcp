# Changelog

## [0.4.0-alpha] — 2026-03-05

### Added

- **parse_output**: real cclib-based parsing for ORCA/Gaussian/PySCF outputs
- **compute_partial_charges**: IAO-based partial charge calculation tool (fully functional)
- **convert_format**: ASE-based structure file conversion with security validation
- **Molden export**: `export_molden` method for IBO/IAO/canonical orbitals (IboView compatible)
- **IBO validation module**: orbital spread (σ²), Molden roundtrip, charge comparison
- Test fixtures: ORCA mock, Gaussian mock, water.xyz
- `test_parse_output.py` (5 tests), `test_partial_charges.py` (4), `test_convert_format.py` (4), `test_molden_validation.py` (6)
- JOSS paper: all 6 required sections complete, comparison table, AI disclosure finalized
- paper.bib: 11 references (Argonne MCP, El Agente, Löwdin, Anthropic MCP spec)

### Changed

- paper.md: 0 TODO markers remaining
- Version bumped to 0.4.0-alpha

## [0.3.0-alpha] — 2026-03-05

### Security

- Path traversal prevention on parse_output and convert_format
- Input size limits (200 atoms max)

### Added

- cc-pVDZ benchmarks, analyze_bonding upgrade, API docs (mkdocs), security tests

## [0.2.0-alpha] — 2026-03-05

- Benchmark suite (10 molecules), MCP server verification

## [0.1.0-alpha] — 2026-03-05

- Initial MVP: PySCF/cclib/py3Dmol/ASE backends, 6 MCP tools, E2E pipeline
