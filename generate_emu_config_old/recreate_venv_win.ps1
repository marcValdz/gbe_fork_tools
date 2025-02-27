# Enable strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Define constants
$ROOT = (Get-Location).Path
$VENV = "$ROOT\.env-win"
$REQS_FILE = "$ROOT\requirements.txt"

# Remove existing virtual environment if it exists
if (Test-Path $VENV) {
    Remove-Item -Recurse -Force $VENV
}

# Create virtual environment
python -m venv $VENV
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to create virtual environment"
    exit 1
}

Start-Sleep -Seconds 1

# Activate virtual environment and install dependencies
& "$VENV\Scripts\Activate.ps1"
pip install -r $REQS_FILE
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install dependencies"
    exit 1
}

# Deactivate virtual environment
& "$VENV\Scripts\Deactivate.ps1"

Write-Output "Virtual environment setup completed successfully."
