# Enable strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Define constants
$ROOT = (Get-Location).Path
$BUILD_DIR = "$ROOT\bin\win"
$OUT_DIR = "$ROOT\bin\package\win"

# Ensure output directory exists
if (-not (Test-Path $OUT_DIR)) {
    New-Item -ItemType Directory -Path $OUT_DIR | Out-Null
}

$ARCHIVE_FILE = "$OUT_DIR\generate_emu_config-win.zip"
if (Test-Path $ARCHIVE_FILE) {
    Remove-Item -Force $ARCHIVE_FILE
}

# Create a ZIP archive using built-in PowerShell compression
Compress-Archive -Path "$BUILD_DIR\*" -DestinationPath $ARCHIVE_FILE -Force

Write-Output "Build and packaging completed successfully."
