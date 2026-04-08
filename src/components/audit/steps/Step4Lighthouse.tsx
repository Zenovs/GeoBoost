import { useState, useEffect } from "react";
import type { Step4Lighthouse } from "../../../api";
import { fetchLighthouseForAudit } from "../../../api";

interface Props {
  auditId: number;
  websiteUrl?: string;
  initial?: Partial<Step4Lighthouse>;
  onChange: (data: Step4Lighthouse) => void;
}

const EMPTY: Step4Lighthouse = {
  mobile_performance: undefined,
  mobile_accessibility: undefined,
  mobile_best_practices: undefined,
  mobile_seo: undefined,
  desktop_performance: undefined,
  desktop_accessibility: undefined,
  desktop_best_practices: undefined,
  desktop_seo: undefined,
  cwv_lcp: "",
  cwv_fid: "",
  cwv_cls: "",
  notes: "",
};

function ScoreInput({ label, value, onChange }: { label: string; value?: number; onChange: (v?: number) => void }) {
  const color = value === undefined ? "var(--gray-300)" : value >= 90 ? "#16a34a" : value >= 50 ? "#d97706" : "#dc2626";
  return (
    <label className="form-group">
      <span>{label}</span>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <input
          className="form-input"
          type="number"
          min={0}
          max={100}
          value={value ?? ""}
          placeholder="0–100"
          onChange={(e) => onChange(e.target.value === "" ? undefined : Number(e.target.value))}
          style={{ flex: 1 }}
        />
        {value !== undefined && (
          <div style={{
            width: 36,
            height: 36,
            borderRadius: "50%",
            background: color,
            color: "white",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontWeight: 800,
            fontSize: 12,
            flexShrink: 0,
          }}>
            {value}
          </div>
        )}
      </div>
    </label>
  );
}

export default function Step4Lighthouse({ auditId, websiteUrl, initial, onChange }: Props) {
  const [data, setData] = useState<Step4Lighthouse>({ ...EMPTY, ...initial });
  const [fetching, setFetching] = useState(false);
  const [fetchErr, setFetchErr] = useState("");

  useEffect(() => { onChange(data); }, [data]);

  const set = <K extends keyof Step4Lighthouse>(k: K, v: Step4Lighthouse[K]) =>
    setData((d) => ({ ...d, [k]: v }));

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
      <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 8 }}>PageSpeed / Lighthouse Scores</h3>
      <p style={{ fontSize: 13, color: "var(--gray-500,#6b7280)", marginBottom: 16 }}>
        Werte können automatisch via Google PageSpeed API abgerufen oder manuell eingetragen werden.
      </p>

      {websiteUrl && (
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
          <button
            type="button"
            onClick={handleFetch}
            disabled={fetching}
            style={{
              background: "var(--blue-600,#2563eb)",
              color: "white",
              border: "none",
              borderRadius: 8,
              padding: "10px 20px",
              fontSize: 13,
              fontWeight: 600,
              cursor: fetching ? "wait" : "pointer",
              opacity: fetching ? 0.7 : 1,
            }}
          >
            {fetching ? "⏳ Wird abgerufen..." : "🚀 Via PageSpeed API abrufen"}
          </button>
          <span style={{ fontSize: 12, color: "var(--gray-400,#9ca3af)" }}>für {websiteUrl}</span>
          {fetchErr && <span style={{ fontSize: 12, color: "#dc2626" }}>{fetchErr}</span>}
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
        <div>
          <h4 style={{ fontSize: 13, fontWeight: 700, marginBottom: 12, color: "var(--gray-600,#4b5563)" }}>📱 Mobile</h4>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <ScoreInput label="Performance" value={data.mobile_performance} onChange={(v) => set("mobile_performance", v)} />
            <ScoreInput label="SEO" value={data.mobile_seo} onChange={(v) => set("mobile_seo", v)} />
            <ScoreInput label="Barrierefreiheit" value={data.mobile_accessibility} onChange={(v) => set("mobile_accessibility", v)} />
            <ScoreInput label="Best Practices" value={data.mobile_best_practices} onChange={(v) => set("mobile_best_practices", v)} />
          </div>
        </div>
        <div>
          <h4 style={{ fontSize: 13, fontWeight: 700, marginBottom: 12, color: "var(--gray-600,#4b5563)" }}>🖥️ Desktop</h4>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <ScoreInput label="Performance" value={data.desktop_performance} onChange={(v) => set("desktop_performance", v)} />
            <ScoreInput label="SEO" value={data.desktop_seo} onChange={(v) => set("desktop_seo", v)} />
            <ScoreInput label="Barrierefreiheit" value={data.desktop_accessibility} onChange={(v) => set("desktop_accessibility", v)} />
            <ScoreInput label="Best Practices" value={data.desktop_best_practices} onChange={(v) => set("desktop_best_practices", v)} />
          </div>
        </div>
      </div>

      <h3 style={{ fontSize: 14, fontWeight: 600, marginTop: 24, marginBottom: 12 }}>Core Web Vitals</h3>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
        <label className="form-group">
          <span>LCP (Largest Contentful Paint)</span>
          <input className="form-input" value={data.cwv_lcp ?? ""} placeholder="z.B. 2.1 s" onChange={(e) => set("cwv_lcp", e.target.value)} />
        </label>
        <label className="form-group">
          <span>INP / FID (Interaktivität)</span>
          <input className="form-input" value={data.cwv_fid ?? ""} placeholder="z.B. 120 ms" onChange={(e) => set("cwv_fid", e.target.value)} />
        </label>
        <label className="form-group">
          <span>CLS (Layout Shift)</span>
          <input className="form-input" value={data.cwv_cls ?? ""} placeholder="z.B. 0.05" onChange={(e) => set("cwv_cls", e.target.value)} />
        </label>
      </div>

      <label className="form-group" style={{ marginTop: 16 }}>
        <span>Notizen / Bewertung</span>
        <textarea className="form-input" rows={3} value={data.notes ?? ""} onChange={(e) => set("notes", e.target.value)} placeholder="Besondere Erkenntnisse zur Performance, Optimierungspotenzial..." />
      </label>
    </div>
  );
}
