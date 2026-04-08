"""
GeoBoost – FastAPI Backend Server
Läuft auf localhost:8765
"""

import json
import os
import sys
import asyncio
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# ── macOS: point cffi/WeasyPrint at Homebrew libs ────────────────────────────
_brew_lib = "/opt/homebrew/lib"
if sys.platform == "darwin" and os.path.isdir(_brew_lib):
    _existing = os.environ.get("DYLD_LIBRARY_PATH", "")
    if _brew_lib not in _existing:
        os.environ["DYLD_LIBRARY_PATH"] = f"{_brew_lib}:{_existing}".strip(":")
        # Also create the expected symlink name if missing
        _src = Path(_brew_lib) / "libgobject-2.0.0.dylib"
        _dst = Path(_brew_lib) / "libgobject-2.0-0.dylib"
        if _src.exists() and not _dst.exists():
            try:
                _dst.symlink_to(_src)
            except OSError:
                pass

from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Make sure backend dir is in path
sys.path.insert(0, str(Path(__file__).parent))

from database import Database, Project, Analysis
from crawler import WebsiteCrawler
from ga4_api import GA4API
from pagespeed_api import PageSpeedAPI
from speedtest import SpeedTester
from analyzer import KIAnalyzer
from pdf_generator import PDFGenerator

# Config path (relative to project root)
CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.json"

app = FastAPI(title="GeoBoost API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()


DEFAULTS_PATH = Path(__file__).parent.parent / "config" / "config.defaults.json"


def load_config() -> Dict[str, Any]:
    # Start from shipped defaults
    defaults: Dict[str, Any] = {}
    if DEFAULTS_PATH.exists():
        with open(DEFAULTS_PATH) as f:
            defaults = json.load(f)
    # Overlay with user config (never overwritten by git pull)
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            user = json.load(f)
        defaults.update(user)
    return defaults


def save_config(config: Dict[str, Any]):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


# ─── Models ───────────────────────────────────────────────────────────────────

class KickoffData(BaseModel):
    website_url: str
    ga4_property_id: str
    project_name: str
    analysis_period: str = "last_28_days"
    primary_goal: str = ""
    main_action: str = ""
    lead_value: Optional[float] = None
    target_audience: str = ""
    audience_type: str = "B2B"
    seasonality: bool = False
    seasonality_notes: str = ""
    active_campaigns: List[str] = []
    expected_channels: List[str] = []
    known_issues: str = ""
    tech_feedback: str = ""
    recent_changes: bool = False
    recent_changes_notes: str = ""
    responsible_person: str = ""
    ga4_setup_by: str = "Intern"
    third_party_tools: List[str] = []
    competitors: str = ""
    main_question: str = ""
    use_search_console: bool = False
    search_console_url: Optional[str] = None


class CheckConfig(BaseModel):
    crawling: bool = True
    pagespeed: bool = True
    speedtest: bool = True
    ga4_traffic: bool = True
    ga4_channels: bool = True
    ga4_landingpages: bool = True
    ga4_devices: bool = True
    search_console: bool = False
    ai_analysis: bool = True
    pdf_report: bool = True


class StartAnalysisRequest(BaseModel):
    kickoff: KickoffData
    checks: CheckConfig


class ConfigUpdate(BaseModel):
    storage_path: Optional[str] = None
    google_credentials_path: Optional[str] = None
    pagespeed_api_key: Optional[str] = None
    ollama_model: Optional[str] = None
    crawler_max_depth: Optional[int] = None
    crawler_max_urls: Optional[int] = None
    primary_color: Optional[str] = None
    accent_color: Optional[str] = None
    company_name: Optional[str] = None
    company_contact: Optional[str] = None


# ─── Health ───────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0", "name": "GeoBoost"}


# ─── Version & Update ─────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent

@app.get("/api/version")
def get_version():
    """Returns current git commit info."""
    import subprocess
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(PROJECT_ROOT), text=True, stderr=subprocess.DEVNULL
        ).strip()
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(PROJECT_ROOT), text=True, stderr=subprocess.DEVNULL
        ).strip()
        date = subprocess.check_output(
            ["git", "log", "-1", "--format=%cd", "--date=format:%d.%m.%Y %H:%M"],
            cwd=str(PROJECT_ROOT), text=True, stderr=subprocess.DEVNULL
        ).strip()
        msg = subprocess.check_output(
            ["git", "log", "-1", "--format=%s"],
            cwd=str(PROJECT_ROOT), text=True, stderr=subprocess.DEVNULL
        ).strip()
        return {"commit": commit, "branch": branch, "date": date, "message": msg, "error": None}
    except Exception as e:
        return {"commit": "unbekannt", "branch": "–", "date": "–", "message": "–", "error": str(e)}


@app.post("/api/update")
async def run_update():
    """Pulls latest code from git and reinstalls Python dependencies."""
    import subprocess
    log_lines: List[str] = []
    success = True

    def run(cmd: List[str], cwd: str = str(PROJECT_ROOT)) -> str:
        try:
            out = subprocess.check_output(
                cmd, cwd=cwd, text=True,
                stderr=subprocess.STDOUT, timeout=120
            )
            return out.strip()
        except subprocess.CalledProcessError as e:
            return f"FEHLER: {e.output.strip()}"
        except Exception as e:
            return f"FEHLER: {e}"

    # 1. git pull
    log_lines.append("▶ git pull origin main …")
    git_out = run(["git", "pull", "origin", "main"])
    log_lines.append(git_out or "(keine Ausgabe)")
    if "FEHLER" in git_out:
        success = False

    # 2. pip install -r requirements.txt
    python = sys.executable
    req_path = str(PROJECT_ROOT / "backend" / "requirements.txt")
    log_lines.append("\n▶ pip install -r requirements.txt …")
    pip_out = run([python, "-m", "pip", "install", "-r", req_path, "--quiet", "--upgrade"])
    log_lines.append(pip_out if pip_out else "Alle Pakete aktuell.")
    if "FEHLER" in pip_out:
        success = False

    # 3. New version info
    commit = run(["git", "rev-parse", "--short", "HEAD"])
    date = run(["git", "log", "-1", "--format=%cd", "--date=format:%d.%m.%Y %H:%M"])
    log_lines.append(f"\n✓ Aktueller Stand: {commit} ({date})")

    return {
        "success": success,
        "log": "\n".join(log_lines),
        "commit": commit,
        "date": date,
        "restart_required": success,
    }


# ─── Config ───────────────────────────────────────────────────────────────────

@app.get("/api/config")
def get_config():
    config = load_config()
    # Never return credentials content, only paths
    return config


@app.put("/api/config")
def update_config(update: ConfigUpdate):
    config = load_config()
    for k, v in update.dict(exclude_none=True).items():
        config[k] = v
    save_config(config)
    return {"ok": True}


@app.post("/api/config/upload-credentials")
async def upload_credentials(file: UploadFile = File(...)):
    config = load_config()
    storage = Path(config.get("storage_path", "~/Documents/GeoBoost_Projects")).expanduser()
    creds_path = storage / "credentials" / file.filename
    creds_path.parent.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    with open(creds_path, "wb") as f:
        f.write(content)
    config["google_credentials_path"] = str(creds_path)
    save_config(config)
    return {"ok": True, "path": str(creds_path)}


# ─── Projects ─────────────────────────────────────────────────────────────────

@app.get("/api/projects")
def list_projects():
    return db.list_projects()


@app.get("/api/projects/{project_id}")
def get_project(project_id: int):
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(404, "Projekt nicht gefunden")
    return project


@app.delete("/api/projects/{project_id}")
def delete_project(project_id: int):
    db.delete_project(project_id)
    return {"ok": True}


# ─── Analysis ─────────────────────────────────────────────────────────────────

# In-memory status tracker (per analysis_id)
analysis_status: Dict[int, Dict[str, Any]] = {}


def update_status(analysis_id: int, step: str, progress: int, message: str, error: str = ""):
    analysis_status[analysis_id] = {
        "step": step,
        "progress": progress,
        "message": message,
        "error": error,
        "done": progress >= 100,
    }
    db.update_analysis_status(analysis_id, step, progress, message, error)


@app.post("/api/analyze/start")
def start_analysis(req: StartAnalysisRequest, background_tasks: BackgroundTasks):
    config = load_config()

    # Create project + analysis records
    project_id = db.create_or_get_project(
        name=req.kickoff.project_name,
        website_url=req.kickoff.website_url,
        ga4_property_id=req.kickoff.ga4_property_id,
        kickoff_data=req.kickoff.model_dump(),
    )
    analysis_id = db.create_analysis(project_id, req.checks.model_dump())

    background_tasks.add_task(
        run_analysis, analysis_id, req.kickoff.model_dump(), req.checks.model_dump(), config
    )

    return {"analysis_id": analysis_id, "project_id": project_id}


@app.get("/api/analyze/status/{analysis_id}")
def get_status(analysis_id: int):
    status = analysis_status.get(analysis_id)
    if not status:
        # Try DB fallback
        status = db.get_analysis_status(analysis_id)
    if not status:
        raise HTTPException(404, "Analyse nicht gefunden")
    return status


@app.get("/api/analyze/results/{analysis_id}")
def get_results(analysis_id: int):
    results = db.get_analysis_results(analysis_id)
    if not results:
        raise HTTPException(404, "Keine Ergebnisse gefunden")
    return results


@app.get("/api/reports/{analysis_id}/pdf")
def download_pdf(analysis_id: int):
    config = load_config()
    storage = Path(config.get("storage_path", "~/Documents/GeoBoost_Projects")).expanduser()
    pdf_path = storage / "reports" / f"report_{analysis_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(404, "PDF nicht gefunden")
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"geoboost_report_{analysis_id}.pdf",
    )


# ─── Analysis Runner ──────────────────────────────────────────────────────────

def run_analysis(analysis_id: int, kickoff: dict, checks: dict, config: dict):
    """Runs all selected checks and generates PDF. Called as background task."""
    try:
        results = {}
        update_status(analysis_id, "start", 2, "Analyse wird gestartet...")

        website_url = kickoff["website_url"]
        period = kickoff.get("analysis_period", "last_28_days")
        start_date, end_date = _resolve_date_range(period)

        import time as _time

        # ── 1. Website Crawling ──────────────────────────────────────────────
        if checks.get("crawling", True):
            update_status(analysis_id, "crawling", 5,
                          "Website wird vollständig gecrawlt (alle Seiten, inkl. Unterseiten)...")
            try:
                crawler = WebsiteCrawler(
                    website_url,
                    max_depth=int(config.get("crawler_max_depth", 5)),
                    max_urls=int(config.get("crawler_max_urls", 500)),
                    politeness_delay=float(config.get("crawler_delay", 0.3)),
                )
                crawler_results = crawler.crawl()
                results["crawler"] = crawler_results
                n = len(crawler_results.get("pages", []))
                issues_count = sum(1 for k, v in crawler_results.get("issues", {}).items()
                                   if isinstance(v, list) and len(v) > 0)
                update_status(analysis_id, "crawling", 28,
                              f"Crawling abgeschlossen: {n} Seiten analysiert, {issues_count} Problem-Kategorien gefunden")
            except Exception as e:
                results["crawler"] = {"error": str(e), "pages": []}
                update_status(analysis_id, "crawling", 28, f"Crawling Fehler: {e}")

        # ── 2. PageSpeed ─────────────────────────────────────────────────────
        if checks.get("pagespeed", True):
            update_status(analysis_id, "pagespeed", 29,
                          "Google PageSpeed wird analysiert (Startseite, Mobile + Desktop)...")
            try:
                ps = PageSpeedAPI(api_key=config.get("pagespeed_api_key", ""))
                mob = ps.get_pagespeed_data(website_url, "mobile")
                _time.sleep(2)  # Avoid hitting rate limit between mobile/desktop
                desk = ps.get_pagespeed_data(website_url, "desktop")
                ps_results = {"mobile": mob, "desktop": desk}
                results["pagespeed"] = ps_results
                score = mob.get("performance_score")
                if score is not None:
                    update_status(analysis_id, "pagespeed", 42,
                                  f"PageSpeed abgeschlossen: Mobile Score {score}/100 – {len(mob.get('failed_audits', []))} Audits nicht bestanden")
                else:
                    update_status(analysis_id, "pagespeed", 42,
                                  f"PageSpeed: {mob.get('error', 'Unbekannter Fehler')}")
            except Exception as e:
                results["pagespeed"] = {"error": str(e)}
                update_status(analysis_id, "pagespeed", 42, f"PageSpeed Fehler: {e}")

        # ── 3. Speed Test ────────────────────────────────────────────────────
        if checks.get("speedtest", True):
            update_status(analysis_id, "speedtest", 43,
                          "Ladezeit-Test: Startseite + 9 Unterseiten werden je 5x gemessen...")
            try:
                # Homepage + up to 9 diverse crawled subpages
                urls_to_test = [website_url]
                if results.get("crawler", {}).get("pages"):
                    crawled_ok = [
                        p["url"] for p in results["crawler"]["pages"]
                        if p.get("status", 0) == 200 and p["url"] != website_url
                    ]
                    # Sample pages from different depths for diversity
                    urls_to_test += crawled_ok[:9]

                tester = SpeedTester(urls=urls_to_test, runs=5)
                speed_results = tester.run()
                results["speedtest"] = speed_results
                avg = speed_results["summary"].get("avg_total_ms")
                ttfb = speed_results["summary"].get("avg_ttfb_ms")
                rating = speed_results["summary"].get("avg_ttfb_rating", "")
                msg = (f"Ladezeit-Test abgeschlossen: Ø TTFB {ttfb:.0f} ms, Ø Gesamt {avg:.0f} ms "
                       f"({'gut' if rating == 'good' else 'verbesserbar' if rating == 'needs_work' else 'kritisch'})"
                       if avg and ttfb else "Ladezeit-Test abgeschlossen")
                update_status(analysis_id, "speedtest", 55, msg)
            except Exception as e:
                results["speedtest"] = {"error": str(e)}
                update_status(analysis_id, "speedtest", 55, f"Speed-Test Fehler: {e}")

        # ── 4. GA4 ───────────────────────────────────────────────────────────
        property_id = kickoff.get("ga4_property_id", "")
        credentials_path = config.get("google_credentials_path", "")
        ga4_ok = property_id and credentials_path and Path(credentials_path).exists()

        if checks.get("ga4_traffic", True):
            update_status(analysis_id, "ga4", 51, "GA4 Traffic-Daten werden abgerufen...")
            try:
                if ga4_ok:
                    ga4 = GA4API(property_id, credentials_path)
                    if checks.get("ga4_traffic"):
                        results["ga4_traffic"] = ga4.get_traffic_overview(start_date, end_date)
                    if checks.get("ga4_channels"):
                        results["ga4_channels"] = ga4.get_channel_data(start_date, end_date)
                    if checks.get("ga4_landingpages"):
                        results["ga4_landingpages"] = ga4.get_landingpage_data(start_date, end_date)
                    if checks.get("ga4_devices"):
                        results["ga4_devices"] = ga4.get_device_data(start_date, end_date)
                    update_status(analysis_id, "ga4", 68, "GA4 Daten erfolgreich abgerufen")
                else:
                    results["ga4_traffic"] = {"error": "Keine gültigen GA4-Zugangsdaten", "demo": True, "rows": _demo_ga4_data()}
                    update_status(analysis_id, "ga4", 68, "GA4 Demo-Daten verwendet (keine Zugangsdaten)")
            except Exception as e:
                results["ga4_traffic"] = {"error": str(e), "demo": True, "rows": _demo_ga4_data()}
                update_status(analysis_id, "ga4", 68, f"GA4 Fehler, Demo-Daten: {e}")

        # ── 5. AI Analysis ───────────────────────────────────────────────────
        if checks.get("ai_analysis", True):
            update_status(analysis_id, "ai", 69, "KI-Analyse wird durchgeführt (Ollama)...")
            try:
                analyzer = KIAnalyzer(model=config.get("ollama_model", "llama3.1:8b"))
                ai_result = analyzer.analyze(results, kickoff)
                results["ai_analysis"] = ai_result
                update_status(analysis_id, "ai", 85, "KI-Analyse abgeschlossen")
            except Exception as e:
                results["ai_analysis"] = {"error": str(e), "text": _demo_ai_analysis(kickoff)}
                update_status(analysis_id, "ai", 85, f"KI nicht verfügbar, Demo-Text verwendet: {e}")

        # ── 6. PDF Generation ────────────────────────────────────────────────
        if checks.get("pdf_report", True):
            update_status(analysis_id, "pdf", 86, "PDF wird generiert...")
            try:
                storage = Path(config.get("storage_path", "~/Documents/GeoBoost_Projects")).expanduser()
                pdf_dir = storage / "reports"
                pdf_dir.mkdir(parents=True, exist_ok=True)
                pdf_path = pdf_dir / f"report_{analysis_id}.pdf"

                template_dir = Path(__file__).parent.parent / "templates"
                gen = PDFGenerator(template_dir=str(template_dir), config=config)
                gen.generate_pdf(
                    data={
                        "kickoff": kickoff,
                        "results": results,
                        "analysis_id": analysis_id,
                        "date": datetime.now().strftime("%d.%m.%Y"),
                        "period_label": _period_label(period),
                    },
                    output_path=str(pdf_path),
                )
                results["pdf_path"] = str(pdf_path)
                update_status(analysis_id, "pdf", 98, f"PDF erstellt: {pdf_path.name}")
            except Exception as e:
                results["pdf_path"] = None
                update_status(analysis_id, "pdf", 98, f"PDF Fehler: {e}")
                traceback.print_exc()

        # ── Done ─────────────────────────────────────────────────────────────
        db.save_analysis_results(analysis_id, results)
        update_status(analysis_id, "done", 100, "Analyse abgeschlossen!")

    except Exception as e:
        traceback.print_exc()
        update_status(analysis_id, "error", 0, f"Kritischer Fehler: {e}", error=str(e))


def _resolve_date_range(period: str):
    from datetime import datetime, timedelta
    today = datetime.today()
    if period == "last_28_days":
        start = today - timedelta(days=28)
    elif period == "last_3_months":
        start = today - timedelta(days=90)
    elif period == "last_6_months":
        start = today - timedelta(days=180)
    else:
        start = today - timedelta(days=28)
    return start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")


def _period_label(period: str) -> str:
    labels = {
        "last_28_days": "Letzte 28 Tage",
        "last_3_months": "Letzte 3 Monate",
        "last_6_months": "Letzte 6 Monate",
    }
    return labels.get(period, "Letzte 28 Tage")


def _demo_ga4_data():
    return [
        {"channel": "Organic Search", "sessions": 1240, "conversions": 48, "conversion_rate": 3.87},
        {"channel": "Direct", "sessions": 620, "conversions": 31, "conversion_rate": 5.00},
        {"channel": "Paid Search", "sessions": 380, "conversions": 19, "conversion_rate": 5.00},
        {"channel": "Social", "sessions": 210, "conversions": 4, "conversion_rate": 1.90},
        {"channel": "Referral", "sessions": 150, "conversions": 6, "conversion_rate": 4.00},
        {"channel": "Email", "sessions": 90, "conversions": 12, "conversion_rate": 13.33},
    ]


def _demo_ai_analysis(kickoff: dict) -> str:
    url = kickoff.get("website_url", "Ihre Website")
    return f"""## Tracking-Status
Die Datenqualität für {url} erscheint grundsätzlich solide. Es wurden keine kritischen Tracking-Lücken festgestellt. Eine detaillierte Überprüfung der Conversion-Events wird empfohlen.

## Technische Analyse – Top 5 Probleme
1. **Mobile Performance** (P1) – Der Mobile PageSpeed-Score liegt unter dem Benchmark. Optimierung der Bildgrössen und Eliminierung von Render-Blocking-Ressourcen empfohlen.
2. **Fehlende Alt-Texte** (P1) – Mehrere Bilder ohne Alt-Attribut gefunden. Dies beeinträchtigt sowohl SEO als auch Barrierefreiheit.
3. **404-Fehler** (P2) – Einige interne Links führen zu nicht mehr vorhandenen Seiten. Diese sollten mit 301-Weiterleitungen behoben werden.
4. **Title-Tag-Duplikate** (P2) – Mehrere Seiten teilen identische Title-Tags. Einzigartige, keyword-relevante Titel verbessern die organische Sichtbarkeit.
5. **Core Web Vitals** (P3) – LCP-Wert liegt über dem empfohlenen Schwellenwert von 2.5 Sekunden.

## Performance-Insights
- **Organic Search** ist der stärkste Traffic-Kanal – hier liegt grosses Ausbaupotenzial
- **Email** zeigt die höchste Conversion Rate – Newsletter-Aktivitäten sollten intensiviert werden
- **Social Media** hat die niedrigste Conversion Rate – Landing Pages für Social Traffic optimieren
- **Mobile Traffic** dominiert, aber Conversion Rate auf Mobile ist unterdurchschnittlich
- **Direct Traffic** signalisiert starke Markenbekanntheit – Markenbindung ausbauen

## Massnahmenkatalog

### Quick Wins (1–3 Tage)
**P1 | S – Alt-Texte ergänzen**
Problem: Bilder ohne Alt-Text reduzieren SEO-Ranking und Barrierefreiheit.
Empfehlung: Alle Bilder mit beschreibenden Alt-Texten versehen, inkl. Keywords wo sinnvoll.
Erwarteter Effekt: Verbesserter SEO-Score, bessere Zugänglichkeit.

**P1 | S – 404-Links korrigieren**
Problem: Interne Broken Links schaden User Experience und Crawlability.
Empfehlung: 301-Weiterleitungen für alle gefundenen 404-Seiten einrichten.
Erwarteter Effekt: Keine verlorenen PageRank-Signale, bessere User Experience.

### Optimierungen (1–2 Wochen)
**P1 | M – Mobile Performance optimieren**
Problem: Mobile PageSpeed-Score unter 60 führt zu höheren Absprungraten.
Empfehlung: Bilder in WebP konvertieren, Lazy Loading aktivieren, CSS/JS minifizieren.
Erwarteter Effekt: Score-Verbesserung auf 75+, Reduktion der Absprungrate um 15–20%.

**P2 | M – Title-Tags und Meta-Descriptions überarbeiten**
Problem: Doppelte Title-Tags verhindern klare Positionierung in Suchergebnissen.
Empfehlung: Einzigartige, keyword-optimierte Title-Tags (50–60 Zeichen) für alle Hauptseiten.
Erwarteter Effekt: Verbesserter CTR in organischer Suche um 10–25%.

### Strategisch (3–6 Wochen)
**P2 | L – Email-Marketing ausbauen**
Problem: Email zeigt die höchste Conversion Rate (13%), wird aber wenig genutzt.
Empfehlung: Newsletter-Frequenz erhöhen, Segmentierung einführen, Automation aufbauen.
Erwarteter Effekt: 30–50% mehr Conversions aus dem Email-Kanal.

**P3 | L – Social-Media-Landingpages optimieren**
Problem: Social Traffic konvertiert schlecht (1.9% vs. 5% bei Direct).
Empfehlung: Dedizierte Landing Pages für Social-Kampagnen erstellen, mit klarem CTA und schnellerer Ladezeit.
Erwarteter Effekt: Steigerung der Social Conversion Rate auf 3–4%."""


# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT WORKFLOW ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

from audit_parsers import parse_screaming_frog_csv, parse_semrush_csv


class CreateAuditRequest(BaseModel):
    title: str
    client_name: str = ""
    website_url: str = ""
    project_id: Optional[int] = None


class UpdateAuditStepRequest(BaseModel):
    step: int  # 0-6
    data: dict


@app.get("/api/audits")
def list_audits():
    return db.list_audits()


@app.post("/api/audits")
def create_audit(req: CreateAuditRequest):
    audit_id = db.create_audit(
        title=req.title,
        client_name=req.client_name,
        website_url=req.website_url,
        project_id=req.project_id,
    )
    return {"audit_id": audit_id}


@app.get("/api/audits/{audit_id}")
def get_audit(audit_id: int):
    audit = db.get_audit(audit_id)
    if not audit:
        raise HTTPException(404, "Audit nicht gefunden")
    return audit


@app.delete("/api/audits/{audit_id}")
def delete_audit(audit_id: int):
    db.delete_audit(audit_id)
    return {"ok": True}


@app.put("/api/audits/{audit_id}/step")
def update_audit_step(audit_id: int, req: UpdateAuditStepRequest):
    audit = db.get_audit(audit_id)
    if not audit:
        raise HTTPException(404, "Audit nicht gefunden")
    db.update_audit_step(audit_id, req.step, req.data)
    return {"ok": True, "step": req.step}


@app.post("/api/audits/{audit_id}/upload/screaming-frog")
async def upload_screaming_frog(audit_id: int, file: UploadFile = File(...)):
    audit = db.get_audit(audit_id)
    if not audit:
        raise HTTPException(404, "Audit nicht gefunden")
    content = (await file.read()).decode("utf-8", errors="replace")
    try:
        parsed = parse_screaming_frog_csv(content)
    except Exception as e:
        raise HTTPException(400, f"CSV konnte nicht gelesen werden: {e}")

    # Merge into step3 (Background-Crawl)
    existing = audit.get("step3_semrush") or {}
    if isinstance(existing, str):
        try:
            existing = json.loads(existing)
        except Exception:
            existing = {}
    existing["summary"] = parsed["summary"]
    existing["issues"] = parsed["issues"]
    db.update_audit_step(audit_id, 3, existing)
    return {
        "ok": True,
        "summary": parsed["summary"],
        "issues_count": len(parsed["issues"]),
    }


@app.post("/api/audits/{audit_id}/upload/semrush")
async def upload_semrush(audit_id: int, file: UploadFile = File(...)):
    audit = db.get_audit(audit_id)
    if not audit:
        raise HTTPException(404, "Audit nicht gefunden")
    content = (await file.read()).decode("utf-8", errors="replace")
    try:
        parsed = parse_semrush_csv(content)
    except Exception as e:
        raise HTTPException(400, f"CSV konnte nicht gelesen werden: {e}")

    # Merge into step4 (SemRush Check)
    existing = audit.get("step4_lighthouse") or {}
    if isinstance(existing, str):
        try:
            existing = json.loads(existing)
        except Exception:
            existing = {}
    existing["semrush_summary"] = parsed["summary"]
    existing["semrush_issues"] = parsed["issues"]
    db.update_audit_step(audit_id, 4, existing)
    return {
        "ok": True,
        "summary": parsed["summary"],
        "issues_count": len(parsed["issues"]),
    }


@app.post("/api/audits/{audit_id}/lighthouse/fetch")
def fetch_lighthouse(audit_id: int, body: dict):
    """Fetch PageSpeed data and save to audit step 5 (Lighthouse)."""
    audit = db.get_audit(audit_id)
    if not audit:
        raise HTTPException(404, "Audit nicht gefunden")
    config = load_config()
    url = body.get("url", "")
    strategy = body.get("strategy", "mobile")
    if not url:
        raise HTTPException(400, "URL fehlt")
    ps = PageSpeedAPI(api_key=config.get("pagespeed_api_key", ""))
    data = ps.get_pagespeed_data(url, strategy)
    if data.get("error"):
        raise HTTPException(502, data["error"])

    step_data = {
        "source": "api",
        "url_tested": url,
        "strategy": strategy,
        "performance": data.get("performance_score"),
        "accessibility": data.get("accessibility_score"),
        "best_practices": data.get("best_practices_score"),
        "seo": data.get("seo_score"),
        "lcp_value": data.get("lcp", ""),
        "lcp_rating": data.get("lcp_rating", ""),
        "cls_value": data.get("cls", ""),
        "cls_rating": data.get("cls_rating", ""),
        "fcp_value": data.get("fcp", ""),
        "fcp_rating": data.get("fcp_rating", ""),
        "tbt_value": data.get("tbt", ""),
        "tbt_rating": data.get("tbt_rating", ""),
        "top_issues": [
            {"title": a["title"], "description": a.get("explanation_de") or a.get("description", ""),
             "impact": "hoch" if a["rating"] == "fail" else "mittel"}
            for a in data.get("failed_audits", [])[:3]
        ],
    }
    existing = audit.get("step5_notes") or {}
    if isinstance(existing, str):
        try:
            existing = json.loads(existing)
        except Exception:
            existing = {}
    existing.update(step_data)
    db.update_audit_step(audit_id, 5, existing)
    return step_data


class GenerateReportRequest(BaseModel):
    theme: str = "light"

@app.post("/api/audits/{audit_id}/report/generate")
def generate_audit_report(audit_id: int, req: GenerateReportRequest = None):
    """Generate PDF report from audit data."""
    from audit_pdf_generator import AuditPDFGenerator, THEMES
    theme = (req.theme if req else None) or "light"
    if theme not in THEMES:
        theme = "light"
    audit = db.get_audit(audit_id)
    if not audit:
        raise HTTPException(404, "Audit nicht gefunden")
    config = load_config()
    storage = Path(config.get("storage_path", "~/Documents/GeoBoost_Projects")).expanduser()
    pdf_dir = storage / "audits"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = pdf_dir / f"audit_{audit_id}_{theme}.pdf"
    try:
        gen = AuditPDFGenerator(config=config)
        gen.generate(audit, str(pdf_path), theme=theme)
        db.save_audit_pdf(audit_id, str(pdf_path))
        return {"ok": True, "pdf_path": str(pdf_path)}
    except Exception as e:
        raise HTTPException(500, f"PDF-Fehler: {e}")


@app.get("/api/audits/{audit_id}/report/pdf")
def download_audit_pdf(audit_id: int):
    audit = db.get_audit(audit_id)
    if not audit or not audit.get("pdf_path"):
        raise HTTPException(404, "PDF nicht gefunden")
    pdf_path = Path(audit["pdf_path"])
    if not pdf_path.exists():
        raise HTTPException(404, "PDF-Datei nicht vorhanden")
    return FileResponse(str(pdf_path), media_type="application/pdf",
                        filename=f"audit_{audit_id}.pdf")


if __name__ == "__main__":
    import uvicorn
    print("GeoBoost Backend startet auf http://localhost:8765")
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
