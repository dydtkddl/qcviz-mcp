# Changelog

## [0.5.0-alpha] — 2026-03-05

### Added

- Transition metal support: `_resolve_minao()` auto-fallback from MINAO to STO-3G for ECP systems
- Full UHF IBO support: `compute_scf_flexible()`, `compute_iao_uhf()`, `compute_ibo_uhf()`, `compute_uhf_charges()`
- Headless PNG export via Playwright + SwiftShader (`renderers/png_exporter.py`, optional)
- Fe(CO)₅ and TiCl₄ transition metal benchmark molecules (def2-SVP)
- O₂ triplet and NO radical open-shell benchmark molecules
- `minao` parameter for `compute_iao()`
- `png` optional dependency group in pyproject.toml

### Changed

- `compute_iao()` now accepts `minao` parameter with ECP auto-detection
- benchmark/molecules.py: added TRANSITION_METAL_MOLECULES and OPEN_SHELL_MOLECULES

## [0.4.0-alpha] — 2026-03-05

### Added

- parse_output: real cclib-based parsing for ORCA/Gaussian/PySCF outputs
- compute_partial_charges: IAO-based partial charge calculation tool
- convert_format: ASE-based structure file conversion with security validation
- Molden export: `export_molden` for IBO/IAO/canonical orbitals (IboView compatible)
- IBO validation module: orbital spread (σ²), Molden roundtrip, charge comparison
- JOSS paper: all 6 required sections complete, AI disclosure finalized

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
