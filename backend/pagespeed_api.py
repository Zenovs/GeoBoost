"""
GeoBoost – PageSpeed Insights API (erweitert)
Holt alle Lighthouse-Audits mit Beschreibungen, Spar-Schätzungen und Fix-Hinweisen.
"""

import requests
from typing import Dict, Any, Optional, List

# Kategorien + Reihenfolge der wichtigsten Audits
PRIORITY_AUDITS = [
    # Performance
    "render-blocking-resources",
    "uses-optimized-images",
    "uses-webp-images",
    "uses-responsive-images",
    "offscreen-images",
    "unminified-javascript",
    "unminified-css",
    "unused-javascript",
    "unused-css-rules",
    "uses-text-compression",
    "uses-rel-preconnect",
    "server-response-time",
    "redirects",
    "uses-rel-preload",
    "efficient-animated-content",
    "duplicated-javascript",
    "legacy-javascript",
    "total-byte-weight",
    "dom-size",
    "critical-request-chains",
    "largest-contentful-paint-element",
    "layout-shift-elements",
    # SEO
    "meta-description",
    "document-title",
    "crawlable-anchors",
    "link-text",
    "is-crawlable",
    "robots-txt",
    "image-alt",
    "hreflang",
    "canonical",
    "font-size",
    "tap-targets",
    # Accessibility
    "color-contrast",
    "image-alt",
    "label",
    "aria-*",
    # Best Practices
    "uses-https",
    "js-libraries",
    "deprecations",
    "errors-in-console",
]

# German explanations for key audits
AUDIT_EXPLANATIONS = {
    "render-blocking-resources": "CSS/JS-Dateien blockieren den Seitenaufbau. Jede blockierende Ressource verzögert den First Contentful Paint.",
    "uses-optimized-images": "Bilder sind nicht optimal komprimiert. JPEG/PNG können oft um 30–60% reduziert werden ohne sichtbaren Qualitätsverlust.",
    "uses-webp-images": "Modernere Bildformate (WebP, AVIF) reduzieren die Bildgrösse um 25–35% gegenüber JPEG/PNG.",
    "unused-javascript": "JavaScript wird geladen aber nicht ausgeführt. Jedes KB ungenutztes JS verzögert die Ausführungszeit.",
    "unused-css-rules": "CSS-Regeln werden geladen aber nie angewendet. Erhöht unnötig die Parsing-Zeit.",
    "uses-text-compression": "Textdateien (HTML, CSS, JS) werden ohne gzip/Brotli-Komprimierung übertragen.",
    "server-response-time": "Der Server antwortet zu langsam. Ursachen: langsames Hosting, keine Query-Optimierung, kein Caching.",
    "dom-size": "Zu viele DOM-Elemente verlangsamem Rendering und JavaScript-Ausführung erheblich.",
    "total-byte-weight": "Gesamtgrösse der Seite zu hoch. Betrifft vor allem mobile Nutzer mit schlechter Verbindung.",
    "largest-contentful-paint-element": "Das grösste sichtbare Element lädt zu langsam. Meist ein Hero-Bild oder grosser Text.",
    "uses-https": "Die Seite nutzt kein HTTPS. Google bestraft HTTP-Seiten im Ranking.",
    "meta-description": "Fehlende Meta-Description. Google zeigt Snippets schlechter an, CTR sinkt.",
    "image-alt": "Bilder ohne Alt-Text sind nicht barrierefrei und werden von Suchmaschinen nicht indexiert.",
    "tap-targets": "Klickbare Elemente sind zu klein oder zu eng beieinander (Mobile UX-Problem).",
    "is-crawlable": "Die Seite ist möglicherweise für Suchmaschinen nicht zugänglich (robots-Tag, noindex).",
    "layout-shift-elements": "Elemente verschieben sich während des Ladens (schlechter CLS). Betrifft vor allem Bilder ohne feste Grösse.",
}


class PageSpeedAPI:
    BASE_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key.strip()

    def get_pagespeed_data(self, url: str, strategy: str = "mobile") -> Dict[str, Any]:
        params = {
            "url": url,
            "strategy": strategy,
            "category": ["performance", "seo", "accessibility", "best-practices"],
        }
        if self.api_key and self.api_key not in ("YOUR_PAGESPEED_API_KEY", ""):
            params["key"] = self.api_key

        last_error = ""
        for attempt in range(3):
            try:
                resp = requests.get(self.BASE_URL, params=params, timeout=60)
                if resp.status_code == 429:
                    wait = 15 * (attempt + 1)
                    import time as _time
                    _time.sleep(wait)
                    last_error = f"429 Rate limit – warte {wait}s"
                    continue
                resp.raise_for_status()
                data = resp.json()
                break
            except Exception as e:
                last_error = str(e)
                if attempt < 2:
                    import time as _time
                    _time.sleep(5)
        else:
            return {"url": url, "strategy": strategy, "error": last_error}

        lhr = data.get("lighthouseResult", {})
        cats = lhr.get("categories", {})
        audits = lhr.get("audits", {})

        def score(key: str) -> Optional[int]:
            s = cats.get(key, {}).get("score")
            return round(s * 100) if s is not None else None

        def audit_val(key: str) -> str:
            return audits.get(key, {}).get("displayValue", "n/a")

        def audit_score_flag(key: str) -> str:
            s = audits.get(key, {}).get("score")
            if s is None:
                return "n/a"
            if s >= 0.9:
                return "pass"
            if s >= 0.5:
                return "warn"
            return "fail"

        # ── Collect all failed/warning audits ────────────────────────────────
        failed_audits = self._collect_failed_audits(audits)
        opportunities = self._collect_opportunities(audits)

        # ── Core Web Vitals raw values ────────────────────────────────────────
        def cwv_numeric(key: str) -> Optional[float]:
            """Return the numeric value in ms for a CWV audit."""
            a = audits.get(key, {})
            v = a.get("numericValue")
            return round(v, 0) if v is not None else None

        def cwv_rating(key: str) -> str:
            a = audits.get(key, {})
            score_val = a.get("score")
            if score_val is None:
                return "n/a"
            if score_val >= 0.9:
                return "good"
            if score_val >= 0.5:
                return "needs_improvement"
            return "poor"

        return {
            "url": url,
            "strategy": strategy,
            # Scores
            "performance_score": score("performance"),
            "seo_score": score("seo"),
            "accessibility_score": score("accessibility"),
            "best_practices_score": score("best-practices"),
            # Core Web Vitals (display values)
            "lcp": audit_val("largest-contentful-paint"),
            "lcp_ms": cwv_numeric("largest-contentful-paint"),
            "lcp_rating": cwv_rating("largest-contentful-paint"),
            "fid": audit_val("max-potential-fid"),
            "cls": audit_val("cumulative-layout-shift"),
            "cls_numeric": audits.get("cumulative-layout-shift", {}).get("numericValue"),
            "cls_rating": cwv_rating("cumulative-layout-shift"),
            "fcp": audit_val("first-contentful-paint"),
            "fcp_ms": cwv_numeric("first-contentful-paint"),
            "fcp_rating": cwv_rating("first-contentful-paint"),
            "tti": audit_val("interactive"),
            "tti_ms": cwv_numeric("interactive"),
            "speed_index": audit_val("speed-index"),
            "speed_index_ms": cwv_numeric("speed-index"),
            "tbt": audit_val("total-blocking-time"),
            "tbt_ms": cwv_numeric("total-blocking-time"),
            "tbt_rating": cwv_rating("total-blocking-time"),
            # Audit results
            "lcp_status": audit_score_flag("largest-contentful-paint"),
            "cls_status": audit_score_flag("cumulative-layout-shift"),
            "tbt_status": audit_score_flag("total-blocking-time"),
            "fcp_status": audit_score_flag("first-contentful-paint"),
            # Failed audits with details
            "failed_audits": failed_audits,
            "opportunities": opportunities,
            # Meta
            "total_byte_weight": audits.get("total-byte-weight", {}).get("numericValue"),
            "dom_size": audits.get("dom-size", {}).get("numericValue"),
            "js_execution_time": audits.get("bootup-time", {}).get("numericValue"),
        }

    def _collect_failed_audits(self, audits: Dict) -> List[Dict]:
        """Return all non-passing audits with explanation and fix hint."""
        failed = []
        for audit_id, audit_data in audits.items():
            score_val = audit_data.get("score")
            if score_val is None or score_val >= 0.9:
                continue
            if audit_data.get("scoreDisplayMode") in ("notApplicable", "manual", "informative"):
                continue

            title = audit_data.get("title", audit_id)
            description = audit_data.get("description", "")
            display_value = audit_data.get("displayValue", "")
            savings_ms = None

            # Try to extract potential savings
            details = audit_data.get("details", {})
            if details.get("overallSavingsMs"):
                savings_ms = round(details["overallSavingsMs"])
            elif details.get("overallSavingsBytes"):
                savings_ms = None  # byte savings

            rating = "warn" if score_val >= 0.5 else "fail"

            failed.append({
                "id": audit_id,
                "title": title,
                "description": description[:300] if description else "",
                "explanation_de": AUDIT_EXPLANATIONS.get(audit_id, ""),
                "display_value": display_value,
                "score": round(score_val * 100) if score_val is not None else None,
                "savings_ms": savings_ms,
                "rating": rating,
                "category": self._audit_category(audit_id),
            })

        # Sort by: fail first, then by savings_ms desc
        failed.sort(key=lambda x: (0 if x["rating"] == "fail" else 1, -(x["savings_ms"] or 0)))
        return failed[:20]  # Top 20 issues

    def _collect_opportunities(self, audits: Dict) -> List[Dict]:
        """Return performance opportunities with byte/ms savings."""
        opps = []
        for audit_id, audit_data in audits.items():
            details = audit_data.get("details", {})
            savings_ms = details.get("overallSavingsMs")
            savings_bytes = details.get("overallSavingsBytes")
            if not savings_ms and not savings_bytes:
                continue
            if audit_data.get("score", 1) >= 0.9:
                continue

            opps.append({
                "id": audit_id,
                "title": audit_data.get("title", audit_id),
                "savings_ms": round(savings_ms) if savings_ms else None,
                "savings_kb": round(savings_bytes / 1024) if savings_bytes else None,
                "display_value": audit_data.get("displayValue", ""),
            })

        opps.sort(key=lambda x: -(x.get("savings_ms") or 0))
        return opps[:10]

    def _audit_category(self, audit_id: str) -> str:
        perf_audits = {
            "render-blocking-resources", "uses-optimized-images", "uses-webp-images",
            "uses-responsive-images", "offscreen-images", "unminified-javascript",
            "unminified-css", "unused-javascript", "unused-css-rules",
            "uses-text-compression", "server-response-time", "total-byte-weight",
            "dom-size", "efficient-animated-content", "largest-contentful-paint",
            "cumulative-layout-shift", "total-blocking-time", "first-contentful-paint",
        }
        seo_audits = {
            "meta-description", "document-title", "crawlable-anchors", "link-text",
            "is-crawlable", "robots-txt", "hreflang", "canonical", "font-size",
            "tap-targets", "structured-data",
        }
        acc_audits = {
            "color-contrast", "image-alt", "label", "button-name", "aria-allowed-attr",
            "aria-required-attr", "aria-valid-attr", "aria-valid-attr-value",
        }
        if audit_id in perf_audits:
            return "performance"
        if audit_id in seo_audits:
            return "seo"
        if audit_id in acc_audits:
            return "accessibility"
        return "best-practices"
