import { useEffect, useState } from "react";
import { listAudits } from "../api";
import type { AuditSummary } from "../api";
import { Plus, FileText, User, Globe, TrendingUp, FileCheck, Clock, LayoutDashboard } from "lucide-react";

interface Props {
  onNewAnalysis: () => void;
  onViewAnalysis: (analysisId: number, projectId: number) => void;
}

const STATUS_STYLE: Record<string, { bg: string; color: string }> = {
  draft:       { bg: "var(--gray-100)", color: "var(--gray-500)" },
  in_progress: { bg: "#fef3c7",         color: "#d97706" },
  complete:    { bg: "#dcfce7",         color: "#16a34a" },
};
const STATUS_LABEL: Record<string, string> = {
  draft: "Entwurf", in_progress: "In Bearbeitung", complete: "Abgeschlossen",
};
const STEP_LABELS = ["Kickoff", "Website & Kunden", "Tech. Scan", "Background-Crawl", "SemRush Check", "Lighthouse", "Report / PDF"];

export default function Dashboard({ onNewAnalysis }: Props) {
  const [audits, setAudits] = useState<AuditSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listAudits().then(setAudits).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const total = audits.length;
  const done = audits.filter((a) => a.status === "complete").length;
  const inProgress = audits.filter((a) => a.status === "in_progress").length;
  const hasPdf = audits.filter((a) => a.pdf_path).length;

  return (
    <div>
      {/* Header */}
      <div className="section-header" style={{ marginBottom: 28 }}>
        <div>
          <h1 style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <LayoutDashboard size={22} strokeWidth={1.75} style={{ color: "var(--primary)" }} />
            Dashboard
          </h1>
          <p className="text-muted mt-2">Alle Analysen auf einen Blick.</p>
        </div>
        <button className="btn btn-primary" onClick={onNewAnalysis}>
          <Plus size={15} strokeWidth={2.5} />
          Neue Analyse
        </button>
      </div>

      {/* KPI Cards */}
      {!loading && total > 0 && (
        <div className="dashboard-kpi-grid">
          <div className="dashboard-kpi-card">
            <div className="dashboard-kpi-icon" style={{ background: "#eff6ff" }}>
              <FileText size={18} strokeWidth={1.75} style={{ color: "var(--primary)" }} />
            </div>
            <div>
              <div className="dashboard-kpi-value">{total}</div>
              <div className="dashboard-kpi-label">Analysen total</div>
            </div>
          </div>
          <div className="dashboard-kpi-card">
            <div className="dashboard-kpi-icon" style={{ background: "#fef3c7" }}>
              <TrendingUp size={18} strokeWidth={1.75} style={{ color: "#d97706" }} />
            </div>
            <div>
              <div className="dashboard-kpi-value" style={{ color: "#d97706" }}>{inProgress}</div>
              <div className="dashboard-kpi-label">In Bearbeitung</div>
            </div>
          </div>
          <div className="dashboard-kpi-card">
            <div className="dashboard-kpi-icon" style={{ background: "#dcfce7" }}>
              <FileCheck size={18} strokeWidth={1.75} style={{ color: "#16a34a" }} />
            </div>
            <div>
              <div className="dashboard-kpi-value" style={{ color: "#16a34a" }}>{done}</div>
              <div className="dashboard-kpi-label">Abgeschlossen</div>
            </div>
          </div>
          <div className="dashboard-kpi-card">
            <div className="dashboard-kpi-icon" style={{ background: "#f3e8ff" }}>
              <FileText size={18} strokeWidth={1.75} style={{ color: "#7c3aed" }} />
            </div>
            <div>
              <div className="dashboard-kpi-value" style={{ color: "#7c3aed" }}>{hasPdf}</div>
              <div className="dashboard-kpi-label">PDFs erstellt</div>
            </div>
          </div>
        </div>
      )}

      {/* Recent audits */}
      <div style={{ marginTop: total > 0 ? 28 : 0 }}>
        {total > 0 && (
          <h2 style={{ fontSize: 15, fontWeight: 700, marginBottom: 14, color: "var(--gray-700)" }}>
            Zuletzt bearbeitet
          </h2>
        )}

        {loading && (
          <div style={{ display: "flex", justifyContent: "center", padding: "60px 0" }}>
            <div className="spinner" />
          </div>
        )}

        {!loading && audits.length === 0 && (
          <div className="empty-state" style={{ padding: "80px 24px" }}>
            <div style={{ width: 64, height: 64, borderRadius: 16, background: "var(--primary-light)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px" }}>
              <FileText size={28} strokeWidth={1.5} style={{ color: "var(--primary)" }} />
            </div>
            <h3 style={{ fontSize: 17, fontWeight: 700, marginBottom: 8 }}>Noch keine Analysen</h3>
            <p style={{ fontSize: 14, marginBottom: 24 }}>Starte deine erste geführte Website-Analyse.</p>
            <button className="btn btn-primary" onClick={onNewAnalysis}>
              <Plus size={15} strokeWidth={2.5} />
              Erste Analyse starten
            </button>
          </div>
        )}

        {!loading && audits.length > 0 && (
          <div className="audit-list">
            {audits.slice(0, 5).map((audit) => {
              const style = STATUS_STYLE[audit.status] || STATUS_STYLE.draft;
              const progress = Math.round(((audit.current_step) / 6) * 100);
              return (
                <div key={audit.id} className="audit-card" onClick={onNewAnalysis}>
                  <div className="audit-card-icon">
                    {audit.status === "complete"
                      ? <FileCheck size={20} strokeWidth={1.5} style={{ color: "#16a34a" }} />
                      : audit.status === "in_progress"
                      ? <Clock size={20} strokeWidth={1.5} style={{ color: "#d97706" }} />
                      : <FileText size={20} strokeWidth={1.5} style={{ color: "var(--gray-400)" }} />
                    }
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                      <span className="audit-card-title">{audit.title}</span>
                      <span className="audit-status-badge" style={{ background: style.bg, color: style.color }}>
                        {STATUS_LABEL[audit.status] || audit.status}
                      </span>
                    </div>
                    <div className="audit-card-meta">
                      {audit.client_name && (
                        <span className="audit-meta-item"><User size={11} strokeWidth={2} />{audit.client_name}</span>
                      )}
                      {audit.website_url && (
                        <span className="audit-meta-item"><Globe size={11} strokeWidth={2} />{audit.website_url}</span>
                      )}
                      <span className="audit-meta-item">
                        Schritt {audit.current_step + 1}/7: {STEP_LABELS[audit.current_step] || "–"}
                      </span>
                    </div>
                    <div className="audit-progress-bar" style={{ marginTop: 10 }}>
                      <div className="audit-progress-fill" style={{ width: `${progress}%`, background: audit.status === "complete" ? "#16a34a" : "var(--primary)" }} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
