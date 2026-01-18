#!/usr/bin/env bash
set -euo pipefail

ROOT=$(pwd)
VENV="$ROOT/.env-linux"
OUT_DIR="$ROOT/bin/linux"
BUILD_TEMP_DIR="$ROOT/bin/tmp/linux"
ICON_FILE="$ROOT/icon/Froyoshark-Enkel-Steam.png"

EMU_CONFIG_DIR="$OUT_DIR/generate_emu_config"
PARSE_CONTROLLER_DIR="$OUT_DIR/parse_controller_vdf"
PARSE_ACHIEVEMENTS_DIR="$OUT_DIR/parse_achievements_schema"

# Clean and recreate directories
for dir in "$OUT_DIR" "$EMU_CONFIG_DIR" "$PARSE_CONTROLLER_DIR" "$PARSE_ACHIEVEMENTS_DIR"; do
    [[ -d "$dir" ]] && rm -rf "$dir"
    mkdir -p "$dir"
done

[[ -d "$BUILD_TEMP_DIR" ]] && rm -rf "$BUILD_TEMP_DIR"

# Activate venv
source "$VENV/bin/activate"

# Build executables
declare -A BUILD_TARGETS=(
    ["generate_emu_config"]="main.py|$EMU_CONFIG_DIR|--include-package=steam.protobufs"
    ["update_achievement_watcher"]="aw_playtime.py|$EMU_CONFIG_DIR|"
    ["parse_controller_vdf"]="controller_config_generator/parse_controller_vdf.py|$PARSE_CONTROLLER_DIR|"
    ["parse_achievements_schema"]="stats_schema_achievement_gen/achievements_gen.py|$PARSE_ACHIEVEMENTS_DIR|"
)

for name in "${!BUILD_TARGETS[@]}"; do
    IFS='|' read -r script outdir extra_args <<< "${BUILD_TARGETS[$name]}"

    echo "Building $name..."

    python -m nuitka \
        --standalone \
        --onefile \
        --remove-output \
        --output-dir="$outdir" \
        --output-filename="$name" \
        "$script" \
        --assume-yes-for-downloads \
        ${extra_args}
done

# Copy extra files
EXTRA_FILES=("steam_default_icon_locked.jpg" "steam_default_icon_unlocked.jpg" "README.md")
for file in "${EXTRA_FILES[@]}"; do
    cp -f "$file" "$EMU_CONFIG_DIR/"
done

echo "Build completed successfully inside: $OUT_DIR"
