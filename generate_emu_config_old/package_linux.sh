#!/usr/bin/env bash
set -euo pipefail

ROOT="$(pwd)"
BUILD_DIR="$ROOT/bin/linux"
OUT_DIR="$ROOT/bin/package/linux"

# Check build directory
if [[ ! -d "$BUILD_DIR" ]]; then
    echo "[X] Build directory not found: $BUILD_DIR" >&2
    exit 1
fi

# Ensure tar is installed
if ! command -v tar &> /dev/null; then
    echo "[*] tar not found. Installing..."
    sudo apt update -y
    sudo apt install -y tar
fi

# Ensure output directory exists
mkdir -p "$OUT_DIR"

ARCHIVE_FILE="$OUT_DIR/generate_emu_config-linux.tar.bz2"
if [[ -f "$ARCHIVE_FILE" ]]; then
    echo "[*] Removing existing archive: $ARCHIVE_FILE"
    rm -f "$ARCHIVE_FILE"
fi

# Package the build directory
pushd "$BUILD_DIR" > /dev/null
tar -cjf "$ARCHIVE_FILE" */
popd > /dev/null

echo "[*] Build and packaging completed successfully: $ARCHIVE_FILE"
