#!/usr/bin/env bash
# claude-music — Interactive Installer
# Works for beginners and experts alike. Asks questions, installs everything.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"
TARGET_DIR="$HOME/.claude/skills"
CONFIG="$SKILLS_DIR/claude-music/config.json"
DEFAULT_ACE_DIR="$HOME/ACE-Step-1.5"

# Colors for friendly output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

print_step() { echo -e "\n${BLUE}${BOLD}[$1]${NC} $2"; }
print_ok()   { echo -e "  ${GREEN}[OK]${NC} $1"; }
print_warn() { echo -e "  ${YELLOW}[!]${NC} $1"; }
print_err()  { echo -e "  ${RED}[ERROR]${NC} $1"; }
ask()        { echo -en "  ${BOLD}$1${NC} "; read -r REPLY; }

echo -e "${BOLD}"
echo "  ================================================================"
echo "      claude-music — AI Music Production for Claude Code"
echo "      Powered by ACE-Step 1.5"
echo "  ================================================================"
echo -e "${NC}"
echo "  This installer will set up everything you need."
echo "  Just answer a few questions — no technical knowledge required."
echo ""

# ──────────────────────────────────────────────────────────────────────
# Step 1: Check basic prerequisites
# ──────────────────────────────────────────────────────────────────────
print_step "1/6" "Checking your system..."

# Check git
if command -v git &>/dev/null; then
    print_ok "git found"
else
    print_err "git not found. Please install git first:"
    echo "       sudo apt install git    (Linux)"
    echo "       brew install git        (macOS)"
    exit 1
fi

# Check Python
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 --version 2>&1)
    print_ok "Python: $PY_VER"
else
    print_err "Python 3 not found. Please install Python 3.11+ first."
    exit 1
fi

# Check NVIDIA GPU
if command -v nvidia-smi &>/dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits 2>/dev/null | head -1)
    GPU_VRAM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1)
    print_ok "GPU: $GPU_NAME (${GPU_VRAM}MB VRAM)"
else
    print_warn "No NVIDIA GPU detected. ACE-Step can run on CPU but will be very slow."
    echo "         For best results, use a system with an NVIDIA GPU (4GB+ VRAM)."
fi

# Check ffmpeg
if command -v ffmpeg &>/dev/null; then
    print_ok "FFmpeg found"
else
    print_warn "FFmpeg not found. Installing..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y ffmpeg 2>/dev/null && print_ok "FFmpeg installed" || print_warn "Could not auto-install FFmpeg. Install manually: sudo apt install ffmpeg"
    elif command -v brew &>/dev/null; then
        brew install ffmpeg 2>/dev/null && print_ok "FFmpeg installed" || print_warn "Could not auto-install FFmpeg. Install manually: brew install ffmpeg"
    else
        print_warn "Please install FFmpeg manually for your system."
    fi
fi

# Check uv
if command -v uv &>/dev/null; then
    print_ok "uv found ($(uv --version 2>&1 | head -1))"
else
    print_warn "uv (Python package manager) not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh 2>/dev/null
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    if command -v uv &>/dev/null; then
        print_ok "uv installed"
    else
        print_err "Could not install uv. Visit: https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi
fi

# Check Claude Code
if command -v claude &>/dev/null; then
    print_ok "Claude Code found"
else
    print_warn "Claude Code CLI not detected (may be running as VS Code extension — that's fine)"
fi

# ──────────────────────────────────────────────────────────────────────
# Step 2: Find or install ACE-Step 1.5
# ──────────────────────────────────────────────────────────────────────
print_step "2/6" "Setting up ACE-Step 1.5 (the AI music engine)..."

ACE_STEP_DIR=""

# Check if config already has a valid path
if [ -f "$CONFIG" ]; then
    EXISTING=$(python3 -c "import json; print(json.load(open('$CONFIG')).get('ace_step_dir',''))" 2>/dev/null || echo "")
    if [ -n "$EXISTING" ] && [ "$EXISTING" != "CHANGE_ME" ] && [ -d "$EXISTING" ]; then
        print_ok "Found existing ACE-Step at: $EXISTING"
        ACE_STEP_DIR="$EXISTING"
    fi
fi

# Search common locations
if [ -z "$ACE_STEP_DIR" ]; then
    for candidate in \
        "$HOME/ACE-Step-1.5" \
        "$HOME/Desktop/Local-AI-Models/ACE-Step-1.5" \
        "$HOME/Desktop/ACE-Step-1.5" \
        "$HOME/Documents/ACE-Step-1.5" \
        "$HOME/ai-models/ACE-Step-1.5" \
        "/opt/ACE-Step-1.5"; do
        if [ -d "$candidate" ] && [ -f "$candidate/pyproject.toml" ]; then
            print_ok "Found ACE-Step at: $candidate"
            ACE_STEP_DIR="$candidate"
            break
        fi
    done
fi

# If not found, offer to install
if [ -z "$ACE_STEP_DIR" ]; then
    echo ""
    echo "  ACE-Step 1.5 is the AI engine that generates music."
    echo "  It's free and open-source, but needs to be downloaded (~5GB)."
    echo ""
    ask "Would you like me to install ACE-Step 1.5 for you? (Y/n):"
    if [[ "${REPLY:-y}" =~ ^[Yy]?$ ]]; then
        echo ""
        ask "Where should I install it? (press Enter for $DEFAULT_ACE_DIR):"
        ACE_STEP_DIR="${REPLY:-$DEFAULT_ACE_DIR}"

        echo ""
        echo "  Downloading ACE-Step 1.5... (this may take a few minutes)"
        if git clone https://github.com/ace-step/ACE-Step-1.5.git "$ACE_STEP_DIR" 2>&1 | tail -3; then
            print_ok "ACE-Step downloaded to $ACE_STEP_DIR"
        else
            print_err "Download failed. Check your internet connection and try again."
            exit 1
        fi

        echo "  Installing Python dependencies..."
        cd "$ACE_STEP_DIR"
        if uv sync 2>&1 | tail -3; then
            print_ok "Dependencies installed"
        else
            print_warn "Some dependencies may have issues (may still work)"
        fi
        cd "$SCRIPT_DIR"
    else
        echo ""
        ask "Enter the path to your existing ACE-Step 1.5 installation:"
        ACE_STEP_DIR="$REPLY"
        if [ ! -d "$ACE_STEP_DIR" ] || [ ! -f "$ACE_STEP_DIR/pyproject.toml" ]; then
            print_err "Not a valid ACE-Step installation: $ACE_STEP_DIR"
            echo "         Looking for a directory containing pyproject.toml"
            exit 1
        fi
        print_ok "Using ACE-Step at: $ACE_STEP_DIR"
    fi
fi

# ──────────────────────────────────────────────────────────────────────
# Step 3: Download model checkpoints
# ──────────────────────────────────────────────────────────────────────
print_step "3/6" "Checking AI model files..."

MODELS_OK=true
for model in "acestep-v15-turbo" "vae" "Qwen3-Embedding-0.6B"; do
    if [ -d "$ACE_STEP_DIR/checkpoints/$model" ]; then
        print_ok "$model"
    else
        MODELS_OK=false
        print_warn "$model — not found"
    fi
done

if [ "$MODELS_OK" = false ]; then
    echo ""
    echo "  Some AI models need to be downloaded (~5GB total)."
    echo "  This is required for music generation to work."
    echo ""
    ask "Download missing models now? (Y/n):"
    if [[ "${REPLY:-y}" =~ ^[Yy]?$ ]]; then
        echo "  Downloading models... (this may take 5-15 minutes)"
        cd "$ACE_STEP_DIR"
        if uv run acestep-download 2>&1 | tail -5; then
            print_ok "Models downloaded"
        else
            print_warn "Some models may not have downloaded. You can retry later with:"
            echo "         cd $ACE_STEP_DIR && uv run acestep-download"
        fi
        cd "$SCRIPT_DIR"
    else
        print_warn "Skipping model download. Music generation won't work until models are downloaded."
        echo "         Run later: cd $ACE_STEP_DIR && uv run acestep-download"
    fi
fi

# ──────────────────────────────────────────────────────────────────────
# Step 4: Write config.json
# ──────────────────────────────────────────────────────────────────────
print_step "4/6" "Saving your configuration..."

python3 -c "
import json
config_path = '$CONFIG'
with open(config_path) as f:
    config = json.load(f)
config['ace_step_dir'] = '$ACE_STEP_DIR'
config['checkpoint_dir'] = '$ACE_STEP_DIR/checkpoints'
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)
    f.write('\n')
print('  config.json updated')
"
print_ok "ACE-Step path: $ACE_STEP_DIR"
print_ok "Output folder: ~/Music/claude-music-output/"

# ──────────────────────────────────────────────────────────────────────
# Step 5: Install skill symlinks
# ──────────────────────────────────────────────────────────────────────
print_step "5/6" "Installing Claude Code skill..."

mkdir -p "$TARGET_DIR"
INSTALLED=0

for skill_dir in "$SKILLS_DIR"/claude-music*; do
    skill_name=$(basename "$skill_dir")
    target="$TARGET_DIR/$skill_name"

    # Remove existing (symlink or directory)
    if [ -L "$target" ]; then
        rm "$target"
    elif [ -d "$target" ]; then
        backup="$target.backup.$(date +%Y%m%d%H%M%S)"
        mv "$target" "$backup"
    fi

    ln -s "$skill_dir" "$target"
    INSTALLED=$((INSTALLED + 1))
done

# Make scripts executable
chmod +x "$SKILLS_DIR/claude-music/scripts/"*.sh "$SKILLS_DIR/claude-music/scripts/"*.py 2>/dev/null || true

# Create output directory
mkdir -p "$HOME/Music/claude-music-output"

print_ok "$INSTALLED skills installed"

# ──────────────────────────────────────────────────────────────────────
# Step 6: Verify
# ──────────────────────────────────────────────────────────────────────
print_step "6/6" "Verifying installation..."

ALL_OK=true

# Check symlinks
if [ -L "$TARGET_DIR/claude-music" ]; then
    print_ok "Skill linked to Claude Code"
else
    print_err "Skill symlink missing"
    ALL_OK=false
fi

# Check ACE-Step accessible
if [ -d "$ACE_STEP_DIR" ] && [ -f "$ACE_STEP_DIR/pyproject.toml" ]; then
    print_ok "ACE-Step accessible"
else
    print_err "ACE-Step not accessible at $ACE_STEP_DIR"
    ALL_OK=false
fi

# Check at least turbo model exists
if [ -d "$ACE_STEP_DIR/checkpoints/acestep-v15-turbo" ]; then
    print_ok "Turbo model ready"
else
    print_warn "Turbo model not yet downloaded (run: cd $ACE_STEP_DIR && uv run acestep-download)"
fi

echo ""
if [ "$ALL_OK" = true ]; then
    echo -e "${GREEN}${BOLD}  ================================================================"
    echo "      Installation Complete!"
    echo "  ================================================================${NC}"
    echo ""
    echo "  Your music will be saved to: ~/Music/claude-music-output/"
    echo ""
    echo -e "  ${BOLD}How to use:${NC}"
    echo "  Open Claude Code and type any of these:"
    echo ""
    echo "    \"Generate a lo-fi hip-hop beat\""
    echo "    \"Make me a pop song with lyrics about summer\""
    echo "    \"/music generate --caption 'jazz piano' --duration 60\""
    echo "    \"/music random\"  (surprise me!)"
    echo ""
    echo -e "  ${BOLD}To uninstall:${NC} bash $(pwd)/uninstall.sh"
else
    echo -e "${YELLOW}${BOLD}  Installation finished with warnings. See above for details.${NC}"
fi
echo ""
