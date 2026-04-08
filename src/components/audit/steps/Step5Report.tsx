import { useState, useEffect } from "react";
import type { Step5Notes, AuditTheme } from "../../../api";
import { generateAuditPdf, getAuditPdfUrl, AUDIT_THEMES } from "../../../api";
import { invoke } from "@tauri-apps/api/core";

interface Props {
  auditId: number;
  pdfPath?: string;
  initial?: Partial<Step5Notes>;
  onChange: (data: Step5Notes) => void;
  onPdfGenerated: (path: string) => void;
}

const EMPTY: Step5Notes = {
  findings: "",
  recommendations: "",
  general_notes: "",
};

export default function Step5Report({ auditId, pdfPath, initial, onChange, onPdfGenerated }: Props) {
  const [data, setData] = useState<Step5Notes>({ ...EMPTY, ...initial });
  const [theme, setTheme] = useState<AuditTheme>("light");
  const [generating, setGenerating] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => { onChange(data); }, [data]);

  const set = (k: keyof Step5Notes, v: string) => setData((d) => ({ ...d, [k]: v }));

  const handleGenerate = async () => {
    setGenerating(true);
    setErr("");
    try {
      const result = await generateAuditPdf(auditId, theme);
      onPdfGenerated(result.pdf_path);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "PDF-Generierung fehlgeschlagen.");
    } finally {
      setGenerating(false);
    }
  };

  const handleOpenPdf = () => {
    if (!pdfPath) return;
    invoke("open_pdf", { path: pdfPath }).catch(() => {
      window.open(getAuditPdfUrl(auditId), "_blank");
    });
  };

  return (
    <div>
      <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 8 }}>Fazit &amp; Bericht generieren</h3>
      <p style={{ fontSize: 13, color: "var(--gray-500,#6b7280)", marginBottom: 24 }}>
        Füge deine Schlussfolgerungen und Empfehlungen hinzu, wähle ein Theme und generiere den PDF-Bericht.
      </p>

      <label className="form-group">
        <span>Wichtigste Erkenntnisse</span>
        <textarea
          className="form-input"
          rows={5}
          value={data.findings}
          onChange={(e) => set("findings", e.target.value)}
          placeholder="Zusammenfassung der wichtigsten Erkenntnisse aus der Analyse. Was sind die grössten Probleme? Was läuft gut?"
        />
      </label>

      <label className="form-group" style={{ marginTop: 16 }}>
        <span>Empfehlungen (eine pro Zeile)</span>
        <textarea
          className="form-input"
          rows={6}
          value={data.recommendations}
          onChange={(e) => set("recommendations", e.target.value)}
          placeholder={"1. Title-Tags auf allen wichtigen Seiten optimieren\n2. Ladezeit auf Mobile verbessern – PageSpeed unter 50 Punkte\n3. Fehlende Meta-Descriptions ergänzen"}
        />
        <span style={{ fontSize: 11, color: "var(--gray-400,#9ca3af)", marginTop: 4 }}>
          Jede Zeile wird als separate Empfehlung im PDF dargestellt.
        </span>
      </label>

      <label className="form-group" style={{ marginTop: 16 }}>
        <span>Weitere Notizen / Nächste Schritte</span>
        <textarea
          className="form-input"
          rows={4}
          value={data.general_notes}
          onChange={(e) => set("general_notes", e.target.value)}
          placeholder="Offene Fragen, geplante Massnahmen, Zeitplan..."
        />
      </label>

      {/* ── Theme Picker ── */}
      <div style={{ marginTop: 28 }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: "var(--gray-700,#374151)", marginBottom: 12 }}>
          Theme auswählen
        </div>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          {AUDIT_THEMES.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setTheme(t.id)}
              style={{
                background: t.bg,
                border: `2px solid ${theme === t.id ? t.accent : "transparent"}`,
                borderRadius: 10,
                padding: "10px 14px",
                cursor: "pointer",
                display: "flex",
                flexDirection: "column",
                alignItems: "flex-start",
                gap: 4,
                minWidth: 110,
                outline: theme === t.id ? `3px solid ${t.accent}44` : "none",
                transition: "all 0.15s",
                boxShadow: theme === t.id ? `0 0 0 3px ${t.accent}33` : "0 1px 4px rgba(0,0,0,0.12)",
              }}
            >
              {/* Mini preview bar */}
              <div style={{ width: "100%", height: 6, borderRadius: 3, background: t.accent, marginBottom: 4 }} />
              <span style={{ fontSize: 13, fontWeight: 700, color: t.text }}>{t.label}</span>
              <span style={{ fontSize: 10, color: t.text, opacity: 0.65 }}>{t.preview}</span>
              {theme === t.id && (
                <span style={{ fontSize: 10, color: t.accent, fontWeight: 700, marginTop: 2 }}>✓ Ausgewählt</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* ── Generate button ── */}
      <div style={{ marginTop: 24, display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <button
          type="button"
          onClick={handleGenerate}
          disabled={generating}
          style={{
            background: generating ? "var(--gray-400,#9ca3af)" : "var(--blue-600,#2563eb)",
            color: "white",
            border: "none",
            borderRadius: 8,
            padding: "12px 28px",
            fontSize: 14,
            fontWeight: 700,
            cursor: generating ? "wait" : "pointer",
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          {generating ? "⏳ PDF wird erstellt..." : "📄 PDF-Bericht erstellen"}
        </button>

        {pdfPath && (
          <button
            type="button"
            onClick={handleOpenPdf}
            style={{
              background: "#16a34a",
              color: "white",
              border: "none",
              borderRadius: 8,
              padding: "12px 24px",
              fontSize: 14,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            ✅ PDF öffnen
          </button>
        )}

        {err && <span style={{ fontSize: 13, color: "#dc2626" }}>{err}</span>}
      </div>

      {pdfPath && (
        <div style={{ marginTop: 16, padding: "12px 16px", background: "#dcfce7", borderRadius: 8, fontSize: 13, color: "#15803d" }}>
          Bericht erfolgreich erstellt. Gespeichert unter: <code style={{ fontSize: 11 }}>{pdfPath}</code>
        </div>
      )}
    </div>
  );
}
