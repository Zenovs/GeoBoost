"""
GeoBoost – Audit HTML Report Generator
Generates a beautiful, self-contained single-file HTML report from the 6-step audit workflow.
Supports 5 visual themes: light, dark, nerd, color, schnyder.
No CDN, no external fonts – completely standalone (works with file:// protocol).
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# ── Re-use theme definitions from PDF generator ───────────────────────────────

THEMES: Dict[str, Dict[str, str]] = {
    "light": {
        "font":               "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif",
        "bg":                 "#f1f5f9",
        "bg_card":            "#ffffff",
        "bg_card_border":     "#e2e8f0",
        "bg_tbl_head":        "#2563eb",
        "bg_tbl_row_alt":     "#f0f4ff",
        "text":               "#1e293b",
        "text_muted":         "#64748b",
        "text_light":         "#94a3b8",
        "primary":            "#2563eb",
        "accent":             "#7c3aed",
        "border":             "#e2e8f0",
        "hero_bg":            "linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)",
        "hero_text":          "#ffffff",
        "hero_sub":           "rgba(255,255,255,0.82)",
        "hero_meta_bg":       "rgba(255,255,255,0.15)",
        "hero_badge_bg":      "rgba(255,255,255,0.22)",
        "hero_badge_text":    "#ffffff",
        "sidebar_bg":         "#ffffff",
        "sidebar_border":     "#e2e8f0",
        "sidebar_active_bg":  "#eff6ff",
        "sidebar_active_text": "#2563eb",
        "sidebar_text":       "#475569",
        "section_border":     "#2563eb",
        "rec_num_bg":         "#2563eb",
        "rec_num_text":       "#ffffff",
        "rec_item_bg":        "#f0f4ff",
        "score_good":         "#16a34a",
        "score_ok":           "#d97706",
        "score_bad":          "#dc2626",
        "kpi_value":          "#2563eb",
        "divider":            "#e2e8f0",
        "notes_bg":           "#f9fafb",
        "notes_border":       "#e2e8f0",
        "chip_bg":            "rgba(255,255,255,0.2)",
        "chip_text":          "#ffffff",
        "nerd_prefix":        "",
    },
    "dark": {
        "font":               "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif",
        "bg":                 "#0f172a",
        "bg_card":            "#1e293b",
        "bg_card_border":     "#334155",
        "bg_tbl_head":        "#334155",
        "bg_tbl_row_alt":     "#1a2540",
        "text":               "#e2e8f0",
        "text_muted":         "#94a3b8",
        "text_light":         "#64748b",
        "primary":            "#60a5fa",
        "accent":             "#a78bfa",
        "border":             "#334155",
        "hero_bg":            "linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)",
        "hero_text":          "#f1f5f9",
        "hero_sub":           "#94a3b8",
        "hero_meta_bg":       "rgba(255,255,255,0.07)",
        "hero_badge_bg":      "#1e3a8a",
        "hero_badge_text":    "#93c5fd",
        "sidebar_bg":         "#1e293b",
        "sidebar_border":     "#334155",
        "sidebar_active_bg":  "#1e3a8a",
        "sidebar_active_text": "#93c5fd",
        "sidebar_text":       "#94a3b8",
        "section_border":     "#60a5fa",
        "rec_num_bg":         "#1d4ed8",
        "rec_num_text":       "#ffffff",
        "rec_item_bg":        "#1e293b",
        "score_good":         "#4ade80",
        "score_ok":           "#fbbf24",
        "score_bad":          "#f87171",
        "kpi_value":          "#60a5fa",
        "divider":            "#334155",
        "notes_bg":           "#1e293b",
        "notes_border":       "#334155",
        "chip_bg":            "rgba(255,255,255,0.1)",
        "chip_text":          "#e2e8f0",
        "nerd_prefix":        "",
    },
    "nerd": {
        "font":               "'Courier New', Courier, 'Lucida Console', monospace",
        "bg":                 "#0d1117",
        "bg_card":            "#161b22",
        "bg_card_border":     "#30363d",
        "bg_tbl_head":        "#161b22",
        "bg_tbl_row_alt":     "#0d1117",
        "text":               "#c9d1d9",
        "text_muted":         "#8b949e",
        "text_light":         "#484f58",
        "primary":            "#3fb950",
        "accent":             "#58a6ff",
        "border":             "#30363d",
        "hero_bg":            "#0d1117",
        "hero_text":          "#3fb950",
        "hero_sub":           "#8b949e",
        "hero_meta_bg":       "#161b22",
        "hero_badge_bg":      "#0d2b0d",
        "hero_badge_text":    "#3fb950",
        "sidebar_bg":         "#161b22",
        "sidebar_border":     "#30363d",
        "sidebar_active_bg":  "#0d2b0d",
        "sidebar_active_text": "#3fb950",
        "sidebar_text":       "#8b949e",
        "section_border":     "#3fb950",
        "rec_num_bg":         "#0d2b0d",
        "rec_num_text":       "#3fb950",
        "rec_item_bg":        "#161b22",
        "score_good":         "#3fb950",
        "score_ok":           "#e3b341",
        "score_bad":          "#f85149",
        "kpi_value":          "#3fb950",
        "divider":            "#30363d",
        "notes_bg":           "#161b22",
        "notes_border":       "#30363d",
        "chip_bg":            "#161b22",
        "chip_text":          "#3fb950",
        "nerd_prefix":        "// ",
    },
    "color": {
        "font":               "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif",
        "bg":                 "#fafafa",
        "bg_card":            "#ffffff",
        "bg_card_border":     "#f0f0f0",
        "bg_tbl_head":        "#f43f5e",
        "bg_tbl_row_alt":     "#fff5f7",
        "text":               "#1e293b",
        "text_muted":         "#64748b",
        "text_light":         "#94a3b8",
        "primary":            "#f43f5e",
        "accent":             "#f97316",
        "border":             "#e5e7eb",
        "hero_bg":            "linear-gradient(135deg, #f43f5e 0%, #f97316 50%, #eab308 100%)",
        "hero_text":          "#ffffff",
        "hero_sub":           "rgba(255,255,255,0.88)",
        "hero_meta_bg":       "rgba(255,255,255,0.25)",
        "hero_badge_bg":      "rgba(255,255,255,0.3)",
        "hero_badge_text":    "#ffffff",
        "sidebar_bg":         "#ffffff",
        "sidebar_border":     "#f0f0f0",
        "sidebar_active_bg":  "#fff1f2",
        "sidebar_active_text": "#f43f5e",
        "sidebar_text":       "#475569",
        "section_border":     "#f43f5e",
        "rec_num_bg":         "#f43f5e",
        "rec_num_text":       "#ffffff",
        "rec_item_bg":        "#fff5f7",
        "score_good":         "#16a34a",
        "score_ok":           "#d97706",
        "score_bad":          "#dc2626",
        "kpi_value":          "#f43f5e",
        "divider":            "#fce7f3",
        "notes_bg":           "#fff9f0",
        "notes_border":       "#fed7aa",
        "chip_bg":            "rgba(255,255,255,0.3)",
        "chip_text":          "#ffffff",
        "nerd_prefix":        "",
    },
    "schnyder": {
        "font":               "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif",
        "bg":                 "#000000",
        "bg_card":            "#111111",
        "bg_card_border":     "#222222",
        "bg_tbl_head":        "#111111",
        "bg_tbl_row_alt":     "#0a0a0a",
        "text":               "#ffffff",
        "text_muted":         "#a0a0a0",
        "text_light":         "#555555",
        "primary":            "#6CFF00",
        "accent":             "#6CFF00",
        "border":             "#222222",
        "hero_bg":            "#000000",
        "hero_text":          "#6CFF00",
        "hero_sub":           "#a0a0a0",
        "hero_meta_bg":       "#111111",
        "hero_badge_bg":      "#0d2000",
        "hero_badge_text":    "#6CFF00",
        "sidebar_bg":         "#0a0a0a",
        "sidebar_border":     "#222222",
        "sidebar_active_bg":  "#0d2000",
        "sidebar_active_text": "#6CFF00",
        "sidebar_text":       "#a0a0a0",
        "section_border":     "#6CFF00",
        "rec_num_bg":         "#0d2000",
        "rec_num_text":       "#6CFF00",
        "rec_item_bg":        "#0a0a0a",
        "score_good":         "#6CFF00",
        "score_ok":           "#FFD700",
        "score_bad":          "#FF4444",
        "kpi_value":          "#6CFF00",
        "divider":            "#222222",
        "notes_bg":           "#0a0a0a",
        "notes_border":       "#333333",
        "chip_bg":            "#0d2000",
        "chip_text":          "#6CFF00",
        "nerd_prefix":        "",
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


# ── HTML Template ─────────────────────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ client_name }} – SEO & Performance Analyse | {{ company }}</title>
<style>
/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: {{ t.font }};
  background: {{ t.bg }};
  color: {{ t.text }};
  font-size: 15px;
  line-height: 1.6;
  min-height: 100vh;
}
a { color: {{ t.primary }}; text-decoration: none; }
a:hover { text-decoration: underline; }

/* ── CSS Variables ── */
:root {
  --bg:              {{ t.bg }};
  --bg-card:         {{ t.bg_card }};
  --bg-card-border:  {{ t.bg_card_border }};
  --text:            {{ t.text }};
  --text-muted:      {{ t.text_muted }};
  --text-light:      {{ t.text_light }};
  --primary:         {{ t.primary }};
  --accent:          {{ t.accent }};
  --border:          {{ t.border }};
  --score-good:      {{ t.score_good }};
  --score-ok:        {{ t.score_ok }};
  --score-bad:       {{ t.score_bad }};
  --kpi-value:       {{ t.kpi_value }};
  --notes-bg:        {{ t.notes_bg }};
  --notes-border:    {{ t.notes_border }};
  --divider:         {{ t.divider }};
  --sidebar-bg:      {{ t.sidebar_bg }};
  --sidebar-border:  {{ t.sidebar_border }};
}

/* ── Hero Section ── */
.hero {
  background: {{ t.hero_bg }};
  color: {{ t.hero_text }};
  padding: 0;
  position: relative;
  overflow: hidden;
  {% if theme_name == "schnyder" %}border-bottom: 3px solid {{ t.primary }};{% endif %}
  {% if theme_name == "nerd" %}border-bottom: 1px solid {{ t.primary }};{% endif %}
}
{% if theme_name == "light" or theme_name == "color" %}
.hero::before {
  content: "";
  position: absolute; top: -80px; right: -80px;
  width: 320px; height: 320px; border-radius: 50%;
  background: rgba(255,255,255,0.08); pointer-events: none;
}
.hero::after {
  content: "";
  position: absolute; bottom: -60px; left: -60px;
  width: 200px; height: 200px; border-radius: 50%;
  background: rgba(255,255,255,0.06); pointer-events: none;
}
{% endif %}
.hero-inner {
  position: relative; z-index: 1;
  max-width: 100%;
  padding: 48px 56px 0;
}
.hero-topbar {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 40px;
}
.hero-company {
  font-size: 11px; font-weight: 700; letter-spacing: 3px;
  text-transform: uppercase; color: {{ t.hero_text }}; opacity: 0.85;
}
.hero-badge {
  background: {{ t.hero_badge_bg }}; color: {{ t.hero_badge_text }};
  font-size: 10px; font-weight: 700; letter-spacing: 1.5px;
  text-transform: uppercase; padding: 5px 16px;
  border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}3px{% else %}20px{% endif %};
  {% if theme_name == "nerd" %}border: 1px solid {{ t.primary }};{% endif %}
  {% if theme_name == "schnyder" %}border: 1px solid {{ t.primary }};{% endif %}
}
.hero-eyebrow {
  font-size: 11px; font-weight: 600; letter-spacing: 3px;
  text-transform: uppercase;
  color: {{ t.hero_sub }};
  margin-bottom: 14px;
  {% if theme_name == "schnyder" or theme_name == "nerd" %}color: {{ t.primary }};{% endif %}
}
{% if theme_name == "nerd" %}
.hero-eyebrow::before { content: "$ "; color: {{ t.primary }}; opacity: 0.6; }
{% endif %}
.hero h1 {
  font-size: clamp(32px, 5vw, 52px);
  font-weight: 800;
  color: {{ t.hero_text }};
  line-height: 1.1;
  margin-bottom: 12px;
  {% if theme_name == "schnyder" %}letter-spacing: -1px;{% endif %}
}
.hero-url {
  font-size: 16px; color: {{ t.hero_sub }};
  margin-bottom: 40px;
  {% if theme_name == "nerd" %}font-size: 14px;{% endif %}
}
.hero-divider {
  width: 60px; height: 3px;
  background: {{ t.primary }};
  margin-bottom: 40px;
  {% if theme_name == "schnyder" %}width: 80px;{% endif %}
}
.hero-meta {
  background: {{ t.hero_meta_bg }};
  border-top: 1px solid rgba(255,255,255,0.15);
  {% if theme_name == "nerd" or theme_name == "schnyder" %}border-top: 1px solid {{ t.border }};{% endif %}
  padding: 24px 56px;
  display: flex; gap: 0; flex-wrap: wrap;
}
.hero-meta-item {
  flex: 1; min-width: 120px;
  padding: 0 24px 0 0;
  border-right: 1px solid rgba(255,255,255,0.15);
  {% if theme_name == "nerd" or theme_name == "schnyder" %}border-right: 1px solid {{ t.border }};{% endif %}
}
.hero-meta-item:first-child { padding-left: 0; }
.hero-meta-item:last-child { border-right: none; padding-right: 0; padding-left: 24px; }
.hero-meta-item label {
  color: rgba(255,255,255,0.6);
  {% if theme_name == "nerd" or theme_name == "schnyder" %}color: {{ t.primary }};{% endif %}
  font-size: 9px; text-transform: uppercase; letter-spacing: 1.2px;
  display: block; margin-bottom: 4px;
}
.hero-meta-item span {
  color: {{ t.hero_text }};
  font-weight: 600; font-size: 13px;
}

/* ── Layout ── */
.layout {
  display: flex;
  max-width: 100%;
  min-height: calc(100vh - 250px);
}

/* ── Sidebar ── */
.sidebar {
  width: 240px;
  flex-shrink: 0;
  background: {{ t.sidebar_bg }};
  border-right: 1px solid {{ t.sidebar_border }};
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  padding: 28px 0 40px;
  {% if theme_name == "nerd" %}border-right: 1px solid {{ t.primary }}33;{% endif %}
}
.sidebar::-webkit-scrollbar { width: 4px; }
.sidebar::-webkit-scrollbar-track { background: transparent; }
.sidebar::-webkit-scrollbar-thumb { background: {{ t.border }}; border-radius: 2px; }
.sidebar-label {
  font-size: 9px; font-weight: 700; letter-spacing: 2px;
  text-transform: uppercase; color: {{ t.text_light }};
  padding: 0 20px; margin-bottom: 8px; margin-top: 20px;
  {% if theme_name == "nerd" %}color: {{ t.primary }};{% endif %}
}
.sidebar-label:first-child { margin-top: 0; }
.sidebar-nav a {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 20px;
  font-size: 13px; font-weight: 500;
  color: {{ t.sidebar_text }};
  text-decoration: none;
  border-left: 3px solid transparent;
  transition: all 0.15s;
}
.sidebar-nav a:hover {
  background: {{ t.sidebar_active_bg }};
  color: {{ t.sidebar_active_text }};
  border-left-color: {{ t.primary }};
}
.sidebar-nav a.active {
  background: {{ t.sidebar_active_bg }};
  color: {{ t.sidebar_active_text }};
  border-left-color: {{ t.primary }};
  font-weight: 600;
}
.sidebar-nav a .nav-icon { font-size: 16px; flex-shrink: 0; }

/* ── Content area ── */
.content {
  flex: 1;
  padding: 36px 40px 60px;
  min-width: 0;
  max-width: 100%;
}

/* ── Section ── */
.section {
  margin-bottom: 48px;
  scroll-margin-top: 20px;
}
.section-header {
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 14px;
  border-bottom: 2px solid {{ t.section_border }};
}
.section-icon {
  width: 36px; height: 36px;
  background: {{ t.primary }}22;
  border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}4px{% else %}10px{% endif %};
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; flex-shrink: 0;
  {% if theme_name == "schnyder" %}border: 1px solid {{ t.primary }}44;{% endif %}
  {% if theme_name == "nerd" %}border: 1px solid {{ t.primary }}44;{% endif %}
}
.section h2 {
  font-size: 20px; font-weight: 700;
  color: {{ t.primary }};
  {% if theme_name == "nerd" %}text-transform: uppercase; letter-spacing: 1px; font-size: 17px;{% endif %}
}
h3.sub {
  font-size: 14px; font-weight: 600; color: {{ t.text }};
  margin: 20px 0 12px;
  {% if theme_name == "nerd" %}text-transform: uppercase; letter-spacing: 0.5px; font-size: 12px; color: {{ t.primary }};{% endif %}
}

/* ── Summary overview cards ── */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 8px;
}
.overview-card {
  background: {{ t.bg_card }};
  border: 1px solid {{ t.bg_card_border }};
  border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}4px{% else %}12px{% endif %};
  padding: 20px;
  {% if theme_name == "schnyder" %}border-left: 3px solid {{ t.primary }};{% endif %}
  transition: transform 0.15s, box-shadow 0.15s;
}
.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}
.overview-card .ov-icon { font-size: 24px; margin-bottom: 10px; display: block; }
.overview-card .ov-label { font-size: 11px; color: {{ t.text_muted }}; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 4px; }
.overview-card .ov-value { font-size: 28px; font-weight: 800; color: {{ t.kpi_value }}; line-height: 1.1; }
.overview-card .ov-sub { font-size: 12px; color: {{ t.text_light }}; margin-top: 4px; }

/* ── Score cards (lighthouse) ── */
.score-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}
.score-card {
  background: {{ t.bg_card }};
  border: 1px solid {{ t.bg_card_border }};
  border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}4px{% else %}10px{% endif %};
  padding: 16px; text-align: center;
}
.score-card .s-label { font-size: 10px; color: {{ t.text_muted }}; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; }
.score-card .s-value { font-size: 32px; font-weight: 800; line-height: 1; }
.score-card .s-sub { font-size: 10px; color: {{ t.text_light }}; margin-top: 6px; }
.score-good { color: {{ t.score_good }}; }
.score-ok   { color: {{ t.score_ok }}; }
.score-bad  { color: {{ t.score_bad }}; }

/* Score meter ring */
.score-ring { position: relative; width: 64px; height: 64px; margin: 0 auto 8px; }
.score-ring svg { transform: rotate(-90deg); }
.score-ring .ring-bg { fill: none; stroke: {{ t.bg_card_border }}; stroke-width: 4; }
.score-ring .ring-fill { fill: none; stroke-width: 4; stroke-linecap: round; transition: stroke-dashoffset 0.6s ease; }
.score-ring .ring-text {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  font-size: 16px; font-weight: 800;
}

/* ── KPI Grid ── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}
.kpi-item {
  background: {{ t.bg_card }};
  border: 1px solid {{ t.bg_card_border }};
  border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}4px{% else %}8px{% endif %};
  padding: 14px 16px;
  {% if theme_name == "schnyder" %}border-left: 3px solid {{ t.primary }};{% endif %}
}
.kpi-item .kpi-label { font-size: 10px; color: {{ t.text_muted }}; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 2px; }
.kpi-item .kpi-value { font-size: 22px; font-weight: 700; color: var(--kpi-value); }
.kpi-item .kpi-sub   { font-size: 10px; color: {{ t.text_light }}; margin-top: 2px; }

/* ── Tables ── */
.table-wrap { overflow-x: auto; border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}4px{% else %}10px{% endif %}; border: 1px solid {{ t.bg_card_border }}; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
thead th {
  background: {{ t.bg_tbl_head }};
  color: {% if theme_name == "nerd" %}{{ t.primary }}{% elif theme_name == "schnyder" %}{{ t.primary }}{% else %}#ffffff{% endif %};
  padding: 10px 14px; text-align: left; font-weight: 600; font-size: 11px;
  letter-spacing: 0.5px; text-transform: uppercase;
  {% if theme_name == "nerd" %}border-bottom: 1px solid {{ t.primary }};{% endif %}
  {% if theme_name == "schnyder" %}border-bottom: 2px solid {{ t.primary }};{% endif %}
}
tbody td {
  padding: 9px 14px; border-bottom: 1px solid {{ t.border }};
  color: {{ t.text }};
  vertical-align: middle;
}
tbody tr:nth-child(even) td { background: {{ t.bg_tbl_row_alt }}; }
tbody tr:last-child td { border-bottom: none; }
tbody tr:hover td { background: {{ t.sidebar_active_bg }}; }

/* ── Badges ── */
.badge {
  display: inline-flex; align-items: center;
  padding: 2px 9px; border-radius: 20px;
  font-size: 10px; font-weight: 700; letter-spacing: 0.3px;
  text-transform: uppercase; white-space: nowrap;
}
.badge-error   {
  background: {% if theme_name == "dark" or theme_name == "nerd" or theme_name == "schnyder" %}#3b000022{% else %}#fee2e2{% endif %};
  color: {% if theme_name == "dark" or theme_name == "nerd" %}#f87171{% elif theme_name == "schnyder" %}{{ t.score_bad }}{% else %}#dc2626{% endif %};
  border: 1px solid {% if theme_name == "dark" or theme_name == "nerd" %}#f8717133{% elif theme_name == "schnyder" %}{{ t.score_bad }}44{% else %}#fca5a5{% endif %};
}
.badge-warning {
  background: {% if theme_name == "dark" or theme_name == "nerd" or theme_name == "schnyder" %}#2d1b0022{% else %}#fef3c7{% endif %};
  color: {% if theme_name == "dark" or theme_name == "nerd" %}#fbbf24{% elif theme_name == "schnyder" %}{{ t.score_ok }}{% else %}#d97706{% endif %};
  border: 1px solid {% if theme_name == "dark" or theme_name == "nerd" %}#fbbf2433{% elif theme_name == "schnyder" %}{{ t.score_ok }}44{% else %}#fcd34d{% endif %};
}
.badge-ok {
  background: {% if theme_name == "dark" or theme_name == "nerd" %}#002b0d{% elif theme_name == "schnyder" %}#0d2000{% else %}#dcfce7{% endif %};
  color: {{ t.score_good }};
  border: 1px solid {{ t.score_good }}44;
}
.badge-notice {
  background: {% if theme_name == "dark" or theme_name == "nerd" or theme_name == "schnyder" %}#1a004022{% else %}#ede9fe{% endif %};
  color: {% if theme_name == "dark" or theme_name == "nerd" or theme_name == "schnyder" %}#a78bfa{% else %}#7c3aed{% endif %};
  border: 1px solid {% if theme_name == "dark" or theme_name == "nerd" or theme_name == "schnyder" %}#a78bfa33{% else %}#c4b5fd{% endif %};
}

/* ── Issue items ── */
.issue-list { display: flex; flex-direction: column; gap: 8px; }
.issue-item {
  background: {{ t.bg_card }};
  border: 1px solid {{ t.bg_card_border }};
  border-left: 4px solid {{ t.border }};
  border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}4px{% else %}8px{% endif %};
  padding: 12px 16px;
  transition: transform 0.1s;
}
.issue-item:hover { transform: translateX(2px); }
.issue-item.error   { border-left-color: {{ t.score_bad }}; }
.issue-item.warning { border-left-color: {{ t.score_ok }}; }
.issue-item.notice  { border-left-color: #8b5cf6; }
.issue-title { font-weight: 600; font-size: 13px; margin-bottom: 4px; color: {{ t.text }}; }
.issue-meta  { font-size: 12px; color: {{ t.text_muted }}; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

/* ── Priority cards ── */
.prio-card {
  border: 1px solid {{ t.bg_card_border }};
  border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}4px{% else %}10px{% endif %};
  overflow: hidden; margin-bottom: 12px;
}
.prio-header {
  padding: 10px 16px; font-size: 13px; font-weight: 700;
  color: white; display: flex; align-items: center; gap: 8px;
}
.prio-body {
  background: {{ t.bg_card }};
  display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px; padding: 16px;
}
.prio-col .prio-col-label {
  font-size: 10px; color: {{ t.text_muted }}; text-transform: uppercase;
  letter-spacing: 0.8px; margin-bottom: 4px;
}
.prio-col .prio-col-text { font-size: 13px; color: {{ t.text }}; }

/* ── Checklist ── */
.checklist { display: flex; flex-direction: column; gap: 8px; }
.check-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 14px;
  background: {{ t.notes_bg }};
  border: 1px solid {{ t.border }};
  border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}4px{% else %}8px{% endif %};
}
.check-icon { font-size: 18px; flex-shrink: 0; }
.check-label { font-size: 13px; color: {{ t.text }}; }

/* ── Recommendations ── */
.rec-list { display: flex; flex-direction: column; gap: 10px; }
.rec-item {
  display: flex; gap: 14px; align-items: flex-start;
  background: {{ t.rec_item_bg }};
  border: 1px solid {{ t.bg_card_border }};
  border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}4px{% else %}10px{% endif %};
  padding: 14px 16px;
  {% if theme_name == "schnyder" %}border-left: 3px solid {{ t.primary }};{% endif %}
  transition: transform 0.1s;
}
.rec-item:hover { transform: translateX(3px); }
.rec-num {
  background: {{ t.rec_num_bg }};
  color: {{ t.rec_num_text }};
  font-size: 13px; font-weight: 800;
  min-width: 30px; height: 30px;
  border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}4px{% else %}50%{% endif %};
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  {% if theme_name == "schnyder" %}border: 1px solid {{ t.primary }};{% endif %}
}
.rec-content .rec-title { font-weight: 700; font-size: 14px; margin-bottom: 2px; color: {{ t.text }}; }
.rec-content .rec-desc  { font-size: 13px; color: {{ t.text_muted }}; }

/* ── Notes box ── */
.notes-box {
  background: {{ t.notes_bg }};
  border: 1px solid {{ t.notes_border }};
  border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}4px{% else %}8px{% endif %};
  padding: 16px 18px;
  font-size: 13px; white-space: pre-wrap; line-height: 1.7;
  color: {{ t.text }};
  {% if theme_name == "nerd" %}border-left: 3px solid {{ t.primary }};{% endif %}
  {% if theme_name == "schnyder" %}border-left: 3px solid {{ t.primary }};{% endif %}
}

/* ── Two-col layout ── */
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
@media (max-width: 700px) { .two-col { grid-template-columns: 1fr; } }

/* ── Divider ── */
hr.divider { border: none; border-top: 1px solid {{ t.divider }}; margin: 28px 0; }

/* ── Footer ── */
.footer {
  text-align: center; padding: 24px 40px;
  font-size: 12px; color: {{ t.text_light }};
  border-top: 1px solid {{ t.divider }};
}

/* ── Mobile: sidebar becomes tabs ── */
@media (max-width: 860px) {
  .layout { flex-direction: column; }
  .sidebar {
    width: 100%; height: auto;
    position: sticky; top: 0; z-index: 100;
    overflow-x: auto; overflow-y: hidden;
    display: flex; flex-direction: row;
    padding: 0;
    border-right: none;
    border-bottom: 1px solid {{ t.sidebar_border }};
    scrollbar-width: none;
  }
  .sidebar::-webkit-scrollbar { display: none; }
  .sidebar-label { display: none; }
  .sidebar-nav {
    display: flex; flex-direction: row;
    white-space: nowrap; width: 100%;
  }
  .sidebar-nav a {
    padding: 12px 16px;
    border-left: none;
    border-bottom: 3px solid transparent;
    flex-shrink: 0;
  }
  .sidebar-nav a:hover,
  .sidebar-nav a.active {
    border-left: none;
    border-bottom-color: {{ t.primary }};
  }
  .content { padding: 24px 20px 48px; }
  .hero-inner { padding: 32px 24px 0; }
  .hero-meta { padding: 20px 24px; flex-wrap: wrap; gap: 16px; }
  .hero-meta-item { border-right: none; padding: 0; min-width: 0; }
  .hero-meta-item:last-child { padding-left: 0; }
  .overview-grid { grid-template-columns: repeat(2, 1fr); }
}

/* ── Print styles ── */
@media print {
  .sidebar { display: none; }
  .layout { display: block; }
  .content { padding: 0; }
}

/* ── Nerd theme extras ── */
{% if theme_name == "nerd" %}
.section h2::before { content: "// "; color: {{ t.primary }}; opacity: 0.7; }
body::before {
  content: "$ geoboost --report --generate --theme=nerd";
  display: block;
  background: {{ t.bg_card }};
  color: {{ t.primary }};
  font-family: {{ t.font }};
  font-size: 12px; padding: 8px 20px;
  border-bottom: 1px solid {{ t.border }};
  opacity: 0.7;
}
{% endif %}

/* ── Schnyder extras ── */
{% if theme_name == "schnyder" %}
.hero { border-top: 4px solid {{ t.primary }}; }
{% endif %}

</style>
</head>
<body>

<!-- ══ HERO ══════════════════════════════════════════════════════════════ -->
<div class="hero">
  <div class="hero-inner">
    <div class="hero-topbar">
      <span class="hero-company">{{ company }}</span>
      <span class="hero-badge">SEO &amp; Performance Analyse</span>
    </div>
    <div class="hero-eyebrow">Website-Analyse · {{ analysis_date }}</div>
    <h1>{{ client_name or "Unbekannter Kunde" }}</h1>
    <div class="hero-url">{{ website_url or "" }}</div>
    <div class="hero-divider"></div>
  </div>
  <div class="hero-meta">
    <div class="hero-meta-item"><label>Analysezeitraum</label><span>{{ analysis_period or "–" }}</span></div>
    <div class="hero-meta-item"><label>Analysedatum</label><span>{{ analysis_date }}</span></div>
    <div class="hero-meta-item"><label>Ansprechpartner</label><span>{{ responsible_person or "–" }}</span></div>
    <div class="hero-meta-item"><label>Erstellt von</label><span>{{ analyst_name or company }}</span></div>
  </div>
</div>

<!-- ══ MAIN LAYOUT ════════════════════════════════════════════════════════ -->
<div class="layout">

  <!-- ── Sidebar Navigation ── -->
  <nav class="sidebar">
    <div class="sidebar-label">Navigation</div>
    <div class="sidebar-nav">
      <a href="#uebersicht" class="active"><span class="nav-icon">📊</span>Übersicht</a>
      {% if crawl %}<a href="#crawl"><span class="nav-icon">🕷️</span>Crawl</a>{% endif %}
      {% if semrush %}<a href="#seo"><span class="nav-icon">🔍</span>Techn. SEO</a>{% endif %}
      {% if lighthouse %}<a href="#performance"><span class="nav-icon">⚡</span>Performance</a>{% endif %}
      <a href="#fazit"><span class="nav-icon">✅</span>Fazit</a>
    </div>
  </nav>

  <!-- ── Content ── -->
  <main class="content">

    <!-- ══ 1. Übersicht ══════════════════════════════════════════════════ -->
    <div class="section" id="uebersicht">
      <div class="section-header">
        <div class="section-icon">📊</div>
        <h2>Übersicht</h2>
      </div>

      <div class="overview-grid">
        {% if semrush and semrush.site_health_score is not none %}
        <div class="overview-card">
          <span class="ov-icon">🏥</span>
          <div class="ov-label">Site Health Score</div>
          <div class="ov-value {{ 'score-good' if semrush.site_health_score >= 80 else 'score-ok' if semrush.site_health_score >= 50 else 'score-bad' }}">{{ semrush.site_health_score }}<small style="font-size:0.45em">/100</small></div>
          <div class="ov-sub">{{ 'Gut' if semrush.site_health_score >= 80 else 'Mittel' if semrush.site_health_score >= 50 else 'Kritisch' }}</div>
        </div>
        {% endif %}
        {% if lighthouse and lighthouse.mobile_performance is not none %}
        <div class="overview-card">
          <span class="ov-icon">📱</span>
          <div class="ov-label">Mobile Performance</div>
          <div class="ov-value {{ 'score-good' if lighthouse.mobile_performance >= 90 else 'score-ok' if lighthouse.mobile_performance >= 50 else 'score-bad' }}">{{ lighthouse.mobile_performance }}<small style="font-size:0.45em">/100</small></div>
          <div class="ov-sub">PageSpeed Score</div>
        </div>
        {% endif %}
        {% if semrush and semrush.semrush_summary and semrush.semrush_summary.total_issues is not none %}
        <div class="overview-card">
          <span class="ov-icon">⚠️</span>
          <div class="ov-label">Gefundene Issues</div>
          <div class="ov-value score-bad">{{ semrush.semrush_summary.total_issues }}</div>
          <div class="ov-sub">{{ semrush.semrush_summary.errors }} Fehler · {{ semrush.semrush_summary.warnings }} Warnungen</div>
        </div>
        {% endif %}
        {% if crawl and crawl.summary and crawl.summary.total_urls is not none %}
        <div class="overview-card">
          <span class="ov-icon">🔗</span>
          <div class="ov-label">Gecrawlte URLs</div>
          <div class="ov-value">{{ crawl.summary.total_urls }}</div>
          <div class="ov-sub">{{ crawl.summary.ok_200 }} OK · {{ (crawl.summary.errors_4xx or 0) + (crawl.summary.errors_5xx or 0) }} Fehler</div>
        </div>
        {% endif %}
        {% if recommendations %}
        <div class="overview-card">
          <span class="ov-icon">💡</span>
          <div class="ov-label">Empfehlungen</div>
          <div class="ov-value">{{ recommendations | length }}</div>
          <div class="ov-sub">Priorisierte Massnahmen</div>
        </div>
        {% endif %}
        {% if lighthouse and lighthouse.desktop_performance is not none %}
        <div class="overview-card">
          <span class="ov-icon">🖥️</span>
          <div class="ov-label">Desktop Performance</div>
          <div class="ov-value {{ 'score-good' if lighthouse.desktop_performance >= 90 else 'score-ok' if lighthouse.desktop_performance >= 50 else 'score-bad' }}">{{ lighthouse.desktop_performance }}<small style="font-size:0.45em">/100</small></div>
          <div class="ov-sub">PageSpeed Score</div>
        </div>
        {% endif %}
      </div>

      {% if kickoff and kickoff.main_goals %}
      <h3 class="sub">Projektziele</h3>
      <div class="notes-box">{{ kickoff.main_goals }}</div>
      {% endif %}
    </div>

    <!-- ══ 2. Website-Crawl Analyse ══════════════════════════════════════ -->
    {% if crawl %}
    <div class="section" id="crawl">
      <div class="section-header">
        <div class="section-icon">🕷️</div>
        <h2>Website-Crawl Analyse</h2>
      </div>

      {% if crawl.summary %}
      <div class="kpi-grid" style="grid-template-columns: repeat(auto-fill, minmax(130px, 1fr))">
        <div class="kpi-item" style="border-left: 3px solid var(--kpi-value)">
          <div class="kpi-label">URLs gecrawlt</div>
          <div class="kpi-value">{{ crawl.summary.total_urls }}</div>
        </div>
        <div class="kpi-item" style="border-left: 3px solid {{ t.score_good }}">
          <div class="kpi-label">200 OK</div>
          <div class="kpi-value score-good">{{ crawl.summary.ok_200 }}</div>
        </div>
        <div class="kpi-item" style="border-left: 3px solid {{ t.score_ok }}">
          <div class="kpi-label">3xx Weiterleit.</div>
          <div class="kpi-value score-ok">{{ crawl.summary.redirects_3xx }}</div>
        </div>
        <div class="kpi-item" style="border-left: 3px solid {{ t.score_bad }}">
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
        <div class="kpi-item" style="border-left: 3px solid {{ t.score_ok }}">
          <div class="kpi-label">Langsame Seiten</div>
          <div class="kpi-value score-ok">{{ crawl.summary.slow_pages }}</div>
        </div>
      </div>
      {% endif %}

      {% if crawl.issues %}
      <h3 class="sub">Top Probleme ({{ [crawl.issues | length, 30] | min }} von {{ crawl.issues | length }})</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th style="width:38%">URL</th>
              <th>Status</th>
              <th>Title</th>
              <th>H1</th>
              <th>Meta</th>
            </tr>
          </thead>
          <tbody>
            {% for issue in crawl.issues[:30] %}
            <tr>
              <td style="font-size:11px; word-break:break-all; color:{{ t.text_muted }}">{{ issue.url }}</td>
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

    <!-- ══ 3. Technische SEO Analyse ═════════════════════════════════════ -->
    {% if semrush %}
    <div class="section" id="seo">
      <div class="section-header">
        <div class="section-icon">🔍</div>
        <h2>Technische SEO Analyse</h2>
      </div>

      {% if semrush.site_health_score is not none %}
      <div class="kpi-grid" style="margin-bottom:20px">
        <div class="kpi-item" style="border-left: 3px solid {{ 'var(--score-good)' if semrush.site_health_score >= 80 else 'var(--score-ok)' if semrush.site_health_score >= 50 else 'var(--score-bad)' }}">
          <div class="kpi-label">Site Health Score</div>
          <div class="kpi-value {{ 'score-good' if semrush.site_health_score >= 80 else 'score-ok' if semrush.site_health_score >= 50 else 'score-bad' }}">{{ semrush.site_health_score }}/100</div>
          <div class="kpi-sub">{{ 'Gut' if semrush.site_health_score >= 80 else 'Mittel' if semrush.site_health_score >= 50 else 'Kritisch' }}</div>
        </div>
        {% if semrush.semrush_summary %}
        <div class="kpi-item" style="border-left: 3px solid {{ t.score_bad }}">
          <div class="kpi-label">Fehler</div>
          <div class="kpi-value score-bad">{{ semrush.semrush_summary.errors }}</div>
        </div>
        <div class="kpi-item" style="border-left: 3px solid {{ t.score_ok }}">
          <div class="kpi-label">Warnungen</div>
          <div class="kpi-value score-ok">{{ semrush.semrush_summary.warnings }}</div>
        </div>
        <div class="kpi-item" style="border-left: 3px solid #8b5cf6">
          <div class="kpi-label">Hinweise</div>
          <div class="kpi-value" style="color:#8b5cf6">{{ semrush.semrush_summary.notices }}</div>
        </div>
        {% endif %}
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
            {% if issue.category %}<span>· {{ issue.category }}</span>{% endif %}
          </div>
        </div>
        {% endfor %}
      </div>
      {% endif %}

      {% if semrush.on_page_seo_notes %}
      <h3 class="sub" style="margin-top:20px">🔍 On-Page SEO</h3>
      <div class="notes-box">{{ semrush.on_page_seo_notes }}</div>
      {% endif %}

      {% if semrush.technical_status_notes %}
      <h3 class="sub" style="margin-top:16px">⚙️ Technischer Zustand</h3>
      <div class="notes-box">{{ semrush.technical_status_notes }}</div>
      {% endif %}

      {% if semrush.geo_ki_notes %}
      <h3 class="sub" style="margin-top:16px">🤖 KI-Suche / GEO</h3>
      <div class="notes-box">{{ semrush.geo_ki_notes }}</div>
      {% endif %}

      {% if semrush.notes %}
      <h3 class="sub" style="margin-top:16px">Allgemeine Notizen</h3>
      <div class="notes-box">{{ semrush.notes }}</div>
      {% endif %}
    </div>
    {% endif %}

    <!-- ══ 4. Performance Analyse ═════════════════════════════════════════ -->
    {% if lighthouse %}
    <div class="section" id="performance">
      <div class="section-header">
        <div class="section-icon">⚡</div>
        <h2>Performance Analyse</h2>
      </div>

      <div class="two-col">
        <div>
          <h3 class="sub">📱 Mobile</h3>
          <div class="score-row">
            {% if lighthouse.mobile_performance is not none %}
            <div class="score-card">
              <div class="s-label">Performance</div>
              <div class="s-value {{ 'score-good' if lighthouse.mobile_performance >= 90 else 'score-ok' if lighthouse.mobile_performance >= 50 else 'score-bad' }}">{{ lighthouse.mobile_performance }}</div>
              <div class="s-sub">/100</div>
            </div>
            {% endif %}
            {% if lighthouse.mobile_seo is not none %}
            <div class="score-card">
              <div class="s-label">SEO</div>
              <div class="s-value {{ 'score-good' if lighthouse.mobile_seo >= 90 else 'score-ok' if lighthouse.mobile_seo >= 50 else 'score-bad' }}">{{ lighthouse.mobile_seo }}</div>
              <div class="s-sub">/100</div>
            </div>
            {% endif %}
            {% if lighthouse.mobile_accessibility is not none %}
            <div class="score-card">
              <div class="s-label">Barrierefrei</div>
              <div class="s-value {{ 'score-good' if lighthouse.mobile_accessibility >= 90 else 'score-ok' if lighthouse.mobile_accessibility >= 50 else 'score-bad' }}">{{ lighthouse.mobile_accessibility }}</div>
              <div class="s-sub">/100</div>
            </div>
            {% endif %}
            {% if lighthouse.mobile_best_practices is not none %}
            <div class="score-card">
              <div class="s-label">Best Practices</div>
              <div class="s-value {{ 'score-good' if lighthouse.mobile_best_practices >= 90 else 'score-ok' if lighthouse.mobile_best_practices >= 50 else 'score-bad' }}">{{ lighthouse.mobile_best_practices }}</div>
              <div class="s-sub">/100</div>
            </div>
            {% endif %}
          </div>
        </div>
        <div>
          <h3 class="sub">🖥️ Desktop</h3>
          <div class="score-row">
            {% if lighthouse.desktop_performance is not none %}
            <div class="score-card">
              <div class="s-label">Performance</div>
              <div class="s-value {{ 'score-good' if lighthouse.desktop_performance >= 90 else 'score-ok' if lighthouse.desktop_performance >= 50 else 'score-bad' }}">{{ lighthouse.desktop_performance }}</div>
              <div class="s-sub">/100</div>
            </div>
            {% endif %}
            {% if lighthouse.desktop_seo is not none %}
            <div class="score-card">
              <div class="s-label">SEO</div>
              <div class="s-value {{ 'score-good' if lighthouse.desktop_seo >= 90 else 'score-ok' if lighthouse.desktop_seo >= 50 else 'score-bad' }}">{{ lighthouse.desktop_seo }}</div>
              <div class="s-sub">/100</div>
            </div>
            {% endif %}
            {% if lighthouse.desktop_accessibility is not none %}
            <div class="score-card">
              <div class="s-label">Barrierefrei</div>
              <div class="s-value {{ 'score-good' if lighthouse.desktop_accessibility >= 90 else 'score-ok' if lighthouse.desktop_accessibility >= 50 else 'score-bad' }}">{{ lighthouse.desktop_accessibility }}</div>
              <div class="s-sub">/100</div>
            </div>
            {% endif %}
            {% if lighthouse.desktop_best_practices is not none %}
            <div class="score-card">
              <div class="s-label">Best Practices</div>
              <div class="s-value {{ 'score-good' if lighthouse.desktop_best_practices >= 90 else 'score-ok' if lighthouse.desktop_best_practices >= 50 else 'score-bad' }}">{{ lighthouse.desktop_best_practices }}</div>
              <div class="s-sub">/100</div>
            </div>
            {% endif %}
          </div>
        </div>
      </div>

      {% if lighthouse.cwv_lcp or lighthouse.cwv_cls or lighthouse.cwv_tbt %}
      <h3 class="sub" style="margin-top:20px">Core Web Vitals</h3>
      <div class="kpi-grid" style="grid-template-columns: repeat(auto-fill, minmax(180px, 1fr))">
        {% if lighthouse.cwv_lcp %}
        <div class="kpi-item">
          <div class="kpi-label">LCP (Largest Contentful Paint)</div>
          <div class="kpi-value">{{ lighthouse.cwv_lcp }}</div>
          <div class="kpi-sub">Ziel: &lt; 2,5s</div>
        </div>
        {% endif %}
        {% if lighthouse.cwv_cls %}
        <div class="kpi-item">
          <div class="kpi-label">CLS (Cumulative Layout Shift)</div>
          <div class="kpi-value">{{ lighthouse.cwv_cls }}</div>
          <div class="kpi-sub">Ziel: &lt; 0.1</div>
        </div>
        {% endif %}
        {% if lighthouse.cwv_tbt %}
        <div class="kpi-item">
          <div class="kpi-label">TBT (Total Blocking Time)</div>
          <div class="kpi-value">{{ lighthouse.cwv_tbt }}</div>
          <div class="kpi-sub">Ziel: &lt; 200ms</div>
        </div>
        {% endif %}
        {% if lighthouse.cwv_fid %}
        <div class="kpi-item">
          <div class="kpi-label">FID / INP</div>
          <div class="kpi-value">{{ lighthouse.cwv_fid }}</div>
          <div class="kpi-sub">Interaktivität</div>
        </div>
        {% endif %}
      </div>
      {% endif %}

      {% set prio_a = lighthouse.prio_a %}
      {% set prio_b = lighthouse.prio_b %}
      {% set prio_c = lighthouse.prio_c %}
      {% if prio_a or prio_b or prio_c %}
      <h3 class="sub" style="margin-top:24px">Top 3 Prioritäten</h3>
      {% for prio, label, color in [(prio_a, 'Priorität A', '#dc2626'), (prio_b, 'Priorität B', '#d97706'), (prio_c, 'Priorität C', '#2563eb')] %}
      {% if prio and (prio.title or prio.warum) %}
      <div class="prio-card">
        <div class="prio-header" style="background:{{ color }}">
          <span style="font-size:16px">{{ '🔴' if loop.index == 1 else '🟠' if loop.index == 2 else '🔵' }}</span>
          {{ label }}{% if prio.title %}: {{ prio.title }}{% endif %}
        </div>
        <div class="prio-body">
          {% if prio.warum %}
          <div class="prio-col">
            <div class="prio-col-label">Warum</div>
            <div class="prio-col-text">{{ prio.warum }}</div>
          </div>
          {% endif %}
          {% if prio.erledigung %}
          <div class="prio-col">
            <div class="prio-col-label">Erledigung</div>
            <div class="prio-col-text">{{ prio.erledigung }}</div>
          </div>
          {% endif %}
          {% if prio.auswirkung %}
          <div class="prio-col">
            <div class="prio-col-label">Auswirkung</div>
            <div class="prio-col-text">{{ prio.auswirkung }}</div>
          </div>
          {% endif %}
        </div>
      </div>
      {% endif %}
      {% endfor %}
      {% endif %}

      {% if lighthouse.checklist %}
      <h3 class="sub" style="margin-top:24px">Technische Checkliste</h3>
      <div class="checklist">
        {% for key, label in [('responsive', 'Mobile-freundlich / Responsives Design'), ('https', 'HTTPS aktiviert'), ('sitemap', 'Sitemap vorhanden'), ('canonical', 'Canonical-Tags gesetzt'), ('meta_tags', 'Meta-Tags vollständig')] %}
        {% set val = lighthouse.checklist[key] if lighthouse.checklist is mapping else none %}
        <div class="check-item">
          <span class="check-icon">{{ '✅' if val else '⬜' }}</span>
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
      <div style="margin-top:14px; padding:14px 18px; background:{{ t.bg_card }}; border:1px solid {{ t.bg_card_border }}; border-radius:8px; font-size:13px">
        <strong>Nächster Schritt:</strong> {{ lighthouse.next_step }}{% if lighthouse.next_step_date %} <span style="color:{{ t.text_muted }}">– {{ lighthouse.next_step_date }}</span>{% endif %}
      </div>
      {% endif %}
    </div>
    {% endif %}

    <!-- ══ 5. Fazit & Empfehlungen ════════════════════════════════════════ -->
    <div class="section" id="fazit">
      <div class="section-header">
        <div class="section-icon">✅</div>
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

<!-- ══ FOOTER ════════════════════════════════════════════════════════════ -->
<div class="footer">
  <strong>{{ company }}</strong> &mdash; SEO &amp; Performance Analyse &mdash; {{ analysis_date }}
  {% if website_url %}&mdash; {{ website_url }}{% endif %}
</div>

<script>
// ── Smooth scroll + active nav highlight ─────────────────────────────────
(function() {
  var navLinks = document.querySelectorAll('.sidebar-nav a');
  var sections = [];

  navLinks.forEach(function(link) {
    var id = link.getAttribute('href').replace('#', '');
    var el = document.getElementById(id);
    if (el) sections.push({ id: id, el: el, link: link });

    link.addEventListener('click', function(e) {
      e.preventDefault();
      var target = document.getElementById(id);
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  function updateActive() {
    var scrollY = window.scrollY + 80;
    var active = null;

    sections.forEach(function(s) {
      if (s.el.offsetTop <= scrollY) {
        active = s;
      }
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

        t_raw = THEMES.get(theme, THEMES["light"])
        t = _D(t_raw)

        env = Environment()
        env.filters["fmt_num"] = self._fmt_num
        env.filters["fmt_pct"] = lambda v: f"{float(v):.1f}%" if v else "–"

        raw_kickoff    = audit.get("step0_kickoff") or {}
        raw_crawl      = audit.get("step3_semrush") or {}    # Background-Crawl (Screaming Frog)
        raw_semrush    = audit.get("step4_lighthouse") or {}  # SemRush Check
        raw_lighthouse = audit.get("step5_notes") or {}       # Lighthouse Bericht
        raw_report     = audit.get("step6_report") or {}      # Report / Fazit

        kickoff    = _d(raw_kickoff)
        crawl      = _d(raw_crawl)      if raw_crawl      else None
        semrush    = _d(raw_semrush)    if raw_semrush    else None
        lighthouse = _d(raw_lighthouse) if raw_lighthouse else None
        report     = _d(raw_report)

        recs_raw = raw_report.get("recommendations", "")
        recommendations = []
        if isinstance(recs_raw, list):
            recommendations = recs_raw
        elif isinstance(recs_raw, str) and recs_raw.strip():
            for line in recs_raw.strip().splitlines():
                line = line.strip().lstrip("0123456789.-) ")
                if line:
                    recommendations.append({"title": line, "description": ""})

        ctx = dict(
            t=t,
            theme_name=theme,
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
