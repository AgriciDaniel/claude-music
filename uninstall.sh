#!/usr/bin/env bash
# claude-music uninstaller
# Removes symlinks from ~/.claude/skills/ (does NOT delete the repo)
set -euo pipefail

TARGET_DIR="$HOME/.claude/skills"

echo "=== claude-music Uninstaller ==="
echo ""

REMOVED=0
for target in "$TARGET_DIR"/claude-music*; do
    if [ -L "$target" ]; then
        rm "$target"
        echo "  [REMOVED] $(basename "$target")"
        REMOVED=$((REMOVED + 1))
    elif [ -d "$target" ]; then
        echo "  [SKIPPED] $(basename "$target") (not a symlink — manual removal needed)"
    fi
done

echo ""
echo "Removed $REMOVED symlinks."
echo "The repo and generated music files are untouched."
echo "Output files remain at: ~/Music/claude-music-output/"
