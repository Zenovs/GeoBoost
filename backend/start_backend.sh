#!/usr/bin/env bash
# GeoBoost – Backend standalone starten (für Tests ohne Tauri)
# Öffne http://127.0.0.1:8765/docs für die interaktive API-Dokumentation
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

VENV_PY="$DIR/venv/bin/python3"
[[ ! -f "$VENV_PY" ]] && VENV_PY="$DIR/venv/Scripts/python.exe"
[[ ! -f "$VENV_PY" ]] && VENV_PY="$(command -v python3)"

echo "[GeoBoost] Backend starten..."
echo "[GeoBoost] API:   http://127.0.0.1:8765"
echo "[GeoBoost] Docs:  http://127.0.0.1:8765/docs"
echo ""

cd "$DIR"
"$VENV_PY" backend/main.py
