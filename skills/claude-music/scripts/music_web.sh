#!/usr/bin/env bash
# claude-music web dashboard launcher.
# Starts the stdlib-only server (system python3, no uv needed for the server
# itself) and opens the dashboard in the default browser.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEBAPP_DIR="$SCRIPT_DIR/../webapp"
PORT="${1:-8765}"

if ! command -v python3 >/dev/null 2>&1; then
    echo '{"success": false, "error": "python3 not found", "suggestion": "Install Python 3 first"}'
    exit 1
fi

CONFIG="$SCRIPT_DIR/../config.json"
if [ ! -f "$CONFIG" ] || grep -q "CHANGE_ME" "$CONFIG" 2>/dev/null; then
    echo "[!] ACE-Step is not configured yet. The dashboard will start in setup mode." >&2
    echo "    Run install.sh to enable generation." >&2
fi

python3 "$WEBAPP_DIR/server.py" --port "$PORT" &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' INT TERM EXIT

# Wait for the server to bind (it may pick a nearby port when busy).
URL=""
for _ in $(seq 1 25); do
    for p in $(seq "$PORT" $((PORT + 10))); do
        if command -v curl >/dev/null 2>&1 &&
           curl -sf -o /dev/null "http://127.0.0.1:$p/api/status" 2>/dev/null; then
            URL="http://127.0.0.1:$p"
            break 2
        fi
    done
    kill -0 "$SERVER_PID" 2>/dev/null || { echo "[ERROR] Server exited early" >&2; exit 1; }
    sleep 0.2
done

if [ -n "$URL" ]; then
    echo "claude-music web: $URL"
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$URL" >/dev/null 2>&1 || true
    elif command -v open >/dev/null 2>&1; then
        open "$URL" >/dev/null 2>&1 || true
    fi
else
    echo "claude-music web: starting on http://127.0.0.1:$PORT (open it manually)"
fi

echo "Press Ctrl-C to stop."
wait "$SERVER_PID"
