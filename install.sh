#!/usr/bin/env bash
# claude-music installer
# Creates symlinks from ~/.claude/skills/ to this repo's skills/ directory
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"
TARGET_DIR="$HOME/.claude/skills"

echo "=== claude-music Installer ==="
echo ""

# Check prerequisites
if [ ! -d "$SKILLS_DIR/claude-music" ]; then
    echo "ERROR: skills/ directory not found. Run this from the repo root."
    exit 1
fi

# Create target directory if needed
mkdir -p "$TARGET_DIR"

# ACE-Step check (read from config.json)
CONFIG="$SKILLS_DIR/claude-music/config.json"
if [ -f "$CONFIG" ] && command -v python3 &>/dev/null; then
    ACE_STEP_DIR=$(python3 -c "import json; print(json.load(open('$CONFIG'))['ace_step_dir'])" 2>/dev/null)
fi
ACE_STEP_DIR="${ACE_STEP_DIR:-}"
if [ -z "$ACE_STEP_DIR" ] || [ ! -d "$ACE_STEP_DIR" ]; then
    echo "NOTE: ACE-Step 1.5 not found at ${ACE_STEP_DIR:-<not configured>}"
    echo "Edit skills/claude-music/config.json and set ace_step_dir to your ACE-Step path."
    echo ""
fi

# Install skill directories as symlinks
INSTALLED=0
SKIPPED=0

for skill_dir in "$SKILLS_DIR"/claude-music*; do
    skill_name=$(basename "$skill_dir")
    target="$TARGET_DIR/$skill_name"

    if [ -L "$target" ]; then
        # Existing symlink — update it
        rm "$target"
        ln -s "$skill_dir" "$target"
        echo "  [UPDATED] $skill_name -> $skill_dir"
        INSTALLED=$((INSTALLED + 1))
    elif [ -d "$target" ]; then
        # Existing real directory — back up and replace
        backup="$target.backup.$(date +%Y%m%d%H%M%S)"
        mv "$target" "$backup"
        ln -s "$skill_dir" "$target"
        echo "  [REPLACED] $skill_name (backup: $backup)"
        INSTALLED=$((INSTALLED + 1))
    else
        # New installation
        ln -s "$skill_dir" "$target"
        echo "  [INSTALLED] $skill_name"
        INSTALLED=$((INSTALLED + 1))
    fi
done

# Make scripts executable
chmod +x "$SKILLS_DIR/claude-music/scripts/"*.sh "$SKILLS_DIR/claude-music/scripts/"*.py 2>/dev/null || true

# Create output directory
mkdir -p "$HOME/Music/claude-music-output"

echo ""
echo "=== Installation Complete ==="
echo "  Skills installed: $INSTALLED"
echo "  Output directory: ~/Music/claude-music-output/"
echo ""
echo "Next steps:"
echo "  1. Install ACE-Step 1.5 (if not already installed)"
echo "  2. Update config.json with your ACE-Step path (if different from default)"
echo "  3. Run: bash ~/.claude/skills/claude-music/scripts/setup.sh"
echo "  4. Use /music in Claude Code to start generating!"
echo ""
echo "To uninstall: bash $(dirname "$0")/uninstall.sh"
