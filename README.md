# GA4 SEO Analyzer

Ein lokal installierbares Desktop-Tool für standardisierte Google Analytics 4 und SEO-Analysen mit automatischer PDF-Generierung.

## Features

- **Kickoff-Assistent**: Strukturierter Fragekatalog für Analyse-Setup
- **Automatisierte Datenerhebung**: Website-Crawling, GA4 API, PageSpeed Insights
- **KI-gestützte Analyse**: Lokale Ollama-Integration für professionelle Berichte
- **PDF-Generierung**: Modernes, präsentationsfertiges PDF
- **Cross-Platform**: Mac, Windows, Linux

## Installation

1. Klone das Repository:
   ```bash
   git clone https://github.com/yourusername/ga4-seo-analyzer.git
   cd ga4-seo-analyzer
   ```

2. Führe das Installationsskript aus:
   ```bash
   ./install.sh
   ```

   Oder manuell:
   - Installiere Python 3, Node.js, Rust
   - Installiere Ollama und pull llama3.1:8b
   - `cd backend && pip install -r requirements.txt`
   - `npm install`
   - `npm run tauri build`

3. Konfiguriere APIs:
   - Google Cloud Console: GA4 Data API, PageSpeed API aktivieren
   - Service Account Key herunterladen
   - In `config/config.json` eintragen

## Verwendung

1. Starte die App: `npm run tauri dev`
2. Durchlaufe den Kickoff-Assistenten
3. Wähle Checks aus
4. Warte auf automatische Analyse
5. Öffne das generierte PDF

## Projektstruktur

```
ga4-seo-analyzer/
├── src/                    # React Frontend
├── src-tauri/             # Rust Backend
├── backend/               # Python Scripts
│   ├── crawler.py
│   ├── ga4_api.py
│   ├── pagespeed_api.py
│   ├── analyzer.py
│   └── pdf_generator.py
├── plugins/checks/        # Erweiterbare Checks
├── templates/             # PDF Templates
├── config/                # Konfiguration
└── install.sh             # Installationsskript
```

## Entwicklung

- Frontend: `npm run dev`
- Backend: Python-Scripts in `backend/`
- Build: `npm run tauri build`

## Lizenz

Proprietär - wireon