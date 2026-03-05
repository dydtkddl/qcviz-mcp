# QCViz-MCP API Reference

## Tools

The MCP server exposes the following tools to Claude.

- **compute_ibo(xyz_string, basis="cc-pvdz", method="RHF")**: Computes Intrinsic Bond Orbitals.
- **visualize_orbital(xyz_string, orbital_type="HOMO")**: Returns py3Dmol HTML rendering for user inspection.
- **parse_output(file_path)**: Wraps cclib.ccopen to parse generic computational chemistry output files.
- **compute_partial_charges(xyz_string, basis, method)**: Computes basis-set-independent atomic charges using IAOs.
- **convert_format(input_path, output_path)**: Uses ASE to parse and write different molecular formats.
- **analyze_bonding(xyz_string)**: High-level reasoning tool using IBO occupation logic.

## Backends

The registry system `qcviz_mcp.backends.registry` automatically provisions:

1. `PySCFBackend`: Heavy computing and electron density logic.
2. `CclibBackend`: Log scraping.
3. `Py3DmolBackend`: 3D HTML builder.
4. `ASEBackend`: Coordinates converter.
