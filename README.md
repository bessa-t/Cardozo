# Cardozo

Computational analysis software for arbitrary reinforced concrete sections.

Cardozo generates biaxial interaction diagrams (`N-Mx-My`) for reinforced concrete sections extracted from DXF files. It parses CAD geometry, builds the reinforced concrete section, applies material models compatible with NBR 6118, and provides a desktop GUI built with CustomTkinter.

## Features

- DXF parser for concrete boundaries and steel bars.
- Material library for concrete and steel classes.
- Geometry builder for arbitrary reinforced concrete sections.
- Desktop interface for material selection, DXF loading, geometry preview, and interaction diagram plotting.

## Project Structure

```text
Cardozo/
├── README.md
├── requirements.txt
├── pyproject.toml
├── Cardozo.spec
├── docs/
│   └── dxf_specs.md
├── examples/
│   └── dxf_files/
│       └── section_7.dxf
├── scripts/
│   ├── build_exe.bat
│   ├── run_dev.bat
│   └── run_dev.sh
├── src/
│   └── cardozo/
│       ├── main.py
│       ├── backend/
│       │   ├── dxf_parser.py
│       │   └── geometry_builder.py
│       ├── data/
│       │   └── std_materials.py
│       └── frontend/
│           └── app_window.py
└── tests/
    ├── test_dxf_parser.py
    ├── test_geometry_builder.py
    └── test_imports.py
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Running

From the project root:

```bash
PYTHONPATH=src python -m cardozo.main
```

On Windows, you can also run:

```bat
scripts\run_dev.bat
```

## Testing

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## Building the Executable

The distributable executable is generated with PyInstaller using `Cardozo.spec`:

```bash
pip install -r requirements-build.txt
pyinstaller Cardozo.spec
```

On Windows:

```bat
scripts\build_exe.bat
```

The generated executable will be created under:

```text
dist/Cardozo/Cardozo.exe
```

## DXF Input Format

The DXF file must use these layers:

- `concrete`: closed `LWPOLYLINE` entities for concrete boundaries.
- `steel bars`: `CIRCLE` entities for reinforcement bars.

Additional details are documented in `docs/dxf_specs.md`.

## Engineering Assumptions

- Plane sections remain plane after deformation.
- Perfect bond between steel and concrete.
- Concrete tensile strength is neglected for ultimate limit state analysis.
- Design moments supplied by the user should already include applicable second-order effects.

## Author

Tarso Bessa  
bessatarso@gmail.com
