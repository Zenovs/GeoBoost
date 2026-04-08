"""
GeoBoost – Speed Test Module
Misst HTTP-Ladezeiten direkt (kein externes Tool nötig).

Gemessene Werte pro URL:
  - DNS-Lookup
  - TCP-Verbindungsaufbau
  - TLS-Handshake
  - Time to First Byte (TTFB)
  - Content-Transfer-Zeit
  - Gesamtzeit
  - Response-Grösse (compressed + uncompressed)
  - HTTP/2 aktiv?
  - Compression (gzip/br)?

Jede URL wird 3x gemessen → Median wird verwendet (eliminiert Ausreisser).
"""

import time
import socket
import ssl
import statistics
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional
import requests
from requests.adapters import HTTPAdapter

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GeoBoost/1.0)",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "de-CH,de;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

# Benchmark thresholds (in ms)
BENCHMARKS = {
    "ttfb":     {"good": 200,   "needs_work": 600,   "unit": "ms", "label": "Time to First Byte"},
    "total":    {"good": 1500,  "needs_work": 3000,  "unit": "ms", "label": "Gesamtladezeit"},
    "dns":      {"good": 50,    "needs_work": 150,   "unit": "ms", "label": "DNS-Lookup"},
    "connect":  {"good": 100,   "needs_work": 300,   "unit": "ms", "label": "TCP-Verbindung"},
    "tls":      {"good": 150,   "needs_work": 400,   "unit": "ms", "label": "TLS-Handshake"},
    "transfer": {"good": 500,   "needs_work": 2000,  "unit": "ms", "label": "Content-Transfer"},
}

def _rate(value: float, key: str) -> str:
    """Returns 'good', 'needs_work', or 'poor' based on benchmarks."""
    b = BENCHMARKS.get(key, {})
    if not b or value is None:
        return "unknown"
    if value <= b["good"]:
        return "good"
    if value <= b["needs_work"]:
        return "needs_work"
    return "poor"


def _measure_once(url: str, session: requests.Session, timeout: int = 15) -> Dict[str, Any]:
    """Single measurement with detailed timing via requests event hooks."""
    timings: Dict[str, float] = {}

    def on_response(r, **kwargs):
        timings["response_received"] = time.perf_counter()

    parsed = urlparse(url)
    is_https = parsed.scheme == "https"

    t_start = time.perf_counter()

    # Manual socket timing for DNS + connect + TLS
    host = parsed.hostname
    port = parsed.port or (443 if is_https else 80)

    try:
        t_dns_start = time.perf_counter()
        addr_info = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
        t_dns_end = time.perf_counter()
        dns_ms = round((t_dns_end - t_dns_start) * 1000, 1)

        ip = addr_info[0][4][0]

        t_connect_start = time.perf_counter()
        sock = socket.create_connection((ip, port), timeout=timeout)
        t_connect_end = time.perf_counter()
        connect_ms = round((t_connect_end - t_connect_start) * 1000, 1)

        tls_ms = None
        http2 = False
        if is_https:
            t_tls_start = time.perf_counter()
            ctx = ssl.create_default_context()
            ctx.set_alpn_protocols(["h2", "http/1.1"])
            ssl_sock = ctx.wrap_socket(sock, server_hostname=host)
            t_tls_end = time.perf_counter()
            tls_ms = round((t_tls_end - t_tls_start) * 1000, 1)
            http2 = ssl_sock.selected_alpn_protocol() == "h2"
            sock = ssl_sock
        sock.close()
    except Exception:
        dns_ms = None
        connect_ms = None
        tls_ms = None
        http2 = False

    # Full HTTP request with timing
    try:
        t_req = time.perf_counter()
        resp = session.get(url, timeout=timeout, hooks={"response": on_response},
                          allow_redirects=True)
        t_end = time.perf_counter()

        total_ms = round((t_end - t_req) * 1000, 1)
        ttfb_ms = round((timings.get("response_received", t_end) - t_req) * 1000, 1)
        transfer_ms = max(0, round(total_ms - ttfb_ms, 1))

        content_length_compressed = len(resp.content)
        content_encoding = resp.headers.get("Content-Encoding", "")
        content_length_header = resp.headers.get("Content-Length")

        # Try to get uncompressed size
        try:
            uncompressed = len(resp.text.encode("utf-8"))
        except Exception:
            uncompressed = content_length_compressed

        compression_ratio = round(uncompressed / max(content_length_compressed, 1), 2) if content_length_compressed else 1.0

        return {
            "url": resp.url,
            "status": resp.status_code,
            "dns_ms": dns_ms,
            "connect_ms": connect_ms,
            "tls_ms": tls_ms,
            "ttfb_ms": ttfb_ms,
            "transfer_ms": transfer_ms,
            "total_ms": total_ms,
            "size_bytes_compressed": content_length_compressed,
            "size_bytes_uncompressed": uncompressed,
            "compression_ratio": compression_ratio,
            "content_encoding": content_encoding,
            "server": resp.headers.get("Server", ""),
            "cache_control": resp.headers.get("Cache-Control", ""),
            "http2": http2,
            "error": None,
        }
    except requests.exceptions.Timeout:
        return {"url": url, "error": "Timeout", "total_ms": timeout * 1000}
    except Exception as e:
        return {"url": url, "error": str(e), "total_ms": None}


def _measure_median(url: str, session: requests.Session, runs: int = 3) -> Dict[str, Any]:
    """Run N times, return median of numeric fields + all raw runs."""
    results = []
    for _ in range(runs):
        r = _measure_once(url, session)
        results.append(r)
        if r.get("error"):
            break  # Don't retry on error

    valid = [r for r in results if not r.get("error") and r.get("total_ms") is not None]
    if not valid:
        return results[0] if results else {"url": url, "error": "No valid measurements"}

    # Use the result closest to median total_ms
    totals = [r["total_ms"] for r in valid]
    med = statistics.median(totals)
    best = min(valid, key=lambda r: abs(r["total_ms"] - med))

    best["runs"] = len(valid)
    best["total_ms_min"] = min(totals)
    best["total_ms_max"] = max(totals)
    best["total_ms_median"] = round(med, 1)

    # Add ratings
    for key in ["ttfb", "total", "dns", "connect", "tls", "transfer"]:
        field = f"{key}_ms"
        val = best.get(field)
        if val is not None:
            best[f"{key}_rating"] = _rate(val, key)

    return best


def _detect_issues(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate structured issues from timing data."""
    issues = []
    url = result.get("url", "")

    ttfb = result.get("ttfb_ms")
    if ttfb and ttfb > 600:
        issues.append({
            "id": "SPEED_TTFB",
            "priority": "P1" if ttfb > 1500 else "P2",
            "title": f"TTFB zu hoch ({ttfb:.0f} ms)",
            "explanation": (
                "Der Server benötigt zu lange, bis er das erste Byte antwortet. "
                "Ursachen: langsamer Server/Hosting, kein Caching, schwere Datenbankabfragen, kein CDN."
            ),
            "fix": "Server-seitiges Caching aktivieren (Redis, Varnish), Hosting upgraden oder CDN einsetzen.",
            "benchmark": f"Gut: <200 ms · Akzeptabel: <600 ms · Aktuell: {ttfb:.0f} ms",
            "effort": "M",
        })

    total = result.get("total_ms")
    if total and total > 3000:
        issues.append({
            "id": "SPEED_TOTAL",
            "priority": "P1" if total > 5000 else "P2",
            "title": f"Ladezeit zu lang ({total/1000:.1f}s)",
            "explanation": (
                "Die Gesamtladezeit übersteigt den Schwellenwert. "
                "53% der mobilen Nutzer verlassen eine Seite, die länger als 3 Sekunden lädt."
            ),
            "fix": "Bilder komprimieren (WebP), JS/CSS minifizieren, Lazy Loading aktivieren.",
            "benchmark": f"Gut: <1.5s · Akzeptabel: <3s · Aktuell: {total/1000:.1f}s",
            "effort": "M",
        })

    size = result.get("size_bytes_compressed", 0)
    if size and size > 500_000:
        issues.append({
            "id": "SPEED_SIZE",
            "priority": "P2",
            "title": f"Seitengrösse zu gross ({size//1024} KB komprimiert)",
            "explanation": "Eine grosse HTML-Antwort deutet auf überflüssige Inline-Ressourcen oder fehlende Komprimierung hin.",
            "fix": "HTML-Caching aktivieren, Inline-Skripte auslagern, Komprimierung (gzip/br) aktivieren.",
            "benchmark": f"Gut: <100 KB · Akzeptabel: <500 KB · Aktuell: {size//1024} KB",
            "effort": "S",
        })

    if not result.get("content_encoding"):
        issues.append({
            "id": "SPEED_NO_COMPRESSION",
            "priority": "P2",
            "title": "Keine HTTP-Komprimierung (gzip/br)",
            "explanation": "Der Server liefert unkomprimierte Inhalte. Komprimierung reduziert die Übertragungsgrösse um 60–80%.",
            "fix": "gzip oder Brotli auf dem Webserver aktivieren (Apache: mod_deflate, Nginx: gzip on).",
            "benchmark": "Sollte immer aktiviert sein",
            "effort": "S",
        })

    tls = result.get("tls_ms")
    if tls and tls > 400:
        issues.append({
            "id": "SPEED_TLS",
            "priority": "P3",
            "title": f"TLS-Handshake langsam ({tls:.0f} ms)",
            "explanation": "Ein langsamer TLS-Handshake verzögert den Verbindungsaufbau für jeden neuen Besucher.",
            "fix": "TLS 1.3 aktivieren, HSTS und Session Resumption einrichten.",
            "benchmark": f"Gut: <150 ms · Akzeptabel: <400 ms · Aktuell: {tls:.0f} ms",
            "effort": "S",
        })

    if not result.get("cache_control") or "no-store" in result.get("cache_control", ""):
        issues.append({
            "id": "SPEED_NO_CACHE",
            "priority": "P2",
            "title": "Kein Browser-Caching konfiguriert",
            "explanation": "Ohne Cache-Control-Header müssen Besucher die Seite bei jedem Besuch neu laden.",
            "fix": "Cache-Control-Header setzen: 'public, max-age=3600' für HTML, länger für statische Assets.",
            "benchmark": "Cache-Control sollte immer gesetzt sein",
            "effort": "S",
        })

    return issues


class SpeedTester:
    def __init__(self, urls: List[str], runs: int = 5):
        self.urls = urls[:10]  # max 10 URLs
        self.runs = runs
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def run(self) -> Dict[str, Any]:
        results = []
        all_issues = []

        for url in self.urls:
            result = _measure_median(url, self.session, self.runs)
            result["issues"] = _detect_issues(result)
            all_issues.extend(result["issues"])
            results.append(result)

        # Summary
        valid = [r for r in results if not r.get("error") and r.get("total_ms")]
        avg_ttfb = round(statistics.mean([r["ttfb_ms"] for r in valid if r.get("ttfb_ms")]), 1) if valid else None
        avg_total = round(statistics.mean([r["total_ms"] for r in valid]), 1) if valid else None

        slowest = max(valid, key=lambda r: r.get("total_ms", 0)) if valid else None
        fastest = min(valid, key=lambda r: r.get("total_ms", 0)) if valid else None

        # Deduplicate issues by id
        seen_ids: set = set()
        unique_issues = []
        for iss in all_issues:
            if iss["id"] not in seen_ids:
                seen_ids.add(iss["id"])
                unique_issues.append(iss)

        return {
            "pages": results,
            "summary": {
                "pages_tested": len(results),
                "avg_ttfb_ms": avg_ttfb,
                "avg_total_ms": avg_total,
                "slowest_url": slowest.get("url") if slowest else None,
                "slowest_ms": slowest.get("total_ms") if slowest else None,
                "fastest_url": fastest.get("url") if fastest else None,
                "fastest_ms": fastest.get("total_ms") if fastest else None,
                "avg_ttfb_rating": _rate(avg_ttfb, "ttfb") if avg_ttfb else "unknown",
                "avg_total_rating": _rate(avg_total, "total") if avg_total else "unknown",
            },
            "issues": unique_issues,
            "benchmarks": BENCHMARKS,
        }
