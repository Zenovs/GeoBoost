import { useState, useEffect } from "react";

export interface WebsiteKundenData {
  ui_ux_notes: string;
  backlinks_notes: string;
  social_media_notes: string;
  news_blog_partner_notes: string;
  language_check_notes: string;
  faq_check_notes: string;
  general_notes: string;
}

interface Props {
  initial?: Partial<WebsiteKundenData>;
  onChange: (data: WebsiteKundenData) => void;
}

const EMPTY: WebsiteKundenData = {
  ui_ux_notes: "", backlinks_notes: "", social_media_notes: "",
  news_blog_partner_notes: "", language_check_notes: "", faq_check_notes: "", general_notes: "",
};

function NoteCard({ icon, title, hint, value, onChange }: { icon: string; title: string; hint: string; value: string; onChange: (v: string) => void }) {
  return (
    <div style={{ background: "var(--gray-50,#f9fafb)", border: "1px solid var(--gray-200,#e5e7eb)", borderRadius: 10, padding: "16px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <span style={{ fontSize: 18 }}>{icon}</span>
        <span style={{ fontWeight: 700, fontSize: 13, color: "var(--gray-800,#1f2937)" }}>{title}</span>
      </div>
      <p style={{ fontSize: 11, color: "var(--gray-400,#9ca3af)", marginBottom: 8 }}>{hint}</p>
      <textarea
        className="form-input"
        rows={3}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Beobachtungen und Erkenntnisse..."
        style={{ fontSize: 12 }}
      />
    </div>
  );
}

export default function Step1Website({ initial, onChange }: Props) {
  const [data, setData] = useState<WebsiteKundenData>({ ...EMPTY, ...initial });
  useEffect(() => { onChange(data); }, [data]);
  const set = (k: keyof WebsiteKundenData, v: string) => setData((d) => ({ ...d, [k]: v }));

  return (
    <div>
      <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 4 }}>Website & Kunden analysieren / kennenlernen</h3>
      <p style={{ fontSize: 13, color: "var(--gray-500,#6b7280)", marginBottom: 20 }}>
        Klare Bedingungen und Einsicht in den Kunden und sein Produkt gewinnen
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        <NoteCard
          icon="🖥️" title="UI / UX Analyse"
          hint="Optimierung der Nutzersignale – Wie benutzerfreundlich ist die Website? Navigation, CTAs, Conversion-Pfade"
          value={data.ui_ux_notes} onChange={(v) => set("ui_ux_notes", v)}
        />
        <NoteCard
          icon="🔗" title="Backlinks"
          hint="Qualität und Quantität der eingehenden Links – Welche Seiten verlinken? Authority, Relevanz"
          value={data.backlinks_notes} onChange={(v) => set("backlinks_notes", v)}
        />
        <NoteCard
          icon="📱" title="Social Media"
          hint="Präsenz und Aktivität auf Social-Media-Kanälen – Facebook, Instagram, LinkedIn etc."
          value={data.social_media_notes} onChange={(v) => set("social_media_notes", v)}
        />
        <NoteCard
          icon="📰" title="News / Blog / Partner"
          hint="Aktualität des Blogs, News-Bereich und Partnerverweise – Wird regelmässig publiziert?"
          value={data.news_blog_partner_notes} onChange={(v) => set("news_blog_partner_notes", v)}
        />
        <NoteCard
          icon="🔤" title="Sprach Check"
          hint="Rechtschreibung, Grammatik, Tonalität – Ist die Sprache korrekt und zur Zielgruppe passend?"
          value={data.language_check_notes} onChange={(v) => set("language_check_notes", v)}
        />
        <NoteCard
          icon="❓" title="FAQ Check"
          hint="Gibt es einen FAQ-Bereich? Werden häufige Fragen abgedeckt? Potenzial für Featured Snippets?"
          value={data.faq_check_notes} onChange={(v) => set("faq_check_notes", v)}
        />
      </div>

      <label className="form-group" style={{ marginTop: 16 }}>
        <span>Allgemeine Notizen / Gesamteindruck</span>
        <textarea className="form-input" rows={3} value={data.general_notes} onChange={(e) => set("general_notes", e.target.value)} placeholder="Gesamteindruck der Website, auffällige Stärken oder Schwächen..." />
      </label>
    </div>
  );
}
