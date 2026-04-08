"""
GeoBoost – Audit HTML Report Generator
Generates a beautiful, self-contained single-file HTML report from the 6-step audit workflow.
5 themes, in-page theme switcher, SVG charts, clean outline icons.
No CDN, no external fonts – completely standalone (works with file:// protocol).
"""

import math
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# ── Theme definitions ─────────────────────────────────────────────────────────
# Keys map to CSS variable names (snake_case → kebab-case automatically)

THEMES: Dict[str, Dict[str, str]] = {
    "light": {
        "font":                "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif",
        "bg":                  "#f1f5f9",
        "bg_card":             "#ffffff",
        "bg_card_border":      "#e2e8f0",
        "bg_tbl_head":         "#2563eb",
        "bg_tbl_row_alt":      "#f0f4ff",
        "tbl_head_text":       "#ffffff",
        "text":                "#1e293b",
        "text_muted":          "#64748b",
        "text_light":          "#94a3b8",
        "primary":             "#2563eb",
        "accent":              "#7c3aed",
        "border":              "#e2e8f0",
        "hero_bg":             "linear-gradient(135deg,#2563eb 0%,#7c3aed 100%)",
        "hero_text":           "#ffffff",
        "hero_sub":            "rgba(255,255,255,0.82)",
        "hero_meta_bg":        "rgba(255,255,255,0.15)",
        "hero_badge_bg":       "rgba(255,255,255,0.22)",
        "hero_badge_text":     "#ffffff",
        "sidebar_bg":          "#ffffff",
        "sidebar_border":      "#e2e8f0",
        "sidebar_active_bg":   "#eff6ff",
        "sidebar_active_text": "#2563eb",
        "sidebar_text":        "#475569",
        "section_border":      "#2563eb",
        "rec_num_bg":          "#2563eb",
        "rec_num_text":        "#ffffff",
        "rec_item_bg":         "#f0f4ff",
        "score_good":          "#16a34a",
        "score_ok":            "#d97706",
        "score_bad":           "#dc2626",
        "kpi_value":           "#2563eb",
        "divider":             "#e2e8f0",
        "notes_bg":            "#f9fafb",
        "notes_border":        "#e2e8f0",
        "radius_card":         "12px",
        "radius_sm":           "8px",
        "radius_badge":        "20px",
        "radius_num":          "50%",
        "badge_error_bg":      "#fee2e2",
        "badge_error_text":    "#dc2626",
        "badge_error_border":  "#fca5a5",
        "badge_warn_bg":       "#fef3c7",
        "badge_warn_text":     "#d97706",
        "badge_warn_border":   "#fcd34d",
        "badge_ok_bg":         "#dcfce7",
        "badge_notice_bg":     "#ede9fe",
        "badge_notice_text":   "#7c3aed",
        "badge_notice_border": "#c4b5fd",
        "theme_picker_border": "rgba(255,255,255,0.4)",
    },
    "dark": {
        "font":                "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif",
        "bg":                  "#0f172a",
        "bg_card":             "#1e293b",
        "bg_card_border":      "#334155",
        "bg_tbl_head":         "#334155",
        "bg_tbl_row_alt":      "#1a2540",
        "tbl_head_text":       "#e2e8f0",
        "text":                "#e2e8f0",
        "text_muted":          "#94a3b8",
        "text_light":          "#64748b",
        "primary":             "#60a5fa",
        "accent":              "#a78bfa",
        "border":              "#334155",
        "hero_bg":             "linear-gradient(135deg,#0f172a 0%,#1e1b4b 100%)",
        "hero_text":           "#f1f5f9",
        "hero_sub":            "#94a3b8",
        "hero_meta_bg":        "rgba(255,255,255,0.07)",
        "hero_badge_bg":       "#1e3a8a",
        "hero_badge_text":     "#93c5fd",
        "sidebar_bg":          "#1e293b",
        "sidebar_border":      "#334155",
        "sidebar_active_bg":   "#1e3a8a",
        "sidebar_active_text": "#93c5fd",
        "sidebar_text":        "#94a3b8",
        "section_border":      "#60a5fa",
        "rec_num_bg":          "#1d4ed8",
        "rec_num_text":        "#ffffff",
        "rec_item_bg":         "#1e293b",
        "score_good":          "#4ade80",
        "score_ok":            "#fbbf24",
        "score_bad":           "#f87171",
        "kpi_value":           "#60a5fa",
        "divider":             "#334155",
        "notes_bg":            "#1e293b",
        "notes_border":        "#334155",
        "radius_card":         "12px",
        "radius_sm":           "8px",
        "radius_badge":        "20px",
        "radius_num":          "50%",
        "badge_error_bg":      "#3b000044",
        "badge_error_text":    "#f87171",
        "badge_error_border":  "#f8717133",
        "badge_warn_bg":       "#2d1b0044",
        "badge_warn_text":     "#fbbf24",
        "badge_warn_border":   "#fbbf2433",
        "badge_ok_bg":         "#002b0d",
        "badge_notice_bg":     "#1a004044",
        "badge_notice_text":   "#a78bfa",
        "badge_notice_border": "#a78bfa33",
        "theme_picker_border": "rgba(255,255,255,0.3)",
    },
    "nerd": {
        "font":                "'Courier New',Courier,'Lucida Console',monospace",
        "bg":                  "#0d1117",
        "bg_card":             "#161b22",
        "bg_card_border":      "#30363d",
        "bg_tbl_head":         "#161b22",
        "bg_tbl_row_alt":      "#0d1117",
        "tbl_head_text":       "#3fb950",
        "text":                "#c9d1d9",
        "text_muted":          "#8b949e",
        "text_light":          "#484f58",
        "primary":             "#3fb950",
        "accent":              "#58a6ff",
        "border":              "#30363d",
        "hero_bg":             "#0d1117",
        "hero_text":           "#3fb950",
        "hero_sub":            "#8b949e",
        "hero_meta_bg":        "#161b22",
        "hero_badge_bg":       "#0d2b0d",
        "hero_badge_text":     "#3fb950",
        "sidebar_bg":          "#161b22",
        "sidebar_border":      "#30363d",
        "sidebar_active_bg":   "#0d2b0d",
        "sidebar_active_text": "#3fb950",
        "sidebar_text":        "#8b949e",
        "section_border":      "#3fb950",
        "rec_num_bg":          "#0d2b0d",
        "rec_num_text":        "#3fb950",
        "rec_item_bg":         "#161b22",
        "score_good":          "#3fb950",
        "score_ok":            "#e3b341",
        "score_bad":           "#f85149",
        "kpi_value":           "#3fb950",
        "divider":             "#30363d",
        "notes_bg":            "#161b22",
        "notes_border":        "#30363d",
        "radius_card":         "4px",
        "radius_sm":           "3px",
        "radius_badge":        "3px",
        "radius_num":          "4px",
        "badge_error_bg":      "#3b000044",
        "badge_error_text":    "#f85149",
        "badge_error_border":  "#f8514933",
        "badge_warn_bg":       "#2d1b0044",
        "badge_warn_text":     "#e3b341",
        "badge_warn_border":   "#e3b34133",
        "badge_ok_bg":         "#0d2b0d",
        "badge_notice_bg":     "#1a004044",
        "badge_notice_text":   "#58a6ff",
        "badge_notice_border": "#58a6ff33",
        "theme_picker_border": "#3fb95066",
    },
    "color": {
        "font":                "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif",
        "bg":                  "#fafafa",
        "bg_card":             "#ffffff",
        "bg_card_border":      "#f0f0f0",
        "bg_tbl_head":         "#f43f5e",
        "bg_tbl_row_alt":      "#fff5f7",
        "tbl_head_text":       "#ffffff",
        "text":                "#1e293b",
        "text_muted":          "#64748b",
        "text_light":          "#94a3b8",
        "primary":             "#f43f5e",
        "accent":              "#f97316",
        "border":              "#e5e7eb",
        "hero_bg":             "linear-gradient(135deg,#f43f5e 0%,#f97316 50%,#eab308 100%)",
        "hero_text":           "#ffffff",
        "hero_sub":            "rgba(255,255,255,0.88)",
        "hero_meta_bg":        "rgba(255,255,255,0.25)",
        "hero_badge_bg":       "rgba(255,255,255,0.3)",
        "hero_badge_text":     "#ffffff",
        "sidebar_bg":          "#ffffff",
        "sidebar_border":      "#f0f0f0",
        "sidebar_active_bg":   "#fff1f2",
        "sidebar_active_text": "#f43f5e",
        "sidebar_text":        "#475569",
        "section_border":      "#f43f5e",
        "rec_num_bg":          "#f43f5e",
        "rec_num_text":        "#ffffff",
        "rec_item_bg":         "#fff5f7",
        "score_good":          "#16a34a",
        "score_ok":            "#d97706",
        "score_bad":           "#dc2626",
        "kpi_value":           "#f43f5e",
        "divider":             "#fce7f3",
        "notes_bg":            "#fff9f0",
        "notes_border":        "#fed7aa",
        "radius_card":         "12px",
        "radius_sm":           "8px",
        "radius_badge":        "20px",
        "radius_num":          "50%",
        "badge_error_bg":      "#fee2e2",
        "badge_error_text":    "#dc2626",
        "badge_error_border":  "#fca5a5",
        "badge_warn_bg":       "#fef3c7",
        "badge_warn_text":     "#d97706",
        "badge_warn_border":   "#fcd34d",
        "badge_ok_bg":         "#dcfce7",
        "badge_notice_bg":     "#ede9fe",
        "badge_notice_text":   "#7c3aed",
        "badge_notice_border": "#c4b5fd",
        "theme_picker_border": "rgba(255,255,255,0.5)",
    },
    "schnyder": {
        "font":                "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif",
        "bg":                  "#000000",
        "bg_card":             "#111111",
        "bg_card_border":      "#222222",
        "bg_tbl_head":         "#111111",
        "bg_tbl_row_alt":      "#0a0a0a",
        "tbl_head_text":       "#6CFF00",
        "text":                "#ffffff",
        "text_muted":          "#a0a0a0",
        "text_light":          "#555555",
        "primary":             "#6CFF00",
        "accent":              "#6CFF00",
        "border":              "#222222",
        "hero_bg":             "#000000",
        "hero_text":           "#6CFF00",
        "hero_sub":            "#a0a0a0",
        "hero_meta_bg":        "#111111",
        "hero_badge_bg":       "#0d2000",
        "hero_badge_text":     "#6CFF00",
        "sidebar_bg":          "#0a0a0a",
        "sidebar_border":      "#222222",
        "sidebar_active_bg":   "#0d2000",
        "sidebar_active_text": "#6CFF00",
        "sidebar_text":        "#a0a0a0",
        "section_border":      "#6CFF00",
        "rec_num_bg":          "#0d2000",
        "rec_num_text":        "#6CFF00",
        "rec_item_bg":         "#0a0a0a",
        "score_good":          "#6CFF00",
        "score_ok":            "#FFD700",
        "score_bad":           "#FF4444",
        "kpi_value":           "#6CFF00",
        "divider":             "#222222",
        "notes_bg":            "#0a0a0a",
        "notes_border":        "#333333",
        "radius_card":         "4px",
        "radius_sm":           "3px",
        "radius_badge":        "3px",
        "radius_num":          "4px",
        "badge_error_bg":      "#3b000033",
        "badge_error_text":    "#FF4444",
        "badge_error_border":  "#FF444444",
        "badge_warn_bg":       "#2d1b0033",
        "badge_warn_text":     "#FFD700",
        "badge_warn_border":   "#FFD70044",
        "badge_ok_bg":         "#0d2000",
        "badge_notice_bg":     "#1a004033",
        "badge_notice_text":   "#a78bfa",
        "badge_notice_border": "#a78bfa33",
        "theme_picker_border": "#6CFF0066",
    },
}

# ── Helpers ───────────────────────────────────────────────────────────────────

class _D(dict):
    """Dict subclass that returns None for missing attribute/key access."""
    def __getattr__(self, key):
        try:
            v = self[key]
            return _D(v) if isinstance(v, dict) else v
        except KeyError:
            return None
    def __missing__(self, key):
        return None


def _d(data) -> "_D":
    """Recursively wrap dict data in _D for safe Jinja2 attribute access."""
    if not isinstance(data, dict):
        return data
    return _D({k: (_d(v) if isinstance(v, dict) else v) for k, v in data.items()})


def _css_vars(theme_name: str) -> str:
    """Return a CSS :root block for the given theme."""
    t = THEMES.get(theme_name, THEMES["light"])
    lines = ["  --font: " + t["font"] + ";"]
    skip = {"font", "nerd_prefix"}
    for k, v in t.items():
        if k in skip:
            continue
        css_k = "--" + k.replace("_", "-")
        lines.append(f"  {css_k}: {v};")
    return ":root {\n" + "\n".join(lines) + "\n}"


def _js_themes() -> str:
    """Return JS const THEMES = {...} object with all 5 theme variable maps."""
    parts = []
    for name, t in THEMES.items():
        entries = []
        skip = {"font", "nerd_prefix"}
        for k, v in t.items():
            if k in skip:
                continue
            css_k = "--" + k.replace("_", "-")
            escaped = v.replace("'", "\\'")
            entries.append(f"    '{css_k}': '{escaped}'")
        parts.append(f"  {name}: {{\n" + ",\n".join(entries) + "\n  }")
    return "const THEMES = {\n" + ",\n".join(parts) + "\n};"


def _gauge(score, size: int = 80) -> str:
    """SVG circular gauge chart for a 0-100 score. Returns HTML string."""
    if score is None:
        return '<div class="gauge-empty">–</div>'
    r = size * 0.44
    cx = cy = size / 2
    circ = 2 * math.pi * r
    offset = circ * (1 - max(0, min(100, score)) / 100)
    cls = "gauge-good" if score >= 90 else "gauge-ok" if score >= 50 else "gauge-bad"
    sw = size * 0.075
    fs = size * 0.22
    return (
        f'<svg class="gauge-svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}" aria-label="Score {score}">'
        f'<circle class="gauge-track" cx="{cx}" cy="{cy}" r="{r:.1f}" fill="none" stroke-width="{sw:.1f}"/>'
        f'<circle class="{cls}" cx="{cx}" cy="{cy}" r="{r:.1f}" fill="none" stroke-width="{sw:.1f}" '
        f'stroke-linecap="round" stroke-dasharray="{circ:.2f}" stroke-dashoffset="{offset:.2f}" '
        f'transform="rotate(-90 {cx} {cy})"/>'
        f'<text class="gauge-label {cls}-text" x="{cx}" y="{cy + fs*0.35:.1f}" '
        f'text-anchor="middle" font-size="{fs:.1f}" font-weight="800">{score}</text>'
        f'</svg>'
    )


def _donut(errors: int, warnings: int, notices: int) -> str:
    """SVG donut chart for SemRush issue breakdown. Returns HTML string."""
    e = errors or 0
    w = warnings or 0
    n = notices or 0
    total = e + w + n
    if total == 0:
        return ""
    r, cx, cy, sw = 30, 40, 40, 12
    circ = 2 * math.pi * r
    segments = []
    acc = 0
    for count, css_var, label in [(e, "var(--score-bad)", "Fehler"), (w, "var(--score-ok)", "Warn."), (n, "#a78bfa", "Hinweise")]:
        if count > 0:
            arc = circ * count / total
            segments.append(
                f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{css_var}" '
                f'stroke-width="{sw}" stroke-dasharray="{arc:.2f} {circ:.2f}" '
                f'stroke-dashoffset="{-acc:.2f}" transform="rotate(-90 {cx} {cy})">'
                f'<title>{label}: {count}</title></circle>'
            )
            acc += arc
    return (
        f'<svg viewBox="0 0 80 80" width="100" height="100" style="display:block;flex-shrink:0">'
        + "".join(segments)
        + f'<text x="{cx}" y="{cy - 3}" text-anchor="middle" '
        f'font-size="13" font-weight="800" fill="var(--text)">{total}</text>'
        f'<text x="{cx}" y="{cy + 10}" text-anchor="middle" font-size="8" fill="var(--text-muted)">ISSUES</text>'
        f'</svg>'
    )


def _bars(labels_values: list) -> str:
    """Horizontal bar chart. labels_values = [(label, count, kind), ...]
    kind: 'good', 'ok', 'bad', 'neutral'"""
    total = sum(max(0, v) for _, v, _ in labels_values)
    if total == 0:
        return ""
    color_map = {
        "good":    "var(--score-good)",
        "ok":      "var(--score-ok)",
        "bad":     "var(--score-bad)",
        "neutral": "var(--primary)",
    }
    rows = []
    for label, count, kind in labels_values:
        pct = max(0, count) / total * 100
        color = color_map.get(kind, color_map["neutral"])
        rows.append(
            f'<div style="margin-bottom:10px">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'font-size:12px;margin-bottom:5px">'
            f'<span style="color:var(--text)">{label}</span>'
            f'<span style="color:{color};font-weight:700">{count:,}</span>'
            f'</div>'
            f'<div style="background:var(--bg-card-border);border-radius:4px;height:7px;overflow:hidden">'
            f'<div style="width:{pct:.1f}%;height:100%;background:{color};border-radius:4px;'
            f'transition:width .6s ease"></div>'
            f'</div>'
            f'</div>'
        )
    return "".join(rows)


# ── SVG Icons (lucide-style, stroke-based) ────────────────────────────────────
# All icons: viewBox="0 0 24 24", stroke="currentColor", fill="none", stroke-width="1.75"

def _icon(path_data: str, extra: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        f'width="18" height="18" fill="none" stroke="currentColor" '
        f'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
        f'style="display:inline-block;vertical-align:middle;flex-shrink:0" {extra}>'
        f'{path_data}</svg>'
    )


ICONS = {
    "chart":       _icon('<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/><rect x="13" y="13" width="5" height="8"/>'),
    "globe":       _icon('<circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>'),
    "network":     _icon('<circle cx="12" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/><path d="M12 7v4M8.5 16.5 12 11l3.5 5.5M5 17l7-6 7 6"/>'),
    "search":      _icon('<circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>'),
    "zap":         _icon('<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>'),
    "check_circle":_icon('<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4 12 14.01l-3-3"/>'),
    "alert":       _icon('<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>'),
    "link":        _icon('<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>'),
    "mobile":      _icon('<rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><path d="M12 18h.01"/>'),
    "monitor":     _icon('<rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><path d="M8 21h8M12 17v4"/>'),
    "lightbulb":   _icon('<path d="M9 18h6M10 22h4M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/>'),
    "activity":    _icon('<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>'),
    "health":      _icon('<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>'),
    "check":       _icon('<polyline points="20 6 9 17 4 12"/>'),
    "square":      _icon('<rect x="3" y="3" width="18" height="18" rx="2"/>'),
    "trending_up": _icon('<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>'),
}


# ── HTML Template ─────────────────────────────────────────────────────────────

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="de" data-theme="{{ initial_theme }}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ client_name }} – SEO &amp; Performance Analyse | {{ company }}</title>
<style>
/* ── CSS Variables (initial theme) ── */
{{ initial_css_vars }}

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  font-size: 15px;
  line-height: 1.6;
  min-height: 100vh;
  transition: background .25s, color .25s;
}
a { color: var(--primary); text-decoration: none; }
a:hover { text-decoration: underline; }

/* ── Hero ── */
.hero {
  background: var(--hero-bg);
  color: var(--hero-text);
  position: relative;
  overflow: hidden;
}
[data-theme="schnyder"] .hero { border-top: 3px solid var(--primary); border-bottom: 3px solid var(--primary); }
[data-theme="nerd"] .hero { border-bottom: 1px solid var(--primary); }
.hero-inner { position: relative; z-index: 1; padding: 48px 56px 0; }
.hero-topbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 32px; flex-wrap: wrap; gap: 12px; }
.hero-company { font-size: 11px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; color: var(--hero-text); opacity: .85; }
.hero-badge {
  background: var(--hero-badge-bg); color: var(--hero-badge-text);
  font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase;
  padding: 5px 14px; border-radius: var(--radius-badge);
}
[data-theme="nerd"] .hero-badge, [data-theme="schnyder"] .hero-badge { border: 1px solid var(--primary); }
.hero-eyebrow { font-size: 11px; font-weight: 600; letter-spacing: 3px; text-transform: uppercase; color: var(--hero-sub); margin-bottom: 14px; }
[data-theme="schnyder"] .hero-eyebrow, [data-theme="nerd"] .hero-eyebrow { color: var(--primary); }
[data-theme="nerd"] .hero-eyebrow::before { content: "$ "; opacity: .7; }
.hero h1 { font-size: clamp(28px,5vw,52px); font-weight: 800; color: var(--hero-text); line-height: 1.1; margin-bottom: 12px; }
.hero-url { font-size: 16px; color: var(--hero-sub); margin-bottom: 32px; }
.hero-divider { width: 60px; height: 3px; background: var(--primary); margin-bottom: 32px; }
[data-theme="schnyder"] .hero-divider { width: 80px; }

/* ── Theme Picker ── */
.theme-picker {
  display: flex; align-items: center; gap: 8px;
  padding: 0 56px 20px;
  position: relative; z-index: 1;
}
.theme-picker-label { font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; color: var(--hero-sub); margin-right: 4px; }
.theme-btn {
  width: 22px; height: 22px; border-radius: 50%; border: 2px solid transparent;
  cursor: pointer; transition: transform .15s, border-color .15s;
  outline: none; flex-shrink: 0;
}
.theme-btn:hover { transform: scale(1.2); }
.theme-btn.active { border-color: var(--theme-picker-border); transform: scale(1.15); }

/* ── Hero Meta ── */
.hero-meta {
  background: var(--hero-meta-bg);
  border-top: 1px solid rgba(255,255,255,0.12);
  padding: 20px 56px;
  display: flex; gap: 0; flex-wrap: wrap;
}
[data-theme="nerd"] .hero-meta, [data-theme="schnyder"] .hero-meta { border-top: 1px solid var(--border); }
.hero-meta-item { flex: 1; min-width: 100px; padding: 0 20px 0 0; border-right: 1px solid rgba(255,255,255,0.12); }
[data-theme="nerd"] .hero-meta-item, [data-theme="schnyder"] .hero-meta-item { border-right: 1px solid var(--border); }
.hero-meta-item:first-child { padding-left: 0; }
.hero-meta-item:last-child { border-right: none; padding-right: 0; padding-left: 20px; }
.hero-meta-item label { color: rgba(255,255,255,0.55); font-size: 9px; text-transform: uppercase; letter-spacing: 1.2px; display: block; margin-bottom: 3px; }
[data-theme="nerd"] .hero-meta-item label, [data-theme="schnyder"] .hero-meta-item label { color: var(--primary); }
.hero-meta-item span { color: var(--hero-text); font-weight: 600; font-size: 13px; }

/* ── Layout ── */
.layout { display: flex; max-width: 100%; min-height: calc(100vh - 260px); }

/* ── Sidebar ── */
.sidebar {
  width: 230px; flex-shrink: 0;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--sidebar-border);
  position: sticky; top: 0; height: 100vh;
  overflow-y: auto; padding: 28px 0 40px;
}
[data-theme="nerd"] .sidebar { border-right: 1px solid var(--primary)33; }
.sidebar::-webkit-scrollbar { width: 4px; }
.sidebar::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
.sidebar-label { font-size: 9px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: var(--text-light); padding: 0 18px; margin-bottom: 6px; margin-top: 20px; }
[data-theme="nerd"] .sidebar-label { color: var(--primary); }
.sidebar-label:first-child { margin-top: 0; }
.sidebar-nav a {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 18px; font-size: 13px; font-weight: 500;
  color: var(--sidebar-text); text-decoration: none;
  border-left: 3px solid transparent; transition: all .15s;
}
.sidebar-nav a:hover, .sidebar-nav a.active {
  background: var(--sidebar-active-bg);
  color: var(--sidebar-active-text);
  border-left-color: var(--primary);
}
.sidebar-nav a.active { font-weight: 600; }
.nav-icon { display: flex; align-items: center; flex-shrink: 0; opacity: .8; }
.sidebar-nav a.active .nav-icon, .sidebar-nav a:hover .nav-icon { opacity: 1; }

/* ── Content ── */
.content { flex: 1; padding: 36px 40px 60px; min-width: 0; }

/* ── Nerd terminal bar ── */
[data-theme="nerd"] body::before {
  content: "$ geoboost --report --generate";
  display: block; background: var(--bg-card); color: var(--primary);
  font-size: 12px; padding: 8px 20px;
  border-bottom: 1px solid var(--border); opacity: .7;
}

/* ── Section ── */
.section { margin-bottom: 52px; scroll-margin-top: 20px; }
.section-header { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; padding-bottom: 14px; border-bottom: 2px solid var(--section-border); }
.section-icon {
  width: 36px; height: 36px;
  background: color-mix(in srgb, var(--primary) 15%, transparent);
  border-radius: var(--radius-sm);
  display: flex; align-items: center; justify-content: center;
  color: var(--primary); flex-shrink: 0;
}
[data-theme="nerd"] .section-icon, [data-theme="schnyder"] .section-icon { border: 1px solid color-mix(in srgb, var(--primary) 40%, transparent); }
.section h2 { font-size: 20px; font-weight: 700; color: var(--primary); }
[data-theme="nerd"] .section h2 { text-transform: uppercase; letter-spacing: 1px; font-size: 17px; }
[data-theme="nerd"] .section h2::before { content: "// "; opacity: .7; }
h3.sub { font-size: 14px; font-weight: 600; color: var(--text); margin: 20px 0 12px; }
[data-theme="nerd"] h3.sub { text-transform: uppercase; letter-spacing: .5px; font-size: 12px; color: var(--primary); }

/* ── Overview cards ── */
.overview-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 16px; margin-bottom: 8px; }
.overview-card {
  background: var(--bg-card); border: 1px solid var(--bg-card-border);
  border-radius: var(--radius-card); padding: 20px;
  transition: transform .15s, box-shadow .15s;
}
[data-theme="schnyder"] .overview-card { border-left: 3px solid var(--primary); }
.overview-card:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0,0,0,.12); }
.ov-icon { display: flex; align-items: center; color: var(--primary); margin-bottom: 10px; }
.ov-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: .8px; margin-bottom: 4px; }
.ov-value { font-size: 28px; font-weight: 800; color: var(--kpi-value); line-height: 1.1; }
.ov-sub { font-size: 12px; color: var(--text-light); margin-top: 4px; }

/* ── Gauge charts ── */
.gauge-svg { display: block; }
.gauge-track { stroke: var(--bg-card-border); }
.gauge-good { stroke: var(--score-good); }
.gauge-ok   { stroke: var(--score-ok); }
.gauge-bad  { stroke: var(--score-bad); }
.gauge-good-text { fill: var(--score-good); }
.gauge-ok-text   { fill: var(--score-ok); }
.gauge-bad-text  { fill: var(--score-bad); }
.gauge-empty { font-size: 24px; font-weight: 800; color: var(--text-light); width: 80px; text-align: center; }
.score-gauges { display: grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap: 12px; margin-bottom: 16px; }
.score-gauge-card {
  background: var(--bg-card); border: 1px solid var(--bg-card-border);
  border-radius: var(--radius-sm); padding: 16px 12px;
  display: flex; flex-direction: column; align-items: center; gap: 6px;
}
.score-gauge-label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: .8px; text-align: center; }

/* ── KPI Grid ── */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; margin-bottom: 16px; }
.kpi-item {
  background: var(--bg-card); border: 1px solid var(--bg-card-border);
  border-radius: var(--radius-sm); padding: 14px 16px;
}
[data-theme="schnyder"] .kpi-item { border-left: 3px solid var(--primary); }
.kpi-label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: .8px; margin-bottom: 2px; }
.kpi-value { font-size: 22px; font-weight: 700; color: var(--kpi-value); }
.kpi-sub   { font-size: 10px; color: var(--text-light); margin-top: 2px; }
.score-good { color: var(--score-good); }
.score-ok   { color: var(--score-ok); }
.score-bad  { color: var(--score-bad); }

/* ── Donut + bar layout ── */
.chart-row { display: flex; align-items: flex-start; gap: 24px; flex-wrap: wrap; }
.chart-bars { flex: 1; min-width: 200px; }

/* ── Tables ── */
.table-wrap { overflow-x: auto; border-radius: var(--radius-sm); border: 1px solid var(--bg-card-border); }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
thead th {
  background: var(--bg-tbl-head); color: var(--tbl-head-text);
  padding: 10px 14px; text-align: left; font-weight: 600; font-size: 11px;
  letter-spacing: .5px; text-transform: uppercase;
}
[data-theme="nerd"] thead th { border-bottom: 1px solid var(--primary); }
[data-theme="schnyder"] thead th { border-bottom: 2px solid var(--primary); }
tbody td { padding: 9px 14px; border-bottom: 1px solid var(--border); color: var(--text); vertical-align: middle; }
tbody tr:nth-child(even) td { background: var(--bg-tbl-row-alt); }
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover td { background: var(--sidebar-active-bg); }

/* ── Badges ── */
.badge { display: inline-flex; align-items: center; padding: 2px 9px; border-radius: var(--radius-badge); font-size: 10px; font-weight: 700; letter-spacing: .3px; text-transform: uppercase; white-space: nowrap; }
.badge-error   { background: var(--badge-error-bg);   color: var(--badge-error-text);   border: 1px solid var(--badge-error-border); }
.badge-warning { background: var(--badge-warn-bg);    color: var(--badge-warn-text);    border: 1px solid var(--badge-warn-border); }
.badge-ok      { background: var(--badge-ok-bg);      color: var(--score-good);          border: 1px solid color-mix(in srgb, var(--score-good) 40%, transparent); }
.badge-notice  { background: var(--badge-notice-bg);  color: var(--badge-notice-text);   border: 1px solid var(--badge-notice-border); }

/* ── Issues list ── */
.issue-list { display: flex; flex-direction: column; gap: 8px; }
.issue-item {
  background: var(--bg-card); border: 1px solid var(--bg-card-border);
  border-left: 4px solid var(--border); border-radius: var(--radius-sm);
  padding: 12px 16px; transition: transform .1s;
}
.issue-item:hover { transform: translateX(2px); }
.issue-item.error   { border-left-color: var(--score-bad); }
.issue-item.warning { border-left-color: var(--score-ok); }
.issue-item.notice  { border-left-color: var(--badge-notice-text); }
.issue-title { font-weight: 600; font-size: 13px; margin-bottom: 4px; color: var(--text); }
.issue-meta  { font-size: 12px; color: var(--text-muted); display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

/* ── Priority cards ── */
.prio-card { border: 1px solid var(--bg-card-border); border-radius: var(--radius-sm); overflow: hidden; margin-bottom: 12px; }
.prio-header { padding: 10px 16px; font-size: 13px; font-weight: 700; color: white; display: flex; align-items: center; gap: 8px; }
.prio-header .prio-icon { display: flex; align-items: center; }
.prio-body { background: var(--bg-card); display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; padding: 16px; }
.prio-col-label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: .8px; margin-bottom: 4px; }
.prio-col-text  { font-size: 13px; color: var(--text); }

/* ── Checklist ── */
.checklist { display: flex; flex-direction: column; gap: 8px; }
.check-item { display: flex; align-items: center; gap: 12px; padding: 10px 14px; background: var(--notes-bg); border: 1px solid var(--border); border-radius: var(--radius-sm); }
.check-icon { display: flex; align-items: center; flex-shrink: 0; }
.check-label { font-size: 13px; color: var(--text); }

/* ── Recommendations ── */
.rec-list { display: flex; flex-direction: column; gap: 10px; }
.rec-item {
  display: flex; gap: 14px; align-items: flex-start;
  background: var(--rec-item-bg); border: 1px solid var(--bg-card-border);
  border-radius: var(--radius-sm); padding: 14px 16px; transition: transform .1s;
}
[data-theme="schnyder"] .rec-item { border-left: 3px solid var(--primary); }
.rec-item:hover { transform: translateX(3px); }
.rec-num {
  background: var(--rec-num-bg); color: var(--rec-num-text);
  font-size: 13px; font-weight: 800;
  min-width: 30px; height: 30px; border-radius: var(--radius-num);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
[data-theme="schnyder"] .rec-num { border: 1px solid var(--primary); }
.rec-title { font-weight: 700; font-size: 14px; margin-bottom: 2px; color: var(--text); }
.rec-desc  { font-size: 13px; color: var(--text-muted); }

/* ── Notes box ── */
.notes-box {
  background: var(--notes-bg); border: 1px solid var(--notes-border);
  border-radius: var(--radius-sm); padding: 16px 18px;
  font-size: 13px; white-space: pre-wrap; line-height: 1.7; color: var(--text);
}
[data-theme="nerd"] .notes-box, [data-theme="schnyder"] .notes-box { border-left: 3px solid var(--primary); }

/* ── Misc layout ── */
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
hr.divider { border: none; border-top: 1px solid var(--divider); margin: 28px 0; }

/* ── Footer ── */
.footer { text-align: center; padding: 24px 40px; font-size: 12px; color: var(--text-light); border-top: 1px solid var(--divider); }

/* ── Mobile ── */
@media (max-width: 860px) {
  .layout { flex-direction: column; }
  .sidebar { width: 100%; height: auto; position: sticky; top: 0; z-index: 100; overflow-x: auto; overflow-y: hidden; display: flex; flex-direction: row; padding: 0; border-right: none; border-bottom: 1px solid var(--sidebar-border); scrollbar-width: none; }
  .sidebar::-webkit-scrollbar { display: none; }
  .sidebar-label { display: none; }
  .sidebar-nav { display: flex; flex-direction: row; white-space: nowrap; width: 100%; }
  .sidebar-nav a { padding: 12px 14px; border-left: none; border-bottom: 3px solid transparent; flex-shrink: 0; }
  .sidebar-nav a:hover, .sidebar-nav a.active { border-left: none; border-bottom-color: var(--primary); }
  .content { padding: 24px 20px 48px; }
  .hero-inner { padding: 32px 24px 0; }
  .hero-meta { padding: 18px 24px; flex-wrap: wrap; gap: 12px; }
  .hero-meta-item { border-right: none; padding: 0; min-width: 0; }
  .theme-picker { padding: 0 24px 16px; }
  .two-col { grid-template-columns: 1fr; }
  .overview-grid { grid-template-columns: repeat(2, 1fr); }
  .score-gauges { grid-template-columns: repeat(2, 1fr); }
}
@media print { .sidebar { display: none; } .layout { display: block; } .content { padding: 0; } }
</style>
</head>
<body>

<!-- ══ HERO ══════════════════════════════════════════════════════════════════ -->
<div class="hero">
  <div class="hero-inner">
    <div class="hero-topbar">
      <span class="hero-company">{{ company }}</span>
      <span class="hero-badge">SEO &amp; Performance Analyse</span>
    </div>
    <div class="hero-eyebrow">Website-Analyse &middot; {{ analysis_date }}</div>
    <h1>{{ client_name or "Unbekannter Kunde" }}</h1>
    <div class="hero-url">{{ website_url or "" }}</div>
    <div class="hero-divider"></div>
  </div>

  <!-- Theme Picker -->
  <div class="theme-picker">
    <span class="theme-picker-label">Theme</span>
    <button class="theme-btn {% if initial_theme == 'light' %}active{% endif %}" data-theme="light" style="background:linear-gradient(135deg,#2563eb,#7c3aed)" title="Light" onclick="switchTheme('light')"></button>
    <button class="theme-btn {% if initial_theme == 'dark' %}active{% endif %}"  data-theme="dark"  style="background:linear-gradient(135deg,#0f172a,#1e1b4b)" title="Dark"  onclick="switchTheme('dark')"></button>
    <button class="theme-btn {% if initial_theme == 'nerd' %}active{% endif %}"  data-theme="nerd"  style="background:#0d1117;border:2px solid #3fb950" title="Nerd"  onclick="switchTheme('nerd')"></button>
    <button class="theme-btn {% if initial_theme == 'color' %}active{% endif %}" data-theme="color" style="background:linear-gradient(135deg,#f43f5e,#f97316,#eab308)" title="Color" onclick="switchTheme('color')"></button>
    <button class="theme-btn {% if initial_theme == 'schnyder' %}active{% endif %}" data-theme="schnyder" style="background:#000;border:2px solid #6CFF00" title="Schnyder" onclick="switchTheme('schnyder')"></button>
  </div>

  <div class="hero-meta">
    <div class="hero-meta-item"><label>Analysezeitraum</label><span>{{ analysis_period or "–" }}</span></div>
    <div class="hero-meta-item"><label>Analysedatum</label><span>{{ analysis_date }}</span></div>
    <div class="hero-meta-item"><label>Ansprechpartner</label><span>{{ responsible_person or "–" }}</span></div>
    <div class="hero-meta-item"><label>Erstellt von</label><span>{{ analyst_name or company }}</span></div>
  </div>
</div>

<!-- ══ MAIN LAYOUT ════════════════════════════════════════════════════════════ -->
<div class="layout">

  <!-- ── Sidebar ── -->
  <nav class="sidebar">
    <div class="sidebar-label">Navigation</div>
    <div class="sidebar-nav">
      <a href="#uebersicht" class="active">
        <span class="nav-icon">{{ icons.chart | safe }}</span>Übersicht
      </a>
      {% if crawl %}
      <a href="#crawl">
        <span class="nav-icon">{{ icons.network | safe }}</span>Crawl
      </a>
      {% endif %}
      {% if semrush %}
      <a href="#seo">
        <span class="nav-icon">{{ icons.search | safe }}</span>SEO
      </a>
      {% endif %}
      {% if lighthouse %}
      <a href="#performance">
        <span class="nav-icon">{{ icons.zap | safe }}</span>Performance
      </a>
      {% endif %}
      <a href="#fazit">
        <span class="nav-icon">{{ icons.check_circle | safe }}</span>Fazit
      </a>
    </div>
  </nav>

  <!-- ── Content ── -->
  <main class="content">

    <!-- ══ 1. Übersicht ══════════════════════════════════════════════════════ -->
    <div class="section" id="uebersicht">
      <div class="section-header">
        <div class="section-icon">{{ icons.chart | safe }}</div>
        <h2>Übersicht</h2>
      </div>

      <div class="overview-grid">
        {% if semrush and semrush.site_health_score is not none %}
        <div class="overview-card">
          <div class="ov-icon">{{ icons.health | safe }}</div>
          <div class="ov-label">Site Health Score</div>
          <div class="ov-value {{ 'score-good' if semrush.site_health_score >= 80 else 'score-ok' if semrush.site_health_score >= 50 else 'score-bad' }}">{{ semrush.site_health_score }}<small style="font-size:.45em">/100</small></div>
          <div class="ov-sub">{{ 'Gut' if semrush.site_health_score >= 80 else 'Mittel' if semrush.site_health_score >= 50 else 'Kritisch' }}</div>
        </div>
        {% endif %}
        {% if lighthouse and lighthouse.mobile_performance is not none %}
        <div class="overview-card">
          <div class="ov-icon">{{ icons.mobile | safe }}</div>
          <div class="ov-label">Mobile Performance</div>
          <div class="ov-value {{ 'score-good' if lighthouse.mobile_performance >= 90 else 'score-ok' if lighthouse.mobile_performance >= 50 else 'score-bad' }}">{{ lighthouse.mobile_performance }}<small style="font-size:.45em">/100</small></div>
          <div class="ov-sub">PageSpeed Score</div>
        </div>
        {% endif %}
        {% if semrush and semrush.semrush_summary and semrush.semrush_summary.total_issues is not none %}
        <div class="overview-card">
          <div class="ov-icon">{{ icons.alert | safe }}</div>
          <div class="ov-label">Gefundene Issues</div>
          <div class="ov-value score-bad">{{ semrush.semrush_summary.total_issues }}</div>
          <div class="ov-sub">{{ semrush.semrush_summary.errors }} Fehler &middot; {{ semrush.semrush_summary.warnings }} Warnungen</div>
        </div>
        {% endif %}
        {% if crawl and crawl.summary and crawl.summary.total_urls is not none %}
        <div class="overview-card">
          <div class="ov-icon">{{ icons.link | safe }}</div>
          <div class="ov-label">Gecrawlte URLs</div>
          <div class="ov-value">{{ crawl.summary.total_urls }}</div>
          <div class="ov-sub">{{ crawl.summary.ok_200 }} OK &middot; {{ (crawl.summary.errors_4xx or 0) + (crawl.summary.errors_5xx or 0) }} Fehler</div>
        </div>
        {% endif %}
        {% if lighthouse and lighthouse.desktop_performance is not none %}
        <div class="overview-card">
          <div class="ov-icon">{{ icons.monitor | safe }}</div>
          <div class="ov-label">Desktop Performance</div>
          <div class="ov-value {{ 'score-good' if lighthouse.desktop_performance >= 90 else 'score-ok' if lighthouse.desktop_performance >= 50 else 'score-bad' }}">{{ lighthouse.desktop_performance }}<small style="font-size:.45em">/100</small></div>
          <div class="ov-sub">PageSpeed Score</div>
        </div>
        {% endif %}
        {% if recommendations %}
        <div class="overview-card">
          <div class="ov-icon">{{ icons.lightbulb | safe }}</div>
          <div class="ov-label">Empfehlungen</div>
          <div class="ov-value">{{ recommendations | length }}</div>
          <div class="ov-sub">Priorisierte Massnahmen</div>
        </div>
        {% endif %}
      </div>

      {% if kickoff and kickoff.main_goals %}
      <h3 class="sub">Projektziele</h3>
      <div class="notes-box">{{ kickoff.main_goals }}</div>
      {% endif %}
    </div>

    <!-- ══ 2. Website-Crawl Analyse ══════════════════════════════════════════ -->
    {% if crawl %}
    <div class="section" id="crawl">
      <div class="section-header">
        <div class="section-icon">{{ icons.network | safe }}</div>
        <h2>Website-Crawl Analyse</h2>
      </div>

      {% if crawl.summary %}
      <div class="kpi-grid" style="grid-template-columns:repeat(auto-fill,minmax(130px,1fr))">
        <div class="kpi-item" style="border-left:3px solid var(--primary)">
          <div class="kpi-label">URLs gecrawlt</div>
          <div class="kpi-value">{{ crawl.summary.total_urls }}</div>
        </div>
        <div class="kpi-item" style="border-left:3px solid var(--score-good)">
          <div class="kpi-label">200 OK</div>
          <div class="kpi-value score-good">{{ crawl.summary.ok_200 }}</div>
        </div>
        <div class="kpi-item" style="border-left:3px solid var(--score-ok)">
          <div class="kpi-label">3xx Weiterleit.</div>
          <div class="kpi-value score-ok">{{ crawl.summary.redirects_3xx }}</div>
        </div>
        <div class="kpi-item" style="border-left:3px solid var(--score-bad)">
          <div class="kpi-label">4xx/5xx Fehler</div>
          <div class="kpi-value score-bad">{{ (crawl.summary.errors_4xx or 0) + (crawl.summary.errors_5xx or 0) }}</div>
        </div>
        <div class="kpi-item">
          <div class="kpi-label">Fehl. Title</div>
          <div class="kpi-value">{{ crawl.summary.missing_title }}</div>
        </div>
        <div class="kpi-item">
          <div class="kpi-label">Fehl. Meta Desc.</div>
          <div class="kpi-value">{{ crawl.summary.missing_meta }}</div>
        </div>
        <div class="kpi-item">
          <div class="kpi-label">Fehl. H1</div>
          <div class="kpi-value">{{ crawl.summary.missing_h1 }}</div>
        </div>
        <div class="kpi-item" style="border-left:3px solid var(--score-ok)">
          <div class="kpi-label">Langsame Seiten</div>
          <div class="kpi-value score-ok">{{ crawl.summary.slow_pages }}</div>
        </div>
      </div>

      {% if crawl_bars %}
      <h3 class="sub">URL-Status Übersicht</h3>
      <div style="max-width:480px;background:var(--bg-card);border:1px solid var(--bg-card-border);border-radius:var(--radius-sm);padding:16px 20px">
        {{ crawl_bars | safe }}
      </div>
      {% endif %}
      {% endif %}

      {% if crawl.issues %}
      <h3 class="sub" style="margin-top:20px">Top Probleme ({{ [crawl.issues | length, 30] | min }} von {{ crawl.issues | length }})</h3>
      <div class="table-wrap">
        <table>
          <thead><tr>
            <th style="width:38%">URL</th>
            <th>Status</th><th>Title</th><th>H1</th><th>Meta</th>
          </tr></thead>
          <tbody>
            {% for issue in crawl.issues[:30] %}
            <tr>
              <td style="font-size:11px;word-break:break-all;color:var(--text-muted)">{{ issue.url }}</td>
              <td><span class="badge {{ 'badge-error' if issue.status_code >= 400 else 'badge-warning' if issue.status_code >= 300 else 'badge-ok' }}">{{ issue.status_code }}</span></td>
              <td><span class="badge {{ 'badge-error' if issue.title_issue == 'missing' else 'badge-warning' if issue.title_issue != 'ok' else 'badge-ok' }}">{{ issue.title_issue }}</span></td>
              <td><span class="badge {{ 'badge-error' if issue.h1_issue == 'missing' else 'badge-ok' }}">{{ issue.h1_issue }}</span></td>
              <td><span class="badge {{ 'badge-error' if issue.meta_issue == 'missing' else 'badge-warning' if issue.meta_issue != 'ok' else 'badge-ok' }}">{{ issue.meta_issue }}</span></td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
      {% endif %}

      {% if crawl.notes %}
      <h3 class="sub" style="margin-top:20px">Notizen</h3>
      <div class="notes-box">{{ crawl.notes }}</div>
      {% endif %}
    </div>
    {% endif %}

    <!-- ══ 3. Technische SEO Analyse ══════════════════════════════════════════ -->
    {% if semrush %}
    <div class="section" id="seo">
      <div class="section-header">
        <div class="section-icon">{{ icons.search | safe }}</div>
        <h2>Technische SEO Analyse</h2>
      </div>

      {% if semrush.site_health_score is not none %}
      <div class="kpi-grid" style="margin-bottom:20px">
        <div class="kpi-item" style="border-left:3px solid {{ 'var(--score-good)' if semrush.site_health_score >= 80 else 'var(--score-ok)' if semrush.site_health_score >= 50 else 'var(--score-bad)' }}">
          <div class="kpi-label">Site Health Score</div>
          <div class="kpi-value {{ 'score-good' if semrush.site_health_score >= 80 else 'score-ok' if semrush.site_health_score >= 50 else 'score-bad' }}">{{ semrush.site_health_score }}/100</div>
          <div class="kpi-sub">{{ 'Gut' if semrush.site_health_score >= 80 else 'Mittel' if semrush.site_health_score >= 50 else 'Kritisch' }}</div>
        </div>
        {% if semrush.semrush_summary %}
        <div class="kpi-item" style="border-left:3px solid var(--score-bad)">
          <div class="kpi-label">Fehler</div>
          <div class="kpi-value score-bad">{{ semrush.semrush_summary.errors }}</div>
        </div>
        <div class="kpi-item" style="border-left:3px solid var(--score-ok)">
          <div class="kpi-label">Warnungen</div>
          <div class="kpi-value score-ok">{{ semrush.semrush_summary.warnings }}</div>
        </div>
        <div class="kpi-item" style="border-left:3px solid var(--badge-notice-text)">
          <div class="kpi-label">Hinweise</div>
          <div class="kpi-value" style="color:var(--badge-notice-text)">{{ semrush.semrush_summary.notices }}</div>
        </div>
        {% endif %}
      </div>
      {% endif %}

      {% if semrush_donut and semrush.semrush_summary %}
      <h3 class="sub">Issue-Verteilung</h3>
      <div class="chart-row" style="margin-bottom:20px;align-items:center">
        {{ semrush_donut | safe }}
        <div class="chart-bars" style="flex:1;min-width:160px">
          {% if semrush.semrush_summary.errors %}
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;font-size:13px">
            <span style="width:10px;height:10px;border-radius:50%;background:var(--score-bad);flex-shrink:0"></span>
            <span style="color:var(--text)">Fehler</span>
            <span style="margin-left:auto;font-weight:700;color:var(--score-bad)">{{ semrush.semrush_summary.errors }}</span>
          </div>
          {% endif %}
          {% if semrush.semrush_summary.warnings %}
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;font-size:13px">
            <span style="width:10px;height:10px;border-radius:50%;background:var(--score-ok);flex-shrink:0"></span>
            <span style="color:var(--text)">Warnungen</span>
            <span style="margin-left:auto;font-weight:700;color:var(--score-ok)">{{ semrush.semrush_summary.warnings }}</span>
          </div>
          {% endif %}
          {% if semrush.semrush_summary.notices %}
          <div style="display:flex;align-items:center;gap:8px;font-size:13px">
            <span style="width:10px;height:10px;border-radius:50%;background:var(--badge-notice-text);flex-shrink:0"></span>
            <span style="color:var(--text)">Hinweise</span>
            <span style="margin-left:auto;font-weight:700;color:var(--badge-notice-text)">{{ semrush.semrush_summary.notices }}</span>
          </div>
          {% endif %}
        </div>
      </div>
      {% endif %}

      {% if semrush.semrush_issues %}
      <h3 class="sub">Gefundene Probleme</h3>
      <div class="issue-list">
        {% for issue in semrush.semrush_issues[:20] %}
        <div class="issue-item {{ issue.severity }}">
          <div class="issue-title">{{ issue.issue }}</div>
          <div class="issue-meta">
            <span class="badge badge-{{ 'error' if issue.severity == 'error' else 'warning' if issue.severity == 'warning' else 'notice' }}">{{ issue.severity | upper }}</span>
            <span>{{ issue.count }} betroffene URLs</span>
            {% if issue.category %}<span>&middot; {{ issue.category }}</span>{% endif %}
          </div>
        </div>
        {% endfor %}
      </div>
      {% endif %}

      {% if semrush.on_page_seo_notes %}
      <h3 class="sub" style="margin-top:20px">On-Page SEO</h3>
      <div class="notes-box">{{ semrush.on_page_seo_notes }}</div>
      {% endif %}
      {% if semrush.technical_status_notes %}
      <h3 class="sub" style="margin-top:16px">Technischer Zustand</h3>
      <div class="notes-box">{{ semrush.technical_status_notes }}</div>
      {% endif %}
      {% if semrush.geo_ki_notes %}
      <h3 class="sub" style="margin-top:16px">KI-Suche / GEO</h3>
      <div class="notes-box">{{ semrush.geo_ki_notes }}</div>
      {% endif %}
      {% if semrush.notes %}
      <h3 class="sub" style="margin-top:16px">Allgemeine Notizen</h3>
      <div class="notes-box">{{ semrush.notes }}</div>
      {% endif %}
    </div>
    {% endif %}

    <!-- ══ 4. Performance Analyse ═════════════════════════════════════════════ -->
    {% if lighthouse %}
    <div class="section" id="performance">
      <div class="section-header">
        <div class="section-icon">{{ icons.zap | safe }}</div>
        <h2>Performance Analyse</h2>
      </div>

      <div class="two-col">
        <div>
          <h3 class="sub" style="display:flex;align-items:center;gap:8px">
            <span style="display:flex;align-items:center;color:var(--primary)">{{ icons.mobile | safe }}</span>
            Mobile
          </h3>
          <div class="score-gauges">
            {% if lighthouse.mobile_performance is not none %}
            <div class="score-gauge-card">
              <div class="score-gauge-label">Performance</div>
              {{ gauge_mobile_perf | safe }}
            </div>
            {% endif %}
            {% if lighthouse.mobile_seo is not none %}
            <div class="score-gauge-card">
              <div class="score-gauge-label">SEO</div>
              {{ gauge_mobile_seo | safe }}
            </div>
            {% endif %}
            {% if lighthouse.mobile_accessibility is not none %}
            <div class="score-gauge-card">
              <div class="score-gauge-label">Barrierefrei</div>
              {{ gauge_mobile_a11y | safe }}
            </div>
            {% endif %}
            {% if lighthouse.mobile_best_practices is not none %}
            <div class="score-gauge-card">
              <div class="score-gauge-label">Best Practices</div>
              {{ gauge_mobile_bp | safe }}
            </div>
            {% endif %}
          </div>
        </div>
        <div>
          <h3 class="sub" style="display:flex;align-items:center;gap:8px">
            <span style="display:flex;align-items:center;color:var(--primary)">{{ icons.monitor | safe }}</span>
            Desktop
          </h3>
          <div class="score-gauges">
            {% if lighthouse.desktop_performance is not none %}
            <div class="score-gauge-card">
              <div class="score-gauge-label">Performance</div>
              {{ gauge_desktop_perf | safe }}
            </div>
            {% endif %}
            {% if lighthouse.desktop_seo is not none %}
            <div class="score-gauge-card">
              <div class="score-gauge-label">SEO</div>
              {{ gauge_desktop_seo | safe }}
            </div>
            {% endif %}
            {% if lighthouse.desktop_accessibility is not none %}
            <div class="score-gauge-card">
              <div class="score-gauge-label">Barrierefrei</div>
              {{ gauge_desktop_a11y | safe }}
            </div>
            {% endif %}
            {% if lighthouse.desktop_best_practices is not none %}
            <div class="score-gauge-card">
              <div class="score-gauge-label">Best Practices</div>
              {{ gauge_desktop_bp | safe }}
            </div>
            {% endif %}
          </div>
        </div>
      </div>

      {% if lighthouse.cwv_lcp or lighthouse.cwv_cls or lighthouse.cwv_tbt %}
      <h3 class="sub" style="margin-top:20px">Core Web Vitals</h3>
      <div class="kpi-grid" style="grid-template-columns:repeat(auto-fill,minmax(190px,1fr))">
        {% if lighthouse.cwv_lcp %}
        <div class="kpi-item" style="border-left:3px solid var(--primary)">
          <div class="kpi-label">LCP &middot; Largest Contentful Paint</div>
          <div class="kpi-value">{{ lighthouse.cwv_lcp }}</div>
          <div class="kpi-sub">Ziel: &lt; 2,5s</div>
        </div>
        {% endif %}
        {% if lighthouse.cwv_cls %}
        <div class="kpi-item" style="border-left:3px solid var(--primary)">
          <div class="kpi-label">CLS &middot; Cumulative Layout Shift</div>
          <div class="kpi-value">{{ lighthouse.cwv_cls }}</div>
          <div class="kpi-sub">Ziel: &lt; 0.1</div>
        </div>
        {% endif %}
        {% if lighthouse.cwv_tbt %}
        <div class="kpi-item" style="border-left:3px solid var(--primary)">
          <div class="kpi-label">TBT &middot; Total Blocking Time</div>
          <div class="kpi-value">{{ lighthouse.cwv_tbt }}</div>
          <div class="kpi-sub">Ziel: &lt; 200ms</div>
        </div>
        {% endif %}
        {% if lighthouse.cwv_fid %}
        <div class="kpi-item" style="border-left:3px solid var(--primary)">
          <div class="kpi-label">FID / INP &middot; Interaktivität</div>
          <div class="kpi-value">{{ lighthouse.cwv_fid }}</div>
          <div class="kpi-sub">Ziel: &lt; 200ms</div>
        </div>
        {% endif %}
      </div>
      {% endif %}

      {% set prio_a = lighthouse.prio_a %}
      {% set prio_b = lighthouse.prio_b %}
      {% set prio_c = lighthouse.prio_c %}
      {% if prio_a or prio_b or prio_c %}
      <h3 class="sub" style="margin-top:24px">Top 3 Prioritäten</h3>
      {% for prio, label, color in [(prio_a,'Priorität A','#dc2626'),(prio_b,'Priorität B','#d97706'),(prio_c,'Priorität C','#2563eb')] %}
      {% if prio and (prio.title or prio.warum) %}
      <div class="prio-card">
        <div class="prio-header" style="background:{{ color }}">
          <span class="prio-icon">{{ icons.alert | safe }}</span>
          {{ label }}{% if prio.title %}: {{ prio.title }}{% endif %}
        </div>
        <div class="prio-body">
          {% if prio.warum %}<div class="prio-col"><div class="prio-col-label">Warum</div><div class="prio-col-text">{{ prio.warum }}</div></div>{% endif %}
          {% if prio.erledigung %}<div class="prio-col"><div class="prio-col-label">Erledigung</div><div class="prio-col-text">{{ prio.erledigung }}</div></div>{% endif %}
          {% if prio.auswirkung %}<div class="prio-col"><div class="prio-col-label">Auswirkung</div><div class="prio-col-text">{{ prio.auswirkung }}</div></div>{% endif %}
        </div>
      </div>
      {% endif %}
      {% endfor %}
      {% endif %}

      {% if lighthouse.checklist %}
      <h3 class="sub" style="margin-top:24px">Technische Checkliste</h3>
      <div class="checklist">
        {% for key, label in [('responsive','Mobile-freundlich / Responsives Design'),('https','HTTPS aktiviert'),('sitemap','Sitemap vorhanden'),('canonical','Canonical-Tags gesetzt'),('meta_tags','Meta-Tags vollständig')] %}
        {% set val = lighthouse.checklist[key] if lighthouse.checklist is mapping else none %}
        <div class="check-item">
          <span class="check-icon" style="color:{{ 'var(--score-good)' if val else 'var(--text-light)' }}">
            {{ icons.check | safe if val else icons.square | safe }}
          </span>
          <span class="check-label">{{ label }}</span>
        </div>
        {% endfor %}
      </div>
      {% endif %}

      {% if lighthouse.fazit %}
      <h3 class="sub" style="margin-top:24px">Fazit Performance</h3>
      <div class="notes-box">{{ lighthouse.fazit }}</div>
      {% endif %}

      {% if lighthouse.next_step %}
      <div style="margin-top:14px;padding:14px 18px;background:var(--bg-card);border:1px solid var(--bg-card-border);border-radius:var(--radius-sm);font-size:13px;display:flex;align-items:center;gap:10px">
        <span style="color:var(--primary)">{{ icons.trending_up | safe }}</span>
        <span><strong>Nächster Schritt:</strong> {{ lighthouse.next_step }}{% if lighthouse.next_step_date %} <span style="color:var(--text-muted)">– {{ lighthouse.next_step_date }}</span>{% endif %}</span>
      </div>
      {% endif %}
    </div>
    {% endif %}

    <!-- ══ 5. Fazit & Empfehlungen ═════════════════════════════════════════════ -->
    <div class="section" id="fazit">
      <div class="section-header">
        <div class="section-icon">{{ icons.check_circle | safe }}</div>
        <h2>Fazit &amp; Empfehlungen</h2>
      </div>

      {% if findings %}
      <h3 class="sub">Wichtigste Erkenntnisse</h3>
      <div class="notes-box" style="margin-bottom:24px">{{ findings }}</div>
      {% endif %}

      {% if recommendations %}
      <h3 class="sub">Empfehlungen</h3>
      <div class="rec-list">
        {% for rec in recommendations %}
        <div class="rec-item">
          <div class="rec-num">{{ loop.index }}</div>
          <div class="rec-content">
            <div class="rec-title">{{ rec.title }}</div>
            {% if rec.description %}<div class="rec-desc">{{ rec.description }}</div>{% endif %}
          </div>
        </div>
        {% endfor %}
      </div>
      {% endif %}

      {% if general_notes %}
      <h3 class="sub" style="margin-top:24px">Weitere Notizen / Nächste Schritte</h3>
      <div class="notes-box">{{ general_notes }}</div>
      {% endif %}
    </div>

  </main>
</div>

<!-- ══ FOOTER ════════════════════════════════════════════════════════════════ -->
<div class="footer">
  <strong>{{ company }}</strong> &mdash; SEO &amp; Performance Analyse &mdash; {{ analysis_date }}
  {% if website_url %}&mdash; {{ website_url }}{% endif %}
</div>

<script>
// ── Theme Switcher ────────────────────────────────────────────────────────────
{{ js_themes | safe }}

function switchTheme(name) {
  var t = THEMES[name];
  if (!t) return;
  var root = document.documentElement;
  Object.keys(t).forEach(function(k) { root.style.setProperty(k, t[k]); });
  // font needs to be set on body too
  if (t['--font']) document.body.style.fontFamily = t['--font'];
  // update data-theme for CSS structural variants
  root.setAttribute('data-theme', name);
  // update picker buttons
  document.querySelectorAll('.theme-btn').forEach(function(b) {
    b.classList.toggle('active', b.dataset.theme === name);
  });
  try { localStorage.setItem('gb-theme', name); } catch(e) {}
}

// Restore saved theme on load
(function() {
  try {
    var saved = localStorage.getItem('gb-theme');
    if (saved && THEMES[saved]) switchTheme(saved);
  } catch(e) {}
})();

// ── Scroll-spy sidebar ────────────────────────────────────────────────────────
(function() {
  var navLinks = document.querySelectorAll('.sidebar-nav a');
  var sections = [];

  navLinks.forEach(function(link) {
    var id = link.getAttribute('href').replace('#', '');
    var el = document.getElementById(id);
    if (el) sections.push({ el: el, link: link });
    link.addEventListener('click', function(e) {
      e.preventDefault();
      var target = document.getElementById(id);
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  function updateActive() {
    var scrollY = window.scrollY + 80;
    var active = null;
    sections.forEach(function(s) {
      if (s.el.offsetTop <= scrollY) active = s;
    });
    navLinks.forEach(function(l) { l.classList.remove('active'); });
    if (active) active.link.classList.add('active');
  }

  window.addEventListener('scroll', updateActive, { passive: true });
  updateActive();
})();
</script>

</body>
</html>
"""


# ── Generator class ───────────────────────────────────────────────────────────

class AuditHTMLGenerator:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.company = self.config.get("company_name", "GeoBoost")

    def _fmt_num(self, v) -> str:
        try:
            return f"{int(v):,}".replace(",", "'")
        except Exception:
            return str(v) if v is not None else "–"

    def generate(self, audit: Dict[str, Any], output_path: str, theme: str = "light") -> str:
        """Generate self-contained HTML report. Returns output_path."""
        from jinja2 import Environment

        env = Environment()
        env.filters["fmt_num"] = self._fmt_num
        env.filters["fmt_pct"] = lambda v: f"{float(v):.1f}%" if v else "–"

        # ── Unpack audit steps
        raw_kickoff    = audit.get("step0_kickoff")    or {}
        raw_crawl      = audit.get("step3_semrush")    or {}
        raw_semrush    = audit.get("step4_lighthouse") or {}
        raw_lighthouse = audit.get("step5_notes")      or {}
        raw_report     = audit.get("step6_report")     or {}

        kickoff    = _d(raw_kickoff)
        crawl      = _d(raw_crawl)      if raw_crawl      else None
        semrush    = _d(raw_semrush)    if raw_semrush    else None
        lighthouse = _d(raw_lighthouse) if raw_lighthouse else None
        report     = _d(raw_report)

        # ── Recommendations
        recs_raw = raw_report.get("recommendations", "")
        recommendations = []
        if isinstance(recs_raw, list):
            recommendations = recs_raw
        elif isinstance(recs_raw, str) and recs_raw.strip():
            for line in recs_raw.strip().splitlines():
                line = line.strip().lstrip("0123456789.-) ")
                if line:
                    recommendations.append({"title": line, "description": ""})

        # ── Pre-render SVG charts
        lh = lighthouse or _D()
        gauge_mobile_perf  = _gauge(lh.mobile_performance)
        gauge_mobile_seo   = _gauge(lh.mobile_seo)
        gauge_mobile_a11y  = _gauge(lh.mobile_accessibility)
        gauge_mobile_bp    = _gauge(lh.mobile_best_practices)
        gauge_desktop_perf = _gauge(lh.desktop_performance)
        gauge_desktop_seo  = _gauge(lh.desktop_seo)
        gauge_desktop_a11y = _gauge(lh.desktop_accessibility)
        gauge_desktop_bp   = _gauge(lh.desktop_best_practices)

        sm = semrush
        semrush_donut = ""
        if sm and sm.semrush_summary:
            e = sm.semrush_summary.errors or 0
            w = sm.semrush_summary.warnings or 0
            n = sm.semrush_summary.notices or 0
            semrush_donut = _donut(int(e) if e else 0, int(w) if w else 0, int(n) if n else 0)

        crawl_bars = ""
        if crawl and crawl.summary:
            s = crawl.summary
            ok   = int(s.ok_200 or 0)
            r3   = int(s.redirects_3xx or 0)
            e4   = int(s.errors_4xx or 0)
            e5   = int(s.errors_5xx or 0)
            errs = e4 + e5
            data = []
            if ok:   data.append(("200 OK", ok, "good"))
            if r3:   data.append(("3xx Weiterleitungen", r3, "ok"))
            if errs: data.append(("4xx / 5xx Fehler", errs, "bad"))
            crawl_bars = _bars(data) if data else ""

        ctx = dict(
            initial_theme=theme,
            initial_css_vars=_css_vars(theme),
            js_themes=_js_themes(),
            icons=_D({k: v for k, v in ICONS.items()}),
            company=self.company,
            audit_id=audit.get("id", ""),
            client_name=audit.get("client_name") or kickoff.get("client_name", ""),
            website_url=audit.get("website_url") or kickoff.get("website_url", ""),
            analysis_period=kickoff.get("analysis_period", ""),
            analysis_date=kickoff.get("analysis_date") or datetime.now().strftime("%d.%m.%Y"),
            analyst_name=kickoff.get("analyst_name") or self.company,
            responsible_person=kickoff.get("responsible_person", ""),
            kickoff=kickoff,
            crawl=crawl,
            semrush=semrush,
            lighthouse=lighthouse,
            gauge_mobile_perf=gauge_mobile_perf,
            gauge_mobile_seo=gauge_mobile_seo,
            gauge_mobile_a11y=gauge_mobile_a11y,
            gauge_mobile_bp=gauge_mobile_bp,
            gauge_desktop_perf=gauge_desktop_perf,
            gauge_desktop_seo=gauge_desktop_seo,
            gauge_desktop_a11y=gauge_desktop_a11y,
            gauge_desktop_bp=gauge_desktop_bp,
            semrush_donut=semrush_donut,
            crawl_bars=crawl_bars,
            findings=report.get("findings", ""),
            recommendations=recommendations,
            general_notes=report.get("general_notes", ""),
        )

        template = env.from_string(HTML_TEMPLATE)
        html = template.render(**ctx)

        output_path = str(output_path)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(html, encoding="utf-8")
        return output_path
