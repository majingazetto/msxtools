# MSXTOOLS: Technical Reference

Detailed information about the tools in this repository.

## Binary Tools (C/C++)

### Packing & Cutting
- **cutter**: Cuts an SR5 file into 2048-byte chunks.
- **cuttersize**: Cuts a file into chunks of a specified size. Use `-o` to skip the 7-byte SR5 header.
- **tar8k**: Combines multiple binary files into an 8KB-aligned bundle.
- **tarbin**: Packages binary assets and generates corresponding Z80 `#define` headers.

### Disk & ROM Utilities
- **dsktool**: Versatile MSX disk image manager. Supports List, Extract, Add, and Delete commands on 720KB .DSK files.
- **wrdsk / rddsk**: Utilities to write/read files to/from MSX disk images.
- **sms2rom**: Tool related to SEGA Master System to MSX conversions.

### Audio
- **extractwav**: Extracts SCC waveforms from raw data and generates `.mus` and `.wav` files.
- **tsx2wav.py**: (In scripts) Converts TSX tape images to WAV files with high accuracy.
- **playwav.py**: (In scripts) Play WAV files with a live oscilloscope visualization.

### Graphics
- **sr52spr / sr52map / sr52pat**: Tools for converting and managing Screen 5 (MSX2) graphics.
- **mt82map**: Map conversion tool for Screen 8.
- **ViewSRC**: A tool for viewing MSX graphic sources (Screen 5/8).

## Python Scripts (Improved Python 3 Versions)

The following scripts have been updated to Python 3 for better compatibility and performance.

- **Z80PRE-3.py**: Z80 Preprocessor. Handles modern assembly conveniences.
- **bintrozo-3.py**: Split files into "trozos" (pieces) for specialized loading.
- **png2tms-*-3.py**: A suite of tools to convert PNG images to TMS9918 (MSX1) patterns, sprites, and maps.
- **png2sr5-3.py / png2sr8-3.py**: Convert PNGs to Screen 5/8 raw data.
- **tiledtoraw-3.py / csvtiledtoraw-3.py**: Convert maps from the Tiled Map Editor (JSON/CSV) to MSX-ready binary format.
- **ase2pl5-3.py**: Convert Aseprite palette files to MSX Screen 5 palette format.
- **checksms-3.py**: Calculate checksums for SMS/MSX ROMs.
