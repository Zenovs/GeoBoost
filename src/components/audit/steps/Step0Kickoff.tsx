import { useState, useEffect } from "react";

export interface KickoffData {
  // 1. Allgemeine Informationen
  client_name: string;
  website_url: string;
  contact_name: string;
  contact_email: string;
  contact_phone: string;
  // 2. Ziele der Geo-SEO Analyse
  main_goal: string;
  geographic_regions: string;
  // 3. Aktueller Stand & Zugänge
  has_google_business: string;
  has_search_console: string;
  has_ga4: string;
  access_email: string;
  // 4. Technische und inhaltliche Aspekte
  has_local_landingpages: string;
  technical_issues: string;
  // 5. Wettbewerb & Besonderheiten
  competitors: string;
  seasonal_factors: string;
  // 6. Erwartungen & Erfolgsmessung
  key_metrics: string;
  analysis_period: string;
  // 7. Auftrag & Kommunikation
  other_parties: string;
  special_requirements: string;
  // Meta
  analysis_date: string;
  analyst_name: string;
}

interface Props {
  initial?: Partial<KickoffData>;
  onChange: (data: KickoffData) => void;
}

const today = new Date().toLocaleDateString("de-CH", { day: "2-digit", month: "2-digit", year: "numeric" });

const EMPTY: KickoffData = {
  client_name: "", website_url: "", contact_name: "", contact_email: "", contact_phone: "",
  main_goal: "", geographic_regions: "",
  has_google_business: "", has_search_console: "", has_ga4: "", access_email: "",
  has_local_landingpages: "", technical_issues: "",
  competitors: "", seasonal_factors: "",
  key_metrics: "", analysis_period: "",
  other_parties: "", special_requirements: "",
  analysis_date: today, analyst_name: "",
};

function Section({ num, title, children }: { num: number; title: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 28 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
        <div style={{ width: 28, height: 28, borderRadius: "50%", background: "var(--blue-600,#2563eb)", color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontSize: 13, flexShrink: 0 }}>{num}</div>
        <h3 style={{ fontSize: 14, fontWeight: 700, color: "var(--gray-800,#1f2937)", margin: 0 }}>{title}</h3>
      </div>
      <div style={{ paddingLeft: 38 }}>{children}</div>
    </div>
  );
}

function YesNo({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <label className="form-group">
      <span>{label}</span>
      <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
        {["Ja", "Nein", "Unbekannt"].map((opt) => (
          <button key={opt} type="button" onClick={() => onChange(opt)}
            style={{ padding: "6px 16px", borderRadius: 6, border: "1px solid", fontSize: 13, cursor: "pointer", fontWeight: value === opt ? 700 : 400, background: value === opt ? "var(--blue-600,#2563eb)" : "white", color: value === opt ? "white" : "var(--gray-700,#374151)", borderColor: value === opt ? "var(--blue-600,#2563eb)" : "var(--gray-300,#d1d5db)" }}>
            {opt}
          </button>
        ))}
      </div>
    </label>
  );
}

export default function Step0Kickoff({ initial, onChange }: Props) {
  const [data, setData] = useState<KickoffData>({ ...EMPTY, ...initial });
  useEffect(() => { onChange(data); }, [data]);
  const set = (k: keyof KickoffData, v: string) => setData((d) => ({ ...d, [k]: v }));

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <h3 style={{ fontSize: 16, fontWeight: 700, margin: 0 }}>Fragekatalog / Kickoff</h3>
          <p style={{ fontSize: 13, color: "var(--gray-500,#6b7280)", marginTop: 4 }}>Ziele definieren – klare Ziele, Logins vorhanden</p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <label className="form-group" style={{ margin: 0 }}>
            <span>Analysedatum</span>
            <input className="form-input" value={data.analysis_date} onChange={(e) => set("analysis_date", e.target.value)} />
          </label>
          <label className="form-group" style={{ margin: 0 }}>
            <span>Analyst</span>
            <input className="form-input" value={data.analyst_name} onChange={(e) => set("analyst_name", e.target.value)} placeholder="Dein Name" />
          </label>
        </div>
      </div>

      <Section num={1} title="Allgemeine Informationen">
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
          <label className="form-group"><span>Firmenname *</span><input className="form-input" value={data.client_name} onChange={(e) => set("client_name", e.target.value)} placeholder="Musterfirma AG" /></label>
          <label className="form-group"><span>Website-URL *</span><input className="form-input" value={data.website_url} onChange={(e) => set("website_url", e.target.value)} placeholder="https://www.example.com" /></label>
          <label className="form-group"><span>Ansprechpartner (Name)</span><input className="form-input" value={data.contact_name} onChange={(e) => set("contact_name", e.target.value)} placeholder="Max Muster" /></label>
          <label className="form-group"><span>E-Mail</span><input className="form-input" value={data.contact_email} onChange={(e) => set("contact_email", e.target.value)} placeholder="max@example.com" /></label>
          <label className="form-group"><span>Telefon</span><input className="form-input" value={data.contact_phone} onChange={(e) => set("contact_phone", e.target.value)} placeholder="+41 79 123 45 67" /></label>
        </div>
      </Section>

      <Section num={2} title="Ziele der Geo-SEO Analyse">
        <label className="form-group">
          <span>Was ist das Hauptziel der Analyse? (z.B. bessere lokale Sichtbarkeit, mehr Besucher aus bestimmten Regionen, mehr Anfragen/Leads)</span>
          <textarea className="form-input" rows={3} value={data.main_goal} onChange={(e) => set("main_goal", e.target.value)} placeholder="Hauptziel beschreiben..." />
        </label>
        <label className="form-group">
          <span>Welche geografischen Regionen sind besonders wichtig? (z.B. Schweiz gesamt, einzelne Kantone, Städte, Nachbarländer)</span>
          <textarea className="form-input" rows={2} value={data.geographic_regions} onChange={(e) => set("geographic_regions", e.target.value)} placeholder="z.B. Wallis, Bern, Zürich..." />
        </label>
      </Section>

      <Section num={3} title="Aktueller Stand & Zugänge">
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16 }}>
          <YesNo label="Google My Business / Google Business Profile?" value={data.has_google_business} onChange={(v) => set("has_google_business", v)} />
          <YesNo label="Zugriff auf Google Search Console?" value={data.has_search_console} onChange={(v) => set("has_search_console", v)} />
          <YesNo label="Zugriff auf Google Analytics (GA4)?" value={data.has_ga4} onChange={(v) => set("has_ga4", v)} />
        </div>
        <label className="form-group" style={{ marginTop: 8 }}>
          <span>Falls ja: Zugangsdaten oder Nutzer mit Zugriffsrechten (E-Mail-Adresse)</span>
          <input className="form-input" value={data.access_email} onChange={(e) => set("access_email", e.target.value)} placeholder="zugang@example.com" />
        </label>
      </Section>

      <Section num={4} title="Technische und inhaltliche Aspekte">
        <YesNo label="Gibt es bereits lokale Landingpages für die verschiedenen Regionen?" value={data.has_local_landingpages} onChange={(v) => set("has_local_landingpages", v)} />
        <label className="form-group" style={{ marginTop: 8 }}>
          <span>Bekannte Probleme oder Einschränkungen auf der Website? (z.B. langsame Ladezeiten, fehlende mobile Optimierung)</span>
          <textarea className="form-input" rows={2} value={data.technical_issues} onChange={(e) => set("technical_issues", e.target.value)} placeholder="Bekannte Probleme..." />
        </label>
      </Section>

      <Section num={5} title="Wettbewerb & Besonderheiten">
        <label className="form-group">
          <span>Wichtigste lokale Wettbewerber (Websites oder Firmennamen)</span>
          <textarea className="form-input" rows={2} value={data.competitors} onChange={(e) => set("competitors", e.target.value)} placeholder="z.B. konkurrenz.ch, Musterfirma 2 AG..." />
        </label>
        <label className="form-group">
          <span>Saisonale Schwankungen oder besondere Ereignisse die berücksichtigt werden sollen?</span>
          <textarea className="form-input" rows={2} value={data.seasonal_factors} onChange={(e) => set("seasonal_factors", e.target.value)} placeholder="z.B. Wintersaison, Messen, Feiertage..." />
        </label>
      </Section>

      <Section num={6} title="Erwartungen & Erfolgsmessung">
        <label className="form-group">
          <span>Wichtigste Kennzahlen (z.B. organischer Traffic, Anfragen, Telefonanrufe, Ladenbesuche)</span>
          <textarea className="form-input" rows={2} value={data.key_metrics} onChange={(e) => set("key_metrics", e.target.value)} placeholder="Welche KPIs sind am wichtigsten..." />
        </label>
        <label className="form-group">
          <span>Gewünschter Analysezeitraum (z.B. letzte 3 Monate, letztes Jahr)</span>
          <input className="form-input" value={data.analysis_period} onChange={(e) => set("analysis_period", e.target.value)} placeholder="z.B. 01.01.2026 – 31.03.2026" />
        </label>
      </Section>

      <Section num={7} title="Auftrag & Kommunikation">
        <label className="form-group">
          <span>Weitere Personen oder Agenturen, die in den Prozess eingebunden werden sollen?</span>
          <input className="form-input" value={data.other_parties} onChange={(e) => set("other_parties", e.target.value)} placeholder="z.B. Webdesigner, Marketingagentur..." />
        </label>
        <label className="form-group">
          <span>Spezielle Anforderungen oder Wünsche die beachtet werden sollen?</span>
          <textarea className="form-input" rows={2} value={data.special_requirements} onChange={(e) => set("special_requirements", e.target.value)} placeholder="Besondere Hinweise, Einschränkungen..." />
        </label>
      </Section>
    </div>
  );
}
