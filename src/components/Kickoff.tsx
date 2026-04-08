import { useState } from "react";
import type { KickoffData } from "../api";

interface Props {
  initialData?: KickoffData;
  onNext: (data: KickoffData) => void;
  onCancel: () => void;
}

const EMPTY: KickoffData = {
  website_url: "",
  ga4_property_id: "",
  project_name: "",
  analysis_period: "last_28_days",
  primary_goal: "",
  main_action: "",
  lead_value: undefined,
  target_audience: "",
  audience_type: "B2B",
  seasonality: false,
  seasonality_notes: "",
  active_campaigns: [],
  expected_channels: [],
  known_issues: "",
  tech_feedback: "",
  recent_changes: false,
  recent_changes_notes: "",
  responsible_person: "",
  ga4_setup_by: "Intern",
  third_party_tools: [],
  competitors: "",
  main_question: "",
  use_search_console: false,
  search_console_url: "",
};

type Step = 0 | 1 | 2 | 3 | 4;
const STEPS = ["Projekt", "Ziele", "Zielgruppe", "Probleme", "Technik"];

function toggle(arr: string[], val: string): string[] {
  return arr.includes(val) ? arr.filter((v) => v !== val) : [...arr, val];
}

function Pill({
  label, active, onClick,
}: { label: string; active: boolean; onClick: () => void }) {
  return (
    <div className={`checkbox-pill ${active ? "checked" : ""}`} onClick={onClick}>
      {active ? "✓ " : ""}{label}
    </div>
  );
}

export default function Kickoff({ initialData, onNext, onCancel }: Props) {
  const [step, setStep] = useState<Step>(0);
  const [data, setData] = useState<KickoffData>(initialData || EMPTY);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const set = (field: keyof KickoffData, value: unknown) => {
    setData((d) => ({ ...d, [field]: value }));
    setErrors((e) => ({ ...e, [field]: "" }));
  };

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (step === 0) {
      if (!data.project_name) errs.project_name = "Pflichtfeld";
      if (!data.website_url) errs.website_url = "Pflichtfeld";
      else if (!/^https?:\/\//.test(data.website_url)) errs.website_url = "URL muss mit http:// oder https:// beginnen";
      if (!data.ga4_property_id) errs.ga4_property_id = "Pflichtfeld";
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const next = () => {
    if (!validate()) return;
    if (step < 4) setStep((s) => (s + 1) as Step);
    else onNext(data);
  };

  const back = () => {
    if (step === 0) onCancel();
    else setStep((s) => (s - 1) as Step);
  };

  return (
    <div>
      <div className="section-header">
        <div>
          <h1>Neue Analyse</h1>
          <p className="text-muted mt-2">Kickoff-Fragekatalog – Schritt {step + 1} von 5</p>
        </div>
        <button className="btn btn-ghost" onClick={onCancel}>Abbrechen</button>
      </div>

      {/* Wizard Steps */}
      <div className="wizard-steps mb-6">
        {STEPS.map((s, i) => (
          <div
            key={s}
            className={`wizard-step ${i === step ? "active" : i < step ? "done" : ""}`}
          >
            <div className="step-num">{i < step ? "✓" : i + 1}</div>
            <span>{s}</span>
            {i < STEPS.length - 1 && <span style={{ flex: 1, height: 1, background: "var(--gray-300)", margin: "0 10px" }} />}
          </div>
        ))}
      </div>

      <div className="card">
        <div className="card-body">

          {/* ── Step 0: Projekt ── */}
          {step === 0 && (
            <div>
              <h2 className="mb-4">Projektdaten</h2>
              <div className="form-group">
                <label className="form-label">Projektname <span className="required">*</span></label>
                <input className={`form-input ${errors.project_name ? "error" : ""}`} value={data.project_name}
                  onChange={(e) => set("project_name", e.target.value)}
                  placeholder="z.B. Muster AG – April 2026" />
                {errors.project_name && <div className="form-hint text-red">{errors.project_name}</div>}
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Website-URL <span className="required">*</span></label>
                  <input className={`form-input ${errors.website_url ? "error" : ""}`} value={data.website_url}
                    onChange={(e) => set("website_url", e.target.value)}
                    placeholder="https://www.example.com" />
                  {errors.website_url && <div className="form-hint text-red">{errors.website_url}</div>}
                </div>
                <div className="form-group">
                  <label className="form-label">GA4 Property ID <span className="required">*</span></label>
                  <input className={`form-input ${errors.ga4_property_id ? "error" : ""}`} value={data.ga4_property_id}
                    onChange={(e) => set("ga4_property_id", e.target.value)}
                    placeholder="123456789" />
                  {errors.ga4_property_id && <div className="form-hint text-red">{errors.ga4_property_id}</div>}
                  <div className="form-hint">Nur die Zahl, z.B. 123456789</div>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Analysezeitraum</label>
                <select className="form-select" value={data.analysis_period}
                  onChange={(e) => set("analysis_period", e.target.value)}>
                  <option value="last_28_days">Letzte 28 Tage</option>
                  <option value="last_3_months">Letzte 3 Monate</option>
                  <option value="last_6_months">Letzte 6 Monate</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Search Console verwenden?</label>
                <div className="checkbox-group">
                  <Pill label="Ja, Search Console einbinden" active={data.use_search_console}
                    onClick={() => set("use_search_console", !data.use_search_console)} />
                </div>
              </div>
              {data.use_search_console && (
                <div className="form-group">
                  <label className="form-label">Search Console Property URL</label>
                  <input className="form-input" value={data.search_console_url || ""}
                    onChange={(e) => set("search_console_url", e.target.value)}
                    placeholder="https://www.example.com" />
                </div>
              )}
            </div>
          )}

          {/* ── Step 1: Ziele ── */}
          {step === 1 && (
            <div>
              <h2 className="mb-4">Ziele &amp; Erfolgswerte</h2>
              <div className="form-group">
                <label className="form-label">Primäres Website-Ziel</label>
                <select className="form-select" value={data.primary_goal}
                  onChange={(e) => set("primary_goal", e.target.value)}>
                  <option value="">– Bitte wählen –</option>
                  <option value="Lead-Generierung">Lead-Generierung</option>
                  <option value="Verkauf">Verkauf / E-Commerce</option>
                  <option value="Branding">Branding / Bekanntheit</option>
                  <option value="Information">Information / Content</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Wertvollste Nutzeraktion</label>
                <input className="form-input" value={data.main_action}
                  onChange={(e) => set("main_action", e.target.value)}
                  placeholder="z.B. Kontaktformular, Anruf, Newsletter-Anmeldung" />
                <div className="form-hint">Welche Aktion ist die wichtigste Conversion auf der Website?</div>
              </div>
              <div className="form-group">
                <label className="form-label">Ungefährer Wert pro Lead/Sale (CHF, optional)</label>
                <input className="form-input" type="number" value={data.lead_value ?? ""}
                  onChange={(e) => set("lead_value", e.target.value ? parseFloat(e.target.value) : undefined)}
                  placeholder="z.B. 500" style={{ maxWidth: 200 }} />
              </div>
              <div className="form-group">
                <label className="form-label">Wichtigste Frage, die beantwortet werden muss</label>
                <textarea className="form-textarea" value={data.main_question}
                  onChange={(e) => set("main_question", e.target.value)}
                  placeholder="Was möchten Sie durch diese Analyse hauptsächlich herausfinden?" />
              </div>
            </div>
          )}

          {/* ── Step 2: Zielgruppe ── */}
          {step === 2 && (
            <div>
              <h2 className="mb-4">Zielgruppe &amp; Verhalten</h2>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Kernzielgruppe</label>
                  <input className="form-input" value={data.target_audience}
                    onChange={(e) => set("target_audience", e.target.value)}
                    placeholder="z.B. KMU-Entscheider, 35–55 Jahre, Schweiz" />
                </div>
                <div className="form-group">
                  <label className="form-label">Typ</label>
                  <select className="form-select" value={data.audience_type}
                    onChange={(e) => set("audience_type", e.target.value)}>
                    <option value="B2B">B2B</option>
                    <option value="B2C">B2C</option>
                    <option value="Beide">Beide</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Laufende Kampagnen</label>
                <div className="checkbox-group">
                  {["Google Ads", "Meta Ads", "LinkedIn", "Keine"].map((c) => (
                    <Pill key={c} label={c} active={data.active_campaigns.includes(c)}
                      onClick={() => set("active_campaigns", toggle(data.active_campaigns, c))} />
                  ))}
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Erwartete beste Traffic-Kanäle</label>
                <div className="checkbox-group">
                  {["SEO", "SEA", "Social", "Direct", "Referral", "Email"].map((c) => (
                    <Pill key={c} label={c} active={data.expected_channels.includes(c)}
                      onClick={() => set("expected_channels", toggle(data.expected_channels, c))} />
                  ))}
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Bekannte Saisonalitäten</label>
                <div className="checkbox-group">
                  <Pill label="Ja, es gibt saisonale Schwankungen" active={data.seasonality}
                    onClick={() => set("seasonality", !data.seasonality)} />
                </div>
                {data.seasonality && (
                  <textarea className="form-textarea mt-2" value={data.seasonality_notes}
                    onChange={(e) => set("seasonality_notes", e.target.value)}
                    placeholder="Beschreiben Sie die Saisonalitäten..." />
                )}
              </div>
              <div className="form-group">
                <label className="form-label">Direkte Wettbewerber (URLs)</label>
                <textarea className="form-textarea" value={data.competitors}
                  onChange={(e) => set("competitors", e.target.value)}
                  placeholder="https://wettbewerber1.ch&#10;https://wettbewerber2.ch" />
              </div>
            </div>
          )}

          {/* ── Step 3: Probleme ── */}
          {step === 3 && (
            <div>
              <h2 className="mb-4">Bekannte Probleme</h2>
              <div className="form-group">
                <label className="form-label">Bekannte Problembereiche auf der Website</label>
                <textarea className="form-textarea" value={data.known_issues}
                  onChange={(e) => set("known_issues", e.target.value)}
                  placeholder="z.B. Kontaktformular funktioniert auf Mobile nicht gut, Ladezeiten auf der Startseite zu lang..." />
              </div>
              <div className="form-group">
                <label className="form-label">Technisches Feedback von Kunden</label>
                <textarea className="form-textarea" value={data.tech_feedback}
                  onChange={(e) => set("tech_feedback", e.target.value)}
                  placeholder="z.B. Kunden berichten von Problemen beim Checkout..." />
              </div>
              <div className="form-group">
                <label className="form-label">Grössere Änderungen in den letzten 3 Monaten?</label>
                <div className="checkbox-group">
                  <Pill label="Ja, es gab grössere Änderungen" active={data.recent_changes}
                    onClick={() => set("recent_changes", !data.recent_changes)} />
                </div>
                {data.recent_changes && (
                  <textarea className="form-textarea mt-2" value={data.recent_changes_notes}
                    onChange={(e) => set("recent_changes_notes", e.target.value)}
                    placeholder="z.B. Relaunch, neues CMS, Kampagne gestartet..." />
                )}
              </div>
            </div>
          )}

          {/* ── Step 4: Technik ── */}
          {step === 4 && (
            <div>
              <h2 className="mb-4">Technisches</h2>
              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Zuständig für Umsetzung</label>
                  <input className="form-input" value={data.responsible_person}
                    onChange={(e) => set("responsible_person", e.target.value)}
                    placeholder="Name / Firma" />
                </div>
                <div className="form-group">
                  <label className="form-label">GA4-Setup durch</label>
                  <select className="form-select" value={data.ga4_setup_by}
                    onChange={(e) => set("ga4_setup_by", e.target.value)}>
                    <option value="Intern">Intern</option>
                    <option value="Externe Agentur">Externe Agentur</option>
                    <option value="Unbekannt">Unbekannt</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Genutzte Drittanbieter-Tools</label>
                <div className="checkbox-group">
                  {["CRM", "Live-Chat", "Shopify", "WooCommerce", "HubSpot", "Salesforce"].map((t) => (
                    <Pill key={t} label={t} active={data.third_party_tools.includes(t)}
                      onClick={() => set("third_party_tools", toggle(data.third_party_tools, t))} />
                  ))}
                </div>
              </div>
              <div className="alert alert-info mt-4">
                <span>✓</span>
                <div>
                  Alle Angaben können nach dem Start der Analyse nicht mehr geändert werden.
                  Im nächsten Schritt wählst du aus, welche Checks durchgeführt werden sollen.
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="card-footer flex justify-between items-center">
          <button className="btn btn-secondary" onClick={back}>
            {step === 0 ? "Abbrechen" : "← Zurück"}
          </button>
          <button className="btn btn-primary" onClick={next}>
            {step === 4 ? "Weiter zu Checks →" : "Weiter →"}
          </button>
        </div>
      </div>
    </div>
  );
}
