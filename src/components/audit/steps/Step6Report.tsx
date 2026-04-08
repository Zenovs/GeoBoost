import { useState, useEffect } from "react";
import type { AuditTheme } from "../../../api";
import { generateAuditHtml, AUDIT_THEMES } from "../../../api";
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

      <div style={{ marginTop: 24, display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <button type="button" onClick={handleGenerate} disabled={generating}
          style={{ background: generating ? "#9ca3af" : "#2563eb", color: "white", border: "none", borderRadius: 8, padding: "12px 28px", fontSize: 14, fontWeight: 700, cursor: generating ? "wait" : "pointer" }}>
          {generating ? "⏳ Bericht wird erstellt..." : "🌐 Website-Bericht erstellen"}
        </button>
        {pdfPath && (
          <button type="button" onClick={handleOpenHtml}
            style={{ background: "#16a34a", color: "white", border: "none", borderRadius: 8, padding: "12px 24px", fontSize: 14, fontWeight: 700, cursor: "pointer" }}>
            🌐 Im Browser öffnen
          </button>
        )}
        {err && <span style={{ fontSize: 13, color: "#dc2626" }}>{err}</span>}
      </div>

      {pdfPath && (
        <div style={{ marginTop: 14, padding: "12px 16px", background: "#dcfce7", borderRadius: 8, fontSize: 13, color: "#15803d" }}>
          Bericht gespeichert: <code style={{ fontSize: 11 }}>{pdfPath}</code>
        </div>
      )}
    </div>
  );
}
