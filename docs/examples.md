# Examples

## Example 1: Water IBO Analysis

`examples/01_water_ibo.py` — Full E2E pipeline:

1. PySCF SCF calculation (HF/STO-3G)
2. IAO partial charges
3. IBO localization (Pipek-Mezey)
4. Gaussian cube file generation
5. py3Dmol HTML visualization

```bash
python examples/01_water_ibo.py
# Output: examples/output/water_ibo_0.html
```

## Example 2: Molecule Visualization + Format Conversion

`examples/02_orca_parse_viz.py` — Demonstrates:

1. ASE structure reading and format conversion (XYZ → CIF)
2. cclib supported programs listing
3. py3Dmol molecule rendering (ball-and-stick)

```bash
python examples/02_orca_parse_viz.py
# Output: examples/output/molecule_viz.html
```
