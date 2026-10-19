#!/bin/bash
# install_wrappers.sh — Installs msxtools CLI wrappers and binary utilities into ~/.local/bin
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"

mkdir -p "$BIN_DIR"

echo "Installing msxtools Python wrappers to $BIN_DIR..."

python_tools=(
    "tsxplay:scripts/tsxplay.py"
    "playwav:scripts/playwav.py"
    "invertwav:scripts/invertwav.py"
    "z80pre:scripts/Z80PRE.py"
    "Z80PRE:scripts/Z80PRE.py"
    "bintrozo:scripts/bintrozo.py"
    "binpack:scripts/binpack.py"
    "checksms:scripts/checksms.py"
    "csvtiledtomap:scripts/csvtiledtomap.py"
    "csvtiledtoraw:scripts/csvtiledtoraw.py"
    "tiledtoraw:scripts/tiledtoraw.py"
    "tiledtorawxml:scripts/tiledtorawxml.py"
    "ase2pl5:scripts/ase2pl5.py"
    "png2mode2:scripts/png2mode2.py"
    "png2sms:scripts/png2sms.py"
    "png2smsspr:scripts/png2smsspr.py"
    "png2sr5:scripts/png2sr5.py"
    "png2sr8:scripts/png2sr8.py"
    "png2tms-map:scripts/png2tms-map.py"
    "png2tms-pat:scripts/png2tms-pat.py"
    "png2tms-spr:scripts/png2tms-spr.py"
    "png2tms-sr1-pat:scripts/png2tms-sr1-pat.py"
    "png8tops:scripts/png8tops.py"
    "pngpal:scripts/pngpal.py"
    "ACWA:scripts/ACWA.py"
)

for entry in "${python_tools[@]}"; do
    wrapper="${entry%%:*}"
    script="${entry#*:}"
    script_path="$SCRIPT_DIR/$script"
    wrapper_path="$BIN_DIR/$wrapper"

    if [ -f "$script_path" ]; then
        cat << EOF > "$wrapper_path"
#!/bin/bash
exec python3 "$script_path" "\$@"
EOF
        chmod +x "$wrapper_path"
        chmod +x "$script_path"
        echo "  [Python wrapper] $wrapper -> $script"
    else
        echo "  Warning: Script not found: $script_path"
    fi
done

echo "Installing msxtools compiled binaries to $BIN_DIR..."

binary_tools=(
    "cutter"
    "cuttersize"
    "tar8k"
    "tarbin"
    "tarbinmax"
    "dsktool"
    "wrdsk"
    "rddsk"
    "extractwav"
    "freepagebytes"
    "mt82map"
    "sr52map"
    "sr52pat"
    "sr52spr"
    "bgm2tmfall"
)

for bin_name in "${binary_tools[@]}"; do
    bin_path="$SCRIPT_DIR/bin/$bin_name"
    target_path="$BIN_DIR/$bin_name"

    if [ -f "$bin_path" ]; then
        ln -sf "$bin_path" "$target_path"
        chmod +x "$target_path"
        echo "  [Binary symlink] $bin_name -> $bin_path"
    else
        echo "  Warning: Binary not found: $bin_path"
    fi
done

echo "Installing msxtools shell scripts to $BIN_DIR..."

shell_tools=(
    "awake:scripts/awake.sh"
)

for entry in "${shell_tools[@]}"; do
    name="${entry%%:*}"
    script_path="$SCRIPT_DIR/${entry#*:}"
    if [ -f "$script_path" ]; then
        chmod +x "$script_path"
        ln -sf "$script_path" "$BIN_DIR/$name"
        echo "  [Shell symlink] $name -> ${entry#*:}"
    else
        echo "  Warning: Script not found: $script_path"
    fi
done

echo "msxtools successfully installed into $BIN_DIR."
