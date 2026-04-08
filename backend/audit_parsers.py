"""
GeoBoost – CSV-Parser für Screaming Frog und SemRush Exporte
"""

import csv
import io
from typing import Dict, Any


def parse_screaming_frog_csv(content: str) -> Dict[str, Any]:
    """Parse Screaming Frog All Pages CSV export."""
    content = content.lstrip('\ufeff').lstrip('\ufeff')  # strip BOM

    reader = csv.DictReader(io.StringIO(content))
    fieldnames = reader.fieldnames or []

    # Normalize column names (strip whitespace)
    norm = {f.strip(): f for f in fieldnames}

    def col(row: dict, *names: str) -> str:
        for name in names:
            v = row.get(name) or row.get(norm.get(name, name)) or ""
            if v:
                return v.strip()
        return ""

    def col_int(row: dict, *names: str) -> int:
        v = col(row, *names)
        try:
            return int(float(v))
        except (ValueError, TypeError):
            return 0

    summary = {
        "total_urls": 0, "ok_200": 0, "redirects_3xx": 0,
        "errors_4xx": 0, "errors_5xx": 0,
        "missing_title": 0, "title_too_long": 0, "title_too_short": 0,
        "missing_meta": 0, "meta_too_long": 0, "meta_too_short": 0,
        "missing_h1": 0, "slow_pages": 0,
    }
    issues = []

    for row in reader:
        # Strip key whitespace
        row = {k.strip(): v for k, v in row.items()}

        url = row.get("Address", "").strip()
        if not url:
            continue

        summary["total_urls"] += 1

        status_raw = row.get("Status Code", row.get("Status", "0"))
        try:
            status = int(str(status_raw).strip().split()[0])
        except (ValueError, TypeError):
            status = 0

        if 200 <= status < 300:
            summary["ok_200"] += 1
        elif 300 <= status < 400:
            summary["redirects_3xx"] += 1
        elif 400 <= status < 500:
            summary["errors_4xx"] += 1
        elif status >= 500:
            summary["errors_5xx"] += 1

        # Only analyse HTML pages (skip images, CSS, JS etc.)
        content_type = row.get("Content Type", row.get("Content-Type", ""))
        if content_type and "html" not in content_type.lower():
            continue

        # Title
        title = row.get("Title 1", row.get("Title", "")).strip()
        title_len = col_int(row, "Title 1 Length", "Title Length")
        if not title_len and title:
            title_len = len(title)

        # Meta Description
        meta = row.get("Meta Description 1", row.get("Meta Description", "")).strip()
        meta_len = col_int(row, "Meta Description 1 Length", "Meta Description Length")
        if not meta_len and meta:
            meta_len = len(meta)

        # H1
        h1 = row.get("H1-1", row.get("H1", "")).strip()
        h1_len = col_int(row, "H1-1 Length", "H1 Length")
        if not h1_len and h1:
            h1_len = len(h1)

        # H2
        h2 = row.get("H2-1", row.get("H2", "")).strip()

        # Words
        words = col_int(row, "Words", "Word Count")

        # Canonical
        canonical = row.get("Canonical Link Element 1", row.get("Canonical", "")).strip()

        # Response time (SF exports in seconds as float, convert to ms)
        rt_raw = row.get("Response Time", "0")
        try:
            rt_sec = float(str(rt_raw).strip() or "0")
            response_time_ms = int(rt_sec * 1000) if rt_sec < 1000 else int(rt_sec)
        except (ValueError, TypeError):
            response_time_ms = 0

        # Flags per issue
        flags = []
        title_issue = "ok"
        meta_issue = "ok"
        h1_issue = "ok"

        if status >= 400 or status == 0:
            flags.append("error")

        if title_len == 0:
            title_issue = "missing"
            summary["missing_title"] += 1
            flags.append("missing_title")
        elif title_len > 60:
            title_issue = "too_long"
            summary["title_too_long"] += 1
            flags.append("title_too_long")
        elif title_len < 30:
            title_issue = "too_short"
            summary["title_too_short"] += 1
            flags.append("title_too_short")

        if meta_len == 0:
            meta_issue = "missing"
            summary["missing_meta"] += 1
            flags.append("missing_meta")
        elif meta_len > 160:
            meta_issue = "too_long"
            summary["meta_too_long"] += 1
            flags.append("meta_too_long")
        elif 0 < meta_len < 70:
            meta_issue = "too_short"
            summary["meta_too_short"] += 1
            flags.append("meta_too_short")

        if not h1:
            h1_issue = "missing"
            summary["missing_h1"] += 1
            flags.append("missing_h1")

        if response_time_ms > 2000:
            summary["slow_pages"] += 1
            flags.append("slow")

        if flags:
            issues.append({
                "url": url,
                "status_code": status,
                "title": title[:80],
                "title_length": title_len,
                "title_issue": title_issue,
                "meta": meta[:120],
                "meta_length": meta_len,
                "meta_issue": meta_issue,
                "h1": h1[:80],
                "h1_length": h1_len,
                "h1_issue": h1_issue,
                "h2": h2[:60],
                "words": words,
                "canonical": canonical[:100],
                "response_time_ms": response_time_ms,
                "flags": flags,
            })

    # Sort: errors first, then by number of flags desc
    severity = {"error": 0, "missing_title": 1, "missing_h1": 1, "missing_meta": 2,
                "title_too_long": 3, "meta_too_long": 3, "slow": 4}
    issues.sort(key=lambda x: (
        min((severity.get(f, 9) for f in x["flags"]), default=9),
        -len(x["flags"]),
    ))

    return {"summary": summary, "issues": issues[:500]}


def parse_semrush_csv(content: str) -> Dict[str, Any]:
    """Parse SemRush Site Audit CSV export."""
    content = content.lstrip('\ufeff')

    reader = csv.DictReader(io.StringIO(content))

    severity_map = {
        "Error": "error", "Errors": "error",
        "Warning": "warning", "Warnings": "warning",
        "Notice": "notice", "Notices": "notice",
        "Info": "notice",
    }

    summary = {"total_issues": 0, "errors": 0, "warnings": 0, "notices": 0}
    issues = []

    for row in reader:
        row = {k.strip(): v.strip() for k, v in row.items() if k and v}

        issue_text = row.get("Issue", row.get("Issue name", row.get("Name", ""))).strip()
        if not issue_text:
            continue

        count_raw = row.get("Count", row.get("URLs", row.get("Pages", "1")))
        try:
            count = int(str(count_raw).replace(",", "").strip() or "1")
        except (ValueError, TypeError):
            count = 1

        sev_raw = row.get("Severity", row.get("Type", "Notice"))
        sev = severity_map.get(sev_raw.strip(), "notice")

        category = row.get("Category", row.get("Error Category", "")).strip()

        issues.append({
            "issue": issue_text,
            "count": count,
            "severity": sev,
            "category": category,
        })

        summary["total_issues"] += count
        if sev == "error":
            summary["errors"] += count
        elif sev == "warning":
            summary["warnings"] += count
        else:
            summary["notices"] += count

    sev_order = {"error": 0, "warning": 1, "notice": 2}
    issues.sort(key=lambda x: (sev_order.get(x["severity"], 2), -x["count"]))

    return {"summary": summary, "issues": issues}
