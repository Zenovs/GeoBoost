"""
GeoBoost – Audit PDF Generator
Generates a structured PDF report from the 6-step audit workflow data.
Supports 5 visual themes: light, dark, nerd, color, schnyder.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any


# ── Theme definitions ─────────────────────────────────────────────────────────

THEMES: Dict[str, Dict[str, str]] = {
    "light": {
        "font":               "'Helvetica Neue', Arial, sans-serif",
        "bg":                 "#ffffff",
        "bg_card":            "#f8f9ff",
        "bg_card_border":     "#e8eaf0",
        "bg_tbl_head":        "#2563eb",
        "bg_tbl_row_alt":     "#f0f4ff",
        "text":               "#1e293b",
        "text_muted":         "#64748b",
        "text_light":         "#94a3b8",
        "primary":            "#2563eb",
        "accent":             "#7c3aed",
        "border":             "#e8eaf0",
        "cover_bg":           "linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)",
        "cover_text":         "#ffffff",
        "cover_sub":          "rgba(255,255,255,0.82)",
        "cover_meta_bg":      "rgba(255,255,255,0.15)",
        "cover_meta_border":  "transparent",
        "cover_label":        "rgba(255,255,255,0.65)",
        "cover_badge_bg":     "rgba(255,255,255,0.22)",
        "cover_badge_text":   "#ffffff",
        "section_title_border": "#2563eb",
        "rec_num_bg":         "#2563eb",
        "rec_num_text":       "#ffffff",
        "rec_item_bg":        "#f0f4ff",
        "score_good":         "#16a34a",
        "score_ok":           "#d97706",
        "score_bad":          "#dc2626",
        "kpi_value":          "#2563eb",
        "divider":            "#e8eaf0",
        "notes_bg":           "#f9fafb",
        "notes_border":       "#e8eaf0",
        "page_footer_color":  "#94a3b8",
    },
    "dark": {
        "font":               "'Helvetica Neue', Arial, sans-serif",
        "bg":                 "#0f172a",
        "bg_card":            "#1e293b",
        "bg_card_border":     "#334155",
        "bg_tbl_head":        "#334155",
        "bg_tbl_row_alt":     "#1e293b",
        "text":               "#e2e8f0",
        "text_muted":         "#94a3b8",
        "text_light":         "#64748b",
        "primary":            "#60a5fa",
        "accent":             "#a78bfa",
        "border":             "#334155",
        "cover_bg":           "linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)",
        "cover_text":         "#f1f5f9",
        "cover_sub":          "#94a3b8",
        "cover_meta_bg":      "rgba(255,255,255,0.07)",
        "cover_meta_border":  "#334155",
        "cover_label":        "#64748b",
        "cover_badge_bg":     "#1e3a8a",
        "cover_badge_text":   "#93c5fd",
        "section_title_border": "#60a5fa",
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
        "page_footer_color":  "#475569",
    },
    "nerd": {
        "font":               "'Courier New', Courier, monospace",
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
        "cover_bg":           "#0d1117",
        "cover_text":         "#3fb950",
        "cover_sub":          "#8b949e",
        "cover_meta_bg":      "#161b22",
        "cover_meta_border":  "#3fb950",
        "cover_label":        "#58a6ff",
        "cover_badge_bg":     "#0d2b0d",
        "cover_badge_text":   "#3fb950",
        "section_title_border": "#3fb950",
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
        "page_footer_color":  "#484f58",
    },
    "color": {
        "font":               "'Helvetica Neue', Arial, sans-serif",
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
        "cover_bg":           "linear-gradient(135deg, #f43f5e 0%, #f97316 50%, #eab308 100%)",
        "cover_text":         "#ffffff",
        "cover_sub":          "rgba(255,255,255,0.88)",
        "cover_meta_bg":      "rgba(255,255,255,0.25)",
        "cover_meta_border":  "transparent",
        "cover_label":        "rgba(255,255,255,0.7)",
        "cover_badge_bg":     "rgba(255,255,255,0.3)",
        "cover_badge_text":   "#ffffff",
        "section_title_border": "#f43f5e",
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
        "page_footer_color":  "#94a3b8",
    },
    "schnyder": {
        "font":               "'Helvetica Neue', Arial, sans-serif",
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
        "cover_bg":           "#000000",
        "cover_text":         "#6CFF00",
        "cover_sub":          "#a0a0a0",
        "cover_meta_bg":      "#111111",
        "cover_meta_border":  "#6CFF00",
        "cover_label":        "#6CFF00",
        "cover_badge_bg":     "#0d2000",
        "cover_badge_text":   "#6CFF00",
        "section_title_border": "#6CFF00",
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
        "page_footer_color":  "#444444",
    },
}

THEME_LABELS = {
    "light":    "Light – Professionell",
    "dark":     "Dark – Modern",
    "nerd":     "Nerd – Terminal",
    "color":    "Color – Lebhaft",
    "schnyder": "Schnyder – Agentur",
}

# ── HTML Template (uses CSS custom properties) ────────────────────────────────

TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<style>
/* ── Theme variables ── */
:root {
  --font:             {{ t.font }};
  --bg:               {{ t.bg }};
  --bg-card:          {{ t.bg_card }};
  --bg-card-border:   {{ t.bg_card_border }};
  --bg-tbl-head:      {{ t.bg_tbl_head }};
  --bg-tbl-alt:       {{ t.bg_tbl_row_alt }};
  --text:             {{ t.text }};
  --text-muted:       {{ t.text_muted }};
  --text-light:       {{ t.text_light }};
  --primary:          {{ t.primary }};
  --accent:           {{ t.accent }};
  --border:           {{ t.border }};
  --cover-bg:         {{ t.cover_bg }};
  --cover-text:       {{ t.cover_text }};
  --cover-sub:        {{ t.cover_sub }};
  --cover-meta-bg:    {{ t.cover_meta_bg }};
  --cover-meta-border:{{ t.cover_meta_border }};
  --cover-label:      {{ t.cover_label }};
  --cover-badge-bg:   {{ t.cover_badge_bg }};
  --cover-badge-text: {{ t.cover_badge_text }};
  --sec-border:       {{ t.section_title_border }};
  --rec-num-bg:       {{ t.rec_num_bg }};
  --rec-num-text:     {{ t.rec_num_text }};
  --rec-item-bg:      {{ t.rec_item_bg }};
  --score-good:       {{ t.score_good }};
  --score-ok:         {{ t.score_ok }};
  --score-bad:        {{ t.score_bad }};
  --kpi-value:        {{ t.kpi_value }};
  --divider:          {{ t.divider }};
  --notes-bg:         {{ t.notes_bg }};
  --notes-border:     {{ t.notes_border }};
  --footer-color:     {{ t.page_footer_color }};
}

/* ── Base ── */
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: var(--bg); color: var(--text); }
body { font-family: var(--font); font-size: 13px; line-height: 1.55; }

/* ── Cover page ── */
.cover {
  width: 210mm;
  min-height: 297mm;
  background: var(--cover-bg);
  display: flex; flex-direction: column;
  page-break-after: always;
  position: relative;
  overflow: hidden;
}

/* Top bar: company name */
.cover-topbar {
  padding: 28px 52px;
  display: flex; align-items: center; justify-content: space-between;
  background: rgba(0,0,0,0.15);
  {% if theme_name == "light" or theme_name == "color" %}background: rgba(0,0,0,0.12);{% endif %}
}
.cover-company {
  font-size: 12px; font-weight: 700; letter-spacing: 2.5px;
  text-transform: uppercase; color: var(--cover-text); opacity: 0.85;
}
.cover-badge {
  background: var(--cover-badge-bg); color: var(--cover-badge-text);
  font-size: 10px; font-weight: 700; letter-spacing: 1.5px;
  text-transform: uppercase; padding: 5px 14px;
  border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}3px{% else %}20px{% endif %};
  {% if theme_name == "schnyder" %}border: 1px solid var(--primary);{% endif %}
  {% if theme_name == "nerd" %}border: 1px solid var(--primary);{% endif %}
}

/* Decorative accent shapes */
{% if theme_name == "light" %}
.cover::before {
  content: "";
  position: absolute; top: -80px; right: -80px;
  width: 320px; height: 320px; border-radius: 50%;
  background: rgba(255,255,255,0.08);
}
.cover::after {
  content: "";
  position: absolute; bottom: 100px; left: -60px;
  width: 200px; height: 200px; border-radius: 50%;
  background: rgba(255,255,255,0.06);
}
{% endif %}
{% if theme_name == "dark" %}
.cover::before {
  content: "";
  position: absolute; top: -60px; right: -60px;
  width: 280px; height: 280px; border-radius: 50%;
  background: rgba(96,165,250,0.07);
}
{% endif %}
{% if theme_name == "color" %}
.cover::before {
  content: "";
  position: absolute; top: -100px; right: -100px;
  width: 360px; height: 360px; border-radius: 50%;
  background: rgba(255,255,255,0.1);
}
.cover::after {
  content: "";
  position: absolute; bottom: 80px; left: -80px;
  width: 240px; height: 240px; border-radius: 50%;
  background: rgba(255,255,255,0.07);
}
{% endif %}
{% if theme_name == "schnyder" %}
.cover::before {
  content: "";
  position: absolute; top: 0; left: 0; right: 0;
  height: 4px; background: var(--primary);
}
.cover::after {
  content: "";
  position: absolute; bottom: 0; left: 0; right: 0;
  height: 4px; background: var(--primary);
}
{% endif %}
{% if theme_name == "nerd" %}
.cover-nerd-prompt {
  position: absolute; top: 72px; left: 52px;
  font-size: 11px; color: var(--primary); opacity: 0.6;
  font-family: var(--font); letter-spacing: 0;
}
{% endif %}

/* Main hero area */
.cover-hero {
  flex: 1;
  display: flex; flex-direction: column;
  justify-content: center;
  padding: 0 52px;
}
.cover-eyebrow {
  font-size: 11px; font-weight: 600; letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--cover-sub);
  margin-bottom: 20px;
  {% if theme_name == "schnyder" %}color: var(--primary);{% endif %}
  {% if theme_name == "nerd" %}color: var(--primary);{% endif %}
}
.cover h1 {
  color: var(--cover-text);
  font-size: 48px; font-weight: 800;
  line-height: 1.1; margin-bottom: 14px;
  {% if theme_name == "schnyder" %}letter-spacing: -1.5px;{% endif %}
  {% if theme_name == "nerd" %}font-size: 38px; letter-spacing: -0.5px;{% endif %}
}
.cover-url {
  font-size: 16px; font-weight: 400;
  color: var(--cover-sub);
  margin-bottom: 48px;
  {% if theme_name == "nerd" %}font-family: var(--font); font-size: 14px;{% endif %}
}
.cover-divider {
  width: 60px; height: 3px;
  background: var(--primary);
  margin-bottom: 48px;
  {% if theme_name == "schnyder" %}width: 80px;{% endif %}
}

/* Bottom meta strip */
.cover-meta {
  background: var(--cover-meta-bg);
  border-top: 1px solid var(--cover-meta-border);
  {% if theme_name == "light" or theme_name == "color" %}border-top: 1px solid rgba(255,255,255,0.18);{% endif %}
  padding: 28px 52px;
  display: grid; grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 0;
}
.cover-meta-item {
  padding: 0 20px 0 0;
  border-right: 1px solid rgba(255,255,255,0.12);
  {% if theme_name == "nerd" or theme_name == "schnyder" %}border-right: 1px solid var(--border);{% endif %}
}
.cover-meta-item:first-child { padding-left: 0; }
.cover-meta-item:last-child { border-right: none; padding-right: 0; padding-left: 20px; }
.cover-meta-item label {
  color: var(--cover-label); font-size: 9px; text-transform: uppercase;
  letter-spacing: 1.2px; display: block; margin-bottom: 5px;
  {% if theme_name == "schnyder" %}color: var(--primary);{% endif %}
}
.cover-meta-item span { color: var(--cover-text); font-weight: 600; font-size: 12px; }

/* ── Layout ── */
.page { padding: 48px 56px; background: var(--bg); }
.section { margin-bottom: 36px; }
h2.section-title {
  font-size: 17px; font-weight: 700; color: var(--primary);
  border-bottom: 2px solid var(--sec-border);
  padding-bottom: 8px; margin-bottom: 20px;
  {% if theme_name == "nerd" %}text-transform: uppercase; letter-spacing: 1px;{% endif %}
}
h3.subsection { font-size: 13px; font-weight: 600; color: var(--text); margin: 16px 0 10px; }

/* ── Score cards ── */
.score-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
.score-card {
  background: var(--bg-card);
  border: 1px solid var(--bg-card-border);
  border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}4px{% else %}10px{% endif %};
  padding: 16px; text-align: center;
}
.score-card .label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px; }
.score-card .value { font-size: 28px; font-weight: 800; }
.score-card .sublabel { font-size: 10px; color: var(--text-light); margin-top: 2px; }
.score-good { color: var(--score-good); }
.score-ok   { color: var(--score-ok); }
.score-bad  { color: var(--score-bad); }

/* ── KPI grid ── */
.kpi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.kpi-item {
  background: var(--bg-card);
  border: 1px solid var(--bg-card-border);
  border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}4px{% else %}8px{% endif %};
  padding: 14px 16px;
  {% if theme_name == "schnyder" %}border-left: 3px solid var(--primary);{% endif %}
}
.kpi-item .kpi-label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.8px; }
.kpi-item .kpi-value { font-size: 20px; font-weight: 700; color: var(--kpi-value); margin-top: 2px; }
.kpi-item .kpi-sub   { font-size: 10px; color: var(--text-light); }

/* ── Tables ── */
table { width: 100%; border-collapse: collapse; font-size: 12px; }
th {
  background: var(--bg-tbl-head); color: {% if theme_name == "nerd" %}var(--primary){% elif theme_name == "schnyder" %}var(--primary){% else %}#ffffff{% endif %};
  padding: 8px 12px; text-align: left; font-weight: 600; font-size: 11px;
  {% if theme_name == "nerd" %}border-bottom: 1px solid var(--primary);{% endif %}
  {% if theme_name == "schnyder" %}border-bottom: 2px solid var(--primary);{% endif %}
}
td { padding: 7px 12px; border-bottom: 1px solid var(--border); color: var(--text); }
tr:nth-child(even) td { background: var(--bg-tbl-alt); }
tr:last-child td { border-bottom: none; }

/* ── Badges ── */
.badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 600; }
.badge-error   { background: {% if theme_name == "dark" or theme_name == "nerd" or theme_name == "schnyder" %}#3b0000{% else %}#fee2e2{% endif %}; color: {% if theme_name == "dark" or theme_name == "nerd" or theme_name == "schnyder" %}#f87171{% else %}#dc2626{% endif %}; }
.badge-warning { background: {% if theme_name == "dark" or theme_name == "nerd" or theme_name == "schnyder" %}#2d1b00{% else %}#fef3c7{% endif %}; color: {% if theme_name == "dark" or theme_name == "nerd" or theme_name == "schnyder" %}#fbbf24{% else %}#d97706{% endif %}; }
.badge-ok      { background: {% if theme_name == "dark" or theme_name == "nerd" %}#002b0d{% elif theme_name == "schnyder" %}#0d2000{% else %}#dcfce7{% endif %}; color: var(--score-good); }
.badge-notice  { background: {% if theme_name == "dark" or theme_name == "nerd" or theme_name == "schnyder" %}#1a0040{% else %}#ede9fe{% endif %}; color: {% if theme_name == "dark" or theme_name == "nerd" or theme_name == "schnyder" %}#a78bfa{% else %}#7c3aed{% endif %}; }

/* ── Issue cards ── */
.issue-list { display: flex; flex-direction: column; gap: 8px; }
.issue-item {
  background: var(--bg-card);
  border: 1px solid var(--bg-card-border);
  border-left: 4px solid var(--border);
  border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}4px{% else %}8px{% endif %};
  padding: 12px 16px;
}
.issue-item.error   { border-left-color: var(--score-bad); }
.issue-item.warning { border-left-color: var(--score-ok); }
.issue-item.notice  { border-left-color: #8b5cf6; }
.issue-title { font-weight: 600; font-size: 12px; margin-bottom: 2px; color: var(--text); }
.issue-meta  { font-size: 11px; color: var(--text-muted); }

/* ── Recommendations ── */
.rec-list { display: flex; flex-direction: column; gap: 10px; }
.rec-item {
  display: flex; gap: 14px; align-items: flex-start;
  background: var(--rec-item-bg);
  border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}4px{% else %}10px{% endif %};
  padding: 14px 16px;
  {% if theme_name == "schnyder" %}border-left: 3px solid var(--primary);{% endif %}
}
.rec-num {
  background: var(--rec-num-bg); color: var(--rec-num-text);
  font-size: 13px; font-weight: 800; min-width: 28px; height: 28px;
  border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}4px{% else %}50%{% endif %};
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; margin-top: 1px;
  {% if theme_name == "schnyder" %}border: 1px solid var(--primary);{% endif %}
}
.rec-content .rec-title { font-weight: 700; font-size: 13px; margin-bottom: 3px; color: var(--text); }
.rec-content .rec-desc  { font-size: 12px; color: var(--text-muted); }

/* ── Misc ── */
.divider { border: none; border-top: 1px solid var(--divider); margin: 24px 0; }
.page-break { page-break-before: always; }
.notes-box {
  background: var(--notes-bg);
  border: 1px solid var(--notes-border);
  border-radius: {% if theme_name == "nerd" or theme_name == "schnyder" %}4px{% else %}8px{% endif %};
  padding: 16px; font-size: 12px; white-space: pre-wrap;
  color: var(--text);
}
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

/* Page margins – schnyder: zero on all pages so black background bleeds to edge */
{% if theme_name == "schnyder" %}
@page        { margin: 0; background: #000000; }
@page :first { margin: 0; background: #000000; }
.page { padding: 52px 64px; }
{% else %}
@page        { margin: 1.5cm 1.8cm; @bottom-right { content: "{{ company }} · Seite " counter(page); font-size: 10px; color: var(--footer-color); } }
@page :first { margin: 0; @bottom-right { content: none; } }
{% endif %}
</style>
</head>
<body>

<!-- ══ Cover ══════════════════════════════════════════════════════════════ -->
<div class="cover">
  {% if theme_name == "nerd" %}<div class="cover-nerd-prompt">$ analyse --report --generate</div>{% endif %}

  <!-- Top bar -->
  <div class="cover-topbar">
    <span class="cover-company">{{ company }}</span>
    <span class="cover-badge">SEO &amp; Performance Analyse</span>
  </div>

  <!-- Hero -->
  <div class="cover-hero">
    <div class="cover-eyebrow">Website-Analyse · {{ analysis_date }}</div>
    <h1>{{ client_name or "Unbekannter Kunde" }}</h1>
    <div class="cover-url">{{ website_url or "" }}</div>
    <div class="cover-divider"></div>
  </div>

  <!-- Bottom meta strip -->
  <div class="cover-meta">
    <div class="cover-meta-item"><label>Analysezeitraum</label><span>{{ analysis_period or "–" }}</span></div>
    <div class="cover-meta-item" style="padding-left:20px"><label>Analysedatum</label><span>{{ analysis_date }}</span></div>
    <div class="cover-meta-item" style="padding-left:20px"><label>Ansprechpartner</label><span>{{ responsible_person or "–" }}</span></div>
    <div class="cover-meta-item"><label>Erstellt von</label><span>{{ analyst_name or company }}</span></div>
  </div>
</div>

<!-- ══ 1. Website-Crawl Analyse ═══════════════════════════════════════════ -->
{% if crawl %}
<div class="page page-break">
  <div class="section">
    <h2 class="section-title">{% if theme_name == "nerd" %}// {% endif %}1. Website-Crawl Analyse</h2>
    {% if crawl.summary %}
    <div class="kpi-grid" style="grid-template-columns: repeat(4,1fr)">
      <div class="kpi-item"><div class="kpi-label">URLs gecrawlt</div><div class="kpi-value" style="color:var(--kpi-value)">{{ crawl.summary.total_urls | fmt_num }}</div></div>
      <div class="kpi-item"><div class="kpi-label">200 OK</div><div class="kpi-value" style="color:var(--score-good)">{{ crawl.summary.ok_200 | fmt_num }}</div></div>
      <div class="kpi-item"><div class="kpi-label">3xx Weiterleit.</div><div class="kpi-value" style="color:var(--score-ok)">{{ crawl.summary.redirects_3xx | fmt_num }}</div></div>
      <div class="kpi-item"><div class="kpi-label">4xx/5xx Fehler</div><div class="kpi-value" style="color:var(--score-bad)">{{ (crawl.summary.errors_4xx + crawl.summary.errors_5xx) | fmt_num }}</div></div>
      <div class="kpi-item"><div class="kpi-label">Fehl. Title</div><div class="kpi-value">{{ crawl.summary.missing_title | fmt_num }}</div></div>
      <div class="kpi-item"><div class="kpi-label">Fehl. Meta Desc.</div><div class="kpi-value">{{ crawl.summary.missing_meta | fmt_num }}</div></div>
      <div class="kpi-item"><div class="kpi-label">Fehl. H1</div><div class="kpi-value">{{ crawl.summary.missing_h1 | fmt_num }}</div></div>
      <div class="kpi-item"><div class="kpi-label">Langsame Seiten</div><div class="kpi-value" style="color:var(--score-ok)">{{ crawl.summary.slow_pages | fmt_num }}</div></div>
    </div>
    {% endif %}

    {% if crawl.issues %}
    <h3 class="subsection">Top Probleme</h3>
    <table>
      <thead><tr><th style="width:40%">URL</th><th>Status</th><th>Title</th><th>H1</th><th>Meta</th></tr></thead>
      <tbody>
        {% for issue in crawl.issues[:30] %}
        <tr>
          <td style="font-size:10px;word-break:break-all;color:var(--text-muted)">{{ issue.url }}</td>
          <td><span class="badge {{ 'badge-error' if issue.status_code >= 400 else 'badge-warning' if issue.status_code >= 300 else 'badge-ok' }}">{{ issue.status_code }}</span></td>
          <td><span class="badge {{ 'badge-error' if issue.title_issue == 'missing' else 'badge-warning' if issue.title_issue != 'ok' else 'badge-ok' }}">{{ issue.title_issue }}</span></td>
          <td><span class="badge {{ 'badge-error' if issue.h1_issue == 'missing' else 'badge-ok' }}">{{ issue.h1_issue }}</span></td>
          <td><span class="badge {{ 'badge-error' if issue.meta_issue == 'missing' else 'badge-warning' if issue.meta_issue != 'ok' else 'badge-ok' }}">{{ issue.meta_issue }}</span></td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% endif %}

    {% if crawl.notes %}
    <h3 class="subsection" style="margin-top:16px">Notizen</h3>
    <div class="notes-box">{{ crawl.notes }}</div>
    {% endif %}
  </div>
</div>
{% endif %}

<!-- ══ 2. Technische SEO Analyse ══════════════════════════════════════════ -->
{% if semrush %}
<div class="page page-break">
  <div class="section">
    <h2 class="section-title">{% if theme_name == "nerd" %}// {% endif %}2. Technische SEO Analyse</h2>

    {% if semrush.site_health_score is not none %}
    <div class="kpi-grid" style="grid-template-columns: repeat(4,1fr); margin-bottom: 16px">
      <div class="kpi-item" style="border-left: 3px solid {{ 'var(--score-good)' if semrush.site_health_score >= 80 else 'var(--score-ok)' if semrush.site_health_score >= 50 else 'var(--score-bad)' }}">
        <div class="kpi-label">Site Health Score</div>
        <div class="kpi-value" style="color: {{ 'var(--score-good)' if semrush.site_health_score >= 80 else 'var(--score-ok)' if semrush.site_health_score >= 50 else 'var(--score-bad)' }}">{{ semrush.site_health_score }}/100</div>
        <div class="kpi-sub">{{ 'Gut' if semrush.site_health_score >= 80 else 'Mittel' if semrush.site_health_score >= 50 else 'Kritisch' }}</div>
      </div>
      {% if semrush.semrush_summary %}
      <div class="kpi-item" style="border-left: 3px solid var(--score-bad)"><div class="kpi-label">Fehler</div><div class="kpi-value" style="color:var(--score-bad)">{{ semrush.semrush_summary.errors | fmt_num }}</div></div>
      <div class="kpi-item" style="border-left: 3px solid var(--score-ok)"><div class="kpi-label">Warnungen</div><div class="kpi-value" style="color:var(--score-ok)">{{ semrush.semrush_summary.warnings | fmt_num }}</div></div>
      <div class="kpi-item" style="border-left: 3px solid #8b5cf6"><div class="kpi-label">Hinweise</div><div class="kpi-value" style="color:#8b5cf6">{{ semrush.semrush_summary.notices | fmt_num }}</div></div>
      {% endif %}
    </div>
    {% endif %}

    {% if semrush.semrush_issues %}
    <h3 class="subsection">Gefundene Probleme</h3>
    <div class="issue-list">
      {% for issue in semrush.semrush_issues[:20] %}
      <div class="issue-item {{ issue.severity }}">
        <div class="issue-title">{{ issue.issue }}</div>
        <div class="issue-meta">
          <span class="badge badge-{{ 'error' if issue.severity == 'error' else 'warning' if issue.severity == 'warning' else 'notice' }}">{{ issue.severity | upper }}</span>
          &nbsp;{{ issue.count }} betroffene URLs{% if issue.category %} · {{ issue.category }}{% endif %}
        </div>
      </div>
      {% endfor %}
    </div>
    {% endif %}

    {% if semrush.on_page_seo_notes %}
    <h3 class="subsection" style="margin-top:16px">🔍 On-Page SEO</h3>
    <div class="notes-box">{{ semrush.on_page_seo_notes }}</div>
    {% endif %}

    {% if semrush.technical_status_notes %}
    <h3 class="subsection" style="margin-top:12px">⚙️ Technischer Zustand</h3>
    <div class="notes-box">{{ semrush.technical_status_notes }}</div>
    {% endif %}

    {% if semrush.geo_ki_notes %}
    <h3 class="subsection" style="margin-top:12px">🤖 KI-Suche / GEO</h3>
    <div class="notes-box">{{ semrush.geo_ki_notes }}</div>
    {% endif %}

    {% if semrush.notes %}
    <h3 class="subsection" style="margin-top:12px">Allgemeine Notizen</h3>
    <div class="notes-box">{{ semrush.notes }}</div>
    {% endif %}
  </div>
</div>
{% endif %}

<!-- ══ 3. Performance Analyse ═════════════════════════════════════════════ -->
{% if lighthouse %}
<div class="page page-break">
  <div class="section">
    <h2 class="section-title">{% if theme_name == "nerd" %}// {% endif %}3. Performance Analyse</h2>
    <div class="two-col">
      <div>
        <h3 class="subsection">📱 Mobile</h3>
        <div class="score-grid" style="grid-template-columns: repeat(2,1fr)">
          {% if lighthouse.mobile_performance is not none %}
          <div class="score-card"><div class="label">Performance</div>
            <div class="value {{ 'score-good' if lighthouse.mobile_performance >= 90 else 'score-ok' if lighthouse.mobile_performance >= 50 else 'score-bad' }}">{{ lighthouse.mobile_performance }}</div></div>
          {% endif %}
          {% if lighthouse.mobile_seo is not none %}
          <div class="score-card"><div class="label">SEO</div>
            <div class="value {{ 'score-good' if lighthouse.mobile_seo >= 90 else 'score-ok' if lighthouse.mobile_seo >= 50 else 'score-bad' }}">{{ lighthouse.mobile_seo }}</div></div>
          {% endif %}
          {% if lighthouse.mobile_accessibility is not none %}
          <div class="score-card"><div class="label">Barrierefreiheit</div>
            <div class="value {{ 'score-good' if lighthouse.mobile_accessibility >= 90 else 'score-ok' if lighthouse.mobile_accessibility >= 50 else 'score-bad' }}">{{ lighthouse.mobile_accessibility }}</div></div>
          {% endif %}
          {% if lighthouse.mobile_best_practices is not none %}
          <div class="score-card"><div class="label">Best Practices</div>
            <div class="value {{ 'score-good' if lighthouse.mobile_best_practices >= 90 else 'score-ok' if lighthouse.mobile_best_practices >= 50 else 'score-bad' }}">{{ lighthouse.mobile_best_practices }}</div></div>
          {% endif %}
        </div>
      </div>
      <div>
        <h3 class="subsection">🖥️ Desktop</h3>
        <div class="score-grid" style="grid-template-columns: repeat(2,1fr)">
          {% if lighthouse.desktop_performance is not none %}
          <div class="score-card"><div class="label">Performance</div>
            <div class="value {{ 'score-good' if lighthouse.desktop_performance >= 90 else 'score-ok' if lighthouse.desktop_performance >= 50 else 'score-bad' }}">{{ lighthouse.desktop_performance }}</div></div>
          {% endif %}
          {% if lighthouse.desktop_seo is not none %}
          <div class="score-card"><div class="label">SEO</div>
            <div class="value {{ 'score-good' if lighthouse.desktop_seo >= 90 else 'score-ok' if lighthouse.desktop_seo >= 50 else 'score-bad' }}">{{ lighthouse.desktop_seo }}</div></div>
          {% endif %}
          {% if lighthouse.desktop_accessibility is not none %}
          <div class="score-card"><div class="label">Barrierefreiheit</div>
            <div class="value {{ 'score-good' if lighthouse.desktop_accessibility >= 90 else 'score-ok' if lighthouse.desktop_accessibility >= 50 else 'score-bad' }}">{{ lighthouse.desktop_accessibility }}</div></div>
          {% endif %}
          {% if lighthouse.desktop_best_practices is not none %}
          <div class="score-card"><div class="label">Best Practices</div>
            <div class="value {{ 'score-good' if lighthouse.desktop_best_practices >= 90 else 'score-ok' if lighthouse.desktop_best_practices >= 50 else 'score-bad' }}">{{ lighthouse.desktop_best_practices }}</div></div>
          {% endif %}
        </div>
      </div>
    </div>

    {% if lighthouse.cwv_lcp or lighthouse.cwv_cls or lighthouse.cwv_tbt %}
    <h3 class="subsection" style="margin-top:16px">Core Web Vitals</h3>
    <div class="kpi-grid" style="grid-template-columns: repeat(3,1fr)">
      {% if lighthouse.cwv_lcp %}<div class="kpi-item"><div class="kpi-label">LCP (Largest Contentful Paint)</div><div class="kpi-value">{{ lighthouse.cwv_lcp }}</div><div class="kpi-sub">Ziel: &lt; 2,5s</div></div>{% endif %}
      {% if lighthouse.cwv_cls %}<div class="kpi-item"><div class="kpi-label">CLS (Cumulative Layout Shift)</div><div class="kpi-value">{{ lighthouse.cwv_cls }}</div><div class="kpi-sub">Ziel: &lt; 0.1</div></div>{% endif %}
      {% if lighthouse.cwv_tbt %}<div class="kpi-item"><div class="kpi-label">TBT (Total Blocking Time)</div><div class="kpi-value">{{ lighthouse.cwv_tbt }}</div><div class="kpi-sub">Ziel: &lt; 200ms</div></div>{% endif %}
    </div>
    {% endif %}

    {% set prio_a = lighthouse.prio_a %}
    {% set prio_b = lighthouse.prio_b %}
    {% set prio_c = lighthouse.prio_c %}
    {% if prio_a or prio_b or prio_c %}
    <h3 class="subsection" style="margin-top:20px">Top 3 Prioritäten</h3>
    <div style="display:flex; flex-direction:column; gap:12px">
      {% for prio, label, color in [(prio_a, 'Priorität A', '#dc2626'), (prio_b, 'Priorität B', '#d97706'), (prio_c, 'Priorität C', '#2563eb')] %}
      {% if prio and (prio.title or prio.warum) %}
      <div style="border:1px solid var(--bg-card-border); border-left:4px solid {{ color }}; border-radius:8px; overflow:hidden;">
        <div style="background:{{ color }}; color:white; padding:8px 14px; font-size:12px; font-weight:700;">{{ label }}{% if prio.title %}: {{ prio.title }}{% endif %}</div>
        <div style="padding:12px 14px; display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; background:var(--bg-card)">
          {% if prio.warum %}<div><div style="font-size:10px; color:var(--text-muted); text-transform:uppercase; margin-bottom:4px">Warum</div><div style="font-size:12px; color:var(--text)">{{ prio.warum }}</div></div>{% endif %}
          {% if prio.erledigung %}<div><div style="font-size:10px; color:var(--text-muted); text-transform:uppercase; margin-bottom:4px">Erledigung</div><div style="font-size:12px; color:var(--text)">{{ prio.erledigung }}</div></div>{% endif %}
          {% if prio.auswirkung %}<div><div style="font-size:10px; color:var(--text-muted); text-transform:uppercase; margin-bottom:4px">Auswirkung</div><div style="font-size:12px; color:var(--text)">{{ prio.auswirkung }}</div></div>{% endif %}
        </div>
      </div>
      {% endif %}
      {% endfor %}
    </div>
    {% endif %}

    {% if lighthouse.checklist %}
    <h3 class="subsection" style="margin-top:20px">Technische Checkliste</h3>
    <div style="display:flex; flex-direction:column; gap:6px">
      {% for key, label in [('responsive', 'Mobile-freundlich / Responsives Design'), ('https', 'HTTPS aktiviert'), ('sitemap', 'Sitemap vorhanden'), ('canonical', 'Canonical-Tags gesetzt'), ('meta_tags', 'Meta-Tags vollständig')] %}
      {% set val = lighthouse.checklist[key] if lighthouse.checklist is mapping else none %}
      <div style="display:flex; align-items:center; gap:10px; padding:8px 12px; background:{{ 'var(--notes-bg)' }}; border-radius:6px; border:1px solid var(--border)">
        <span style="font-size:16px">{{ '✅' if val else '⬜' }}</span>
        <span style="font-size:12px; color:var(--text)">{{ label }}</span>
      </div>
      {% endfor %}
    </div>
    {% endif %}

    {% if lighthouse.fazit %}
    <h3 class="subsection" style="margin-top:20px">Fazit</h3>
    <div class="notes-box">{{ lighthouse.fazit }}</div>
    {% endif %}

    {% if lighthouse.next_step %}
    <div style="margin-top:12px; padding:12px 16px; background:var(--bg-card); border:1px solid var(--bg-card-border); border-radius:8px; font-size:12px">
      <strong>Nächster Schritt:</strong> {{ lighthouse.next_step }}{% if lighthouse.next_step_date %} <span style="color:var(--text-muted)">– {{ lighthouse.next_step_date }}</span>{% endif %}
    </div>
    {% endif %}
  </div>
</div>
{% endif %}

<!-- ══ 5. Fazit & Empfehlungen ════════════════════════════════════════════ -->
<div class="page page-break">
  <div class="section">
    <h2 class="section-title">{% if theme_name == "nerd" %}// {% endif %}4. Fazit &amp; Empfehlungen</h2>

    {% if findings %}
    <h3 class="subsection">Wichtigste Erkenntnisse</h3>
    <div class="notes-box" style="margin-bottom:20px">{{ findings }}</div>
    {% endif %}

    {% if recommendations %}
    <h3 class="subsection">Empfehlungen</h3>
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
    <h3 class="subsection" style="margin-top:20px">Weitere Notizen</h3>
    <div class="notes-box">{{ general_notes }}</div>
    {% endif %}
  </div>

  <hr class="divider">
  <div style="font-size:11px; color:var(--footer-color); text-align:center">
    {{ company }} &mdash; {{ analysis_date }}
  </div>
</div>

</body>
</html>
"""


class _D(dict):
    """Dict subclass that returns None for missing attribute/key access.
    This makes Jinja2 'is not none' checks work correctly for optional fields:
    missing key → None (falsy), existing key → value.
    """
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


class AuditPDFGenerator:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.company = self.config.get("company_name", "GeoBoost")

    def _fmt_num(self, v) -> str:
        try:
            return f"{int(v):,}".replace(",", "'")
        except Exception:
            return str(v) if v is not None else "–"

    def generate(self, audit: Dict[str, Any], output_path: str, theme: str = "light") -> str:
        """Generate PDF from audit data. theme: light | dark | nerd | color | schnyder"""
        import weasyprint
        from jinja2 import Environment

        t = THEMES.get(theme, THEMES["light"])

        env = Environment()
        env.filters["fmt_num"] = self._fmt_num
        env.filters["fmt_pct"] = lambda v: f"{float(v):.1f}%" if v else "–"

        raw_kickoff    = audit.get("step0_kickoff") or {}
        raw_crawl      = audit.get("step3_semrush") or {}    # Background-Crawl (Screaming Frog)
        raw_semrush    = audit.get("step4_lighthouse") or {}  # SemRush Check
        raw_lighthouse = audit.get("step5_notes") or {}       # Lighthouse Bericht
        raw_report     = audit.get("step6_report") or {}      # Report / Fazit

        # Wrap all dict data so that missing keys return None (not Undefined)
        # This makes {% if x.y is not none %} checks work correctly in Jinja2.
        kickoff    = _d(raw_kickoff)
        crawl      = _d(raw_crawl)    if raw_crawl      else None
        semrush    = _d(raw_semrush)  if raw_semrush    else None
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
            analysis_date=kickoff.get("analysis_date", datetime.now().strftime("%d.%m.%Y")),
            analyst_name=kickoff.get("analyst_name", self.company),
            responsible_person=kickoff.get("responsible_person", ""),
            crawl=crawl,
            semrush=semrush,
            lighthouse=lighthouse,
            findings=report.get("findings", ""),
            recommendations=recommendations,
            general_notes=report.get("general_notes", ""),
        )

        template = env.from_string(TEMPLATE)
        html = template.render(**ctx)

        output_path = str(output_path)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        weasyprint.HTML(string=html).write_pdf(output_path)
        return output_path
