# MSXTOOLS

Custom MSX development tools and scripts. This repository serves as a centralized "store" for high-quality, verified tools used in MSX game development.

## Project Structure

- `src/`: Source code for C/C++ utilities.
- `scripts/`: Python 3, AWK, and TCL scripts for conversion and preprocessing.
- `bin/`: (Generated) Compiled binaries.
- `DOCS.md`: Detailed technical reference and usage instructions.

## Key Features

- **Improved Python 3 Scripts**: Updated versions of standard MSX conversion tools (suffixed with `-3.py`).
- **Unified Build System**: A single `Makefile` in the root builds all C tools and installs them to `bin/`.
- **Verified Graphics Tools**: Specialized converters for Screen 1 (TMS9918), Screen 5, and Screen 8.

## Compilation

To build all C tools, simply run:

```bash
make
```

The binaries will be placed in the `bin/` directory.

## Documentation

For detailed usage information on each tool, please refer to [DOCS.md](./DOCS.md).
