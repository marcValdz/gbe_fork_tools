#!/usr/bin/env bash
set -euo pipefail

ROOT="$(pwd)"
VENV="$ROOT/.env-linux"
REQS_FILE="$ROOT/requirements.txt"
PYTHON_VERSION="3.13"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Python if missing
if ! command_exists python$PYTHON_VERSION; then
    echo "[*] Python $PYTHON_VERSION not found. Installing..."
    sudo apt update -y
    sudo apt install -y python$PYTHON_VERSION python$PYTHON_VERSION-venv python$PYTHON_VERSION-dev
fi

# Install dependencies if missing
for cmd in git patchelf ccache; do
    if ! command_exists "$cmd"; then
        echo "[*] $cmd not found. Installing..."
        sudo apt update -y
        sudo apt install -y "$cmd"
    fi
done

# Install C compiler if missing (needed for Nuitka)
if ! command_exists gcc || ! command_exists g++; then
    echo "[*] GCC/G++ not found. Installing build-essential..."
    sudo apt update -y
    sudo apt install -y build-essential
fi

# Remove existing virtual environment if it exists
if [[ -d "$VENV" ]]; then
    rm -rf "$VENV"
fi

# Create virtual environment
python$PYTHON_VERSION -m venv "$VENV"
echo "Virtual environment created at $VENV"
sleep 1

# Activate virtual environment
source "$VENV/bin/activate"

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r "$REQS_FILE"

# Deactivate virtual environment
deactivate

echo "Virtual environment setup completed successfully."
