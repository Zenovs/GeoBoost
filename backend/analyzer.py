"""
GeoBoost – KI-Analyse via Ollama (lokal)
"""

import json
from typing import Dict, Any


class KIAnalyzer:
    def __init__(self, model: str = "llama3.1:8b"):
        self.model = model

    def analyze(self, results: Dict[str, Any], kickoff: Dict[str, Any]) -> Dict[str, Any]:
        import ollama

        summary = self._build_summary(results, kickoff)
        prompt = self._build_prompt(summary, kickoff)

        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.3, "num_ctx": 4096},
        )
        text = response["message"]["content"]

        return {"text": text, "model": self.model, "prompt_tokens": len(prompt.split())}

    def _build_summary(self, results: Dict, kickoff: Dict) -> str:
        lines = []

        # Crawler
        crawler = results.get("crawler", {})
        if crawler and not crawler.get("error"):
            s = crawler.get("summary", {})
            lines.append(f"Website Crawl: {s.get('total_pages',0)} Seiten gecrawlt")
            lines.append(f"  - SEO Score: {s.get('seo_score',0)}/100")
            lines.append(f"  - Fehlende Titles: {s.get('missing_titles',0)}")
            lines.append(f"  - Fehlende Meta-Descriptions: {s.get('missing_meta',0)}")
            lines.append(f"  - Seiten ohne H1: {s.get('no_h1_pages',0)}")
            lines.append(f"  - Bilder ohne Alt-Text: {s.get('images_without_alt',0)}")
            lines.append(f"  - 404-Fehler: {s.get('pages_error',0)}")

        # PageSpeed
        ps = results.get("pagespeed", {})
        if ps and not ps.get("error"):
            mob = ps.get("mobile", {})
            desk = ps.get("desktop", {})
            if mob:
                lines.append(f"PageSpeed Mobile: {mob.get('performance_score','n/a')}/100")
                lines.append(f"  - LCP: {mob.get('lcp','n/a')}, CLS: {mob.get('cls','n/a')}, TBT: {mob.get('tbt','n/a')}")
            if desk:
                lines.append(f"PageSpeed Desktop: {desk.get('performance_score','n/a')}/100")

        # GA4
        ga4 = results.get("ga4_traffic", {})
        if ga4 and not ga4.get("error"):
            lines.append(f"GA4 Übersicht: {ga4.get('sessions',0)} Sessions, {ga4.get('conversions',0)} Conversions")
            lines.append(f"  - Bounce Rate: {ga4.get('bounce_rate',0)}%")

        channels = results.get("ga4_channels", [])
        if channels:
            lines.append("GA4 Kanäle (Top 5):")
            for ch in channels[:5]:
                lines.append(f"  - {ch['channel']}: {ch['sessions']} Sessions, {ch['conversions']} Conv. ({ch['conversion_rate']}%)")

        devices = results.get("ga4_devices", [])
        if devices:
            lines.append("GA4 Geräte:")
            for d in devices:
                lines.append(f"  - {d['device']}: {d['sessions']} Sessions, {d['conversion_rate']}% Conv.-Rate")

        return "\n".join(lines)

    def _build_prompt(self, data_summary: str, kickoff: Dict) -> str:
        url = kickoff.get("website_url", "die Website")
        goal = kickoff.get("primary_goal", "nicht angegeben")
        audience = kickoff.get("target_audience", "nicht angegeben")
        question = kickoff.get("main_question", "")

        return f"""Du bist ein erfahrener Digital-Analytics-Berater. Analysiere die folgenden Daten für {url} und erstelle einen strukturierten Bericht auf Schweizer Hochdeutsch.

**Website:** {url}
**Primäres Ziel:** {goal}
**Zielgruppe:** {audience}
**Wichtigste Frage:** {question}

**Analysedaten:**
{data_summary}

Erstelle bitte folgende Abschnitte:

## Tracking-Status
Kurze Bewertung der Datenqualität (2–3 Sätze).

## Technische Analyse
Top 5 technische Probleme mit Impact-Bewertung (P1/P2/P3). Format pro Eintrag:
**[Priorität] | [Aufwand S/M/L] – [Titel]**
Problem: ...
Empfehlung: ...

## Performance-Insights
5–8 konkrete Erkenntnisse aus den Daten, jeweils mit Datenbeleg.

## Massnahmenkatalog

### Quick Wins (1–3 Tage)
[3–5 Massnahmen]

### Optimierungen (1–2 Wochen)
[3–5 Massnahmen]

### Strategisch (3–6 Wochen)
[2–3 Massnahmen]

Pro Massnahme: **[P1/P2/P3] | [S/M/L] – [Titel]**
Problem: | Empfehlung: | Erwarteter Effekt: | Aufwand: | Priorität:

Sprache: Schweizer Hochdeutsch. Keine Ausrufezeichen. Professionell und konkret. Keine Floskeln.
"""
