#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
#  GeoBoost – One-Line Installer
#  Supports: macOS (Intel + Apple Silicon), Linux (Ubuntu/Debian/Arch), Windows (WSL)
#
#  Usage:
#    curl -fsSL https://raw.githubusercontent.com/Zenovs/GeoBoost/main/install.sh | bash
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${BLUE}[GeoBoost]${RESET} $*"; }
success() { echo -e "${GREEN}[✓]${RESET} $*"; }
warn()    { echo -e "${YELLOW}[!]${RESET} $*"; }
error()   { echo -e "${RED}[✗]${RESET} $*"; exit 1; }
step()    { echo -e "\n${BOLD}${BLUE}── $* ──${RESET}"; }

# ── Detect OS ─────────────────────────────────────────────────────────────────
OS=""
ARCH=$(uname -m)
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v apt-get &>/dev/null; then
        OS="debian"
    elif command -v pacman &>/dev/null; then
        OS="arch"
    elif command -v dnf &>/dev/null; then
        OS="fedora"
    else
        OS="linux"
    fi
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
else
    error "Nicht unterstütztes Betriebssystem: $OSTYPE"
fi

info "System erkannt: $OS ($ARCH)"

# ── Detect script location (git clone vs curl) ────────────────────────────────
REPO_DIR=""
if [[ -f "${BASH_SOURCE[0]:-./install.sh}" ]] && [[ -d "$(dirname "${BASH_SOURCE[0]}")"/.git ]]; then
    # Running from inside the cloned repo
    REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    info "Repo gefunden unter: $REPO_DIR"
else
    # Running via curl – clone the repo first
    step "Repository klonen"
    INSTALL_DIR="${HOME}/GeoBoost"
    if [[ -d "$INSTALL_DIR" ]]; then
        warn "Ordner $INSTALL_DIR existiert bereits – wird aktualisiert"
        git -C "$INSTALL_DIR" pull --ff-only 2>/dev/null || true
    else
        git clone https://github.com/Zenovs/GeoBoost.git "$INSTALL_DIR"
    fi
    REPO_DIR="$INSTALL_DIR"
fi

cd "$REPO_DIR"

# ── 1. Homebrew (macOS) ───────────────────────────────────────────────────────
if [[ "$OS" == "macos" ]]; then
    step "Homebrew prüfen"
    if ! command -v brew &>/dev/null; then
        info "Homebrew wird installiert..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv 2>/dev/null)"
    else
        success "Homebrew bereits installiert"
    fi
fi

# ── 2. Python ─────────────────────────────────────────────────────────────────
step "Python 3 prüfen"
PYTHON=""
for py in python3.12 python3.11 python3.10 python3 python; do
    if command -v "$py" &>/dev/null; then
        VER=$("$py" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        MAJOR=$(echo "$VER" | cut -d. -f1)
        MINOR=$(echo "$VER" | cut -d. -f2)
        if [[ "$MAJOR" -ge 3 && "$MINOR" -ge 10 ]]; then
            PYTHON="$py"
            success "Python $VER gefunden ($py)"
            break
        fi
    fi
done

if [[ -z "$PYTHON" ]]; then
    info "Python 3.10+ wird installiert..."
    case "$OS" in
        macos)   brew install python@3.12; PYTHON=python3.12 ;;
        debian)  sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv; PYTHON=python3 ;;
        arch)    sudo pacman -S --noconfirm python python-pip; PYTHON=python3 ;;
        fedora)  sudo dnf install -y python3 python3-pip; PYTHON=python3 ;;
        *)       error "Bitte Python 3.10+ manuell installieren: https://python.org" ;;
    esac
fi

# ── 3. Node.js ────────────────────────────────────────────────────────────────
step "Node.js prüfen"
if ! command -v node &>/dev/null; then
    info "Node.js wird installiert..."
    case "$OS" in
        macos)  brew install node ;;
        debian) curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs ;;
        arch)   sudo pacman -S --noconfirm nodejs npm ;;
        fedora) sudo dnf install -y nodejs ;;
        *)      error "Bitte Node.js manuell installieren: https://nodejs.org" ;;
    esac
else
    success "Node.js $(node --version) gefunden"
fi

# ── 4. Rust ───────────────────────────────────────────────────────────────────
step "Rust prüfen"
if ! command -v cargo &>/dev/null; then
    info "Rust wird installiert..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path
    # shellcheck source=/dev/null
    source "$HOME/.cargo/env"
else
    success "Rust $(rustc --version) gefunden"
fi
export PATH="$HOME/.cargo/bin:$PATH"

# ── 5. Tauri system dependencies (Linux only) ─────────────────────────────────
if [[ "$OS" == "debian" ]]; then
    step "Tauri Linux-Abhängigkeiten"
    sudo apt-get install -y \
        libwebkit2gtk-4.1-dev \
        libgtk-3-dev \
        libayatana-appindicator3-dev \
        librsvg2-dev \
        patchelf \
        libssl-dev \
        libxdo-dev \
        2>/dev/null || true
    success "Linux-Abhängigkeiten installiert"
fi

# ── 6. Python virtual environment + dependencies ─────────────────────────────
step "Python Abhängigkeiten installieren"
VENV_DIR="$REPO_DIR/venv"

if [[ ! -d "$VENV_DIR" ]]; then
    info "Virtuelle Umgebung erstellen..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

VENV_PY="$VENV_DIR/bin/python3"
[[ "$OS" == "windows" ]] && VENV_PY="$VENV_DIR/Scripts/python.exe"

info "Pakete installieren (requirements.txt)..."
"$VENV_PY" -m pip install --upgrade pip -q
"$VENV_PY" -m pip install -r "$REPO_DIR/backend/requirements.txt" -q
success "Python-Pakete installiert"

# ── 7. WeasyPrint system dependencies ────────────────────────────────────────
if [[ "$OS" == "macos" ]]; then
    # WeasyPrint needs pango + gobject on macOS
    for pkg in pango gobject-introspection cairo; do
        if ! brew list "$pkg" &>/dev/null; then
            brew install "$pkg" 2>/dev/null || true
        fi
    done
elif [[ "$OS" == "debian" ]]; then
    sudo apt-get install -y libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libffi-dev 2>/dev/null || true
fi

# ── 8. Ollama (optional) ──────────────────────────────────────────────────────
step "Ollama (lokale KI) prüfen"
if ! command -v ollama &>/dev/null; then
    warn "Ollama nicht gefunden. Die KI-Analyse benötigt Ollama."
    echo -e "   Installieren mit:"
    case "$OS" in
        macos)  echo -e "   ${YELLOW}brew install ollama${RESET}" ;;
        linux*|debian|arch|fedora) echo -e "   ${YELLOW}curl -fsSL https://ollama.ai/install.sh | sh${RESET}" ;;
    esac
    echo ""
    read -r -p "   Ollama jetzt installieren? [j/N] " INSTALL_OLLAMA
    if [[ "${INSTALL_OLLAMA,,}" == "j" || "${INSTALL_OLLAMA,,}" == "y" ]]; then
        case "$OS" in
            macos)  brew install ollama ;;
            *)      curl -fsSL https://ollama.ai/install.sh | sh ;;
        esac
        info "Llama 3.1 8B Modell wird heruntergeladen (~5 GB)..."
        ollama pull llama3.1:8b
        success "Ollama und Modell installiert"
    else
        warn "Ollama übersprungen. KI-Analyse wird im Demo-Modus laufen."
    fi
else
    success "Ollama gefunden"
    # Pull model if not present
    if ! ollama list 2>/dev/null | grep -q "llama3.1:8b"; then
        warn "Modell llama3.1:8b nicht gefunden"
        read -r -p "   Jetzt herunterladen (~5 GB)? [j/N] " DL
        if [[ "${DL,,}" == "j" || "${DL,,}" == "y" ]]; then
            ollama pull llama3.1:8b
            success "Modell heruntergeladen"
        fi
    else
        success "Modell llama3.1:8b vorhanden"
    fi
fi

# ── 9. npm install ────────────────────────────────────────────────────────────
step "Frontend-Abhängigkeiten"
cd "$REPO_DIR"
npm install -q
success "npm install abgeschlossen"

# ── 10. Schreibe start.sh ─────────────────────────────────────────────────────
step "Startskript erstellen"
cat > "$REPO_DIR/start.sh" << 'STARTSCRIPT'
#!/usr/bin/env bash
# GeoBoost – Starten (Dev-Modus)
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

VENV_PY="$DIR/venv/bin/python3"
[[ ! -f "$VENV_PY" ]] && VENV_PY="$DIR/venv/Scripts/python.exe"
[[ ! -f "$VENV_PY" ]] && VENV_PY=python3

# Start Python backend in background
echo "[GeoBoost] Backend wird gestartet..."
"$VENV_PY" backend/main.py &
BACKEND_PID=$!

# Wait for backend
for i in $(seq 1 20); do
    if curl -sf http://127.0.0.1:8765/api/health > /dev/null 2>&1; then
        echo "[GeoBoost] Backend bereit."
        break
    fi
    sleep 0.5
done

# Start Tauri dev
echo "[GeoBoost] App wird gestartet..."
npm run tauri dev

# Cleanup on exit
kill "$BACKEND_PID" 2>/dev/null || true
STARTSCRIPT

chmod +x "$REPO_DIR/start.sh"
success "start.sh erstellt"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}  GeoBoost erfolgreich installiert!         ${RESET}"
echo -e "${GREEN}${BOLD}════════════════════════════════════════════${RESET}"
echo ""
echo -e "  ${BOLD}Starten:${RESET}"
echo -e "  ${YELLOW}cd $REPO_DIR && ./start.sh${RESET}"
echo ""
echo -e "  ${BOLD}Nur Backend (für Browser-Tests):${RESET}"
echo -e "  ${YELLOW}cd $REPO_DIR && venv/bin/python3 backend/main.py${RESET}"
echo -e "  ${YELLOW}→ http://localhost:8765${RESET}"
echo ""
echo -e "  ${BOLD}Nächste Schritte:${RESET}"
echo -e "  1. Google Service Account JSON in Einstellungen hinterlegen"
echo -e "  2. GA4 Property ID bereithalten"
echo -e "  3. ./start.sh ausführen"
echo ""
