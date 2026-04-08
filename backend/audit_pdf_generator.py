"""
GeoBoost – Audit PDF Generator
Generates a structured PDF report from the 6-step audit workflow data.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Helvetica Neue', Arial, sans-serif; color: #1a1a2e; font-size: 13px; line-height: 1.5; }

  /* ── Cover ── */
  .cover { min-height: 100vh; background: linear-gradient(135deg, {{ primary }} 0%, {{ accent }} 100%);
           display: flex; flex-direction: column; justify-content: center; align-items: flex-start;
           padding: 80px 60px; page-break-after: always; }
  .cover-badge { background: rgba(255,255,255,0.2); color: white; font-size: 11px; font-weight: 600;
                 letter-spacing: 2px; text-transform: uppercase; padding: 6px 16px; border-radius: 20px;
                 margin-bottom: 32px; display: inline-block; }
  .cover h1 { color: white; font-size: 42px; font-weight: 800; line-height: 1.15; margin-bottom: 16px; }
  .cover h2 { color: rgba(255,255,255,0.85); font-size: 22px; font-weight: 400; margin-bottom: 48px; }
  .cover-meta { background: rgba(255,255,255,0.15); border-radius: 12px; padding: 24px 32px;
                display: grid; grid-template-columns: 1fr 1fr; gap: 16px; min-width: 400px; }
  .cover-meta-item label { color: rgba(255,255,255,0.7); font-size: 11px; text-transform: uppercase;
                           letter-spacing: 1px; display: block; margin-bottom: 2px; }
  .cover-meta-item span { color: white; font-weight: 600; font-size: 14px; }
  .cover-footer { position: absolute; bottom: 40px; left: 60px; color: rgba(255,255,255,0.5); font-size: 11px; }

  /* ── Layout ── */
  .page { padding: 48px 56px; }
  .section { margin-bottom: 36px; }
  h2.section-title { font-size: 18px; font-weight: 700; color: {{ primary }}; border-bottom: 2px solid {{ primary }};
                     padding-bottom: 8px; margin-bottom: 20px; }
  h3.subsection { font-size: 14px; font-weight: 600; color: #333; margin: 16px 0 10px; }

  /* ── Score cards ── */
  .score-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
  .score-card { background: #f8f9ff; border-radius: 10px; padding: 16px; text-align: center; border: 1px solid #e8eaf0; }
  .score-card .label { font-size: 10px; color: #777; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px; }
  .score-card .value { font-size: 28px; font-weight: 800; }
  .score-card .sublabel { font-size: 10px; color: #999; margin-top: 2px; }
  .score-good { color: #16a34a; }
  .score-ok { color: #d97706; }
  .score-bad { color: #dc2626; }

  /* ── KPI grid ── */
  .kpi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
  .kpi-item { background: #f8f9ff; border-radius: 8px; padding: 14px 16px; border: 1px solid #e8eaf0; }
  .kpi-item .kpi-label { font-size: 10px; color: #888; text-transform: uppercase; letter-spacing: 0.8px; }
  .kpi-item .kpi-value { font-size: 20px; font-weight: 700; color: {{ primary }}; margin-top: 2px; }
  .kpi-item .kpi-sub { font-size: 10px; color: #aaa; }

  /* ── Tables ── */
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  th { background: {{ primary }}; color: white; padding: 8px 12px; text-align: left; font-weight: 600; font-size: 11px; }
  td { padding: 7px 12px; border-bottom: 1px solid #eef0f6; }
  tr:nth-child(even) td { background: #f9fafb; }
  tr:last-child td { border-bottom: none; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 600; }
  .badge-error { background: #fee2e2; color: #dc2626; }
  .badge-warning { background: #fef3c7; color: #d97706; }
  .badge-ok { background: #dcfce7; color: #16a34a; }
  .badge-notice { background: #ede9fe; color: #7c3aed; }

  /* ── Issues ── */
  .issue-list { display: flex; flex-direction: column; gap: 8px; }
  .issue-item { background: #fff; border: 1px solid #e8eaf0; border-radius: 8px; padding: 12px 16px;
                border-left: 4px solid #e5e7eb; }
  .issue-item.error { border-left-color: #dc2626; }
  .issue-item.warning { border-left-color: #f59e0b; }
  .issue-item.notice { border-left-color: #8b5cf6; }
  .issue-title { font-weight: 600; font-size: 12px; margin-bottom: 2px; }
  .issue-meta { font-size: 11px; color: #888; }

  /* ── Recommendations ── */
  .rec-list { counter-reset: rec; display: flex; flex-direction: column; gap: 10px; }
  .rec-item { display: flex; gap: 14px; align-items: flex-start; background: #f8f9ff; border-radius: 10px; padding: 14px 16px; }
  .rec-num { background: {{ primary }}; color: white; font-size: 13px; font-weight: 800; min-width: 28px; height: 28px;
             border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 1px; }
  .rec-content .rec-title { font-weight: 700; font-size: 13px; margin-bottom: 3px; }
  .rec-content .rec-desc { font-size: 12px; color: #555; }

  /* ── Divider ── */
  .divider { border: none; border-top: 1px solid #eef0f6; margin: 24px 0; }
  .page-break { page-break-before: always; }

  /* ── Footer ── */
  @page { @bottom-right { content: "{{ company }} · Seite " counter(page); font-size: 10px; color: #aaa; } }

  /* ── Notes box ── */
  .notes-box { background: #fafafa; border: 1px solid #e8eaf0; border-radius: 8px; padding: 16px; font-size: 12px; white-space: pre-wrap; }
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
</style>
</head>
<body>

<!-- ══ Cover ══════════════════════════════════════════════════════════════ -->
<div class="cover">
  <div class="cover-badge">Website-Analyse</div>
  <h1>{{ client_name }}</h1>
  <h2>{{ website_url }}</h2>
  <div class="cover-meta">
    <div class="cover-meta-item"><label>Analysezeitraum</label><span>{{ analysis_period }}</span></div>
    <div class="cover-meta-item"><label>Analysedatum</label><span>{{ analysis_date }}</span></div>
    <div class="cover-meta-item"><label>Ansprechpartner Kunde</label><span>{{ responsible_person or '–' }}</span></div>
    <div class="cover-meta-item"><label>Erstellt von</label><span>{{ analyst_name or company }}</span></div>
  </div>
</div>

<!-- ══ 1. Traffic-Übersicht ═══════════════════════════════════════════════ -->
{% if traffic %}
<div class="page">
  <div class="section">
    <h2 class="section-title">1. Traffic-Übersicht (GA4)</h2>
    <div class="kpi-grid">
      {% if traffic.sessions_total %}<div class="kpi-item"><div class="kpi-label">Sessions gesamt</div><div class="kpi-value">{{ traffic.sessions_total | fmt_num }}</div></div>{% endif %}
      {% if traffic.new_users_total %}<div class="kpi-item"><div class="kpi-label">Neue Nutzer</div><div class="kpi-value">{{ traffic.new_users_total | fmt_num }}</div></div>{% endif %}
      {% if traffic.bounce_rate %}<div class="kpi-item"><div class="kpi-label">Absprungrate</div><div class="kpi-value">{{ traffic.bounce_rate }}%</div></div>{% endif %}
      {% if traffic.avg_session_duration %}<div class="kpi-item"><div class="kpi-label">Ø Sitzungsdauer</div><div class="kpi-value">{{ traffic.avg_session_duration }}</div></div>{% endif %}
      {% if traffic.conversions_total %}<div class="kpi-item"><div class="kpi-label">Conversions</div><div class="kpi-value">{{ traffic.conversions_total | fmt_num }}</div></div>{% endif %}
      {% if traffic.conversion_rate %}<div class="kpi-item"><div class="kpi-label">Conv.-Rate</div><div class="kpi-value">{{ traffic.conversion_rate }}%</div></div>{% endif %}
    </div>

    {% if traffic.channel_breakdown %}
    <h3 class="subsection">Kanal-Übersicht</h3>
    <table>
      <thead><tr><th>Kanal</th><th>Sessions</th><th>Anteil</th></tr></thead>
      <tbody>
        {% for ch in traffic.channel_breakdown %}
        <tr><td>{{ ch.channel }}</td><td>{{ ch.sessions | fmt_num }}</td><td>{{ ch.pct }}%</td></tr>
        {% endfor %}
      </tbody>
    </table>
    {% endif %}

    {% if traffic.device_breakdown %}
    <h3 class="subsection" style="margin-top:16px">Geräte</h3>
    <div class="kpi-grid" style="grid-template-columns: repeat(3,1fr)">
      <div class="kpi-item"><div class="kpi-label">Desktop</div><div class="kpi-value">{{ traffic.device_breakdown.desktop or '–' }}%</div></div>
      <div class="kpi-item"><div class="kpi-label">Mobile</div><div class="kpi-value">{{ traffic.device_breakdown.mobile or '–' }}%</div></div>
      <div class="kpi-item"><div class="kpi-label">Tablet</div><div class="kpi-value">{{ traffic.device_breakdown.tablet or '–' }}%</div></div>
    </div>
    {% endif %}

    {% if traffic.notes %}
    <h3 class="subsection" style="margin-top:16px">Notizen</h3>
    <div class="notes-box">{{ traffic.notes }}</div>
    {% endif %}
  </div>
</div>
{% endif %}

<!-- ══ 2. Technische SEO (Screaming Frog) ═════════════════════════════════ -->
{% if crawl %}
<div class="page page-break">
  <div class="section">
    <h2 class="section-title">2. Technische SEO (Screaming Frog)</h2>
    {% if crawl.summary %}
    <div class="kpi-grid">
      <div class="kpi-item"><div class="kpi-label">URLs gecrawlt</div><div class="kpi-value">{{ crawl.summary.total_urls | fmt_num }}</div></div>
      <div class="kpi-item"><div class="kpi-label">200 OK</div><div class="kpi-value" style="color:#16a34a">{{ crawl.summary.ok_200 | fmt_num }}</div></div>
      <div class="kpi-item"><div class="kpi-label">3xx Weiterleit.</div><div class="kpi-value" style="color:#d97706">{{ crawl.summary.redirects_3xx | fmt_num }}</div></div>
      <div class="kpi-item"><div class="kpi-label">4xx/5xx Fehler</div><div class="kpi-value" style="color:#dc2626">{{ (crawl.summary.errors_4xx + crawl.summary.errors_5xx) | fmt_num }}</div></div>
      <div class="kpi-item"><div class="kpi-label">Fehl. Title</div><div class="kpi-value">{{ crawl.summary.missing_title | fmt_num }}</div></div>
      <div class="kpi-item"><div class="kpi-label">Fehl. Meta Desc.</div><div class="kpi-value">{{ crawl.summary.missing_meta | fmt_num }}</div></div>
      <div class="kpi-item"><div class="kpi-label">Fehl. H1</div><div class="kpi-value">{{ crawl.summary.missing_h1 | fmt_num }}</div></div>
      <div class="kpi-item"><div class="kpi-label">Langsame Seiten</div><div class="kpi-value">{{ crawl.summary.slow_pages | fmt_num }}</div></div>
    </div>
    {% endif %}

    {% if crawl.issues %}
    <h3 class="subsection">Top Probleme</h3>
    <table>
      <thead><tr><th style="width:40%">URL</th><th>Status</th><th>Title</th><th>H1</th><th>Meta</th></tr></thead>
      <tbody>
        {% for issue in crawl.issues[:30] %}
        <tr>
          <td style="font-size:10px;word-break:break-all">{{ issue.url }}</td>
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

<!-- ══ 3. SemRush Site Audit ══════════════════════════════════════════════ -->
{% if semrush %}
<div class="page page-break">
  <div class="section">
    <h2 class="section-title">3. SemRush Site Audit</h2>
    {% if semrush.summary %}
    <div class="kpi-grid" style="grid-template-columns: repeat(3,1fr)">
      <div class="kpi-item"><div class="kpi-label">Fehler</div><div class="kpi-value" style="color:#dc2626">{{ semrush.summary.errors | fmt_num }}</div></div>
      <div class="kpi-item"><div class="kpi-label">Warnungen</div><div class="kpi-value" style="color:#d97706">{{ semrush.summary.warnings | fmt_num }}</div></div>
      <div class="kpi-item"><div class="kpi-label">Hinweise</div><div class="kpi-value" style="color:#7c3aed">{{ semrush.summary.notices | fmt_num }}</div></div>
    </div>
    {% endif %}

    {% if semrush.issues %}
    <h3 class="subsection">Gefundene Probleme</h3>
    <div class="issue-list">
      {% for issue in semrush.issues[:20] %}
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

    {% if semrush.notes %}
    <h3 class="subsection" style="margin-top:16px">Notizen</h3>
    <div class="notes-box">{{ semrush.notes }}</div>
    {% endif %}
  </div>
</div>
{% endif %}

<!-- ══ 4. PageSpeed / Core Web Vitals ════════════════════════════════════ -->
{% if lighthouse %}
<div class="page page-break">
  <div class="section">
    <h2 class="section-title">4. PageSpeed &amp; Core Web Vitals</h2>
    <div class="two-col">
      <div>
        <h3 class="subsection">Mobile</h3>
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
        <h3 class="subsection">Desktop</h3>
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

    {% if lighthouse.cwv_lcp or lighthouse.cwv_fid or lighthouse.cwv_cls %}
    <h3 class="subsection" style="margin-top:16px">Core Web Vitals</h3>
    <div class="kpi-grid" style="grid-template-columns: repeat(3,1fr)">
      {% if lighthouse.cwv_lcp %}<div class="kpi-item"><div class="kpi-label">LCP (Largest Contentful Paint)</div><div class="kpi-value">{{ lighthouse.cwv_lcp }}</div><div class="kpi-sub">Ziel: &lt; 2,5s</div></div>{% endif %}
      {% if lighthouse.cwv_fid %}<div class="kpi-item"><div class="kpi-label">INP / FID</div><div class="kpi-value">{{ lighthouse.cwv_fid }}</div><div class="kpi-sub">Ziel: &lt; 200ms</div></div>{% endif %}
      {% if lighthouse.cwv_cls %}<div class="kpi-item"><div class="kpi-label">CLS (Layout Shift)</div><div class="kpi-value">{{ lighthouse.cwv_cls }}</div><div class="kpi-sub">Ziel: &lt; 0.1</div></div>{% endif %}
    </div>
    {% endif %}

    {% if lighthouse.notes %}
    <h3 class="subsection" style="margin-top:16px">Notizen</h3>
    <div class="notes-box">{{ lighthouse.notes }}</div>
    {% endif %}
  </div>
</div>
{% endif %}

<!-- ══ 5. Fazit & Empfehlungen ════════════════════════════════════════════ -->
<div class="page page-break">
  <div class="section">
    <h2 class="section-title">5. Fazit &amp; Empfehlungen</h2>

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

  <!-- Footer info -->
  <hr class="divider">
  <div style="font-size:11px; color:#aaa; text-align:center">
    Erstellt mit GeoBoost &mdash; {{ analysis_date }} &mdash; {{ company }}
  </div>
</div>

</body>
</html>
"""


class AuditPDFGenerator:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.primary = config.get("primary_color", "#1a56db") if config else "#1a56db"
        self.accent = config.get("accent_color", "#7e3af2") if config else "#7e3af2"
        self.company = config.get("company_name", "GeoBoost") if config else "GeoBoost"

    def _fmt_num(self, v) -> str:
        try:
            return f"{int(v):,}".replace(",", "'")
        except Exception:
            return str(v) if v is not None else "–"

    def generate(self, audit: Dict[str, Any], output_path: str) -> str:
        """Generate PDF from audit data and return output path."""
        import weasyprint
        from jinja2 import Environment

        env = Environment()
        env.filters["fmt_num"] = self._fmt_num
        env.filters["fmt_pct"] = lambda v: f"{float(v):.1f}%" if v else "–"

        kickoff = audit.get("step0_kickoff") or {}
        traffic = audit.get("step1_website") or {}
        crawl = audit.get("step2_crawl") or {}
        semrush = audit.get("step3_semrush") or {}
        lighthouse = audit.get("step4_lighthouse") or {}
        notes = audit.get("step5_notes") or {}

        # Build recommendations list from free-text or structured
        recs_raw = notes.get("recommendations", "")
        recommendations = []
        if isinstance(recs_raw, list):
            recommendations = recs_raw
        elif isinstance(recs_raw, str) and recs_raw.strip():
            for line in recs_raw.strip().splitlines():
                line = line.strip().lstrip("0123456789.-) ")
                if line:
                    recommendations.append({"title": line, "description": ""})

        ctx = dict(
            company=self.company,
            primary=self.primary,
            accent=self.accent,
            client_name=audit.get("client_name") or kickoff.get("client_name", ""),
            website_url=audit.get("website_url") or kickoff.get("website_url", ""),
            analysis_period=kickoff.get("analysis_period", ""),
            analysis_date=kickoff.get("analysis_date", datetime.now().strftime("%d.%m.%Y")),
            analyst_name=kickoff.get("analyst_name", self.company),
            responsible_person=kickoff.get("responsible_person", ""),
            traffic=traffic if traffic else None,
            crawl=crawl if crawl else None,
            semrush=semrush if semrush else None,
            lighthouse=lighthouse if lighthouse else None,
            findings=notes.get("findings", ""),
            recommendations=recommendations,
            general_notes=notes.get("general_notes", ""),
        )

        template = env.from_string(TEMPLATE)
        html = template.render(**ctx)

        output_path = str(output_path)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        weasyprint.HTML(string=html).write_pdf(output_path)
        return output_path
