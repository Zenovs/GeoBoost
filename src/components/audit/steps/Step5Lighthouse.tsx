import { useState, useEffect } from "react";
import { fetchLighthouseForAudit } from "../../../api";

export interface PriorityItem {
  problem: string;
  warum: string;
  erledigung: string;
  auswirkung: string;
}

export interface LighthouseData {
  // 1. Scores
  mobile_performance?: number;
  mobile_accessibility?: number;
  mobile_best_practices?: number;
  mobile_seo?: number;
  desktop_performance?: number;
  desktop_accessibility?: number;
  desktop_best_practices?: number;
  desktop_seo?: number;
  // 2. Core Web Vitals
  cwv_lcp?: string;
  cwv_cls?: string;
  cwv_tbt?: string;
  // 3. Top 3 Optimierungspotenziale
  priority_a: PriorityItem;
  priority_b: PriorityItem;
  priority_c: PriorityItem;
  // 4. Technische Checkliste
  checklist_mobile: boolean;
  checklist_https: boolean;
  checklist_bildformate: boolean;
  checklist_textkontrast: boolean;
  checklist_urls: boolean;
  // 5. Fazit & Nächste Schritte
  fazit: string;
  performance_status: string;
  next_step: string;
  next_step_date: string;
}

const EMPTY_PRIORITY: PriorityItem = { problem: "", warum: "", erledigung: "", auswirkung: "" };
const EMPTY: LighthouseData = {
  mobile_performance: undefined, mobile_accessibility: undefined,
  mobile_best_practices: undefined, mobile_seo: undefined,
  desktop_performance: undefined, desktop_accessibility: undefined,
  desktop_best_practices: undefined, desktop_seo: undefined,
  cwv_lcp: "", cwv_cls: "", cwv_tbt: "",
  priority_a: { ...EMPTY_PRIORITY }, priority_b: { ...EMPTY_PRIORITY }, priority_c: { ...EMPTY_PRIORITY },
  checklist_mobile: false, checklist_https: false, checklist_bildformate: false,
  checklist_textkontrast: false, checklist_urls: false,
  fazit: "", performance_status: "", next_step: "", next_step_date: "",
};

interface Props {
  auditId: number;
  websiteUrl?: string;
  initial?: Partial<LighthouseData>;
  onChange: (data: LighthouseData) => void;
}

function scoreColor(v?: number) {
  if (v === undefined) return "#9ca3af";
  return v >= 90 ? "#16a34a" : v >= 50 ? "#d97706" : "#dc2626";
}
function scoreEmoji(v?: number) {
  if (v === undefined) return "⚪";
  return v >= 90 ? "🟢" : v >= 50 ? "🟡" : "🔴";
}

function ScoreInput({ label, value, onChange }: { label: string; value?: number; onChange: (v?: number) => void }) {
  const color = scoreColor(value);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 0", borderBottom: "1px solid var(--gray-100,#f3f4f6)" }}>
      <span style={{ fontSize: 16 }}>{scoreEmoji(value)}</span>
      <span style={{ flex: 1, fontSize: 13, fontWeight: 600 }}>{label}</span>
      <input
        type="number" min={0} max={100}
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value === "" ? undefined : Number(e.target.value))}
        style={{ width: 64, padding: "5px 8px", borderRadius: 6, border: `2px solid ${color}`, fontSize: 14, fontWeight: 800, color, textAlign: "center", outline: "none" }}
        placeholder="–"
      />
    </div>
  );
}

function PriorityCard({ label, color, value, onChange }: { label: string; color: string; value: PriorityItem; onChange: (v: PriorityItem) => void }) {
  const set = (k: keyof PriorityItem, v: string) => onChange({ ...value, [k]: v });
  return (
    <div style={{ border: `2px solid ${color}`, borderRadius: 10, overflow: "hidden" }}>
      <div style={{ background: color, padding: "8px 14px", display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{ color: "white", fontWeight: 800, fontSize: 13 }}>{label}</span>
      </div>
      <div style={{ padding: 14, display: "flex", flexDirection: "column", gap: 10 }}>
        <label className="form-group" style={{ margin: 0 }}>
          <span>Problem</span>
          <input className="form-input" value={value.problem} onChange={(e) => set("problem", e.target.value)} placeholder="z.B. Bilder nicht optimiert" />
        </label>
        <label className="form-group" style={{ margin: 0 }}>
          <span>Warum</span>
          <textarea className="form-input" rows={2} value={value.warum} onChange={(e) => set("warum", e.target.value)} placeholder="Warum ist das ein Problem? Hintergrund..." />
        </label>
        <label className="form-group" style={{ margin: 0 }}>
          <span>Erledigung</span>
          <textarea className="form-input" rows={2} value={value.erledigung} onChange={(e) => set("erledigung", e.target.value)} placeholder="Wie kann es behoben werden? Schnell / mittelfristig?" />
        </label>
        <label className="form-group" style={{ margin: 0 }}>
          <span>Auswirkung</span>
          <input className="form-input" value={value.auswirkung} onChange={(e) => set("auswirkung", e.target.value)} placeholder="Hoch auf LCP / TBT / Performance Score..." />
        </label>
      </div>
    </div>
  );
}

export default function Step5Lighthouse({ auditId, websiteUrl, initial, onChange }: Props) {
  const [data, setData] = useState<LighthouseData>({ ...EMPTY, ...initial });
  const [fetching, setFetching] = useState(false);
  const [fetchErr, setFetchErr] = useState("");

  useEffect(() => { onChange(data); }, [data]);
  const set = <K extends keyof LighthouseData>(k: K, v: LighthouseData[K]) => setData((d) => ({ ...d, [k]: v }));

  const handleFetch = async () => {
    if (!websiteUrl) return;
    setFetching(true);
    setFetchErr("");
    try {
      const result = await fetchLighthouseForAudit(auditId, websiteUrl);
      setData((d) => ({ ...d, ...result }));
    } catch (e: unknown) {
      setFetchErr(e instanceof Error ? e.message : "Fehler beim Abrufen.");
    } finally {
      setFetching(false);
    }
  };

  return (
    <div>
      <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 4 }}>Lighthouse Bericht</h3>
      <p style={{ fontSize: 13, color: "var(--gray-500,#6b7280)", marginBottom: 16 }}>
        PageSpeed / Lighthouse Scores nach der Bericht-Vorlage erfassen
      </p>

      {websiteUrl && (
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20, padding: "10px 14px", background: "#f0f4ff", borderRadius: 8 }}>
          <button type="button" onClick={handleFetch} disabled={fetching}
            style={{ background: "#2563eb", color: "white", border: "none", borderRadius: 7, padding: "8px 18px", fontSize: 13, fontWeight: 700, cursor: fetching ? "wait" : "pointer", opacity: fetching ? 0.7 : 1 }}>
            {fetching ? "⏳ Wird abgerufen..." : "🚀 Via PageSpeed API abrufen"}
          </button>
          <span style={{ fontSize: 12, color: "#6b7280" }}>{websiteUrl}</span>
          {fetchErr && <span style={{ fontSize: 12, color: "#dc2626" }}>{fetchErr}</span>}
        </div>
      )}

      {/* 1. Zusammenfassende Bewertung */}
      <div style={{ background: "var(--gray-50,#f9fafb)", border: "1px solid var(--gray-200,#e5e7eb)", borderRadius: 10, padding: 18, marginBottom: 20 }}>
        <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 4 }}>1. Zusammenfassende Bewertung</h4>
        <p style={{ fontSize: 12, color: "#6b7280", marginBottom: 14, fontStyle: "italic" }}>Die vier Haupt-Scores von Lighthouse (0–100) auf einen Blick dargestellt.</p>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
          <div>
            <div style={{ fontSize: 12, fontWeight: 700, color: "#6b7280", marginBottom: 8 }}>📱 MOBILE</div>
            <ScoreInput label="Performance" value={data.mobile_performance} onChange={(v) => set("mobile_performance", v)} />
            <ScoreInput label="Barrierefreiheit (Accessibility)" value={data.mobile_accessibility} onChange={(v) => set("mobile_accessibility", v)} />
            <ScoreInput label="Best Practices" value={data.mobile_best_practices} onChange={(v) => set("mobile_best_practices", v)} />
            <ScoreInput label="SEO" value={data.mobile_seo} onChange={(v) => set("mobile_seo", v)} />
          </div>
          <div>
            <div style={{ fontSize: 12, fontWeight: 700, color: "#6b7280", marginBottom: 8 }}>🖥️ DESKTOP</div>
            <ScoreInput label="Performance" value={data.desktop_performance} onChange={(v) => set("desktop_performance", v)} />
            <ScoreInput label="Barrierefreiheit (Accessibility)" value={data.desktop_accessibility} onChange={(v) => set("desktop_accessibility", v)} />
            <ScoreInput label="Best Practices" value={data.desktop_best_practices} onChange={(v) => set("desktop_best_practices", v)} />
            <ScoreInput label="SEO" value={data.desktop_seo} onChange={(v) => set("desktop_seo", v)} />
          </div>
        </div>
      </div>

      {/* 2. Core Web Vitals */}
      <div style={{ background: "var(--gray-50,#f9fafb)", border: "1px solid var(--gray-200,#e5e7eb)", borderRadius: 10, padding: 18, marginBottom: 20 }}>
        <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 4 }}>2. Core Web Vitals (Nutzererfahrung)</h4>
        <p style={{ fontSize: 12, color: "#6b7280", marginBottom: 14, fontStyle: "italic" }}>Diese Werte entscheiden massgeblich über das Ranking und die gefühlte Geschwindigkeit.</p>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
          <label className="form-group">
            <span style={{ fontWeight: 700 }}>LCP – Largest Contentful Paint</span>
            <input className="form-input" value={data.cwv_lcp ?? ""} onChange={(e) => set("cwv_lcp", e.target.value)} placeholder="z.B. 2.1 s" />
            <span style={{ fontSize: 10, color: "#9ca3af" }}>Wie lange dauert es, bis der Hauptinhalt geladen ist? Ziel: &lt; 2,5s</span>
          </label>
          <label className="form-group">
            <span style={{ fontWeight: 700 }}>CLS – Cumulative Layout Shift</span>
            <input className="form-input" value={data.cwv_cls ?? ""} onChange={(e) => set("cwv_cls", e.target.value)} placeholder="z.B. 0.05" />
            <span style={{ fontSize: 10, color: "#9ca3af" }}>Wie stark verschieben sich Elemente beim Laden? Ziel: &lt; 0.1</span>
          </label>
          <label className="form-group">
            <span style={{ fontWeight: 700 }}>TBT – Total Blocking Time</span>
            <input className="form-input" value={data.cwv_tbt ?? ""} onChange={(e) => set("cwv_tbt", e.target.value)} placeholder="z.B. 320 ms" />
            <span style={{ fontSize: 10, color: "#9ca3af" }}>Wie lange ist die Seite während des Ladens blockiert? Ziel: &lt; 200ms</span>
          </label>
        </div>
      </div>

      {/* 3. Top 3 Optimierungspotenziale */}
      <div style={{ marginBottom: 20 }}>
        <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 4 }}>3. Top 3 Optimierungspotenziale</h4>
        <p style={{ fontSize: 12, color: "#6b7280", marginBottom: 14, fontStyle: "italic" }}>Fokus auf die Massnahmen mit dem grössten Hebel.</p>
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          <PriorityCard label="Priorität A: Problem 1" color="#dc2626" value={data.priority_a} onChange={(v) => set("priority_a", v)} />
          <PriorityCard label="Priorität B: Problem 2" color="#d97706" value={data.priority_b} onChange={(v) => set("priority_b", v)} />
          <PriorityCard label="Priorität C: Problem 3" color="#2563eb" value={data.priority_c} onChange={(v) => set("priority_c", v)} />
        </div>
      </div>

      {/* 4. Technische Checkliste */}
      <div style={{ background: "var(--gray-50,#f9fafb)", border: "1px solid var(--gray-200,#e5e7eb)", borderRadius: 10, padding: 18, marginBottom: 20 }}>
        <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 4 }}>4. Technische Checkliste</h4>
        <p style={{ fontSize: 12, color: "#6b7280", marginBottom: 14, fontStyle: "italic" }}>Kurzer Überblick über wichtige Einzelpunkte.</p>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {[
            { key: "checklist_mobile" as const, label: "Mobile Optimierung", hint: "Ist die Darstellung auf Smartphones fehlerfrei?" },
            { key: "checklist_https" as const, label: "HTTPS", hint: "Ist die Verbindung sicher verschlüsselt?" },
            { key: "checklist_bildformate" as const, label: "Bildformate", hint: "Werden moderne Formate (WebP/AVIF) genutzt?" },
            { key: "checklist_textkontrast" as const, label: "Textkontrast", hint: "Ist die Lesbarkeit für alle Nutzer gegeben?" },
            { key: "checklist_urls" as const, label: "Sprechende URLs", hint: "Sind die Pfade für Nutzer und Google lesbar?" },
          ].map((item) => (
            <label key={item.key} style={{ display: "flex", alignItems: "center", gap: 10, cursor: "pointer", padding: "8px 10px", borderRadius: 8, background: data[item.key] ? "#dcfce7" : "white", border: `1px solid ${data[item.key] ? "#86efac" : "#e5e7eb"}`, transition: "all 0.15s" }}>
              <input type="checkbox" checked={data[item.key]} onChange={(e) => set(item.key, e.target.checked)}
                style={{ width: 16, height: 16, accentColor: "#16a34a", flexShrink: 0 }} />
              <span style={{ fontWeight: 700, fontSize: 13 }}>{item.label}:</span>
              <span style={{ fontSize: 12, color: "#6b7280" }}>{item.hint}</span>
              {data[item.key] && <span style={{ marginLeft: "auto", color: "#16a34a", fontSize: 14 }}>✓</span>}
            </label>
          ))}
        </div>
      </div>

      {/* 5. Fazit & Nächste Schritte */}
      <div style={{ background: "var(--gray-50,#f9fafb)", border: "1px solid var(--gray-200,#e5e7eb)", borderRadius: 10, padding: 18 }}>
        <h4 style={{ fontSize: 14, fontWeight: 700, marginBottom: 4 }}>5. Fazit & Nächste Schritte</h4>
        <p style={{ fontSize: 12, color: "#6b7280", marginBottom: 14, fontStyle: "italic" }}>Kurze Einordnung des Ergebnisses.</p>
        <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 14, marginBottom: 14 }}>
          <label className="form-group" style={{ margin: 0 }}>
            <span>Performance-Status der Website</span>
            <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
              {["gut", "mittelmässig", "kritisch"].map((opt) => (
                <button key={opt} type="button" onClick={() => set("performance_status", opt)}
                  style={{ padding: "6px 14px", borderRadius: 6, border: "1px solid", fontSize: 13, cursor: "pointer", fontWeight: data.performance_status === opt ? 700 : 400,
                    background: data.performance_status === opt ? (opt === "gut" ? "#16a34a" : opt === "mittelmässig" ? "#d97706" : "#dc2626") : "white",
                    color: data.performance_status === opt ? "white" : "#374151",
                    borderColor: data.performance_status === opt ? "transparent" : "#d1d5db" }}>
                  {opt}
                </button>
              ))}
            </div>
          </label>
        </div>
        <label className="form-group">
          <span>Fazit-Text</span>
          <textarea className="form-input" rows={3} value={data.fazit} onChange={(e) => set("fazit", e.target.value)}
            placeholder="Die Performance der Website ist aktuell [gut / mittelmässig / kritisch]. Während die SEO-Grundlagen solide sind, liegt das grösste Potenzial in der [z.B. Ladezeit-Optimierung]." />
        </label>
        <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 12 }}>
          <label className="form-group" style={{ margin: 0 }}>
            <span>Nächster Schritt</span>
            <input className="form-input" value={data.next_step} onChange={(e) => set("next_step", e.target.value)} placeholder="z.B. Implementierung der Bilder-Optimierung" />
          </label>
          <label className="form-group" style={{ margin: 0 }}>
            <span>Bis zum</span>
            <input className="form-input" value={data.next_step_date} onChange={(e) => set("next_step_date", e.target.value)} placeholder="Datum" style={{ width: 140 }} />
          </label>
        </div>
      </div>
    </div>
  );
}
