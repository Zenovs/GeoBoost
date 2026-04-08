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
import {
  LayoutDashboard,
  ClipboardList,
  Settings as SettingsIcon,
  Zap,
} from "lucide-react";

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
  const [auditListShowCreate, setAuditListShowCreate] = useState(false);

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

  const navItems = [
    { id: "dashboard" as View, Icon: LayoutDashboard, label: "Dashboard" },
    { id: "audits" as View, Icon: ClipboardList, label: "Analysen" },
    { id: "settings" as View, Icon: SettingsIcon, label: "Einstellungen" },
  ];

  const handleNewAudit = () => {
    setAuditListShowCreate(true);
    nav("audits");
  };

  return (
    <div className="app-shell">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">
            <Zap size={16} strokeWidth={2.5} />
          </div>
          <div>
            <h1>GeoBoost</h1>
            <span>SEO Analyse Tool</span>
          </div>
        </div>
        <nav className="sidebar-nav">
          {navItems.map(({ id, Icon, label }) => (
            <div
              key={id}
              className={`nav-item ${view === id || (id === "audits" && view === "audit-workflow") ? "active" : ""}`}
              onClick={() => nav(id)}
            >
              <Icon size={16} strokeWidth={1.75} className="nav-icon" />
              {label}
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="sidebar-status">
            <span className={`status-dot ${backendOk === null ? "gray" : backendOk ? "green" : "red"}`} />
            <span className="sidebar-status-label">
              {backendOk === null ? "Verbinde..." : backendOk ? "Backend aktiv" : "Backend offline"}
            </span>
          </div>
          {version && <div className="sidebar-version">v {version}</div>}
        </div>
      </aside>

      {/* Main */}
      <main className="main-content">
        {/* Backend starting */}
        {!backendOk && startupGrace && (
          <div className="alert alert-warning mb-4" style={{ borderRadius: "var(--radius-sm)" }}>
            <span className="status-dot orange" />
            <span>Backend wird gestartet, bitte warten...</span>
          </div>
        )}
        {/* Offline banner */}
        {backendOk === false && !startupGrace && (
          <div className="offline-banner mb-4" style={{ borderRadius: "var(--radius-sm)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span>Backend nicht erreichbar – App neu starten oder <code>python3 backend/main.py</code> ausführen.</span>
            <button className="btn btn-secondary btn-sm" onClick={() => checkHealth().then(() => setBackendOk(true)).catch(() => {})}>
              Erneut versuchen
            </button>
          </div>
        )}

        {view === "dashboard" && (
          <Dashboard onNewAnalysis={handleNewAudit} onViewAnalysis={(analysisId, projectId) => {
            setWizard({ analysisId, projectId });
            nav("progress");
          }} />
        )}
        {view === "kickoff" && (
          <Kickoff initialData={wizard.kickoff}
            onNext={(kickoff) => { setWizard((w) => ({ ...w, kickoff })); nav("checks"); }}
            onCancel={() => nav("dashboard")} />
        )}
        {view === "checks" && wizard.kickoff && (
          <CheckSelector kickoff={wizard.kickoff} initialChecks={wizard.checks || DEFAULT_CHECKS}
            backendOk={backendOk === true}
            onStart={(checks, analysisId, projectId) => { setWizard((w) => ({ ...w, checks, analysisId, projectId })); nav("progress"); }}
            onBack={() => nav("kickoff")} />
        )}
        {view === "progress" && (
          <AnalysisProgress analysisId={wizard.analysisId!} projectId={wizard.projectId!}
            onDone={() => nav("dashboard")}
            onNewAnalysis={() => { setWizard({}); nav("kickoff"); }} />
        )}
        {view === "audits" && (
          <AuditList
            initialShowCreate={auditListShowCreate}
            onCreateShown={() => setAuditListShowCreate(false)}
            onOpen={(id) => { setActiveAuditId(id); nav("audit-workflow"); }} />
        )}
        {view === "audit-workflow" && activeAuditId !== null && (
          <AuditWorkflow auditId={activeAuditId} onBack={() => nav("audits")} />
        )}
        {view === "settings" && <Settings />}
      </main>
    </div>
  );
}
