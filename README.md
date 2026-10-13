# MSXTOOLS

Custom MSX development tools and scripts. This repository serves as a centralized "store" for high-quality, verified tools used in MSX game development.

## Project Structure

- `src/`: Source code for C/C++ utilities.
- `scripts/`: Python 3, AWK, and TCL scripts for conversion and preprocessing.
- `bin/`: (Generated) Compiled binaries.
- `openmsx/`: openMSX launchers (`m1`, `m1d2`, `m2+`, `m2d2`, and `mtr` for
  Tides-Rider), the custom
  `Custom_MSX1_*` machines and the `nextor` extension. `openmsx/install.sh`
  symlinks them into `~/.local/bin` and `~/.openMSX/share`, runs
  `msx_dma_sw/openmsx`'s `make setup-machines` (Tides-Rider, Boosted, Yamanooto)
  when that repo sits next to msxtools, and `--check` validates every machine
  with `openmsx -testconfig`.
- `DOCS.md`: Detailed technical reference and usage instructions.

## Key Features

- **Improved Python 3 Scripts**: Updated versions of standard MSX conversion tools (suffixed with `.py`).
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
