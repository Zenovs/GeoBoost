"""
GeoBoost – Website Crawler
Nutzt requests + BeautifulSoup für schnelles, robustes Crawling.

Erfasst pro Seite:
  - Status-Code, Response-Zeit
  - Title, Meta-Description, H1–H6-Hierarchie
  - Canonical-Tag, noindex-Erkennung
  - Strukturierte Daten (JSON-LD / Schema.org)
  - Bilder (Anzahl, ohne Alt)
  - Wortanzahl (sichtbarer Text)
  - Interne / externe Links
"""

import json
import time
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import Dict, Any, List, Set, Optional

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GeoBoost/1.0; +https://geoboost.app)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "de-CH,de;q=0.9,en;q=0.8",
}


class WebsiteCrawler:
    def __init__(self, url: str, max_depth: int = 3, max_urls: int = 200):
        self.base_url = url.rstrip("/")
        self.domain = urlparse(url).netloc
        self.max_depth = max_depth
        self.max_urls = max_urls
        self.visited: Set[str] = set()
        self.pages: List[Dict[str, Any]] = []
        self.log: List[str] = []
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def crawl(self) -> Dict[str, Any]:
        self._crawl_page(self.base_url, depth=0)

        pages = self.pages
        issues = self._extract_issues(pages)
        summary = self._build_summary(pages, issues)

        return {
            "pages": pages,
            "issues": issues,
            "summary": summary,
            "log": self.log,
        }

    def _crawl_page(self, url: str, depth: int):
        if depth > self.max_depth:
            return
        if len(self.pages) >= self.max_urls:
            return
        if url in self.visited:
            return
        if not self._is_same_domain(url):
            return

        self.visited.add(url)

        try:
            t_start = time.perf_counter()
            resp = self.session.get(url, timeout=10, allow_redirects=True)
            response_time_ms = round((time.perf_counter() - t_start) * 1000, 1)

            final_url = resp.url
            status = resp.status_code
            content_type = resp.headers.get("Content-Type", "")

            if "text/html" not in content_type:
                return

            soup = BeautifulSoup(resp.text, "lxml")

            # ── Title ─────────────────────────────────────────────────────────
            title_tag = soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else ""

            # ── Meta description ──────────────────────────────────────────────
            meta_desc_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
            meta_desc = meta_desc_tag.get("content", "") if meta_desc_tag else ""

            # ── Robots / noindex ──────────────────────────────────────────────
            robots_tag = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
            robots_content = (robots_tag.get("content", "") if robots_tag else "").lower()
            noindex = "noindex" in robots_content

            # ── Canonical ─────────────────────────────────────────────────────
            canonical_tag = soup.find("link", rel="canonical")
            canonical_url = canonical_tag.get("href", "").strip() if canonical_tag else ""
            # Make absolute
            if canonical_url and not canonical_url.startswith("http"):
                canonical_url = urljoin(url, canonical_url)

            # ── Heading hierarchy ─────────────────────────────────────────────
            headings: Dict[str, List[str]] = {}
            for level in range(1, 7):
                tags = soup.find_all(f"h{level}")
                headings[f"h{level}"] = [t.get_text(strip=True)[:120] for t in tags]

            h1_texts = headings.get("h1", [])
            h1_count = len(h1_texts)

            # ── Images ────────────────────────────────────────────────────────
            imgs = soup.find_all("img")
            img_count = len(imgs)
            imgs_without_alt = sum(1 for img in imgs if not img.get("alt"))

            # ── Word count ────────────────────────────────────────────────────
            # Remove script and style blocks, count remaining words
            for tag in soup(["script", "style", "nav", "header", "footer"]):
                tag.decompose()
            body_text = soup.get_text(separator=" ")
            word_count = len([w for w in body_text.split() if len(w) > 1])

            # ── Structured data (JSON-LD) ──────────────────────────────────────
            schema_types: List[str] = []
            for script in soup.find_all("script", type="application/ld+json"):
                try:
                    ld = json.loads(script.string or "{}")
                    if isinstance(ld, list):
                        for item in ld:
                            t = item.get("@type")
                            if t:
                                schema_types.append(t if isinstance(t, str) else str(t))
                    elif isinstance(ld, dict):
                        t = ld.get("@type")
                        if t:
                            schema_types.append(t if isinstance(t, str) else str(t))
                except Exception:
                    pass

            # ── Links ─────────────────────────────────────────────────────────
            links = soup.find_all("a", href=True)
            internal_links = []
            external_links = []
            for link in links:
                href = link["href"].strip()
                if href.startswith(("#", "javascript:", "mailto:", "tel:")):
                    continue
                abs_href = urljoin(url, href).split("#")[0]
                if self._is_same_domain(abs_href):
                    internal_links.append(abs_href)
                else:
                    external_links.append(abs_href)

            page_data = {
                "url": final_url,
                "status": status,
                "response_time_ms": response_time_ms,
                "title": title,
                "title_length": len(title),
                "meta_description": meta_desc,
                "meta_description_length": len(meta_desc),
                "noindex": noindex,
                "canonical_url": canonical_url,
                "canonical_self": (canonical_url == url or canonical_url == final_url) if canonical_url else None,
                "headings": headings,
                "h1_count": h1_count,
                "h1_texts": h1_texts,
                "image_count": img_count,
                "images_without_alt": imgs_without_alt,
                "word_count": word_count,
                "schema_types": schema_types,
                "has_structured_data": len(schema_types) > 0,
                "internal_links_count": len(set(internal_links)),
                "external_links_count": len(set(external_links)),
                "page_size_kb": round(len(resp.content) / 1024, 1),
                "depth": depth,
            }

            self.pages.append(page_data)

            # ── Logging ───────────────────────────────────────────────────────
            if not title:
                self.log.append(f"⚠ Kein Title-Tag: {url}")
            elif len(title) > 60:
                self.log.append(f"⚠ Title zu lang ({len(title)} Zeichen): {url}")
            if not meta_desc:
                self.log.append(f"⚠ Keine Meta-Description: {url}")
            if h1_count == 0:
                self.log.append(f"⚠ Kein H1-Tag: {url}")
            elif h1_count > 1:
                self.log.append(f"⚠ Mehrere H1-Tags ({h1_count}): {url}")
            if noindex:
                self.log.append(f"ℹ noindex gesetzt: {url}")
            if canonical_url and not page_data["canonical_self"]:
                self.log.append(f"ℹ Canonical zeigt auf andere URL: {canonical_url}")

            # Crawl internal links
            for link in list(set(internal_links))[:50]:
                self._crawl_page(link, depth + 1)

        except Exception as e:
            self.log.append(f"✗ Fehler beim Crawlen von {url}: {e}")
            self.pages.append({
                "url": url,
                "status": 0,
                "error": str(e),
                "title": "",
                "title_length": 0,
                "meta_description": "",
                "meta_description_length": 0,
                "noindex": False,
                "canonical_url": "",
                "canonical_self": None,
                "headings": {},
                "h1_count": 0,
                "h1_texts": [],
                "image_count": 0,
                "images_without_alt": 0,
                "word_count": 0,
                "schema_types": [],
                "has_structured_data": False,
                "internal_links_count": 0,
                "external_links_count": 0,
                "page_size_kb": 0,
                "response_time_ms": None,
                "depth": depth,
            })

    def _is_same_domain(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            return parsed.netloc == self.domain or parsed.netloc == ""
        except Exception:
            return False

    def _extract_issues(self, pages: List[Dict]) -> Dict[str, Any]:
        missing_title = [p["url"] for p in pages if not p.get("title")]
        missing_meta = [p["url"] for p in pages if not p.get("meta_description")]
        no_h1 = [p["url"] for p in pages if p.get("h1_count", 0) == 0 and not p.get("error")]
        multiple_h1 = [{"url": p["url"], "count": p["h1_count"]} for p in pages if p.get("h1_count", 0) > 1]
        long_title = [{"url": p["url"], "length": p["title_length"], "title": p.get("title", "")}
                      for p in pages if p.get("title_length", 0) > 60]
        short_meta = [{"url": p["url"], "length": p["meta_description_length"]}
                      for p in pages if 0 < p.get("meta_description_length", 0) < 50]
        long_meta = [{"url": p["url"], "length": p["meta_description_length"]}
                     for p in pages if p.get("meta_description_length", 0) > 160]
        error_pages = [p["url"] for p in pages if p.get("status", 200) >= 400]
        noindex_pages = [p["url"] for p in pages if p.get("noindex")]
        canonical_issues = [
            {"url": p["url"], "canonical": p.get("canonical_url", "")}
            for p in pages
            if p.get("canonical_url") and p.get("canonical_self") is False
        ]
        imgs_no_alt = sum(p.get("images_without_alt", 0) for p in pages)
        pages_with_schema = [p["url"] for p in pages if p.get("has_structured_data")]
        slow_pages = [
            {"url": p["url"], "response_time_ms": p["response_time_ms"]}
            for p in pages
            if p.get("response_time_ms") and p["response_time_ms"] > 1000
        ]

        # Duplicate titles
        titles_seen: Dict[str, List[str]] = {}
        for p in pages:
            t = p.get("title", "")
            if t:
                titles_seen.setdefault(t, []).append(p["url"])
        duplicate_titles = [
            {"title": t[:60], "urls": urls}
            for t, urls in titles_seen.items() if len(urls) > 1
        ]

        return {
            "missing_title": missing_title,
            "missing_meta_description": missing_meta,
            "no_h1": no_h1,
            "multiple_h1": multiple_h1,
            "title_too_long": long_title,
            "meta_too_short": short_meta,
            "meta_too_long": long_meta,
            "error_pages": error_pages,
            "noindex_pages": noindex_pages,
            "canonical_issues": canonical_issues,
            "duplicate_titles": duplicate_titles,
            "images_without_alt_total": imgs_no_alt,
            "pages_with_structured_data": pages_with_schema,
            "slow_pages": slow_pages,
        }

    def _build_summary(self, pages: List[Dict], issues: Dict) -> Dict[str, Any]:
        total = len(pages)
        ok = sum(1 for p in pages if 200 <= p.get("status", 0) < 300)
        redirects = sum(1 for p in pages if 300 <= p.get("status", 0) < 400)
        errors = sum(1 for p in pages if p.get("status", 0) >= 400)
        response_times = [p["response_time_ms"] for p in pages if p.get("response_time_ms")]
        avg_response_ms = round(sum(response_times) / len(response_times), 1) if response_times else None
        max_response_ms = max(response_times) if response_times else None

        return {
            "total_pages": total,
            "pages_ok": ok,
            "pages_redirect": redirects,
            "pages_error": errors,
            "missing_titles": len(issues["missing_title"]),
            "missing_meta": len(issues["missing_meta_description"]),
            "no_h1_pages": len(issues["no_h1"]),
            "multiple_h1_pages": len(issues["multiple_h1"]),
            "images_without_alt": issues["images_without_alt_total"],
            "duplicate_titles": len(issues["duplicate_titles"]),
            "noindex_pages": len(issues["noindex_pages"]),
            "canonical_issues": len(issues["canonical_issues"]),
            "pages_with_structured_data": len(issues["pages_with_structured_data"]),
            "slow_pages_count": len(issues["slow_pages"]),
            "avg_response_ms": avg_response_ms,
            "max_response_ms": max_response_ms,
            "seo_score": self._calc_seo_score(pages, issues),
        }

    def _calc_seo_score(self, pages: List[Dict], issues: Dict) -> int:
        """Heuristic SEO score 0–100"""
        if not pages:
            return 0
        total = len(pages)
        deductions = 0
        deductions += (len(issues["missing_title"]) / total) * 25
        deductions += (len(issues["missing_meta_description"]) / total) * 15
        deductions += (len(issues["no_h1"]) / total) * 15
        deductions += (len(issues["multiple_h1"]) / total) * 10
        deductions += (len(issues["error_pages"]) / total) * 20
        deductions += min(issues["images_without_alt_total"] / max(total, 1), 1) * 15
        return max(0, round(100 - deductions * 100))
