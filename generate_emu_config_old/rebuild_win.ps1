# Enable strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Define constants
$ROOT = (Get-Location).Path
$VENV = "$ROOT\.env-win"
$OUT_DIR = "$ROOT\bin\win"
$BUILD_TEMP_DIR = "$ROOT\bin\tmp\win"
$ICON_FILE = "$ROOT\icon\Froyoshark-Enkel-Steam.ico"

# Define output directories for specific executables
$EMU_CONFIG_DIR = "$OUT_DIR\generate_emu_config"
$PARSE_CONTROLLER_DIR = "$OUT_DIR\parse_controller_vdf"
$PARSE_ACHIEVEMENTS_DIR = "$OUT_DIR\parse_achievements_schema"

# Ensure output directories exist
foreach ($dir in @($OUT_DIR, $EMU_CONFIG_DIR, $PARSE_CONTROLLER_DIR, $PARSE_ACHIEVEMENTS_DIR)) {
    if (Test-Path $dir) { Remove-Item -Recurse -Force $dir }
    New-Item -ItemType Directory -Path $dir | Out-Null
}

if (Test-Path $BUILD_TEMP_DIR) { Remove-Item -Recurse -Force $BUILD_TEMP_DIR }

# Activate virtual environment
& "$VENV\Scripts\activate.ps1"

# Build executables
$buildTargets = @(
    @{ Script = "main.py"; Name = "generate_emu_config"; Dir = $EMU_CONFIG_DIR },
    @{ Script = "aw_playtime.py"; Name = "update_achievement_watcher"; Dir = $EMU_CONFIG_DIR },
    @{ Script = "controller_config_generator\parse_controller_vdf.py"; Name = "parse_controller_vdf"; Dir = $PARSE_CONTROLLER_DIR },
    @{ Script = "stats_schema_achievement_gen\achievements_gen.py"; Name = "parse_achievements_schema"; Dir = $PARSE_ACHIEVEMENTS_DIR }
)

foreach ($target in $buildTargets) {
    Write-Output "Building $($target.Name)..."
    pyinstaller $target.Script --distpath "$($target.Dir)" -y --clean --onefile --name "$($target.Name)" --noupx --console -i "$ICON_FILE" --workpath "$BUILD_TEMP_DIR" --specpath "$BUILD_TEMP_DIR"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Build failed for $($target.Name)"
        exit 1
    }
}

# Copy additional files to the generate_emu_config directory
$extraFiles = @(
    "steam_default_icon_locked.jpg",
    "steam_default_icon_unlocked.jpg",
    "README.md"
)

foreach ($file in $extraFiles) {
    Copy-Item -Path "$file" -Destination "$EMU_CONFIG_DIR\" -Force
}

Set-Content "$EMU_CONFIG_DIR\my_login.EXAMPLE.txt" "Check the README"
Set-Content "$EMU_CONFIG_DIR\top_owners_ids.EXAMPLE.txt" "Check the README`nYou can use a website like: https://steamladder.com/games/"

Write-Output "Build completed successfully inside: $OUT_DIR"
