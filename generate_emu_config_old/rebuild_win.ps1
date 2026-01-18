Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ROOT = (Get-Location).Path
$VENV = "$ROOT\.env-win"
$OUT_DIR = "$ROOT\bin\win"
$BUILD_TEMP_DIR = "$ROOT\bin\tmp\win"
$ICON_FILE = "$ROOT\icon\Froyoshark-Enkel-Steam.ico"

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
    @{
        ExeName = "generate_emu_config"
        ScriptName = "main.py"
        Dir = $EMU_CONFIG_DIR
        ExtraArgs = @("--include-package=steam.protobufs")
    },
    @{
        ExeName = "update_achievement_watcher"
        ScriptName = "aw_playtime.py"
        Dir = $EMU_CONFIG_DIR
        ExtraArgs = @()
    },
    @{
        ExeName = "parse_controller_vdf"
        ScriptName = "controller_config_generator\parse_controller_vdf.py"
        Dir = $PARSE_CONTROLLER_DIR
        ExtraArgs = @()
    },
    @{
        ExeName = "parse_achievements_schema"
        ScriptName = "stats_schema_achievement_gen\achievements_gen.py"
        Dir = $PARSE_ACHIEVEMENTS_DIR
        ExtraArgs = @()
    }
)

foreach ($t in $buildTargets) {
    Write-Output "Building $($t.ExeName)..."

    $args = @(
        "-m", "nuitka",
        "--msvc=latest",
        "--standalone",
        "--onefile",
        "--remove-output",
        "--output-dir=$($t.Dir)",
        "--output-filename=$($t.ExeName).exe",
        $t.ScriptName,
        "--assume-yes-for-downloads",
        "--windows-icon-from-ico=$ICON_FILE"
    ) + $t.ExtraArgs

    python @args

    if ($LASTEXITCODE -ne 0) {
        throw "Build failed for $($t.Name)"
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

Write-Output "Build completed successfully inside: $OUT_DIR"
