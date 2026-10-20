#!/usr/bin/env bash
# Install the openMSX launchers, custom machines and extensions of the workspace.
#
# Usage: openmsx/install.sh [--no-dma] [--check]
#
#   bin/*            -> ~/.local/bin              (m1, m1d2, m2+, m2d2)
#   machines/*.xml   -> ~/.openMSX/share/machines (Custom_MSX1_*)
#   extensions/*.xml -> ~/.openMSX/share/extensions (nextor)
#
# Everything is a symlink into this checkout, so a `git pull` updates the
# installed copies. A real file already in the way is moved aside to NAME.bak
# first -- the machines used to be copied by hand and drifted apart between
# the Mac mini and the MacBook Air.
#
# The Tides-Rider, Boosted and Yamanooto machines are NOT here: they depend on
# the ROMs patched by msx_dma_sw and live in msx_dma_sw/openmsx. When that repo
# sits next to msxtools (the workspace root differs per machine: ~/Code/brew/MSX
# on the mini, ~/Code/brew on the Air) its `make setup-machines` is run too,
# unless --no-dma is given.
#
# --check runs `openmsx -testconfig` on every machine and launcher combination
# afterwards and reports which ones would not start.

set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
WORKSPACE=$(cd "$HERE/../.." && pwd)
BIN_DIR=${BIN_DIR:-$HOME/.local/bin}
SHARE_DIR=${SHARE_DIR:-$HOME/.openMSX/share}

DMA=1
CHECK=0
for arg in "$@"; do
  case "$arg" in
    --no-dma) DMA=0 ;;
    --check)  CHECK=1 ;;
    -h|--help) sed -n '2,24p' "$0"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

link() {
  local src=$1 dst=$2
  if [[ -e "$dst" && ! -L "$dst" ]]; then
    mv "$dst" "$dst.bak"
    echo "  kept the old file as $dst.bak"
  fi
  ln -sfn "$src" "$dst"
  echo "  $dst"
}

mkdir -p "$BIN_DIR" "$SHARE_DIR/machines" "$SHARE_DIR/extensions"

echo "launchers -> $BIN_DIR"
for f in "$HERE"/bin/*; do link "$f" "$BIN_DIR/$(basename "$f")"; done

echo "machines -> $SHARE_DIR/machines"
for f in "$HERE"/machines/*.xml; do link "$f" "$SHARE_DIR/machines/$(basename "$f")"; done

echo "extensions -> $SHARE_DIR/extensions"
for f in "$HERE"/extensions/*.xml; do link "$f" "$SHARE_DIR/extensions/$(basename "$f")"; done

if [[ $DMA -eq 1 ]]; then
  if [[ -f "$WORKSPACE/msx_dma_sw/openmsx/Makefile" ]]; then
    echo "msx_dma_sw: Tides-Rider, Boosted and Yamanooto machines"
    make -C "$WORKSPACE/msx_dma_sw/openmsx" setup-machines
  else
    echo "msx_dma_sw not found next to msxtools ($WORKSPACE): skipped"
  fi
fi

if [[ $CHECK -eq 1 ]]; then
  echo "checking with openmsx -testconfig"
  fail=0
  try() {
    if openmsx "$@" -testconfig >/dev/null 2>&1; then
      echo "  ok    $*"
    else
      echo "  FAIL  $*"; fail=1
    fi
  }
  for f in "$HERE"/machines/*.xml; do try -machine "$(basename "$f" .xml)"; done
  # what the launchers actually start
  try -machine Custom_MSX1_DOS2 -ext nextor
  try -machine Custom_MSX1_DOS2_256K -ext nextor
  try -machine Custom_MSX1_DOS2_1M -ext nextor
  try -machine National_CF-3300 -ext ram1mb -ext nextor
  try -machine Boosted_MSX2_EN -ext msxdos2
  try -machine Philips_NMS_8250 -ext msxdos2
  try -machine Boosted_MSX2_EN -ext nextor
  try -machine Boosted_MSX2_EN -ext SunriseIDE_Nextor
  try -machine Boosted_MSX2+_JP -ext msxdos2
  try -machine Sony_HB-F1XV -ext ram512k -ext msxdos2
  try -machine Boosted_MSX2+_JP
  try -machine Panasonic_FS-A1WSX
  try -machine Sony_HB-20P
  try -machine Sony_HB-10
  if [[ $DMA -eq 1 && -d "$WORKSPACE/msx_dma_sw/openmsx/machines" ]]; then
    for f in "$WORKSPACE"/msx_dma_sw/openmsx/machines/*.xml; do
      try -machine "$(basename "$f" .xml)"
    done
    try -machine Boosted_MSX2P_Combo -ext Yamanooto
  fi
  exit $fail
fi
