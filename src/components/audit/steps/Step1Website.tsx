import { useState, useEffect } from "react";
import type { Step1Website, ChannelRow } from "../../../api";

interface Props {
  initial?: Partial<Step1Website>;
  onChange: (data: Step1Website) => void;
}

const EMPTY: Step1Website = {
  sessions_total: undefined,
  sessions_organic: undefined,
  sessions_paid: undefined,
  sessions_direct: undefined,
  sessions_social: undefined,
  new_users_total: undefined,
  bounce_rate: undefined,
  avg_session_duration: "",
  conversions_total: undefined,
  conversion_rate: undefined,
  channel_breakdown: [],
  device_breakdown: { desktop: undefined, mobile: undefined, tablet: undefined },
  notes: "",
};

function NumInput({ label, value, onChange, placeholder = "" }: { label: string; value?: number; onChange: (v?: number) => void; placeholder?: string }) {
  return (
    <label className="form-group">
      <span>{label}</span>
      <input
        className="form-input"
        type="number"
        min={0}
        value={value ?? ""}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value === "" ? undefined : Number(e.target.value))}
      />
    </label>
  );
}

export default function Step1Website({ initial, onChange }: Props) {
  const [data, setData] = useState<Step1Website>({ ...EMPTY, ...initial });
  const [channelRows, setChannelRows] = useState<ChannelRow[]>(
    initial?.channel_breakdown?.length ? initial.channel_breakdown : [
      { channel: "Organic Search", sessions: 0, pct: 0 },
      { channel: "Direct", sessions: 0, pct: 0 },
      { channel: "Paid Search", sessions: 0, pct: 0 },
      { channel: "Social", sessions: 0, pct: 0 },
      { channel: "Referral", sessions: 0, pct: 0 },
    ]
  );

  const set = <K extends keyof Step1Website>(k: K, v: Step1Website[K]) => setData((d) => ({ ...d, [k]: v }));

  useEffect(() => {
    onChange({ ...data, channel_breakdown: channelRows });
  }, [data, channelRows]);

  const setChannel = (i: number, field: keyof ChannelRow, val: string | number) => {
    setChannelRows((rows) => rows.map((r, idx) => idx === i ? { ...r, [field]: val } : r));
  };

  return (
    <div>
      <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 20 }}>Traffic-Übersicht (GA4)</h3>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
        <NumInput label="Sessions gesamt" value={data.sessions_total} onChange={(v) => set("sessions_total", v)} />
        <NumInput label="Neue Nutzer" value={data.new_users_total} onChange={(v) => set("new_users_total", v)} />
        <label className="form-group">
          <span>Ø Sitzungsdauer</span>
          <input className="form-input" value={data.avg_session_duration ?? ""} placeholder="z.B. 2:34" onChange={(e) => set("avg_session_duration", e.target.value)} />
        </label>
        <NumInput label="Absprungrate (%)" value={data.bounce_rate} onChange={(v) => set("bounce_rate", v)} placeholder="z.B. 42" />
        <NumInput label="Conversions gesamt" value={data.conversions_total} onChange={(v) => set("conversions_total", v)} />
        <NumInput label="Conversion-Rate (%)" value={data.conversion_rate} onChange={(v) => set("conversion_rate", v)} placeholder="z.B. 2.4" />
      </div>

      <h3 style={{ fontSize: 14, fontWeight: 600, marginTop: 24, marginBottom: 12 }}>Kanal-Aufschlüsselung</h3>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
        <thead>
          <tr style={{ background: "var(--gray-100,#f3f4f6)" }}>
            <th style={{ padding: "8px 10px", textAlign: "left", fontWeight: 600 }}>Kanal</th>
            <th style={{ padding: "8px 10px", textAlign: "left", fontWeight: 600 }}>Sessions</th>
            <th style={{ padding: "8px 10px", textAlign: "left", fontWeight: 600 }}>Anteil (%)</th>
          </tr>
        </thead>
        <tbody>
          {channelRows.map((row, i) => (
            <tr key={i} style={{ borderBottom: "1px solid var(--gray-200,#e5e7eb)" }}>
              <td style={{ padding: "6px 4px" }}>
                <input className="form-input" style={{ fontSize: 12 }} value={row.channel} onChange={(e) => setChannel(i, "channel", e.target.value)} />
              </td>
              <td style={{ padding: "6px 4px" }}>
                <input className="form-input" type="number" min={0} style={{ fontSize: 12 }} value={row.sessions || ""} onChange={(e) => setChannel(i, "sessions", Number(e.target.value))} />
              </td>
              <td style={{ padding: "6px 4px" }}>
                <input className="form-input" type="number" min={0} max={100} step={0.1} style={{ fontSize: 12 }} value={row.pct || ""} onChange={(e) => setChannel(i, "pct", Number(e.target.value))} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <button
        type="button"
        onClick={() => setChannelRows((r) => [...r, { channel: "", sessions: 0, pct: 0 }])}
        style={{ marginTop: 8, fontSize: 12, color: "var(--blue-600,#2563eb)", background: "none", border: "none", cursor: "pointer", padding: "4px 0" }}
      >
        + Zeile hinzufügen
      </button>

      <h3 style={{ fontSize: 14, fontWeight: 600, marginTop: 24, marginBottom: 12 }}>Geräte-Aufteilung (%)</h3>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
        <NumInput label="Desktop" value={data.device_breakdown?.desktop} onChange={(v) => set("device_breakdown", { ...data.device_breakdown, desktop: v })} />
        <NumInput label="Mobile" value={data.device_breakdown?.mobile} onChange={(v) => set("device_breakdown", { ...data.device_breakdown, mobile: v })} />
        <NumInput label="Tablet" value={data.device_breakdown?.tablet} onChange={(v) => set("device_breakdown", { ...data.device_breakdown, tablet: v })} />
      </div>

      <label className="form-group" style={{ marginTop: 20 }}>
        <span>Notizen / Auffälligkeiten</span>
        <textarea className="form-input" rows={3} value={data.notes ?? ""} onChange={(e) => set("notes", e.target.value)} placeholder="Besondere Beobachtungen zu Traffic, Trends, Anomalien..." />
      </label>
    </div>
  );
}
