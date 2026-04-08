import { useState } from "react";
import type { Step2Crawl, CrawlSummary, CrawlIssue } from "../../../api";
import CsvUploadZone from "../CsvUploadZone";
import { uploadScreamingFrogCsv, updateAuditStep } from "../../../api";

interface Props {
  auditId: number;
  initial?: Partial<Step2Crawl>;
  onUpdate: (data: Step2Crawl) => void;
}

function KpiCard({ label, value, color }: { label: string; value?: number; color?: string }) {
  return (
    <div style={{ background: "var(--gray-50,#f9fafb)", border: "1px solid var(--gray-200,#e5e7eb)", borderRadius: 8, padding: "12px 14px", textAlign: "center" }}>
      <div style={{ fontSize: 10, color: "var(--gray-500,#6b7280)", textTransform: "uppercase", letterSpacing: "0.8px", marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 800, color: color || "var(--gray-800,#1f2937)" }}>{value ?? "–"}</div>
    </div>
  );
}

const SEV_BADGE: Record<string, string> = {
  ok: "background:#dcfce7;color:#16a34a",
  missing: "background:#fee2e2;color:#dc2626",
  too_long: "background:#fef3c7;color:#d97706",
  too_short: "background:#fef3c7;color:#d97706",
};

function IssueBadge({ val }: { val: string }) {
  return (
    <span style={{ padding: "2px 8px", borderRadius: 10, fontSize: 10, fontWeight: 600, display: "inline-block", ...(Object.fromEntries((SEV_BADGE[val] || "background:#f3f4f6;color:#374151").split(";").map((s) => s.split(":")))) }}>
      {val}
    </span>
  );
}

export default function Step2Crawl({ auditId, initial, onUpdate }: Props) {
  const [data, setData] = useState<Step2Crawl>(initial || {});
  const [loading, setLoading] = useState(false);
  const [notes, setNotes] = useState(initial?.notes ?? "");

  const handleUpload = async (file: File) => {
    setLoading(true);
    try {
      const result = await uploadScreamingFrogCsv(auditId, file);
      const merged = { ...result, notes };
      setData(merged);
      onUpdate(merged);
    } finally {
      setLoading(false);
    }
  };

  const handleNotesBlur = async () => {
    const merged = { ...data, notes };
    setData(merged);
    onUpdate(merged);
    await updateAuditStep(auditId, 2, merged).catch(() => {});
  };

  const summary: CrawlSummary | undefined = data.summary;
  const issues: CrawlIssue[] = data.issues || [];

  return (
    <div>
      <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 8 }}>Screaming Frog – Crawl-Analyse</h3>
      <p style={{ fontSize: 13, color: "var(--gray-500,#6b7280)", marginBottom: 20 }}>
        Exportiere in Screaming Frog unter <strong>Reports → All Pages</strong> und lade die CSV hier hoch.
      </p>

      <CsvUploadZone
        label="Screaming Frog CSV hochladen"
        hint="Datei per Drag & Drop oder Klick auswählen · Nur .csv Dateien"
        onFile={handleUpload}
        loading={loading}
        done={!!summary}
      />

      {summary && (
        <>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginTop: 24, marginBottom: 12 }}>Zusammenfassung</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10 }}>
            <KpiCard label="URLs gesamt" value={summary.total_urls} />
            <KpiCard label="200 OK" value={summary.ok_200} color="#16a34a" />
            <KpiCard label="3xx Weiterleit." value={summary.redirects_3xx} color="#d97706" />
            <KpiCard label="4xx/5xx Fehler" value={(summary.errors_4xx || 0) + (summary.errors_5xx || 0)} color="#dc2626" />
            <KpiCard label="Fehlender Title" value={summary.missing_title} />
            <KpiCard label="Title zu lang" value={summary.title_too_long} />
            <KpiCard label="Fehlende Meta Desc." value={summary.missing_meta} />
            <KpiCard label="Fehlender H1" value={summary.missing_h1} />
            <KpiCard label="Langsame Seiten" value={summary.slow_pages} color="#d97706" />
          </div>

          {issues.length > 0 && (
            <>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginTop: 24, marginBottom: 12 }}>
                Seiten mit Problemen ({issues.length})
              </h3>
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
                  <thead>
                    <tr style={{ background: "var(--gray-100,#f3f4f6)" }}>
                      <th style={{ padding: "8px 10px", textAlign: "left" }}>URL</th>
                      <th style={{ padding: "8px 10px" }}>Status</th>
                      <th style={{ padding: "8px 10px" }}>Title</th>
                      <th style={{ padding: "8px 10px" }}>H1</th>
                      <th style={{ padding: "8px 10px" }}>Meta</th>
                      <th style={{ padding: "8px 10px" }}>Ladezeit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {issues.slice(0, 50).map((issue, i) => (
                      <tr key={i} style={{ borderBottom: "1px solid var(--gray-100,#f3f4f6)" }}>
                        <td style={{ padding: "6px 10px", maxWidth: 260, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }} title={issue.url}>
                          <span style={{ fontSize: 11, color: "var(--blue-600,#2563eb)" }}>{issue.url}</span>
                        </td>
                        <td style={{ padding: "6px 10px", textAlign: "center" }}>
                          <span style={{ padding: "2px 7px", borderRadius: 10, fontSize: 10, fontWeight: 600, background: issue.status_code >= 400 ? "#fee2e2" : issue.status_code >= 300 ? "#fef3c7" : "#dcfce7", color: issue.status_code >= 400 ? "#dc2626" : issue.status_code >= 300 ? "#d97706" : "#16a34a" }}>
                            {issue.status_code}
                          </span>
                        </td>
                        <td style={{ padding: "6px 10px", textAlign: "center" }}><IssueBadge val={issue.title_issue} /></td>
                        <td style={{ padding: "6px 10px", textAlign: "center" }}><IssueBadge val={issue.h1_issue} /></td>
                        <td style={{ padding: "6px 10px", textAlign: "center" }}><IssueBadge val={issue.meta_issue} /></td>
                        <td style={{ padding: "6px 10px", textAlign: "center", fontSize: 11, color: issue.response_time_ms > 2000 ? "#dc2626" : "var(--gray-500,#6b7280)" }}>
                          {issue.response_time_ms > 0 ? `${issue.response_time_ms}ms` : "–"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {issues.length > 50 && (
                  <div style={{ textAlign: "center", fontSize: 12, color: "var(--gray-400,#9ca3af)", padding: 10 }}>
                    … und {issues.length - 50} weitere Seiten
                  </div>
                )}
              </div>
            </>
          )}
        </>
      )}

      <label className="form-group" style={{ marginTop: 20 }}>
        <span>Notizen / Bewertung</span>
        <textarea
          className="form-input"
          rows={3}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          onBlur={handleNotesBlur}
          placeholder="Eigene Bewertung der Crawl-Ergebnisse, wichtige Auffälligkeiten..."
        />
      </label>
    </div>
  );
}
