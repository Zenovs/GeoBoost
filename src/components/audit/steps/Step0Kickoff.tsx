import { useState, useEffect } from "react";
import type { Step0Kickoff } from "../../../api";

interface Props {
  initial?: Partial<Step0Kickoff>;
  onChange: (data: Step0Kickoff) => void;
}

const today = new Date().toLocaleDateString("de-CH", { day: "2-digit", month: "2-digit", year: "numeric" });

const EMPTY: Step0Kickoff = {
  client_name: "",
  website_url: "",
  analysis_period: "",
  analysis_date: today,
  analyst_name: "",
  responsible_person: "",
  main_goals: "",
  notes: "",
};

export default function Step0Kickoff({ initial, onChange }: Props) {
  const [data, setData] = useState<Step0Kickoff>({ ...EMPTY, ...initial });

  useEffect(() => { onChange(data); }, [data]);

  const set = (k: keyof Step0Kickoff, v: string) => setData((d) => ({ ...d, [k]: v }));

  return (
    <div>
      <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 20, color: "var(--gray-800,#1f2937)" }}>
        Allgemeine Informationen
      </h3>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <label className="form-group">
          <span>Kundenname *</span>
          <input className="form-input" value={data.client_name} onChange={(e) => set("client_name", e.target.value)} placeholder="z.B. Musterfirma AG" />
        </label>
        <label className="form-group">
          <span>Website URL *</span>
          <input className="form-input" value={data.website_url} onChange={(e) => set("website_url", e.target.value)} placeholder="https://www.example.com" />
        </label>
        <label className="form-group">
          <span>Analysezeitraum</span>
          <input className="form-input" value={data.analysis_period} onChange={(e) => set("analysis_period", e.target.value)} placeholder="z.B. 01.01.2026 – 31.03.2026" />
        </label>
        <label className="form-group">
          <span>Analysedatum</span>
          <input className="form-input" value={data.analysis_date} onChange={(e) => set("analysis_date", e.target.value)} />
        </label>
        <label className="form-group">
          <span>Analyst (erstellt von)</span>
          <input className="form-input" value={data.analyst_name} onChange={(e) => set("analyst_name", e.target.value)} placeholder="Dein Name" />
        </label>
        <label className="form-group">
          <span>Ansprechpartner Kunde</span>
          <input className="form-input" value={data.responsible_person} onChange={(e) => set("responsible_person", e.target.value)} placeholder="Name beim Kunden" />
        </label>
      </div>
      <label className="form-group" style={{ marginTop: 16 }}>
        <span>Hauptziele / Fokus der Analyse</span>
        <textarea className="form-input" rows={3} value={data.main_goals} onChange={(e) => set("main_goals", e.target.value)} placeholder="Was soll die Analyse hauptsächlich aufzeigen? Welche Fragen sollen beantwortet werden?" />
      </label>
      <label className="form-group" style={{ marginTop: 12 }}>
        <span>Notizen / Hintergrundinformationen</span>
        <textarea className="form-input" rows={3} value={data.notes} onChange={(e) => set("notes", e.target.value)} placeholder="Bekannte Probleme, aktuelle Kampagnen, besondere Hinweise..." />
      </label>
    </div>
  );
}
