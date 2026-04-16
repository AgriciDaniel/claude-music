# claude-music — Windows Installer (PowerShell)
# Port of install.sh for Windows users. Requires PowerShell 5.1+ and Developer Mode
# (or Administrator) for symlink creation.
#
# Run with:    powershell -ExecutionPolicy Bypass -File .\install.ps1
#
# This installer:
#   1. Checks prerequisites (git, Python, NVIDIA, FFmpeg, uv)
#   2. Finds or installs ACE-Step 1.5
#   3. Downloads model checkpoints (optional)
#   4. Updates config.json with your ACE-Step path
#   5. Creates symlinks in %USERPROFILE%\.claude\skills\

$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition
$SKILLS_DIR = Join-Path $SCRIPT_DIR "skills"
$TARGET_DIR = Join-Path $env:USERPROFILE ".claude\skills"
$CONFIG = Join-Path $SKILLS_DIR "claude-music\config.json"
$DEFAULT_ACE_DIR = Join-Path $env:USERPROFILE "ACE-Step-1.5"

function Write-Step  { param($n, $msg) Write-Host "`n[$n] $msg" -ForegroundColor Blue }
function Write-Ok    { param($msg)    Write-Host "  [OK] $msg"    -ForegroundColor Green }
function Write-Warn  { param($msg)    Write-Host "  [!]  $msg"    -ForegroundColor Yellow }
function Write-Err   { param($msg)    Write-Host "  [ERROR] $msg" -ForegroundColor Red }
function Ask-User    { param($prompt) Write-Host "  $prompt " -NoNewline -ForegroundColor White; return Read-Host }

Write-Host ""
Write-Host "  ================================================================" -ForegroundColor White
Write-Host "      claude-music - AI Music Production for Claude Code"          -ForegroundColor White
Write-Host "      Powered by ACE-Step 1.5 (Windows installer)"                   -ForegroundColor White
Write-Host "  ================================================================" -ForegroundColor White
Write-Host ""
Write-Host "  This installer will set up everything you need."
Write-Host ""

# ----------------------------------------------------------------------
# 1. Prerequisites
# ----------------------------------------------------------------------
Write-Step "1/6" "Checking your system..."

function Test-Command { param($name) $null -ne (Get-Command $name -ErrorAction SilentlyContinue) }

if (Test-Command git)    { Write-Ok "git found" }
else { Write-Err "git not found. Install from https://git-scm.com/download/win"; exit 1 }

$pyCmd = $null
foreach ($c in @("python", "python3", "py")) {
    if (Test-Command $c) {
        $ver = & $c --version 2>&1
        if ($LASTEXITCODE -eq 0) { $pyCmd = $c; Write-Ok "Python: $ver (via '$c')"; break }
    }
}
if (-not $pyCmd) { Write-Err "Python 3.10+ not found. Install from https://www.python.org/"; exit 1 }

if (Test-Command nvidia-smi) {
    $gpu = (nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>$null | Select-Object -First 1)
    Write-Ok "GPU: $gpu"
} else {
    Write-Warn "No NVIDIA GPU detected. ACE-Step can run on CPU but will be very slow."
}

if (Test-Command ffmpeg) {
    Write-Ok "FFmpeg found"
} else {
    Write-Warn "FFmpeg not found. Attempting to install via winget..."
    if (Test-Command winget) {
        winget install -e --id Gyan.FFmpeg --silent --accept-package-agreements --accept-source-agreements 2>&1 | Out-Null
        if (Test-Command ffmpeg) { Write-Ok "FFmpeg installed" }
        else { Write-Warn "Install FFmpeg manually: https://ffmpeg.org/download.html" }
    } else {
        Write-Warn "winget not available. Install FFmpeg manually: https://ffmpeg.org/download.html"
    }
}

if (Test-Command uv) { Write-Ok "uv found" }
else {
    Write-Warn "uv not found. Installing..."
    Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    if (Test-Command uv) { Write-Ok "uv installed" }
    else { Write-Err "uv install failed. Install manually: https://docs.astral.sh/uv/getting-started/installation/"; exit 1 }
}

# ----------------------------------------------------------------------
# 2. Find or install ACE-Step
# ----------------------------------------------------------------------
Write-Step "2/6" "Locating ACE-Step 1.5..."

$aceDir = $null
$candidates = @(
    $DEFAULT_ACE_DIR,
    (Join-Path $env:USERPROFILE "Desktop\ACE-Step-1.5"),
    (Join-Path $env:USERPROFILE "Desktop\Local-AI-Models\ACE-Step-1.5"),
    (Join-Path $env:USERPROFILE "Documents\ACE-Step-1.5")
)
foreach ($c in $candidates) {
    if (Test-Path (Join-Path $c "acestep")) { $aceDir = $c; Write-Ok "Found ACE-Step at $c"; break }
}

if (-not $aceDir) {
    $answer = Ask-User "ACE-Step not found. Clone it now to ${DEFAULT_ACE_DIR}? [Y/n]"
    if ($answer -eq "" -or $answer -match '^[Yy]') {
        git clone https://github.com/ACE-Step/ACE-Step-1.5.git $DEFAULT_ACE_DIR
        if ($LASTEXITCODE -ne 0) {
            Write-Err "git clone failed. Check your internet connection and try again."
            exit 1
        }
        $aceDir = $DEFAULT_ACE_DIR
        Push-Location $aceDir
        Write-Host "  Installing ACE-Step Python deps (this can take 5-15 min)..."
        uv sync
        if ($LASTEXITCODE -ne 0) {
            Write-Warn "uv sync reported errors. ACE-Step may still work — test with a small /music generate call."
        }
        Pop-Location
        Write-Ok "ACE-Step installed"
    } else {
        $manual = Ask-User "Enter path to your ACE-Step-1.5 install:"
        if (-not (Test-Path (Join-Path $manual "acestep"))) {
            Write-Err "Path does not contain an 'acestep' package: $manual"; exit 1
        }
        $aceDir = $manual
    }
}

# ----------------------------------------------------------------------
# 3. Update config.json
# ----------------------------------------------------------------------
Write-Step "3/6" "Updating config.json..."
$cfgJson = Get-Content $CONFIG -Raw | ConvertFrom-Json
$cfgJson.ace_step_dir    = $aceDir
$cfgJson.checkpoint_dir  = (Join-Path $aceDir "checkpoints")
$cfgJson | ConvertTo-Json -Depth 10 | Set-Content $CONFIG -Encoding utf8
Write-Ok "config.json updated"

# ----------------------------------------------------------------------
# 4. Model checkpoints
# ----------------------------------------------------------------------
Write-Step "4/6" "Checking model checkpoints..."
$ckpt = Join-Path $aceDir "checkpoints"
if (-not (Test-Path $ckpt)) { New-Item -ItemType Directory -Force -Path $ckpt | Out-Null }
$hasTurbo = (Get-ChildItem -Path $ckpt -Filter "*turbo*" -ErrorAction SilentlyContinue).Count -gt 0
if ($hasTurbo) {
    Write-Ok "Turbo model present"
} else {
    $download = Ask-User "Download ACE-Step turbo model (~5GB)? [Y/n]"
    if ($download -eq "" -or $download -match '^[Yy]') {
        Push-Location $aceDir
        # Match install.sh: use the acestep-download CLI exposed by pyproject.toml
        # (entry point: acestep.model_downloader:main). 5-15 min typical.
        uv run acestep-download
        $dlExit = $LASTEXITCODE
        Pop-Location
        if ($dlExit -eq 0 -and (Get-ChildItem -Path $ckpt -Filter "*turbo*" -ErrorAction SilentlyContinue).Count -gt 0) {
            Write-Ok "Model downloaded"
        } else {
            Write-Warn "Model download exited with code $dlExit. Retry later with:"
            Write-Host  "    cd `"$aceDir`"; uv run acestep-download"
        }
    } else {
        Write-Warn "Skipped. Music generation will fail until you run:"
        Write-Host  "    cd `"$aceDir`"; uv run acestep-download"
    }
}

# ----------------------------------------------------------------------
# 5. Symlinks (requires Developer Mode or Admin)
# ----------------------------------------------------------------------
Write-Step "5/6" "Creating skill symlinks..."
if (-not (Test-Path $TARGET_DIR)) { New-Item -ItemType Directory -Force -Path $TARGET_DIR | Out-Null }

$skillDirs = Get-ChildItem -Path $SKILLS_DIR -Directory | Where-Object { $_.Name -like "claude-music*" }
foreach ($s in $skillDirs) {
    $link = Join-Path $TARGET_DIR $s.Name
    if (Test-Path $link) {
        Remove-Item $link -Force -Recurse -ErrorAction SilentlyContinue
    }
    try {
        New-Item -ItemType SymbolicLink -Path $link -Target $s.FullName -ErrorAction Stop | Out-Null
        Write-Ok "Linked $($s.Name)"
    } catch {
        Write-Warn "Symlink failed for $($s.Name). Falling back to copy."
        Copy-Item -Path $s.FullName -Destination $link -Recurse -Force
        Write-Ok "Copied $($s.Name) (note: edits won't auto-sync — re-run installer after changes)"
    }
}

# ----------------------------------------------------------------------
# 6. Done
# ----------------------------------------------------------------------
Write-Step "6/6" "All done!"
Write-Host ""
Write-Host "  Next:"
Write-Host "    1. Open Claude Code"
Write-Host "    2. Try:   /music generate 'upbeat pop, female vocal'"
Write-Host ""
Write-Host "  Config:   $CONFIG"
Write-Host "  Skills:   $TARGET_DIR"
Write-Host ""
