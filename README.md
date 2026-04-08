# GeoBoost – GA4 & SEO Analyse-Tool

Ein lokal installierbares Desktop-Tool für Mac, Windows und Linux. Analysiert Google Analytics 4 und SEO-Daten vollautomatisch und generiert ein präsentationsfertiges PDF.

---

## Installation (ein Befehl)

**Mac / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/Zenovs/GeoBoost/main/install.sh | bash
```

**Windows (PowerShell als Administrator):**
```powershell
irm https://raw.githubusercontent.com/Zenovs/GeoBoost/main/install.ps1 | iex
```

Das Skript installiert automatisch: Python 3, Node.js, Rust, alle Abhängigkeiten, optionales Ollama (lokale KI).

---

## Starten

```bash
cd ~/GeoBoost && ./start.sh
```

Oder nur das Backend (für Tests im Browser):
```bash
cd ~/GeoBoost && ./backend/start_backend.sh
# → http://127.0.0.1:8765/docs  (interaktive API-Dokumentation)
```

---

## Features

| Feature | Beschreibung |
|---|---|
| **Kickoff-Assistent** | 5-Schritt Fragekatalog für strukturierte Projekt-Erfassung |
| **Website-Crawling** | Vollständiger Crawl: Titles, H1, Meta, Alt-Texte, 404s, Duplikate |
| **PageSpeed Insights** | Mobile + Desktop Score, Core Web Vitals (LCP, CLS, TBT) |
| **GA4 Analytics** | Traffic, Conversions, Kanäle, Geräte, Landing Pages |
| **KI-Analyse (lokal)** | Ollama (Llama 3.1 / Mistral) generiert Massnahmenkatalog auf Deutsch |
| **PDF-Report** | Präsentationsfertiges PDF mit Charts, automatisch generiert |
| **Plugin-Architektur** | Neue Checks als Plugins in `plugins/checks/` erweiterbar |
| **Offline-fähig** | Alle Daten bleiben lokal, keine Cloud-Abhängigkeit |

---

## Setup nach der Installation

### 1. Google Service Account einrichten

1. [Google Cloud Console](https://console.cloud.google.com) öffnen
2. **APIs aktivieren:** *Google Analytics Data API* + *PageSpeed Insights API*
3. **Service Account erstellen:** IAM & Verwaltung → Dienstkonten → JSON-Key herunterladen
4. **GA4-Zugriff:** GA4 Admin → Property → Nutzerverwaltung → Service Account E-Mail als Betrachter hinzufügen
5. JSON-Datei in GeoBoost **Einstellungen** hochladen

### 2. Ollama-Modell (KI-Analyse)

```bash
ollama pull llama3.1:8b   # ~5 GB – empfohlen
# oder
ollama pull mistral:7b    # ~4 GB – gut für Deutsch
```

### 3. Erste Analyse starten

1. App starten: `./start.sh`
2. **Neue Analyse** → Kickoff ausfüllen (URL + GA4 Property ID)
3. Checks auswählen (oder Preset "Level 1 Standard" verwenden)
4. Analyse starten → nach ~20 Minuten PDF herunterladen

---

## Projektstruktur

```
GeoBoost/
├── backend/
│   ├── main.py              # FastAPI Server (Port 8765)
│   ├── database.py          # SQLite Projektverwaltung
│   ├── crawler.py           # Website-Crawling (requests + BeautifulSoup)
│   ├── ga4_api.py           # Google Analytics 4 API
│   ├── pagespeed_api.py     # PageSpeed Insights API
│   ├── analyzer.py          # KI-Analyse via Ollama
│   ├── pdf_generator.py     # PDF-Generierung (WeasyPrint + matplotlib)
│   └── requirements.txt
├── src/                     # React Frontend (Tauri)
│   ├── App.tsx
│   ├── api.ts               # API-Client
│   ├── styles.css
│   └── components/
│       ├── Dashboard.tsx    # Projekt-Übersicht
│       ├── Kickoff.tsx      # 5-Schritt Fragekatalog
│       ├── CheckSelector.tsx # Check-Auswahl + Presets
│       ├── AnalysisProgress.tsx # Live-Status + Ergebnisse
│       └── Settings.tsx     # Konfiguration
├── src-tauri/               # Tauri/Rust (Desktop-Wrapper)
│   ├── src/main.rs          # Startet Python-Backend automatisch
│   └── tauri.conf.json
├── templates/
│   └── report.html          # PDF-Template (Jinja2)
├── plugins/checks/          # Erweiterbare Plugin-Checks
├── config/
│   ├── config.json          # App-Konfiguration
│   └── cookie_selectors.json
├── install.sh               # One-Line Installer (Mac/Linux)
├── start.sh                 # App starten (Dev-Modus)
└── README.md
```

---

## Analyse-Presets

| Preset | Checks | Laufzeit |
|---|---|---|
| **Level 1 – Standard** | Crawl + PageSpeed + GA4 + KI + PDF | ~20 min |
| **Schnell-Check** | PageSpeed + GA4 Übersicht + PDF | ~8 min |
| **Nur Technisch** | Crawl + PageSpeed + PDF | ~10 min |
| **Custom** | Freie Auswahl | variabel |

---

## Tech-Stack

| Bereich | Technologie |
|---|---|
| Desktop-App | [Tauri 2](https://tauri.app) (Rust) |
| Frontend | React 18 + TypeScript + Vite |
| Backend | Python 3.10+ + FastAPI + uvicorn |
| Crawler | requests + BeautifulSoup4 |
| PDF | WeasyPrint + Jinja2 + matplotlib |
| Analytics | Google Analytics Data API v1beta |
| KI | [Ollama](https://ollama.ai) (lokal) |
| Datenbank | SQLite (via Python stdlib) |

---

## Hardware-Anforderungen

| | Minimum | Empfohlen |
|---|---|---|
| RAM | 8 GB | 16 GB |
| Speicher | 10 GB frei | 20 GB frei |
| Internet | Ja (für APIs) | Stabile Verbindung |
| OS | macOS 12+, Win 10+, Ubuntu 22+ | macOS 14+, Win 11, Ubuntu 24+ |

---

## Datenschutz

- Alle Projektdaten bleiben **lokal** auf dem Computer
- API-Zugangsdaten werden **verschlüsselt** gespeichert
- KI-Analyse läuft **vollständig lokal** via Ollama
- Einzige externe Verbindungen: Google APIs (GA4, PageSpeed)

---

## Lizenz

Proprietär – wireon. Nicht für die Weitergabe bestimmt.
