#!/usr/bin/env bash
# GeoBoost – Starten (Dev-Modus)
# Startet Python-Backend + Tauri-Frontend
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# ── Find Python in venv ───────────────────────────────────────────────────────
VENV_PY="$DIR/venv/bin/python3"
if [[ ! -f "$VENV_PY" ]]; then
    VENV_PY="$DIR/venv/Scripts/python.exe"   # Windows
fi
if [[ ! -f "$VENV_PY" ]]; then
    VENV_PY="$(command -v python3 || command -v python)"
fi

echo "[GeoBoost] Verwende Python: $VENV_PY"

# ── Kill any leftover backend ─────────────────────────────────────────────────
pkill -f "backend/main.py" 2>/dev/null || true
sleep 0.3

# ── Start Python backend ──────────────────────────────────────────────────────
echo "[GeoBoost] Backend wird gestartet (Port 8765)..."
"$VENV_PY" backend/main.py &
BACKEND_PID=$!

# ── Wait up to 10 s ───────────────────────────────────────────────────────────
READY=0
for i in $(seq 1 40); do
    if curl -sf http://127.0.0.1:8765/api/health > /dev/null 2>&1; then
        READY=1
        break
    fi
    sleep 0.25
done

if [[ "$READY" -eq 1 ]]; then
    echo "[GeoBoost] Backend bereit → http://127.0.0.1:8765"
else
    echo "[GeoBoost] WARNUNG: Backend antwortet nicht – trotzdem weiter..."
fi

# ── Start Tauri dev ───────────────────────────────────────────────────────────
echo "[GeoBoost] Tauri App wird gestartet..."
npm run tauri dev

# ── Cleanup on exit ───────────────────────────────────────────────────────────
echo "[GeoBoost] App beendet – Backend wird gestoppt..."
kill "$BACKEND_PID" 2>/dev/null || true
