<div align="center">

# GeoBoost

**SEO & Performance Analyse-Tool für Agenturen**

Ein lokales Desktop-Tool, das SEO-Audits strukturiert erfasst, Websites analysiert und professionelle Berichte generiert – ohne Cloud, ohne Abo, vollständig auf deinem Computer.

[![macOS](https://img.shields.io/badge/macOS-12+-black?logo=apple&logoColor=white)](https://github.com/Zenovs/GeoBoost/releases/latest)
[![Windows](https://img.shields.io/badge/Windows-10+-0078D4?logo=windows&logoColor=white)](https://github.com/Zenovs/GeoBoost/releases/latest)
[![Linux](https://img.shields.io/badge/Linux-Ubuntu%2022+-E95420?logo=ubuntu&logoColor=white)](https://github.com/Zenovs/GeoBoost/releases/latest)
[![License](https://img.shields.io/badge/Lizenz-Proprietär-red)](./LICENSE)

</div>

---

## Was ist GeoBoost?

GeoBoost ist ein Desktop-Tool für SEO-Agenturen und Freelancer, mit dem du strukturierte SEO-Audits direkt auf deinem Computer durchführen und professionell dokumentieren kannst.

Du erfasst alle relevanten Daten in einem geführten 7-Schritte-Workflow – von der Kundenbefragung über Crawl-Analyse und Lighthouse-Tests bis zur finalen Empfehlung – und erzeugst mit einem Klick einen präsentationsfertigen Bericht als interaktive Website oder PDF.

**Alles bleibt lokal.** Keine Cloud, kein Abo, keine Datenweitergabe.

### Was GeoBoost kann

| | |
|---|---|
| **Audit-Workflow** | Geführter 7-Schritte-Prozess: Kickoff → Website-Analyse → Crawl → SEO → Performance → Fazit → Bericht |
| **Website-Crawl** | Erkennt fehlende Titles, H1-Tags, Meta-Descriptions, 404-Fehler, Weiterleitungen und langsame Seiten |
| **Technische SEO** | Site Health Score, Issue-Kategorisierung nach Schweregrad (Fehler / Warnungen / Hinweise) |
| **Performance** | Lighthouse/PageSpeed-Scores für Mobile & Desktop, Core Web Vitals (LCP, CLS, TBT) |
| **HTML-Bericht** | Interaktiver, responsiver Bericht mit 5 Themes, Grafiken und eingebautem Theme-Switcher |
| **PDF-Export** | Druckfertiges PDF – direkt aus dem Browser oder via WeasyPrint |
| **Mehrere Audits** | Unbegrenzte Projekte, alle Daten lokal in SQLite gespeichert |
| **Offline-fähig** | Funktioniert ohne Internetverbindung (ausser für externe APIs) |

---

## Download & Installation

### Desktop-App (empfohlen)

Lade die neueste Version direkt herunter – keine weiteren Abhängigkeiten nötig:

| Betriebssystem | Download |
|---|---|
| **macOS** (Apple Silicon, M1/M2/M3) | [GeoBoost.dmg (ARM)](https://github.com/Zenovs/GeoBoost/releases/latest) |
| **macOS** (Intel) | [GeoBoost.dmg (x64)](https://github.com/Zenovs/GeoBoost/releases/latest) |
| **Windows** (64-bit) | [GeoBoost-Setup.exe](https://github.com/Zenovs/GeoBoost/releases/latest) |
| **Linux** (Debian/Ubuntu) | [GeoBoost.deb](https://github.com/Zenovs/GeoBoost/releases/latest) |
| **Linux** (AppImage) | [GeoBoost.AppImage](https://github.com/Zenovs/GeoBoost/releases/latest) |

> Alle Downloads sind auf der [Releases-Seite](https://github.com/Zenovs/GeoBoost/releases/latest) verfügbar.

---

### Installation per Skript (Entwicklermodus)

Alternativ kann die App direkt aus dem Quellcode installiert und gestartet werden:

**Mac / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/Zenovs/GeoBoost/main/install.sh | bash
```

**Windows (PowerShell als Administrator):**
```powershell
irm https://raw.githubusercontent.com/Zenovs/GeoBoost/main/install.ps1 | iex
```

Das Skript installiert automatisch alle Abhängigkeiten (Python, Node.js, Rust) und richtet die App ein.

Nach der Installation starten:
```bash
cd ~/GeoBoost && ./start.sh
```

---

## Schnellstart

1. **App öffnen** – GeoBoost startet direkt, keine Konfiguration notwendig
2. **Neuen Audit erstellen** – Klick auf „Neue Analyse" im Dashboard
3. **Workflow durchlaufen** – 7 Schritte von Kickoff bis Bericht, jeder Schritt wird automatisch gespeichert
4. **Bericht generieren** – Theme wählen → HTML-Bericht oder PDF in Sekunden erstellt

---

## SEO-Audit Workflow

GeoBoost führt dich durch einen strukturierten 7-Schritte-Prozess:

```
Schritt 0 – Kickoff          Kundendaten, Ziele, Analysezeitraum, GA4 Property
Schritt 1 – Website & Kunden UX-Bewertung, Backlinks, Social Media, Wettbewerb
Schritt 2 – Technischer Scan Allgemeine technische Notizen und Beobachtungen
Schritt 3 – Crawl-Analyse    URL-Status, fehlende Meta-Daten, Weiterleitungen
Schritt 4 – SEO-Analyse      Site Health Score, Issues nach Schweregrad
Schritt 5 – Performance      Lighthouse Scores, Core Web Vitals, Top-3-Prioritäten
Schritt 6 – Bericht          Erkenntnisse, Empfehlungen → HTML + PDF Export
```

---

## Berichte & Themes

Der generierte HTML-Bericht ist vollständig interaktiv:

- **5 Themes:** Light, Dark, Nerd (Terminal), Color, Schnyder (Schwarz/Grün)
- **Theme-Wechsel live** direkt im Bericht – auch für den Kunden
- **SVG-Grafiken:** Gauge-Charts für Lighthouse-Scores, Donut-Chart für SEO-Issues, Balkendiagramm für Crawl-Status
- **Responsive:** funktioniert auf Desktop und Tablet
- **PDF-Export:** Floating-Button im Bericht oder als separate .pdf-Datei

---

## Tech-Stack

| Bereich | Technologie |
|---|---|
| Desktop-App | [Tauri 2](https://tauri.app) (Rust) |
| Frontend | React 18 + TypeScript + Vite |
| Backend | Python 3.10+ + FastAPI |
| Bericht | WeasyPrint + Jinja2 (PDF), selbstständiges HTML (Browser) |
| Datenbank | SQLite (lokal) |

---

## Datenschutz

- Alle Projektdaten bleiben **lokal** auf deinem Computer
- Keine Registrierung, kein Account, keine Telemetrie
- Einzige externe Verbindungen: Google APIs (PageSpeed Insights), falls konfiguriert

---

## Lizenz

Proprietär – wireon. Nicht für die Weitergabe bestimmt.
