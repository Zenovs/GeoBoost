import { useEffect, useState } from "react";
import { listProjects, deleteProject, type Project } from "../api";

interface Props {
  onNewAnalysis: () => void;
  onViewAnalysis: (analysisId: number, projectId: number) => void;
}

export default function Dashboard({ onNewAnalysis, onViewAnalysis }: Props) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);
  const [deleting, setDeleting] = useState(false);

  const load = () => {
    setLoading(true);
    listProjects()
      .then(setProjects)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleDeleteClick = (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    setConfirmDeleteId(id);
  };

  const handleDeleteConfirm = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirmDeleteId) return;
    setDeleting(true);
    try {
      await deleteProject(confirmDeleteId);
      setConfirmDeleteId(null);
      load();
    } catch (err: unknown) {
      setError((err as Error).message);
    } finally {
      setDeleting(false);
    }
  };

  const fmt = (d?: string) =>
    d ? new Date(d).toLocaleDateString("de-CH", { day: "2-digit", month: "2-digit", year: "numeric" }) : "–";

  return (
    <div>
      {/* Header */}
      <div className="section-header">
        <div>
          <h1>Dashboard</h1>
          <p className="text-muted mt-2">Alle Projekte und Analysen auf einen Blick.</p>
        </div>
        <button className="btn btn-primary" onClick={onNewAnalysis}>
          + Neue Analyse
        </button>
      </div>

      {/* Loading / Error */}
      {loading && (
        <div className="flex items-center justify-between" style={{ padding: "40px 0", justifyContent: "center" }}>
          <div className="spinner" />
        </div>
      )}
      {error && <div className="alert alert-error mb-4">{error}</div>}

      {/* Project List */}
      {!loading && projects.length === 0 && (
        <div className="empty-state">
          <div className="icon">📊</div>
          <h3>Noch keine Analysen</h3>
          <p>Starte deine erste GA4 &amp; SEO Analyse.</p>
          <button className="btn btn-primary mt-4" onClick={onNewAnalysis}>
            Erste Analyse starten
          </button>
        </div>
      )}

      {!loading && projects.length > 0 && (
        <div className="flex-col gap-3">
          {projects.map((proj) => (
            <div
              key={proj.id}
              className="project-card"
              onClick={() => {
                // Open latest analysis if exists
                const latest = proj.analyses?.[0];
                if (latest) {
                  onViewAnalysis(latest.id, proj.id);
                } else {
                  onNewAnalysis();
                }
              }}
            >
              <div className="project-card-left">
                <div className="flex items-center gap-2">
                  <h3 className="truncate" style={{ maxWidth: 340 }}>{proj.name}</h3>
                  <span className="badge badge-blue">{proj.analysis_count} Analyse{proj.analysis_count !== 1 ? "n" : ""}</span>
                </div>
                <div className="project-url truncate">{proj.website_url}</div>
                {proj.ga4_property_id && (
                  <div className="text-xs text-muted mt-2">GA4: {proj.ga4_property_id}</div>
                )}
              </div>
              <div className="flex items-center gap-3" style={{ flexShrink: 0 }}>
                <div className="text-right">
                  <div className="text-xs text-muted">Letzte Analyse</div>
                  <div className="text-sm font-medium">{fmt(proj.last_analysis)}</div>
                </div>
                {confirmDeleteId === proj.id ? (
                  <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                    <span className="text-xs text-muted">Löschen?</span>
                    <button
                      className="btn btn-sm"
                      style={{ background: "var(--red)", color: "white", padding: "4px 10px" }}
                      onClick={handleDeleteConfirm}
                      disabled={deleting}
                    >
                      {deleting ? "..." : "Ja"}
                    </button>
                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={(e) => { e.stopPropagation(); setConfirmDeleteId(null); }}
                    >
                      Nein
                    </button>
                  </div>
                ) : (
                  <button
                    className="btn btn-ghost btn-sm"
                    onClick={(e) => handleDeleteClick(e, proj.id)}
                    title="Projekt löschen"
                  >
                    🗑
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Info Box */}
      <div className="alert alert-info mt-6">
        <span>ℹ</span>
        <div>
          <strong>GeoBoost v1.0</strong> – GA4 &amp; SEO Analyse-Tool.
          Stelle sicher, dass der Google Service Account korrekt in den{" "}
          <strong>Einstellungen</strong> hinterlegt ist.
        </div>
      </div>
    </div>
  );
}
