import { useState } from "react";
import CsvUploadZone from "../CsvUploadZone";
import { uploadSemrushCsv, updateAuditStep } from "../../../api";

export interface SemrushData {
  site_health_score?: number;
  semrush_summary?: { total_issues: number; errors: number; warnings: number; notices: number };
  semrush_issues?: Array<{ issue: string; count: number; severity: string; category: string }>;
  on_page_seo_notes: string;
  technical_status_notes: string;
  geo_ki_notes: string;
  notes: string;
}

interface Props {
  auditId: number;
  initial?: Partial<SemrushData>;
  onUpdate: (data: SemrushData) => void;
}

const SEV_STYLE: Record<string, { bg: string; color: string; label: string }> = {
  error:   { bg: "#fee2e2", color: "#dc2626", label: "Fehler" },
  warning: { bg: "#fef3c7", color: "#d97706", label: "Warnung" },
  notice:  { bg: "#ede9fe", color: "#7c3aed", label: "Hinweis" },
};

function ScoreMeter({ value }: { value?: number }) {
  if (value === undefined) return null;
  const color = value >= 80 ? "#16a34a" : value >= 50 ? "#d97706" : "#dc2626";
  const label = value >= 80 ? "Gut" : value >= 50 ? "Mittel" : "Kritisch";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <div style={{ width: 64, height: 64, borderRadius: "50%", border: `5px solid ${color}`, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column" }}>
        <span style={{ fontSize: 18, fontWeight: 800, color }}>{value}</span>
      </div>
      <div>
        <div style={{ fontSize: 13, fontWeight: 700, color }}>Site Health Score: {label}</div>
        <div style={{ fontSize: 11, color: "#9ca3af" }}>0 = kritisch, 100 = perfekt</div>
      </div>
    </div>
  );
}

export default function Step4Semrush({ auditId, initial, onUpdate }: Props) {
  const [data, setData] = useState<SemrushData>({ on_page_seo_notes: "", technical_status_notes: "", geo_ki_notes: "", notes: "", ...initial });
  const [loading, setLoading] = useState(false);
  const set = (k: keyof SemrushData, v: unknown) => setData((d) => ({ ...d, [k]: v }));

  const handleUpload = async (file: File) => {
    setLoading(true);
    try {
      const result = await uploadSemrushCsv(auditId, file);
      const merged = { ...data, semrush_summary: (result as any).summary, semrush_issues: (result as any).issues };
      setData(merged);
      onUpdate(merged);
    } finally {
      setLoading(false);
    }
  };

  const save = async () => {
    onUpdate(data);
    await updateAuditStep(auditId, 4, data).catch(() => {});
  };

  const summary = data.semrush_summary;
  const issues = data.semrush_issues || [];

  return (
    <div>
      <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 4 }}>SemRush Check</h3>
      <p style={{ fontSize: 13, color: "var(--gray-500,#6b7280)", marginBottom: 16 }}>
        Exportiere in SemRush unter <strong>Site Audit → Issues → Export CSV</strong>
      </p>

      {/* Site Health Score */}
      <div style={{ background: "var(--gray-50,#f9fafb)", border: "1px solid var(--gray-200,#e5e7eb)", borderRadius: 10, padding: 16, marginBottom: 20 }}>
        <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 10 }}>Site Health Score</div>
        <p style={{ fontSize: 11, color: "#6b7280", marginBottom: 12 }}>Nach dem Audit erhältst du einen Gesamtscore, der anzeigt, wie gut der technische Zustand der Website ist. Probleme werden in drei Schweregrade unterteilt.</p>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <label className="form-group" style={{ margin: 0, flexShrink: 0 }}>
            <span>Score (0–100)</span>
            <input className="form-input" type="number" min={0} max={100} style={{ width: 80 }}
              value={data.site_health_score ?? ""} onChange={(e) => set("site_health_score", e.target.value === "" ? undefined : Number(e.target.value))} onBlur={save} />
          </label>
          <ScoreMeter value={data.site_health_score} />
        </div>
      </div>

      <CsvUploadZone
        label="SemRush CSV hochladen"
        hint=".csv · Drag & Drop oder klicken"
        onFile={handleUpload}
        loading={loading}
        done={!!summary}
      />

      {summary && (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginTop: 20 }}>
            {[["Fehler", summary.errors, "#fee2e2", "#dc2626", "#fecaca"], ["Warnungen", summary.warnings, "#fef3c7", "#d97706", "#fde68a"], ["Hinweise", summary.notices, "#ede9fe", "#7c3aed", "#ddd6fe"]].map(([label, val, bg, color, border]) => (
              <div key={String(label)} style={{ background: String(bg), border: `1px solid ${border}`, borderRadius: 10, padding: "14px 16px", textAlign: "center" }}>
                <div style={{ fontSize: 10, color: String(color), textTransform: "uppercase", letterSpacing: "0.8px", marginBottom: 4 }}>{label}</div>
                <div style={{ fontSize: 28, fontWeight: 800, color: String(color) }}>{val}</div>
              </div>
            ))}
          </div>

          {issues.length > 0 && (
            <div style={{ marginTop: 20, display: "flex", flexDirection: "column", gap: 8 }}>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>Gefundene Probleme ({issues.length})</h3>
              {issues.map((issue, i) => {
                const s = SEV_STYLE[issue.severity] || { bg: "#f3f4f6", color: "#374151", label: issue.severity };
                return (
                  <div key={i} style={{ background: "white", border: "1px solid var(--gray-200,#e5e7eb)", borderLeft: `4px solid ${s.color}`, borderRadius: 8, padding: "10px 14px", display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ padding: "2px 9px", borderRadius: 10, fontSize: 10, fontWeight: 700, background: s.bg, color: s.color, flexShrink: 0 }}>{s.label.toUpperCase()}</span>
                    <div style={{ flex: 1, fontSize: 13, fontWeight: 500 }}>{issue.issue}</div>
                    {issue.category && <span style={{ fontSize: 11, color: "#9ca3af", flexShrink: 0 }}>{issue.category}</span>}
                    <span style={{ fontSize: 12, fontWeight: 700, color: "#4b5563", flexShrink: 0 }}>{issue.count} URLs</span>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      {/* Section notes */}
      <div style={{ display: "flex", flexDirection: "column", gap: 14, marginTop: 20 }}>
        <label className="form-group">
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
            <span style={{ fontSize: 14 }}>🔍</span>
            <span style={{ fontWeight: 600, fontSize: 13 }}>On-Page SEO</span>
            <span style={{ fontSize: 11, color: "#9ca3af" }}>Meta-Tags, Überschriften, Keywords, Seitengeschwindigkeit, Mobilfreundlichkeit, Core Web Vitals</span>
          </div>
          <textarea className="form-input" rows={2} value={data.on_page_seo_notes} onChange={(e) => set("on_page_seo_notes", e.target.value)} onBlur={save} placeholder="On-Page SEO Erkenntnisse..." />
        </label>
        <label className="form-group">
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
            <span style={{ fontSize: 14 }}>⚙️</span>
            <span style={{ fontWeight: 600, fontSize: 13 }}>Technischer Zustand</span>
            <span style={{ fontSize: 11, color: "#9ca3af" }}>Crawlability, Indexierbarkeit, Statuscodes, Robots-Direktiven, Sitemap, Canonical-Tags, strukturierte Daten</span>
          </div>
          <textarea className="form-input" rows={2} value={data.technical_status_notes} onChange={(e) => set("technical_status_notes", e.target.value)} onBlur={save} placeholder="Technischer Zustand der Website..." />
        </label>
        <label className="form-group">
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
            <span style={{ fontSize: 14 }}>🤖</span>
            <span style={{ fontWeight: 600, fontSize: 13 }}>KI-Suche / GEO</span>
            <span style={{ fontSize: 11, background: "#fef9c3", color: "#92400e", padding: "1px 6px", borderRadius: 4, fontWeight: 600 }}>NEU</span>
            <span style={{ fontSize: 11, color: "#9ca3af" }}>Generative Engine Optimization – Sichtbarkeit in SearchGPT, Claude, Perplexity</span>
          </div>
          <textarea className="form-input" rows={2} value={data.geo_ki_notes} onChange={(e) => set("geo_ki_notes", e.target.value)} onBlur={save} placeholder="KI-Sichtbarkeit, strukturierte Daten für AI-Suche, GEO-Massnahmen..." />
        </label>
        <label className="form-group">
          <span>Allgemeine Notizen</span>
          <textarea className="form-input" rows={2} value={data.notes} onChange={(e) => set("notes", e.target.value)} onBlur={save} placeholder="Weitere Beobachtungen..." />
        </label>
      </div>
    </div>
  );
}
