import { useState } from "react";
import CsvUploadZone from "../CsvUploadZone";
import { uploadScreamingFrogCsv, updateAuditStep } from "../../../api";

export interface CrawlData {
  summary?: {
    total_urls: number; ok_200: number; redirects_3xx: number;
    errors_4xx: number; errors_5xx: number; missing_title: number;
    title_too_long: number; missing_meta: number; meta_too_long: number;
    missing_h1: number; slow_pages: number;
  };
  issues?: Array<{
    url: string; status_code: number; title: string; title_length: number;
    title_issue: string; meta: string; meta_length: number; meta_issue: string;
    h1: string; h1_issue: string; response_time_ms: number; flags: string[];
  }>;
  keywords_notes: string;
  notes: string;
}

interface Props {
  auditId: number;
  initial?: Partial<CrawlData>;
  onUpdate: (data: CrawlData) => void;
}

const SEV: Record<string, string> = {
  ok: "background:#dcfce7;color:#16a34a",
  missing: "background:#fee2e2;color:#dc2626",
  too_long: "background:#fef3c7;color:#d97706",
  too_short: "background:#fef3c7;color:#d97706",
};

function Badge({ val }: { val: string }) {
  const s = SEV[val] || "background:#f3f4f6;color:#374151";
  return <span style={{ padding: "2px 7px", borderRadius: 10, fontSize: 10, fontWeight: 600, display: "inline-block", ...(Object.fromEntries(s.split(";").map((x) => x.split(":")))) }}>{val}</span>;
}

function KpiCard({ label, value, color }: { label: string; value?: number; color?: string }) {
  return (
    <div style={{ background: "var(--gray-50,#f9fafb)", border: "1px solid var(--gray-200,#e5e7eb)", borderRadius: 8, padding: "12px 14px", textAlign: "center" }}>
      <div style={{ fontSize: 10, color: "var(--gray-500,#6b7280)", textTransform: "uppercase", letterSpacing: "0.8px", marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 800, color: color || "var(--gray-800,#1f2937)" }}>{value ?? "–"}</div>
    </div>
  );
}

export default function Step3Crawl({ auditId, initial, onUpdate }: Props) {
  const [data, setData] = useState<CrawlData>({ keywords_notes: "", notes: "", ...initial });
  const [loading, setLoading] = useState(false);
  const [notes, setNotes] = useState(initial?.notes ?? "");
  const [kw, setKw] = useState(initial?.keywords_notes ?? "");

  const handleUpload = async (file: File) => {
    setLoading(true);
    try {
      const result = await uploadScreamingFrogCsv(auditId, file);
      const merged = { ...result, keywords_notes: kw, notes } as CrawlData;
      setData(merged);
      onUpdate(merged);
    } finally {
      setLoading(false);
    }
  };

  const save = async () => {
    const merged = { ...data, keywords_notes: kw, notes };
    setData(merged);
    onUpdate(merged);
    await updateAuditStep(auditId, 3, merged).catch(() => {});
  };

  const s = data.summary;
  const issues = data.issues || [];

  return (
    <div>
      <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 4 }}>Background-Crawl (Screaming Frog)</h3>
      <p style={{ fontSize: 13, color: "var(--gray-500,#6b7280)", marginBottom: 16 }}>
        Exportiere in Screaming Frog unter <strong>Reports → All Pages</strong> und lade die CSV hoch.
      </p>

      {/* What we check info */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8, marginBottom: 20 }}>
        {[
          { icon: "🔴", label: "Status Codes", hint: "404-Fehler (Quick Wins)" },
          { icon: "📝", label: "Page Titles & Meta", hint: "Fehlend, zu lang, doppelt?" },
          { icon: "H1", label: "H1-Check", hint: "Genau eine H1 pro Seite?" },
          { icon: "🖼️", label: "Bilder", hint: ">100–200 KB? (für Lighthouse)" },
          { icon: "🔍", label: "Keywords", hint: "Analyse der Keywords" },
        ].map((item) => (
          <div key={item.label} style={{ background: "#f0f4ff", border: "1px solid #c7d2fe", borderRadius: 8, padding: "10px", textAlign: "center" }}>
            <div style={{ fontSize: 16, marginBottom: 4 }}>{item.icon}</div>
            <div style={{ fontSize: 11, fontWeight: 700, color: "#3730a3" }}>{item.label}</div>
            <div style={{ fontSize: 10, color: "#6366f1", marginTop: 2 }}>{item.hint}</div>
          </div>
        ))}
      </div>

      <CsvUploadZone
        label="Screaming Frog CSV hochladen (All Pages Export)"
        hint="Drag & Drop oder klicken · .csv"
        onFile={handleUpload}
        loading={loading}
        done={!!s}
      />

      {s && (
        <>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginTop: 24, marginBottom: 12 }}>Zusammenfassung</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10 }}>
            <KpiCard label="URLs gesamt" value={s.total_urls} />
            <KpiCard label="200 OK" value={s.ok_200} color="#16a34a" />
            <KpiCard label="3xx Weiterleit." value={s.redirects_3xx} color="#d97706" />
            <KpiCard label="4xx/5xx Fehler" value={(s.errors_4xx || 0) + (s.errors_5xx || 0)} color="#dc2626" />
            <KpiCard label="Fehlender Title" value={s.missing_title} />
            <KpiCard label="Title zu lang" value={s.title_too_long} />
            <KpiCard label="Fehlende Meta" value={s.missing_meta} />
            <KpiCard label="Fehlender H1" value={s.missing_h1} />
            <KpiCard label="Langsame Seiten (>2s)" value={s.slow_pages} color="#d97706" />
          </div>

          {issues.length > 0 && (
            <>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginTop: 22, marginBottom: 10 }}>Seiten mit Problemen ({issues.length})</h3>
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
                  <thead>
                    <tr style={{ background: "var(--gray-100,#f3f4f6)" }}>
                      {["URL", "Status", "Title", "H1", "Meta", "Ladezeit"].map((h) => (
                        <th key={h} style={{ padding: "7px 10px", textAlign: "left", fontWeight: 600 }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {issues.slice(0, 50).map((issue, i) => (
                      <tr key={i} style={{ borderBottom: "1px solid #f3f4f6" }}>
                        <td style={{ padding: "5px 10px", maxWidth: 260, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={issue.url}>
                          <span style={{ fontSize: 11, color: "#2563eb" }}>{issue.url}</span>
                        </td>
                        <td style={{ padding: "5px 10px" }}>
                          <span style={{ padding: "2px 7px", borderRadius: 10, fontSize: 10, fontWeight: 600, background: issue.status_code >= 400 ? "#fee2e2" : issue.status_code >= 300 ? "#fef3c7" : "#dcfce7", color: issue.status_code >= 400 ? "#dc2626" : issue.status_code >= 300 ? "#d97706" : "#16a34a" }}>{issue.status_code}</span>
                        </td>
                        <td style={{ padding: "5px 10px" }}><Badge val={issue.title_issue} /></td>
                        <td style={{ padding: "5px 10px" }}><Badge val={issue.h1_issue} /></td>
                        <td style={{ padding: "5px 10px" }}><Badge val={issue.meta_issue} /></td>
                        <td style={{ padding: "5px 10px", fontSize: 11, color: issue.response_time_ms > 2000 ? "#dc2626" : "#9ca3af" }}>
                          {issue.response_time_ms > 0 ? `${issue.response_time_ms}ms` : "–"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {issues.length > 50 && <div style={{ textAlign: "center", fontSize: 12, color: "#9ca3af", padding: 10 }}>… und {issues.length - 50} weitere</div>}
              </div>
            </>
          )}
        </>
      )}

      <label className="form-group" style={{ marginTop: 20 }}>
        <span>Keywords – Notizen & Erkenntnisse (Gewinnung von Neukunden)</span>
        <textarea className="form-input" rows={3} value={kw} onChange={(e) => setKw(e.target.value)} onBlur={save} placeholder="Relevante Keywords, Keyword-Gaps, Potenzial für Neukunden..." />
      </label>
      <label className="form-group">
        <span>Allgemeine Notizen / Bewertung</span>
        <textarea className="form-input" rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} onBlur={save} placeholder="Gesamtbewertung des Crawls, wichtige Auffälligkeiten..." />
      </label>
    </div>
  );
}
