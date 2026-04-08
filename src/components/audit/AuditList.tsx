import { useState, useEffect } from "react";
import type { AuditSummary } from "../../api";
import { listAudits, createAudit, deleteAudit } from "../../api";

interface Props {
  onOpen: (id: number) => void;
}

const STATUS_LABEL: Record<string, string> = {
  draft: "Entwurf",
  in_progress: "In Bearbeitung",
  complete: "Abgeschlossen",
};

const STATUS_STYLE: Record<string, string> = {
  draft: "background:#f3f4f6;color:#6b7280",
  in_progress: "background:#fef3c7;color:#d97706",
  complete: "background:#dcfce7;color:#16a34a",
};

const STEP_LABELS = ["Kickoff", "Website & Kunden", "Tech. Scan", "Background-Crawl", "SemRush Check", "Lighthouse", "Report / PDF"];

export default function AuditList({ onOpen }: Props) {
  const [audits, setAudits] = useState<AuditSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newClient, setNewClient] = useState("");
  const [newUrl, setNewUrl] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [deleting, setDeleting] = useState<number | null>(null);

  const load = () => {
    setLoading(true);
    listAudits()
      .then(setAudits)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    setCreating(true);
    try {
      const { id } = await createAudit(newTitle.trim(), newClient.trim(), newUrl.trim());
      setShowCreate(false);
      setNewTitle("");
      setNewClient("");
      setNewUrl("");
      onOpen(id);
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm) {
      setDeleting(id);
      await deleteAudit(id).catch(() => {});
      setDeleting(null);
      load();
      return;
    }
    if (confirm("Analyse wirklich löschen?")) {
      setDeleting(id);
      await deleteAudit(id).catch(() => {});
      setDeleting(null);
      load();
    }
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h2 style={{ fontSize: 22, fontWeight: 800, margin: 0, color: "var(--gray-900,#111827)" }}>Analysen</h2>
          <p style={{ fontSize: 13, color: "var(--gray-500,#6b7280)", marginTop: 4 }}>
            Geführter 6-Schritte Analyse-Workflow mit PDF-Bericht
          </p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          style={{
            background: "var(--blue-600,#2563eb)",
            color: "white",
            border: "none",
            borderRadius: 8,
            padding: "10px 20px",
            fontSize: 14,
            fontWeight: 700,
            cursor: "pointer",
          }}
        >
          + Neue Analyse
        </button>
      </div>

      {showCreate && (
        <div style={{
          background: "white",
          border: "1px solid var(--gray-200,#e5e7eb)",
          borderRadius: 12,
          padding: 24,
          marginBottom: 24,
          boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
        }}>
          <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 16 }}>Neue Analyse erstellen</h3>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
            <label className="form-group">
              <span>Titel *</span>
              <input className="form-input" value={newTitle} onChange={(e) => setNewTitle(e.target.value)} placeholder="z.B. Analyse Q1 2026" autoFocus />
            </label>
            <label className="form-group">
              <span>Kundenname</span>
              <input className="form-input" value={newClient} onChange={(e) => setNewClient(e.target.value)} placeholder="Musterfirma AG" />
            </label>
            <label className="form-group">
              <span>Website URL</span>
              <input className="form-input" value={newUrl} onChange={(e) => setNewUrl(e.target.value)} placeholder="https://www.example.com" />
            </label>
          </div>
          <div style={{ display: "flex", gap: 10, marginTop: 16 }}>
            <button
              onClick={handleCreate}
              disabled={creating || !newTitle.trim()}
              style={{ background: "var(--blue-600,#2563eb)", color: "white", border: "none", borderRadius: 8, padding: "9px 22px", fontSize: 13, fontWeight: 700, cursor: "pointer", opacity: !newTitle.trim() ? 0.6 : 1 }}
            >
              {creating ? "Erstellt..." : "Analyse starten →"}
            </button>
            <button
              onClick={() => setShowCreate(false)}
              style={{ background: "var(--gray-100,#f3f4f6)", color: "var(--gray-700,#374151)", border: "none", borderRadius: 8, padding: "9px 18px", fontSize: 13, fontWeight: 600, cursor: "pointer" }}
            >
              Abbrechen
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div style={{ textAlign: "center", padding: 48, color: "var(--gray-400,#9ca3af)", fontSize: 14 }}>
          Analysen werden geladen...
        </div>
      ) : audits.length === 0 ? (
        <div style={{
          textAlign: "center",
          padding: 64,
          background: "var(--gray-50,#f9fafb)",
          borderRadius: 12,
          border: "2px dashed var(--gray-200,#e5e7eb)",
        }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>📊</div>
          <div style={{ fontSize: 16, fontWeight: 700, color: "var(--gray-700,#374151)", marginBottom: 6 }}>Noch keine Analysen</div>
          <div style={{ fontSize: 13, color: "var(--gray-400,#9ca3af)" }}>Erstelle deine erste geführte Website-Analyse.</div>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {audits.map((audit) => (
            <div
              key={audit.id}
              onClick={() => onOpen(audit.id)}
              style={{
                background: "white",
                border: "1px solid var(--gray-200,#e5e7eb)",
                borderRadius: 12,
                padding: "16px 20px",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: 16,
                transition: "box-shadow 0.15s, border-color 0.15s",
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.borderColor = "var(--blue-400,#60a5fa)";
                (e.currentTarget as HTMLElement).style.boxShadow = "0 2px 12px rgba(37,99,235,0.08)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.borderColor = "var(--gray-200,#e5e7eb)";
                (e.currentTarget as HTMLElement).style.boxShadow = "none";
              }}
            >
              <div style={{ fontSize: 28 }}>📋</div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
                  <span style={{ fontSize: 15, fontWeight: 700, color: "var(--gray-900,#111827)" }}>{audit.title}</span>
                  <span style={{ padding: "2px 10px", borderRadius: 20, fontSize: 11, fontWeight: 600, ...(Object.fromEntries((STATUS_STYLE[audit.status] || "").split(";").filter(Boolean).map((s) => s.split(":")))) }}>
                    {STATUS_LABEL[audit.status] || audit.status}
                  </span>
                </div>
                <div style={{ fontSize: 12, color: "var(--gray-400,#9ca3af)" }}>
                  {audit.client_name && <span style={{ marginRight: 12 }}>👤 {audit.client_name}</span>}
                  {audit.website_url && <span style={{ marginRight: 12 }}>🌐 {audit.website_url}</span>}
                  <span>Schritt {audit.current_step + 1}/7: {STEP_LABELS[audit.current_step] || "–"}</span>
                </div>
              </div>
              <div style={{ display: "flex", gap: 8, alignItems: "center", flexShrink: 0 }}>
                {/* Step progress mini-pills */}
                {[0,1,2,3,4,5].map((s) => (
                  <div key={s} style={{
                    width: 8,
                    height: 8,
                    borderRadius: "50%",
                    background: s < audit.current_step ? "#16a34a" : s === audit.current_step ? "var(--blue-600,#2563eb)" : "var(--gray-200,#e5e7eb)",
                  }} />
                ))}
                {audit.pdf_path && <span style={{ fontSize: 16, marginLeft: 4 }} title="PDF vorhanden">📄</span>}
                <button
                  onClick={(e) => handleDelete(audit.id, e)}
                  disabled={deleting === audit.id}
                  style={{ background: "none", border: "none", color: "var(--gray-300,#d1d5db)", fontSize: 16, cursor: "pointer", padding: "4px 6px", borderRadius: 6 }}
                  title="Löschen"
                >
                  🗑
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
