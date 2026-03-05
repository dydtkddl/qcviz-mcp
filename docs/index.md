# QCViz-MCP

A Model Context Protocol (MCP) Server for Quantum Chemistry Visualization and Electronic Structure Analysis.

## Overview

QCViz-MCP enables LLM clients (Claude Desktop, etc.) to perform quantum chemistry calculations, file parsing, and orbital visualization through natural language commands via the MCP protocol.

### Key Features

- **Orbital Analysis**: IAO/IBO localization via PySCF
- **Output Parsing**: Parse 16+ QC programs via cclib
- **3D Visualization**: Interactive orbital isosurfaces via py3Dmol
- **Structure Manipulation**: Format conversion via ASE
- **Security**: Path traversal prevention, input size limits

## Quick Start

See the [README](https://github.com/dydtkddl/qcviz-mcp#readme) for installation instructions.
