"""
GeoBoost – KI-Analyse via Ollama (lokal)
Schreibt kundentaugliche Berichte auf Schweizer Hochdeutsch.
"""

from typing import Dict, Any


class KIAnalyzer:
    def __init__(self, model: str = "llama3.1:8b"):
        self.model = model

    def analyze(self, results: Dict[str, Any], kickoff: Dict[str, Any]) -> Dict[str, Any]:
        import ollama

        context = self._build_context(results, kickoff)
        prompt = self._build_prompt(context, kickoff)

        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.3, "num_ctx": 8192},
        )
        text = response["message"]["content"]

        return {"text": text, "model": self.model, "prompt_tokens": len(prompt.split())}

    def _build_context(self, results: Dict, kickoff: Dict) -> str:
        """Build a detailed, structured data summary for the AI prompt."""
        lines = []
        url = kickoff.get("website_url", "")
        goal = kickoff.get("primary_goal", "")
        audience = kickoff.get("target_audience", "")

        lines.append(f"WEBSITE: {url}")
        lines.append(f"ZIEL: {goal}")
        lines.append(f"ZIELGRUPPE: {audience}")
        lines.append("")

        # ── Crawler ───────────────────────────────────────────────────────────
        crawler = results.get("crawler", {})
        if crawler and not crawler.get("error"):
            s = crawler.get("summary", {})
            issues = crawler.get("issues", {})
            lines.append("=== WEBSITE-ANALYSE (Crawler) ===")
            lines.append(f"Gecrawlte Seiten: {s.get('total_pages', 0)}")
            lines.append(f"Fehlerseiten (404 etc.): {s.get('pages_error', 0)}")
            lines.append(f"Ø Ladezeit Server: {s.get('avg_response_ms', 'n/a')} ms")
            lines.append(f"Langsame Seiten (>1s): {s.get('slow_pages_count', 0)}")
            lines.append(f"SEO Crawler-Score: {s.get('seo_score', 0)}/100")
            lines.append("")

            if issues.get("missing_title"):
                lines.append(f"PROBLEM – Seiten ohne Seitentitel ({len(issues['missing_title'])} Seiten):")
                for u in issues["missing_title"][:5]:
                    lines.append(f"  - {u}")

            if issues.get("missing_meta_description"):
                lines.append(f"PROBLEM – Seiten ohne Meta-Beschreibung ({len(issues['missing_meta_description'])} Seiten):")
                for u in issues["missing_meta_description"][:5]:
                    lines.append(f"  - {u}")

            if issues.get("title_too_long"):
                lines.append(f"PROBLEM – Titel zu lang ({len(issues['title_too_long'])} Seiten):")
                for p in issues["title_too_long"][:3]:
                    lines.append(f"  - {p['url']} ({p['length']} Zeichen: '{p.get('title', '')[:60]}')")

            if issues.get("no_h1"):
                lines.append(f"PROBLEM – Seiten ohne Hauptüberschrift H1 ({len(issues['no_h1'])} Seiten):")
                for u in issues["no_h1"][:5]:
                    lines.append(f"  - {u}")

            if issues.get("duplicate_titles"):
                lines.append(f"PROBLEM – Doppelte Seitentitel ({len(issues['duplicate_titles'])} Gruppen):")
                for d in issues["duplicate_titles"][:3]:
                    lines.append(f"  - Titel '{d['title']}' auf {len(d['urls'])} Seiten")

            if issues.get("images_without_alt_total", 0) > 0:
                lines.append(f"PROBLEM – Bilder ohne Beschreibungstext: {issues['images_without_alt_total']} Bilder gesamt")

            if issues.get("thin_content_pages"):
                lines.append(f"PROBLEM – Seiten mit zu wenig Text (<300 Wörter, {len(issues['thin_content_pages'])} Seiten):")
                for p in issues["thin_content_pages"][:5]:
                    lines.append(f"  - {p['url']} ({p.get('word_count', 0)} Wörter)")

            if issues.get("error_pages"):
                lines.append(f"PROBLEM – Nicht erreichbare Seiten ({len(issues['error_pages'])}):")
                for u in issues["error_pages"][:5]:
                    lines.append(f"  - {u}")

            if issues.get("slow_pages"):
                lines.append(f"PROBLEM – Langsame Seiten (>1s Server-Antwort, {len(issues['slow_pages'])}):")
                for p in sorted(issues["slow_pages"], key=lambda x: x.get("response_time_ms", 0), reverse=True)[:5]:
                    lines.append(f"  - {p['url']} ({p.get('response_time_ms', 0):.0f} ms)")

            if issues.get("canonical_issues"):
                lines.append(f"PROBLEM – Canonical-Tag zeigt auf andere Seite ({len(issues['canonical_issues'])} Seiten)")

            lines.append(f"Seiten mit strukturierten Daten (Schema.org): {s.get('pages_with_structured_data', 0)}")
            lines.append("")

        # ── PageSpeed ─────────────────────────────────────────────────────────
        ps = results.get("pagespeed", {})
        mob = ps.get("mobile", {}) if ps else {}
        desk = ps.get("desktop", {}) if ps else {}
        if mob and not mob.get("error"):
            lines.append("=== GOOGLE PAGESPEED ===")
            lines.append(f"Mobile Score: {mob.get('performance_score', 'n/a')}/100")
            lines.append(f"Desktop Score: {desk.get('performance_score', 'n/a')}/100")
            lines.append(f"LCP (grösstes Element): {mob.get('lcp', 'n/a')} (Ziel: unter 2.5s)")
            lines.append(f"CLS (Layoutverschiebungen): {mob.get('cls', 'n/a')} (Ziel: unter 0.1)")
            lines.append(f"TBT (Blockierzeit): {mob.get('tbt', 'n/a')} (Ziel: unter 200ms)")
            lines.append(f"FCP (erster Inhalt sichtbar): {mob.get('fcp', 'n/a')}")
            failed = mob.get("failed_audits", [])
            if failed:
                lines.append(f"Nicht bestandene Audits ({len(failed)}):")
                for a in failed[:8]:
                    sav = f" (spart {a['savings_ms']} ms)" if a.get("savings_ms") else ""
                    lines.append(f"  - [{a['rating'].upper()}] {a['title']}{sav}")
            lines.append("")

        # ── SpeedTest ─────────────────────────────────────────────────────────
        st = results.get("speedtest", {})
        if st and not st.get("error") and st.get("summary"):
            ss = st["summary"]
            lines.append("=== LADEZEIT-TEST ===")
            lines.append(f"Gemessene Seiten: {ss.get('pages_tested', 0)}")
            lines.append(f"Ø TTFB (Server-Antwort): {ss.get('avg_ttfb_ms', 'n/a')} ms (gut: <200ms)")
            lines.append(f"Ø Gesamtladezeit: {ss.get('avg_total_ms', 'n/a')} ms")
            lines.append(f"Langsamste Seite: {ss.get('slowest_url', 'n/a')} ({ss.get('slowest_ms', 'n/a')} ms)")
            pages_s = st.get("pages", [])
            if pages_s:
                p0 = pages_s[0]
                lines.append(f"Komprimierung: {'Ja (' + p0.get('content_encoding', '') + ')' if p0.get('content_encoding') else 'Nein'}")
                lines.append(f"HTTP/2: {'Ja' if p0.get('http2') else 'Nein'}")
            for iss in st.get("issues", [])[:5]:
                lines.append(f"  - [{iss['priority']}] {iss['title']}")
            lines.append("")

        # ── GA4 ───────────────────────────────────────────────────────────────
        ga4 = results.get("ga4_traffic", {})
        if ga4 and not ga4.get("error") and not ga4.get("demo"):
            lines.append("=== GA4 TRAFFIC ===")
            lines.append(f"Sessions: {ga4.get('sessions', 0)}")
            lines.append(f"Nutzer: {ga4.get('users', 0)}")
            lines.append(f"Conversions: {ga4.get('conversions', 0)}")
            lines.append(f"Conversion-Rate: {ga4.get('conversion_rate', 0)}%")
            lines.append(f"Absprungrate: {ga4.get('bounce_rate', 0)}%")
            lines.append(f"Ø Session-Dauer: {ga4.get('avg_session_duration', 0):.0f}s")
            lines.append("")

        channels = results.get("ga4_channels", [])
        if channels and not (isinstance(channels, dict) and channels.get("error")):
            lines.append("GA4 Kanäle:")
            for ch in channels[:6]:
                lines.append(f"  - {ch.get('channel', '')}: {ch.get('sessions', 0)} Sessions, "
                             f"{ch.get('conversions', 0)} Conv. ({ch.get('conversion_rate', 0)}%)")
            lines.append("")

        devices = results.get("ga4_devices", [])
        if devices and not (isinstance(devices, dict) and devices.get("error")):
            lines.append("GA4 Geräte:")
            for d in devices[:3]:
                lines.append(f"  - {d.get('device', '')}: {d.get('sessions', 0)} Sessions, "
                             f"{d.get('conversion_rate', 0)}% Conv.-Rate")
            lines.append("")

        landingpages = results.get("ga4_landingpages", [])
        if landingpages and not (isinstance(landingpages, dict) and landingpages.get("error")):
            lines.append("Top Landing Pages:")
            for lp in landingpages[:5]:
                lines.append(f"  - {lp.get('page', '')}: {lp.get('sessions', 0)} Sessions, "
                             f"{lp.get('conversions', 0)} Conv.")
            lines.append("")

        return "\n".join(lines)

    def _build_prompt(self, context: str, kickoff: Dict) -> str:
        url = kickoff.get("website_url", "die Website")
        goal = kickoff.get("primary_goal", "nicht angegeben")
        audience = kickoff.get("target_audience", "nicht angegeben")
        main_action = kickoff.get("main_action", "")
        question = kickoff.get("main_question", "")
        known_issues = kickoff.get("known_issues", "")

        return f"""Du bist ein erfahrener Digital-Berater und schreibst einen Analysebericht für einen Kunden.
Der Kunde ist kein Techniker – erkläre alles einfach und verständlich. Vermeide Fachjargon wo möglich, oder erkläre Fachbegriffe kurz in Klammern.
Schreibe auf Schweizer Hochdeutsch. Professionell, direkt, keine Ausrufezeichen, keine Floskeln.

AUFTRAGSDETAILS:
- Website: {url}
- Ziel: {goal}
- Zielgruppe: {audience}
- Gewünschte Aktion der Besucher: {main_action or "nicht angegeben"}
- Bekannte Probleme: {known_issues or "keine angegeben"}
- Frage des Kunden: {question or "allgemeine Analyse"}

ANALYSEDATEN:
{context}

Schreibe jetzt den Analysebericht mit genau diesen Abschnitten:

---

## Zusammenfassung

In 3–5 Sätzen: Was ist der Gesamtzustand der Website? Was sind die wichtigsten Erkenntnisse? Was hat direkte Auswirkung auf den Geschäftserfolg?

---

## Was gut funktioniert

Liste 2–4 positive Punkte mit konkreten Werten aus den Daten. Nur echte Stärken nennen, die durch die Daten belegt sind.

---

## Die wichtigsten Probleme

Für jedes Problem folgendes Format verwenden:

**Problem [Nummer]: [Titel in einfacher, kundentauglicher Sprache]**
*Was passiert:* In 1–2 Sätzen, ohne Fachjargon erklären, was das Problem ist.
*Warum das für Sie wichtig ist:* Konkrete Auswirkung auf den Geschäftserfolg (z.B. "Besucher verlassen die Seite", "Google zeigt die Seite schlechter an", "potenzielle Kunden finden das Angebot nicht").
*Betroffene Stellen:* Nenne 1–3 konkrete URLs oder Bereiche direkt aus den Analysedaten.
*Was zu tun ist:* Konkrete Empfehlung in einfacher Sprache.
*Aufwand:* Klein (ein paar Stunden) / Mittel (1–3 Tage) / Gross (mehr als 3 Tage)
*Priorität:* Hoch / Mittel / Niedrig

Liste die 5–8 wichtigsten Probleme, sortiert nach Auswirkung auf das Ziel "{goal}".

---

## Massnahmenplan

### Diese Woche (sofortige Verbesserungen)
3–5 Massnahmen, die schnell umsetzbar sind und sofort Wirkung zeigen.
Format: **[Massnahme]** – [erwarteter Nutzen in einem Satz]

### Nächste 2–4 Wochen
3–5 wichtige Verbesserungen mit etwas mehr Aufwand.

### Langfristig (1–3 Monate)
2–3 strategische Investitionen.

---

## Antwort auf Ihre Frage

{f'Beantworte direkt: "{question}"' if question else 'Die wichtigste Erkenntnis für den Kunden in 2–3 Sätzen.'}

---

Wichtig: Beziehe dich immer auf konkrete Zahlen und URLs aus den Analysedaten. Kein allgemeines Blabla – nur was die Daten zeigen.
"""
