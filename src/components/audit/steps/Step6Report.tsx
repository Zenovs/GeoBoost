import { useState, useEffect } from "react";
import type { AuditTheme } from "../../../api";
import { generateAuditHtml, generateAuditPdf, AUDIT_THEMES } from "../../../api";
import { invoke } from "@tauri-apps/api/core";

export interface ReportData {
  findings: string;
  recommendations: string;
  general_notes: string;
}

interface Props {
  auditId: number;
  pdfPath?: string;
  initial?: Partial<ReportData>;
  onChange: (data: ReportData) => void;
  onPdfGenerated: (path: string) => void;
}

const EMPTY: ReportData = { findings: "", recommendations: "", general_notes: "" };

export default function Step6Report({ auditId, pdfPath, initial, onChange, onPdfGenerated }: Props) {
  const [data, setData] = useState<ReportData>({ ...EMPTY, ...initial });
  const [theme, setTheme] = useState<AuditTheme>("light");
  const [generating, setGenerating] = useState(false);
  const [generatingPdf, setGeneratingPdf] = useState(false);
  const [pdfFilePath, setPdfFilePath] = useState<string>("");
  const [err, setErr] = useState("");

  useEffect(() => { onChange(data); }, [data]);
  const set = (k: keyof ReportData, v: string) => setData((d) => ({ ...d, [k]: v }));

  const handleGenerate = async () => {
    setGenerating(true);
    setErr("");
    try {
      const result = await generateAuditHtml(auditId, theme);
      onPdfGenerated(result.html_path);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Bericht-Generierung fehlgeschlagen.");
    } finally {
      setGenerating(false);
    }
  };

  const handleOpenHtml = () => {
    if (!pdfPath) return;
    invoke("open_pdf", { path: pdfPath }).catch(() => {
      window.open(`file://${pdfPath}`, "_blank");
    });
  };

  const handleGeneratePdf = async () => {
    setGeneratingPdf(true);
    setErr("");
    try {
      const result = await generateAuditPdf(auditId, theme);
      setPdfFilePath(result.pdf_path);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "PDF-Generierung fehlgeschlagen.");
    } finally {
      setGeneratingPdf(false);
    }
  };

  const handleOpenPdf = () => {
    if (!pdfFilePath) return;
    invoke("open_pdf", { path: pdfFilePath }).catch(() => {});
  };

  return (
    <div>
      <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 4 }}>Report / Website-Bericht Erstellen</h3>
      <p style={{ fontSize: 13, color: "var(--gray-500,#6b7280)", marginBottom: 24 }}>
        Abschliessende Notizen hinzufügen, Theme wählen und HTML-Bericht generieren.
      </p>

      <label className="form-group">
        <span>Wichtigste Erkenntnisse (für Report-Zusammenfassung)</span>
        <textarea className="form-input" rows={4} value={data.findings} onChange={(e) => set("findings", e.target.value)}
          placeholder="Zusammenfassung der wichtigsten Erkenntnisse aus allen Analyse-Schritten..." />
      </label>

      <label className="form-group" style={{ marginTop: 14 }}>
        <span>Empfehlungen (eine pro Zeile, erscheinen als nummerierte Liste im Bericht)</span>
        <textarea className="form-input" rows={5} value={data.recommendations} onChange={(e) => set("recommendations", e.target.value)}
          placeholder={"1. Title-Tags auf allen wichtigen Seiten optimieren\n2. Ladezeit Mobile verbessern – aktuell unter 50 Punkte\n3. Bilder auf WebP konvertieren"} />
      </label>

      <label className="form-group" style={{ marginTop: 14 }}>
        <span>Weitere Notizen / Nächste Schritte</span>
        <textarea className="form-input" rows={3} value={data.general_notes} onChange={(e) => set("general_notes", e.target.value)}
          placeholder="Offene Fragen, geplante Massnahmen, Zeitplan, Upsell-Hinweise..." />
      </label>

      {/* Theme Picker */}
      <div style={{ marginTop: 28 }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: "var(--gray-700,#374151)", marginBottom: 12 }}>Theme auswählen</div>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          {AUDIT_THEMES.map((t) => (
            <button key={t.id} type="button" onClick={() => setTheme(t.id)}
              style={{ background: t.bg, border: `2px solid ${theme === t.id ? t.accent : "transparent"}`, borderRadius: 10, padding: "10px 14px", cursor: "pointer", display: "flex", flexDirection: "column", alignItems: "flex-start", gap: 4, minWidth: 110,
                boxShadow: theme === t.id ? `0 0 0 3px ${t.accent}33` : "0 1px 4px rgba(0,0,0,0.12)", transition: "all 0.15s" }}>
              <div style={{ width: "100%", height: 6, borderRadius: 3, background: t.accent, marginBottom: 4 }} />
              <span style={{ fontSize: 13, fontWeight: 700, color: t.text }}>{t.label}</span>
              <span style={{ fontSize: 10, color: t.text, opacity: 0.65 }}>{t.preview}</span>
              {theme === t.id && <span style={{ fontSize: 10, color: t.accent, fontWeight: 700 }}>✓ Ausgewählt</span>}
            </button>
          ))}
        </div>
      </div>

      {/* HTML Report */}
      <div style={{ marginTop: 28, padding: "20px", background: "var(--bg-card,#f9fafb)", border: "1px solid var(--border,#e5e7eb)", borderRadius: 10 }}>
        <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 4 }}>Website-Bericht (HTML)</div>
        <div style={{ fontSize: 12, color: "var(--gray-500,#6b7280)", marginBottom: 14 }}>
          Interaktiver Bericht mit Theme-Wechsel und Grafiken – direkt im Browser öffnen oder dort als PDF speichern.
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
          <button type="button" onClick={handleGenerate} disabled={generating}
            style={{ background: generating ? "#9ca3af" : "#2563eb", color: "white", border: "none", borderRadius: 8, padding: "10px 22px", fontSize: 13, fontWeight: 700, cursor: generating ? "wait" : "pointer" }}>
            {generating ? "Erstellt..." : "HTML erstellen"}
          </button>
          {pdfPath && (
            <button type="button" onClick={handleOpenHtml}
              style={{ background: "#16a34a", color: "white", border: "none", borderRadius: 8, padding: "10px 20px", fontSize: 13, fontWeight: 700, cursor: "pointer" }}>
              Im Browser öffnen
            </button>
          )}
        </div>
        {pdfPath && (
          <div style={{ marginTop: 10, fontSize: 11, color: "var(--gray-500,#6b7280)" }}>
            Gespeichert: <code>{pdfPath}</code>
          </div>
        )}
      </div>

      {/* PDF Export */}
      <div style={{ marginTop: 12, padding: "20px", background: "var(--bg-card,#f9fafb)", border: "1px solid var(--border,#e5e7eb)", borderRadius: 10 }}>
        <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 4 }}>PDF-Export</div>
        <div style={{ fontSize: 12, color: "var(--gray-500,#6b7280)", marginBottom: 14 }}>
          Druckfertiges PDF mit dem gewählten Theme – ideal zum Versenden per E-Mail.
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
          <button type="button" onClick={handleGeneratePdf} disabled={generatingPdf}
            style={{ background: generatingPdf ? "#9ca3af" : "#7c3aed", color: "white", border: "none", borderRadius: 8, padding: "10px 22px", fontSize: 13, fontWeight: 700, cursor: generatingPdf ? "wait" : "pointer" }}>
            {generatingPdf ? "Erstellt..." : "PDF erstellen"}
          </button>
          {pdfFilePath && (
            <button type="button" onClick={handleOpenPdf}
              style={{ background: "#16a34a", color: "white", border: "none", borderRadius: 8, padding: "10px 20px", fontSize: 13, fontWeight: 700, cursor: "pointer" }}>
              PDF öffnen
            </button>
          )}
        </div>
        {pdfFilePath && (
          <div style={{ marginTop: 10, fontSize: 11, color: "var(--gray-500,#6b7280)" }}>
            Gespeichert: <code>{pdfFilePath}</code>
          </div>
        )}
      </div>

      {err && <div style={{ marginTop: 12, fontSize: 13, color: "#dc2626" }}>{err}</div>}
    </div>
  );
}
