# Project Progress

## Phases Completed

### Phase α (MVP)

1. **Foundation**: `pyproject.toml`, CI/CD (GitHub Actions), BSD-3-Clause license.
2. **Core Backends**: ABCs (`OrbitalBackend`, `ParserBackend`, `VisualizationBackend`, `StructureBackend`), `BackendRegistry`, PySCF/cclib/py3Dmol/ASE implementations.
3. **MCP Integration**: FastMCP 3.x server, 6 LLM tools (`compute_ibo`, `visualize_orbital`, `parse_output`, `compute_partial_charges`, `convert_format`, `analyze_bonding`).
4. **Polish & Paper**: JOSS paper draft (4 new required sections), examples, `claude_desktop_config.json`.

### Phase β-1 (Cube→HTML Pipeline)

5. **generate_cube**: PySCF `cubegen.orbital` → temp file → Gaussian cube format string.
6. **render_orbital_from_cube**: py3Dmol dual-isosurface (positive/negative) HTML rendering.
7. **E2E pipeline**: `compute_ibo` tool returns JSON with `visualization_html`.
8. **Tests**: 16+ automated tests (graceful skip on PySCF-absent environments).

### Phase β-2 (Examples)

9. **examples/01_water_ibo.py**: Full IBO pipeline with HTML output.
10. **examples/02_orca_parse_viz.py**: ASE + cclib + py3Dmol demo.

### Phase β-3 (Release Prep)

11. **.gitignore**, **CHANGELOG.md** (v0.1.0-alpha), README conda Quick Start.

## Decision Pending

- `[DECISION-NEEDED]` pyproject.toml/paper.md author info is placeholder.
- JOSS 6-month public history clock: start date TBD.
- 1st-stage journal: JOSS (Sept 2026+) vs J. Cheminform./SoftwareX (sooner).
