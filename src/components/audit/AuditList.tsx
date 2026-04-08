import { useState, useEffect } from "react";
import type { AuditSummary } from "../../api";
import { listAudits, createAudit, deleteAudit } from "../../api";
import {
  Plus, Trash2, FileText, User, Globe, ChevronRight,
  ClipboardList, CheckCircle2, Clock, FileCheck,
} from "lucide-react";

interface Props {
  onOpen: (id: number) => void;
  initialShowCreate?: boolean;
  onCreateShown?: () => void;
}

const STATUS_LABEL: Record<string, string> = {
  draft: "Entwurf",
  in_progress: "In Bearbeitung",
  complete: "Abgeschlossen",
};

const STATUS_STYLE: Record<string, { bg: string; color: string }> = {
  draft:       { bg: "var(--gray-100)", color: "var(--gray-500)" },
  in_progress: { bg: "#fef3c7",         color: "#d97706" },
  complete:    { bg: "#dcfce7",         color: "#16a34a" },
};

const STEP_LABELS = ["Kickoff", "Website & Kunden", "Tech. Scan", "Background-Crawl", "SemRush Check", "Lighthouse", "Report / PDF"];
const STEP_COUNT = 7;

export default function AuditList({ onOpen, initialShowCreate = false, onCreateShown }: Props) {
  const [audits, setAudits] = useState<AuditSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newClient, setNewClient] = useState("");
  const [newUrl, setNewUrl] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [deleting, setDeleting] = useState<number | null>(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);

  const load = () => {
    setLoading(true);
    listAudits().then(setAudits).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  useEffect(() => {
    if (initialShowCreate) {
      setShowCreate(true);
      onCreateShown?.();
    }
  }, [initialShowCreate]);

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    setCreating(true);
    try {
      const { id } = await createAudit(newTitle.trim(), newClient.trim(), newUrl.trim());
      setShowCreate(false);
      setNewTitle(""); setNewClient(""); setNewUrl("");
      onOpen(id);
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    setConfirmDeleteId(id);
  };

  const confirmDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirmDeleteId) return;
    setDeleting(confirmDeleteId);
    await deleteAudit(confirmDeleteId).catch(() => {});
    setDeleting(null);
    setConfirmDeleteId(null);
    load();
  };

  return (
    <div>
      {/* Header */}
      <div className="section-header" style={{ marginBottom: 24 }}>
        <div>
          <h1 style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <ClipboardList size={22} strokeWidth={1.75} style={{ color: "var(--primary)" }} />
            Analysen
          </h1>
          <p className="text-muted mt-2">Geführter 7-Schritte Workflow mit PDF-Bericht</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
          <Plus size={15} strokeWidth={2.5} />
          Neue Analyse
        </button>
      </div>

      {/* Create form */}
      {showCreate && (
        <div className="create-card">
          <div className="create-card-header">
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div className="create-card-icon">
                <FileText size={16} strokeWidth={1.75} />
              </div>
              <h3 style={{ margin: 0, fontSize: 15, fontWeight: 700 }}>Neue Analyse erstellen</h3>
            </div>
          </div>
          <div className="create-card-body">
            <div className="form-row-3">
              <label className="form-group" style={{ marginBottom: 0 }}>
                <span className="form-label">Titel <span style={{ color: "var(--red)" }}>*</span></span>
                <input className="form-input" value={newTitle} onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="z.B. Analyse Q1 2026" autoFocus
                  onKeyDown={(e) => e.key === "Enter" && handleCreate()} />
              </label>
              <label className="form-group" style={{ marginBottom: 0 }}>
                <span className="form-label">Kundenname</span>
                <input className="form-input" value={newClient} onChange={(e) => setNewClient(e.target.value)} placeholder="Musterfirma AG" />
              </label>
              <label className="form-group" style={{ marginBottom: 0 }}>
                <span className="form-label">Website URL</span>
                <input className="form-input" value={newUrl} onChange={(e) => setNewUrl(e.target.value)} placeholder="https://example.com" />
              </label>
            </div>
            <div className="flex gap-2 mt-4">
              <button onClick={handleCreate} disabled={creating || !newTitle.trim()} className="btn btn-primary">
                {creating ? "Erstellt..." : "Analyse starten"}
                {!creating && <ChevronRight size={15} strokeWidth={2.5} />}
              </button>
              <button onClick={() => setShowCreate(false)} className="btn btn-secondary">Abbrechen</button>
            </div>
          </div>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div style={{ display: "flex", justifyContent: "center", padding: "60px 0" }}>
          <div className="spinner" />
        </div>
      )}

      {/* Empty */}
      {!loading && audits.length === 0 && !showCreate && (
        <div className="empty-state" style={{ padding: "80px 24px" }}>
          <div style={{ width: 64, height: 64, borderRadius: 16, background: "var(--primary-light)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px" }}>
            <ClipboardList size={28} strokeWidth={1.5} style={{ color: "var(--primary)" }} />
          </div>
          <h3 style={{ fontSize: 17, fontWeight: 700, marginBottom: 8 }}>Noch keine Analysen</h3>
          <p style={{ fontSize: 14, marginBottom: 24 }}>Erstelle deine erste geführte Website-Analyse.</p>
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
            <Plus size={15} strokeWidth={2.5} />
            Erste Analyse erstellen
          </button>
        </div>
      )}

      {/* Audit list */}
      {!loading && audits.length > 0 && (
        <div className="audit-list">
          {audits.map((audit) => {
            const style = STATUS_STYLE[audit.status] || STATUS_STYLE.draft;
            const progress = Math.round(((audit.current_step) / (STEP_COUNT - 1)) * 100);
            return (
              <div
                key={audit.id}
                className="audit-card"
                onClick={() => onOpen(audit.id)}
              >
                {/* Left icon */}
                <div className="audit-card-icon">
                  {audit.status === "complete"
                    ? <FileCheck size={20} strokeWidth={1.5} style={{ color: "#16a34a" }} />
                    : audit.status === "in_progress"
                    ? <Clock size={20} strokeWidth={1.5} style={{ color: "#d97706" }} />
                    : <FileText size={20} strokeWidth={1.5} style={{ color: "var(--gray-400)" }} />
                  }
                </div>

                {/* Main info */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                    <span className="audit-card-title">{audit.title}</span>
                    <span className="audit-status-badge" style={{ background: style.bg, color: style.color }}>
                      {STATUS_LABEL[audit.status] || audit.status}
                    </span>
                  </div>
                  <div className="audit-card-meta">
                    {audit.client_name && (
                      <span className="audit-meta-item">
                        <User size={11} strokeWidth={2} />
                        {audit.client_name}
                      </span>
                    )}
                    {audit.website_url && (
                      <span className="audit-meta-item">
                        <Globe size={11} strokeWidth={2} />
                        {audit.website_url}
                      </span>
                    )}
                    <span className="audit-meta-item">
                      <CheckCircle2 size={11} strokeWidth={2} />
                      Schritt {audit.current_step + 1}/{STEP_COUNT}: {STEP_LABELS[audit.current_step] || "–"}
                    </span>
                  </div>

                  {/* Progress bar */}
                  <div className="audit-progress-bar" style={{ marginTop: 10 }}>
                    <div className="audit-progress-fill" style={{ width: `${progress}%`, background: audit.status === "complete" ? "#16a34a" : "var(--primary)" }} />
                  </div>
                </div>

                {/* Right actions */}
                <div style={{ display: "flex", alignItems: "center", gap: 6, flexShrink: 0 }}>
                  {audit.pdf_path && (
                    <span className="audit-pdf-badge" title="PDF vorhanden">
                      <FileText size={12} strokeWidth={2} />
                      PDF
                    </span>
                  )}
                  {confirmDeleteId === audit.id ? (
                    <div className="flex gap-2 items-center" onClick={(e) => e.stopPropagation()}>
                      <span style={{ fontSize: 12, color: "var(--gray-500)" }}>Löschen?</span>
                      <button className="btn btn-sm" style={{ background: "var(--red)", color: "white" }}
                        onClick={confirmDelete} disabled={deleting === audit.id}>
                        {deleting === audit.id ? "..." : "Ja"}
                      </button>
                      <button className="btn btn-ghost btn-sm" onClick={(e) => { e.stopPropagation(); setConfirmDeleteId(null); }}>
                        Nein
                      </button>
                    </div>
                  ) : (
                    <button className="audit-delete-btn" onClick={(e) => handleDelete(audit.id, e)} title="Löschen">
                      <Trash2 size={14} strokeWidth={1.75} />
                    </button>
                  )}
                  <ChevronRight size={16} strokeWidth={1.75} style={{ color: "var(--gray-300)" }} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
