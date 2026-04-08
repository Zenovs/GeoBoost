import { useState } from "react";
import type { Step3Semrush, SemrushIssue } from "../../../api";
import CsvUploadZone from "../CsvUploadZone";
import { uploadSemrushCsv, updateAuditStep } from "../../../api";

interface Props {
  auditId: number;
  initial?: Partial<Step3Semrush>;
  onUpdate: (data: Step3Semrush) => void;
}

const SEV_STYLE: Record<string, { bg: string; color: string; label: string }> = {
  error:   { bg: "#fee2e2", color: "#dc2626", label: "Fehler" },
  warning: { bg: "#fef3c7", color: "#d97706", label: "Warnung" },
  notice:  { bg: "#ede9fe", color: "#7c3aed", label: "Hinweis" },
};

function SevBadge({ sev }: { sev: string }) {
  const s = SEV_STYLE[sev] || { bg: "#f3f4f6", color: "#374151", label: sev };
  return (
    <span style={{ padding: "2px 9px", borderRadius: 10, fontSize: 10, fontWeight: 700, background: s.bg, color: s.color }}>
      {s.label.toUpperCase()}
    </span>
  );
}

export default function Step3Semrush({ auditId, initial, onUpdate }: Props) {
  const [data, setData] = useState<Step3Semrush>(initial || {});
  const [loading, setLoading] = useState(false);
  const [notes, setNotes] = useState(initial?.notes ?? "");

  const handleUpload = async (file: File) => {
    setLoading(true);
    try {
      const result = await uploadSemrushCsv(auditId, file);
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
    await updateAuditStep(auditId, 3, merged).catch(() => {});
  };

  const summary = data.summary;
  const issues: SemrushIssue[] = data.issues || [];

  return (
    <div>
      <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 8 }}>SemRush – Site Audit</h3>
      <p style={{ fontSize: 13, color: "var(--gray-500,#6b7280)", marginBottom: 20 }}>
        Exportiere in SemRush unter <strong>Site Audit → Issues → Export CSV</strong> und lade die Datei hier hoch.
      </p>

      <CsvUploadZone
        label="SemRush CSV hochladen"
        hint="Datei per Drag & Drop oder Klick auswählen · Nur .csv Dateien"
        onFile={handleUpload}
        loading={loading}
        done={!!summary}
      />

      {summary && (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginTop: 24 }}>
            <div style={{ background: "#fee2e2", border: "1px solid #fecaca", borderRadius: 10, padding: "14px 16px", textAlign: "center" }}>
              <div style={{ fontSize: 10, color: "#dc2626", textTransform: "uppercase", letterSpacing: "0.8px", marginBottom: 4 }}>Fehler</div>
              <div style={{ fontSize: 28, fontWeight: 800, color: "#dc2626" }}>{summary.errors}</div>
            </div>
            <div style={{ background: "#fef3c7", border: "1px solid #fde68a", borderRadius: 10, padding: "14px 16px", textAlign: "center" }}>
              <div style={{ fontSize: 10, color: "#d97706", textTransform: "uppercase", letterSpacing: "0.8px", marginBottom: 4 }}>Warnungen</div>
              <div style={{ fontSize: 28, fontWeight: 800, color: "#d97706" }}>{summary.warnings}</div>
            </div>
            <div style={{ background: "#ede9fe", border: "1px solid #ddd6fe", borderRadius: 10, padding: "14px 16px", textAlign: "center" }}>
              <div style={{ fontSize: 10, color: "#7c3aed", textTransform: "uppercase", letterSpacing: "0.8px", marginBottom: 4 }}>Hinweise</div>
              <div style={{ fontSize: 28, fontWeight: 800, color: "#7c3aed" }}>{summary.notices}</div>
            </div>
          </div>

          {issues.length > 0 && (
            <>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginTop: 24, marginBottom: 12 }}>
                Gefundene Probleme ({issues.length})
              </h3>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {issues.map((issue, i) => (
                  <div key={i} style={{
                    background: "white",
                    border: "1px solid var(--gray-200,#e5e7eb)",
                    borderLeft: `4px solid ${SEV_STYLE[issue.severity]?.color || "#e5e7eb"}`,
                    borderRadius: 8,
                    padding: "10px 14px",
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                  }}>
                    <SevBadge sev={issue.severity} />
                    <div style={{ flex: 1, fontSize: 13, fontWeight: 500 }}>{issue.issue}</div>
                    {issue.category && (
                      <span style={{ fontSize: 11, color: "var(--gray-400,#9ca3af)", flexShrink: 0 }}>{issue.category}</span>
                    )}
                    <span style={{ fontSize: 12, fontWeight: 700, color: "var(--gray-600,#4b5563)", flexShrink: 0 }}>
                      {issue.count} URL{issue.count !== 1 ? "s" : ""}
                    </span>
                  </div>
                ))}
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
          placeholder="Eigene Bewertung der SemRush-Ergebnisse..."
        />
      </label>
    </div>
  );
}
