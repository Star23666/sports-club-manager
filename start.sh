#!/usr/bin/env bash
# Sports Club Backend — One-Click Launcher (macOS / Linux)
# Usage: bash start.sh   or   chmod +x start.sh && ./start.sh

set -euo pipefail

echo "========================================"
echo " Sports Club Backend Launcher"
echo "========================================"
echo ""

# 1. Find Python
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON="$cmd"
        break
    fi
done
if [ -z "$PYTHON" ]; then
    echo "ERROR: Python not found. Please install Python 3.10+."
    echo "https://www.python.org/downloads/"
    exit 1
fi
echo "[OK] $($PYTHON --version)"

# 2. Check/create venv
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Creating virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
    echo "[OK] venv created"
fi

# 3. Install dependencies
echo "Installing dependencies..."
"$VENV_PYTHON" -m pip install -q -r "$SCRIPT_DIR/python/requirements.txt" 2>/dev/null || \
    "$VENV_PYTHON" -m pip install -r "$SCRIPT_DIR/python/requirements.txt"
echo "[OK] Dependencies ready"

# 4. Start backend (SQLite mode — no MySQL needed)
export DB_TYPE=sqlite

echo ""
echo "========================================"
echo " Starting backend with SQLite..."
echo " API docs: http://localhost:8081/docs"
echo "========================================"
echo ""

cd "$SCRIPT_DIR/python"
exec "$VENV_PYTHON" -m uvicorn app.main:app --app-dir "$SCRIPT_DIR/python" --host 0.0.0.0 --port 8081 --reload
