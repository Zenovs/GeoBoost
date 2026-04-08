import { useState } from "react";
import { startAnalysis, type KickoffData, type CheckConfig } from "../api";

interface Props {
  kickoff: KickoffData;
  initialChecks: CheckConfig;
  backendOk?: boolean;
  onStart: (checks: CheckConfig, analysisId: number, projectId: number) => void;
  onBack: () => void;
}

interface CheckDef {
  key: keyof CheckConfig;
  label: string;
  description: string;
  group: "Technisch" | "Analytics" | "KI" | "Report";
  duration: string;
  required?: boolean;
}

const CHECKS: CheckDef[] = [
  { key: "crawling",        label: "Website-Crawling",          description: "URLs, Status-Codes, Titles, H1, Canonical, Strukturierte Daten, Alt-Texte",  group: "Technisch", duration: "~5 min" },
  { key: "pagespeed",       label: "PageSpeed / Lighthouse",    description: "Mobile + Desktop Score, Core Web Vitals, LCP, CLS, TBT, alle Lighthouse-Audits", group: "Technisch", duration: "~3 min" },
  { key: "speedtest",       label: "HTTP Speed-Test",           description: "DNS, TCP, TLS, TTFB, Transfer – 3 Messungen pro Seite, Median-Auswertung",  group: "Technisch", duration: "~2 min" },
  { key: "ga4_traffic",     label: "GA4 Traffic-Übersicht",     description: "Users, Sessions, Conversions, Bounce Rate",                   group: "Analytics", duration: "~2 min" },
  { key: "ga4_channels",    label: "GA4 Kanal-Analyse",         description: "Traffic nach Channel: Organic, Direct, Paid, Social, Email",  group: "Analytics", duration: "~1 min" },
  { key: "ga4_landingpages",label: "GA4 Landing Pages",         description: "Top 10 Landing Pages mit Sessions, Conversions, Bounce Rate", group: "Analytics", duration: "~1 min" },
  { key: "ga4_devices",     label: "GA4 Device-Split",          description: "Mobile vs. Desktop vs. Tablet – Traffic und Conversions",     group: "Analytics", duration: "~1 min" },
  { key: "search_console",  label: "Search Console (Keywords)", description: "Top Keywords, Impressions, Clicks, CTR, Position",            group: "Analytics", duration: "~1 min" },
  { key: "ai_analysis",     label: "KI-Analyse & Massnahmen",   description: "Lokale Ollama KI generiert Insights und Massnahmenkatalog",   group: "KI",        duration: "~5 min" },
  { key: "pdf_report",      label: "PDF-Report Generierung",    description: "Präsentationsfertiges PDF mit allen Daten und Charts",        group: "Report",    duration: "~2 min", required: true },
];

const GROUPS = ["Technisch", "Analytics", "KI", "Report"] as const;

const PRESETS: { name: string; config: Partial<CheckConfig> }[] = [
  {
    name: "Level 1 – Standard",
    config: { crawling: true, pagespeed: true, speedtest: true, ga4_traffic: true, ga4_channels: true, ga4_landingpages: true, ga4_devices: true, search_console: false, ai_analysis: true, pdf_report: true },
  },
  {
    name: "Schnell-Check",
    config: { crawling: false, pagespeed: true, speedtest: true, ga4_traffic: true, ga4_channels: false, ga4_landingpages: false, ga4_devices: false, search_console: false, ai_analysis: false, pdf_report: true },
  },
  {
    name: "Nur Technisch",
    config: { crawling: true, pagespeed: true, speedtest: true, ga4_traffic: false, ga4_channels: false, ga4_landingpages: false, ga4_devices: false, search_console: false, ai_analysis: false, pdf_report: true },
  },
];

export default function CheckSelector({ kickoff, initialChecks, backendOk = true, onStart, onBack }: Props) {
  const [checks, setChecks] = useState<CheckConfig>(initialChecks);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const toggle = (key: keyof CheckConfig) => {
    const def = CHECKS.find((c) => c.key === key);
    if (def?.required) return;
    setChecks((c) => ({ ...c, [key]: !c[key] }));
  };

  const applyPreset = (preset: Partial<CheckConfig>) => {
    setChecks((c) => ({ ...c, ...preset }));
  };

  const estimatedMinutes = () => {
    return CHECKS.filter((c) => checks[c.key]).reduce((acc, c) => {
      const mins = parseInt(c.duration.replace(/\D/g, ""));
      return acc + (isNaN(mins) ? 0 : mins);
    }, 0);
  };

  const handleStart = async () => {
    setLoading(true);
    setError("");
    try {
      const { analysis_id, project_id } = await startAnalysis(kickoff, checks);
      onStart(checks, analysis_id, project_id);
    } catch (e: unknown) {
      setError((e as Error).message);
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="section-header">
        <div>
          <h1>Checks auswählen</h1>
          <p className="text-muted mt-2">Wähle aus, welche Analysen durchgeführt werden sollen.</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-muted text-sm">⏱ ca. {estimatedMinutes()} min</span>
          <button className="btn btn-ghost" onClick={onBack}>← Zurück</button>
        </div>
      </div>

      {/* Presets */}
      <div className="card mb-4">
        <div className="card-header">
          <h3>Voreinstellungen</h3>
        </div>
        <div className="card-body">
          <div className="flex gap-3">
            {PRESETS.map((p) => (
              <button key={p.name} className="btn btn-secondary btn-sm"
                onClick={() => applyPreset(p.config)}>
                {p.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Checks by Group */}
      {GROUPS.map((group) => {
        const groupChecks = CHECKS.filter((c) => c.group === group);
        return (
          <div key={group} className="card mb-4">
            <div className="card-header">
              <h3>{group}</h3>
            </div>
            <div className="card-body" style={{ padding: "0 20px" }}>
              {groupChecks.map((c) => (
                <div key={c.key} className="toggle-row">
                  <div className="toggle-info">
                    <h4>
                      {c.label}
                      {c.required && <span className="badge badge-gray ml-2" style={{ marginLeft: 8, fontSize: 11 }}>Pflicht</span>}
                    </h4>
                    <p>{c.description}</p>
                    <span className="text-xs text-muted">{c.duration}</span>
                  </div>
                  <label className="toggle-switch">
                    <input
                      type="checkbox"
                      checked={!!checks[c.key]}
                      onChange={() => toggle(c.key)}
                      disabled={c.required}
                    />
                    <span className="toggle-slider" />
                  </label>
                </div>
              ))}
            </div>
          </div>
        );
      })}

      {/* Summary + Start */}
      <div className="card">
        <div className="card-body">
          <div className="flex justify-between items-center">
            <div>
              <h3>Bereit?</h3>
              <p className="text-sm text-muted mt-2">
                <strong>{kickoff.website_url}</strong> –{" "}
                {CHECKS.filter((c) => checks[c.key]).length} Checks ausgewählt –
                ca. {estimatedMinutes()} Minuten
              </p>
            </div>
            <button
              className="btn btn-primary btn-lg"
              onClick={handleStart}
              disabled={loading || !backendOk}
              title={!backendOk ? "Backend nicht erreichbar – bitte warten" : undefined}
            >
              {loading ? "Starte..." : !backendOk ? "⏳ Backend startet..." : "▶ Analyse starten"}
            </button>
          </div>
          {error && <div className="alert alert-error mt-4">{error}</div>}
        </div>
      </div>
    </div>
  );
}
