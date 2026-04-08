#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
#  GeoBoost – Saubere Neuinstallation
#  Sichert Konfiguration + Datenbank, löscht alles, klont neu, installiert.
#
#  Ausführen:
#    cd ~/Github/GeoBoost && bash reinstall.sh
# ═══════════════════════════════════════════════════════════════════════════════

set -eo pipefail

# Zuerst in ein sicheres Verzeichnis wechseln (falls cwd nicht mehr existiert)
cd "$HOME" 2>/dev/null || true

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${BLUE}[GeoBoost]${RESET} $*"; }
success() { echo -e "${GREEN}[✓]${RESET} $*"; }
warn()    { echo -e "${YELLOW}[!]${RESET} $*"; }
error()   { echo -e "${RED}[✗]${RESET} $*"; exit 1; }
step()    { echo -e "\n${BOLD}${BLUE}── $* ──${RESET}"; }

# ── Pfade ─────────────────────────────────────────────────────────────────────
REPO_URL="https://github.com/Zenovs/GeoBoost.git"

# Wenn via curl|bash gestartet, ist BASH_SOURCE nicht gesetzt → Standard verwenden
if [[ -n "${BASH_SOURCE[0]:-}" && "${BASH_SOURCE[0]}" != "bash" && -f "${BASH_SOURCE[0]}" ]]; then
    REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    # Bekannte Installationspfade prüfen
    if [[ -f "$HOME/.geoboost_path" ]]; then
        REPO_DIR="$(cat "$HOME/.geoboost_path")"
    elif [[ -d "$HOME/Github/GeoBoost" ]]; then
        REPO_DIR="$HOME/Github/GeoBoost"
    elif [[ -d "$HOME/GeoBoost" ]]; then
        REPO_DIR="$HOME/GeoBoost"
    else
        REPO_DIR="$HOME/Github/GeoBoost"
    fi
fi

PARENT_DIR="$(dirname "$REPO_DIR")"
REPO_NAME="$(basename "$REPO_DIR")"
BACKUP_DIR="${PARENT_DIR}/.geoboost_backup_$(date +%Y%m%d_%H%M%S)"

echo -e "\n${BOLD}GeoBoost – Saubere Neuinstallation${RESET}"
echo -e "Verzeichnis: ${YELLOW}$REPO_DIR${RESET}"
echo -e "Backup:      ${YELLOW}$BACKUP_DIR${RESET}\n"

# ── Bestätigung ───────────────────────────────────────────────────────────────
read -r -p "Wirklich alles löschen und neu installieren? (ja/nein): " CONFIRM
[[ "$CONFIRM" != "ja" ]] && { info "Abgebrochen."; exit 0; }

# ── 1. User-Daten sichern ─────────────────────────────────────────────────────
step "Konfiguration und Datenbank sichern"
mkdir -p "$BACKUP_DIR"

# config.json (API-Keys, Einstellungen)
[[ -f "$REPO_DIR/config/config.json" ]] && {
    cp "$REPO_DIR/config/config.json" "$BACKUP_DIR/config.json"
    success "config.json gesichert"
}

# geoboost.db (alle Projekte + Analysen)
[[ -f "$REPO_DIR/config/geoboost.db" ]] && {
    cp "$REPO_DIR/config/geoboost.db" "$BACKUP_DIR/geoboost.db"
    success "geoboost.db gesichert"
}

# Google Credentials
[[ -d "$REPO_DIR/config/credentials" ]] && {
    cp -r "$REPO_DIR/config/credentials" "$BACKUP_DIR/credentials"
    success "credentials/ gesichert"
}

success "Backup erstellt: $BACKUP_DIR"

# ── 2. Repo löschen und neu klonen ────────────────────────────────────────────
step "Altes Verzeichnis löschen"
cd "$PARENT_DIR"
rm -rf "$REPO_DIR"
success "Gelöscht: $REPO_DIR"

step "Aktuelles Repository klonen"
git clone "$REPO_URL" "$REPO_NAME"
cd "$REPO_DIR"
success "Geklont: $(git log --oneline -1)"

# ── 3. Pfad-Datei schreiben (damit die App backend/main.py findet) ─────────────
step "App-Pfad registrieren"
echo "$REPO_DIR" > "$HOME/.geoboost_path"
success "Pfad gespeichert: $HOME/.geoboost_path → $REPO_DIR"

# ── 4. User-Daten wiederherstellen ────────────────────────────────────────────
step "Konfiguration wiederherstellen"
mkdir -p "$REPO_DIR/config"

[[ -f "$BACKUP_DIR/config.json" ]] && {
    cp "$BACKUP_DIR/config.json" "$REPO_DIR/config/config.json"
    success "config.json wiederhergestellt"
}

[[ -f "$BACKUP_DIR/geoboost.db" ]] && {
    cp "$BACKUP_DIR/geoboost.db" "$REPO_DIR/config/geoboost.db"
    success "geoboost.db wiederhergestellt (alle Projekte + Analysen erhalten)"
}

[[ -d "$BACKUP_DIR/credentials" ]] && {
    cp -r "$BACKUP_DIR/credentials" "$REPO_DIR/config/credentials"
    success "credentials/ wiederhergestellt"
}

# ── 5. Python Virtual Environment ─────────────────────────────────────────────
step "Python Virtual Environment einrichten"

# Python-Binary ermitteln
PYTHON=""
for py in python3.12 python3.11 python3.10 python3.9 python3; do
    if command -v "$py" &>/dev/null; then
        PYTHON="$py"
        break
    fi
done
[[ -z "$PYTHON" ]] && error "Python 3 nicht gefunden. Bitte installieren."
success "Python: $($PYTHON --version)"

"$PYTHON" -m venv "$REPO_DIR/venv"
VENV_PY="$REPO_DIR/venv/bin/python3"
success "venv erstellt"

"$VENV_PY" -m pip install --upgrade pip -q
"$VENV_PY" -m pip install -r "$REPO_DIR/backend/requirements.txt" -q
success "Python-Abhängigkeiten installiert"

# ── 6. Node / npm ─────────────────────────────────────────────────────────────
step "Node-Abhängigkeiten installieren"
command -v npm &>/dev/null || error "npm nicht gefunden. Node.js installieren."
success "Node: $(node --version) / npm: $(npm --version)"

cd "$REPO_DIR"
npm install --silent
success "npm install abgeschlossen"

# ── 7. Rust / Cargo prüfen ────────────────────────────────────────────────────
step "Rust prüfen"
if ! command -v cargo &>/dev/null; then
    [[ -f "$HOME/.cargo/env" ]] && source "$HOME/.cargo/env"
fi
command -v cargo &>/dev/null || error "Rust/Cargo nicht gefunden. Bitte 'rustup' installieren: https://rustup.rs"
export PATH="$HOME/.cargo/bin:$PATH"
success "Rust: $(rustc --version)"

# ── 8. App bauen ──────────────────────────────────────────────────────────────
step "GeoBoost App bauen (dauert 2–5 Minuten)"
cd "$REPO_DIR"
npm run tauri build -- --bundles app 2>&1 | grep -E "Compiling|Finished|error|warning: unused" | tail -20
success "Build abgeschlossen"

# ── 9. App in /Applications installieren ──────────────────────────────────────
step "App in /Applications installieren"
APP_BUNDLE="$(find "$REPO_DIR/src-tauri/target/release/bundle/macos" -name "*.app" 2>/dev/null | head -1)"

if [[ -z "$APP_BUNDLE" ]]; then
    error "App-Bundle nicht gefunden. Build fehlgeschlagen?"
fi

APP_NAME="$(basename "$APP_BUNDLE")"

# Alte Version entfernen falls vorhanden
[[ -d "/Applications/$APP_NAME" ]] && {
    warn "Alte Version wird entfernt: /Applications/$APP_NAME"
    rm -rf "/Applications/$APP_NAME"
}

cp -r "$APP_BUNDLE" "/Applications/$APP_NAME"
success "Installiert: /Applications/$APP_NAME"

# ── 10. Fertig ────────────────────────────────────────────────────────────────
echo -e "\n${GREEN}${BOLD}✓ Neuinstallation abgeschlossen!${RESET}"
echo -e ""
echo -e "  App installiert: ${YELLOW}/Applications/$APP_NAME${RESET}"
echo -e "  Backup liegt unter: ${YELLOW}$BACKUP_DIR${RESET}"
echo -e ""
echo -e "  GeoBoost jetzt über Launchpad oder Spotlight starten."
echo -e ""
echo -e "  Oder Dev-Modus:"
echo -e "  ${YELLOW}cd $REPO_DIR && npm run tauri dev${RESET}"
