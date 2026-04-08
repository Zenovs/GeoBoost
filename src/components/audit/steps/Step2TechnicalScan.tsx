import { useState, useEffect } from "react";

export interface TechnicalScanData {
  performance_notes: string;
  measures_notes: string;
  report_analysis_notes: string;
}

interface Props {
  initial?: Partial<TechnicalScanData>;
  onChange: (data: TechnicalScanData) => void;
}

const EMPTY: TechnicalScanData = {
  performance_notes: "",
  measures_notes: "",
  report_analysis_notes: "",
};

export default function Step2TechnicalScan({ initial, onChange }: Props) {
  const [data, setData] = useState<TechnicalScanData>({ ...EMPTY, ...initial });
  useEffect(() => { onChange(data); }, [data]);
  const set = (k: keyof TechnicalScanData, v: string) => setData((d) => ({ ...d, [k]: v }));

  return (
    <div>
      <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 4 }}>Technischer Scan & Performance-Analyse</h3>
      <p style={{ fontSize: 13, color: "var(--gray-500,#6b7280)", marginBottom: 24 }}>
        Massnahmen definieren, Berichte analysieren
      </p>

      <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
        <div style={{ background: "var(--gray-50,#f9fafb)", border: "1px solid var(--gray-200,#e5e7eb)", borderRadius: 10, padding: 18 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <span style={{ fontSize: 20 }}>⚡</span>
            <span style={{ fontWeight: 700, fontSize: 14 }}>Performance-Analyse</span>
          </div>
          <p style={{ fontSize: 12, color: "var(--gray-400,#9ca3af)", marginBottom: 10 }}>
            Ladezeiten, Core Web Vitals Überblick, Mobile-Optimierung, Server-Antwortzeiten
          </p>
          <textarea className="form-input" rows={4} value={data.performance_notes} onChange={(e) => set("performance_notes", e.target.value)} placeholder="Performance-Erkenntnisse, erste Beobachtungen zu Ladezeiten, auffällige Mängel..." />
        </div>

        <div style={{ background: "var(--gray-50,#f9fafb)", border: "1px solid var(--gray-200,#e5e7eb)", borderRadius: 10, padding: 18 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <span style={{ fontSize: 20 }}>✅</span>
            <span style={{ fontWeight: 700, fontSize: 14 }}>Massnahmen definieren</span>
          </div>
          <p style={{ fontSize: 12, color: "var(--gray-400,#9ca3af)", marginBottom: 10 }}>
            Welche technischen Massnahmen sind prioritär? Was kann sofort umgesetzt werden?
          </p>
          <textarea className="form-input" rows={4} value={data.measures_notes} onChange={(e) => set("measures_notes", e.target.value)} placeholder="Quick Wins, priorisierte Massnahmen, geschätzter Aufwand..." />
        </div>

        <div style={{ background: "var(--gray-50,#f9fafb)", border: "1px solid var(--gray-200,#e5e7eb)", borderRadius: 10, padding: 18 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <span style={{ fontSize: 20 }}>📊</span>
            <span style={{ fontWeight: 700, fontSize: 14 }}>Analysieren der Berichte</span>
          </div>
          <p style={{ fontSize: 12, color: "var(--gray-400,#9ca3af)", marginBottom: 10 }}>
            GA4, Search Console, sonstige Monitoring-Daten – Erkenntnisse aus den vorhandenen Berichten
          </p>
          <textarea className="form-input" rows={4} value={data.report_analysis_notes} onChange={(e) => set("report_analysis_notes", e.target.value)} placeholder="Erkenntnisse aus GA4, Search Console, Rankings..." />
        </div>
      </div>
    </div>
  );
}
