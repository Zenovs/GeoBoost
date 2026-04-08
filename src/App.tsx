import { useState, useEffect } from "react";
import "./styles.css";
import { checkHealth, getVersion } from "./api";
import Dashboard from "./components/Dashboard";
import Kickoff from "./components/Kickoff";
import CheckSelector from "./components/CheckSelector";
import AnalysisProgress from "./components/AnalysisProgress";
import Settings from "./components/Settings";
import AuditList from "./components/audit/AuditList";
import AuditWorkflow from "./components/audit/AuditWorkflow";
import type { KickoffData, CheckConfig } from "./api";

type View = "dashboard" | "kickoff" | "checks" | "progress" | "settings" | "audits" | "audit-workflow";

interface WizardState {
  kickoff?: KickoffData;
  checks?: CheckConfig;
  analysisId?: number;
  projectId?: number;
}

const DEFAULT_CHECKS: CheckConfig = {
  crawling: true,
  pagespeed: true,
  speedtest: true,
  ga4_traffic: true,
  ga4_channels: true,
  ga4_landingpages: true,
  ga4_devices: true,
  search_console: false,
  ai_analysis: true,
  pdf_report: true,
};

export default function App() {
  const [view, setView] = useState<View>("dashboard");
  const [wizard, setWizard] = useState<WizardState>({});
  const [activeAuditId, setActiveAuditId] = useState<number | null>(null);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const [startupGrace, setStartupGrace] = useState(true);
  const [version, setVersion] = useState<string | null>(null);

  useEffect(() => {
    const graceTimer = setTimeout(() => setStartupGrace(false), 10_000);

    const check = () =>
      checkHealth()
        .then(() => { setBackendOk(true); setStartupGrace(false); })
        .catch(() => setBackendOk(false));

    check();
    const interval = setInterval(check, 3000);
    return () => { clearInterval(interval); clearTimeout(graceTimer); };
  }, []);

  useEffect(() => {
    if (backendOk) {
      getVersion()
        .then((v) => setVersion(v.commit ? `${v.commit.slice(0, 7)} · ${v.date.slice(0, 10)}` : null))
        .catch(() => {});
    }
  }, [backendOk]);

  const nav = (v: View) => setView(v);

  const navItems: { id: View; icon: string; label: string }[] = [
    { id: "dashboard", icon: "🏠", label: "Dashboard" },
    { id: "audits", icon: "📋", label: "Analysen" },
    { id: "settings", icon: "⚙️", label: "Einstellungen" },
  ];

  return (
    <div className="app-shell">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <h1>GeoBoost</h1>
          <span>GA4 &amp; SEO Analyse</span>
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <div
              key={item.id}
              className={`nav-item ${view === item.id || (item.id === "audits" && view === "audit-workflow") ? "active" : ""}`}
              onClick={() => nav(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </div>
          ))}
        </nav>
        <div style={{ padding: "16px 20px", borderTop: "1px solid rgba(255,255,255,0.08)" }}>
          <div className="flex items-center gap-2" style={{ marginBottom: version ? 6 : 0 }}>
            <span className={`status-dot ${backendOk === null ? "gray" : backendOk ? "green" : "red"}`} />
            <span className="text-xs" style={{ color: "var(--gray-500)" }}>
              {backendOk === null ? "Verbinde..." : backendOk ? "Backend aktiv" : "Backend offline"}
            </span>
          </div>
          {version && (
            <div style={{ fontSize: 11, color: "var(--gray-600)", marginTop: 4, fontFamily: "monospace" }}>
              v {version}
            </div>
          )}
        </div>
      </aside>

      {/* Main */}
      <main className="main-content">
        {/* Backend starting – show during grace period regardless of backendOk state */}
        {!backendOk && startupGrace && (
          <div style={{ marginBottom: 16, padding: "10px 16px", background: "var(--gray-100)", borderRadius: 6, fontSize: 13, color: "var(--gray-500)", display: "flex", alignItems: "center", gap: 10 }}>
            <div className="status-dot orange" />
            Backend wird gestartet, bitte warten...
          </div>
        )}
        {/* Offline banner – only after grace period */}
        {backendOk === false && !startupGrace && (
          <div className="offline-banner" style={{ marginBottom: 16, borderRadius: "var(--radius-sm)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span>Backend nicht erreichbar. Bitte App neu starten oder Terminal öffnen und <code>source venv/bin/activate &amp;&amp; python3 backend/main.py</code> ausführen.</span>
            <button className="btn btn-secondary btn-sm" onClick={() => checkHealth().then(() => setBackendOk(true)).catch(() => {})}>
              Erneut versuchen
            </button>
          </div>
        )}

        {view === "dashboard" && (
          <Dashboard
            onNewAnalysis={() => {
              setWizard({});
              nav("kickoff");
            }}
            onViewAnalysis={(analysisId, projectId) => {
              setWizard({ analysisId, projectId });
              nav("progress");
            }}
          />
        )}

        {view === "kickoff" && (
          <Kickoff
            initialData={wizard.kickoff}
            onNext={(kickoff) => {
              setWizard((w) => ({ ...w, kickoff }));
              nav("checks");
            }}
            onCancel={() => nav("dashboard")}
          />
        )}

        {view === "checks" && wizard.kickoff && (
          <CheckSelector
            kickoff={wizard.kickoff}
            initialChecks={wizard.checks || DEFAULT_CHECKS}
            backendOk={backendOk === true}
            onStart={(checks, analysisId, projectId) => {
              setWizard((w) => ({ ...w, checks, analysisId, projectId }));
              nav("progress");
            }}
            onBack={() => nav("kickoff")}
          />
        )}

        {view === "progress" && (
          <AnalysisProgress
            analysisId={wizard.analysisId!}
            projectId={wizard.projectId!}
            onDone={() => nav("dashboard")}
            onNewAnalysis={() => {
              setWizard({});
              nav("kickoff");
            }}
          />
        )}

        {view === "audits" && (
          <AuditList
            onOpen={(id) => {
              setActiveAuditId(id);
              nav("audit-workflow");
            }}
          />
        )}

        {view === "audit-workflow" && activeAuditId !== null && (
          <AuditWorkflow
            auditId={activeAuditId}
            onBack={() => nav("audits")}
          />
        )}

        {view === "settings" && <Settings />}
      </main>
    </div>
  );
}
