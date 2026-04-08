import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/core";
import { getConfig, updateConfig, uploadCredentials, getVersion, runUpdate, type AppConfig, type VersionInfo, type UpdateResult } from "../api";

export default function Settings() {
  const [config, setConfig] = useState<AppConfig>({});
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);

  // Update state
  const [version, setVersion] = useState<VersionInfo | null>(null);
  const [updating, setUpdating] = useState(false);
  const [updateResult, setUpdateResult] = useState<UpdateResult | null>(null);
  const [restarting, setRestarting] = useState(false);

  useEffect(() => {
    getConfig().then(setConfig).catch((e) => setError(e.message));
    getVersion().then(setVersion).catch(() => null);
  }, []);

  const handleUpdate = async () => {
    setUpdating(true);
    setUpdateResult(null);
    try {
      const result = await runUpdate();
      setUpdateResult(result);
      if (result.success) {
        // Refresh version info
        getVersion().then(setVersion).catch(() => null);
      }
    } catch (e: unknown) {
      setUpdateResult({ success: false, log: (e as Error).message, commit: "", date: "", restart_required: false });
    } finally {
      setUpdating(false);
    }
  };

  const handleRestart = async () => {
    setRestarting(true);
    try {
      await invoke("restart_backend");
      // Wait a moment then refresh version
      setTimeout(() => {
        setRestarting(false);
        setUpdateResult(null);
        getVersion().then(setVersion).catch(() => null);
      }, 5000);
    } catch (e: unknown) {
      setError((e as Error).message);
      setRestarting(false);
    }
  };

  const set = (key: keyof AppConfig, value: unknown) => {
    setConfig((c) => ({ ...c, [key]: value }));
    setSaved(false);
  };

  const save = async () => {
    setError("");
    try {
      await updateConfig(config);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e: unknown) {
      setError((e as Error).message);
    }
  };

  const handleCredentials = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const result = await uploadCredentials(file);
      setConfig((c) => ({ ...c, google_credentials_path: result.path }));
      setSaved(false);
    } catch (e: unknown) {
      setError((e as Error).message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <div className="section-header">
        <div>
          <h1>Einstellungen</h1>
          <p className="text-muted mt-2">GeoBoost konfigurieren</p>
        </div>
        <button className="btn btn-primary" onClick={save}>
          {saved ? "✓ Gespeichert" : "Speichern"}
        </button>
      </div>

      {error && <div className="alert alert-error mb-4">{error}</div>}
      {saved && <div className="alert alert-success mb-4">Einstellungen gespeichert.</div>}

      {/* Speicherort */}
      <div className="card mb-4">
        <div className="card-header"><h3>Datenspeicherung</h3></div>
        <div className="card-body">
          <div className="form-group">
            <label className="form-label">Speicherort für Projekte</label>
            <input
              className="form-input"
              value={config.storage_path || ""}
              onChange={(e) => set("storage_path", e.target.value)}
              placeholder="~/Documents/GeoBoost_Projects"
            />
            <div className="form-hint">Ordner, in dem alle Projekte und PDFs gespeichert werden.</div>
          </div>
        </div>
      </div>

      {/* Google APIs */}
      <div className="card mb-4">
        <div className="card-header"><h3>Google APIs</h3></div>
        <div className="card-body">
          <div className="form-group">
            <label className="form-label">Google Service Account (JSON)</label>
            <div className="flex items-center gap-3">
              <input
                className="form-input"
                value={config.google_credentials_path || ""}
                onChange={(e) => set("google_credentials_path", e.target.value)}
                placeholder="/Pfad/zur/service-account.json"
              />
              <label className="btn btn-secondary btn-sm" style={{ cursor: "pointer", whiteSpace: "nowrap" }}>
                {uploading ? "Lädt..." : "Datei wählen"}
                <input type="file" accept=".json" onChange={handleCredentials} style={{ display: "none" }} />
              </label>
            </div>
            <div className="form-hint">
              Service Account JSON aus der Google Cloud Console. Benötigt für GA4 Data API und Search Console.
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">PageSpeed Insights API Key (optional)</label>
            <input
              className="form-input"
              value={config.pagespeed_api_key || ""}
              onChange={(e) => set("pagespeed_api_key", e.target.value)}
              placeholder="AIza..."
              type="password"
            />
            <div className="form-hint">
              Ohne API Key sind PageSpeed-Anfragen auf 400/Tag limitiert.
            </div>
          </div>
        </div>
      </div>

      {/* Crawler */}
      <div className="card mb-4">
        <div className="card-header"><h3>Crawler</h3></div>
        <div className="card-body">
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Max. Crawl-Tiefe</label>
              <input
                className="form-input"
                type="number"
                value={config.crawler_max_depth ?? 3}
                onChange={(e) => set("crawler_max_depth", parseInt(e.target.value))}
                min={1} max={10}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Max. Anzahl URLs</label>
              <input
                className="form-input"
                type="number"
                value={config.crawler_max_urls ?? 200}
                onChange={(e) => set("crawler_max_urls", parseInt(e.target.value))}
                min={10} max={1000}
              />
            </div>
          </div>
        </div>
      </div>

      {/* KI */}
      <div className="card mb-4">
        <div className="card-header"><h3>KI-Modell (Ollama)</h3></div>
        <div className="card-body">
          <div className="form-group">
            <label className="form-label">Ollama Modell</label>
            <select
              className="form-select"
              value={config.ollama_model || "llama3.1:8b"}
              onChange={(e) => set("ollama_model", e.target.value)}
              style={{ maxWidth: 300 }}
            >
              <option value="llama3.1:8b">Llama 3.1 8B (empfohlen)</option>
              <option value="mistral:7b">Mistral 7B (gut für Deutsch)</option>
              <option value="llama3.2:3b">Llama 3.2 3B (schnell)</option>
            </select>
            <div className="form-hint">
              Ollama muss lokal installiert sein. Modell herunterladen:{" "}
              <code>ollama pull llama3.1:8b</code>
            </div>
          </div>
        </div>
      </div>

      {/* Branding */}
      <div className="card mb-4">
        <div className="card-header"><h3>Branding (PDF)</h3></div>
        <div className="card-body">
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Firmenname</label>
              <input
                className="form-input"
                value={config.company_name || ""}
                onChange={(e) => set("company_name", e.target.value)}
                placeholder="GeoBoost / Ihre Agentur"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Kontakt / Website</label>
              <input
                className="form-input"
                value={config.company_contact || ""}
                onChange={(e) => set("company_contact", e.target.value)}
                placeholder="www.example.com"
              />
            </div>
          </div>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label">Primärfarbe</label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={config.primary_color || "#1a56db"}
                  onChange={(e) => set("primary_color", e.target.value)}
                  style={{ width: 40, height: 38, border: "1px solid var(--gray-300)", borderRadius: 6, cursor: "pointer" }}
                />
                <input
                  className="form-input"
                  value={config.primary_color || "#1a56db"}
                  onChange={(e) => set("primary_color", e.target.value)}
                  placeholder="#1a56db"
                  style={{ maxWidth: 120 }}
                />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Akzentfarbe</label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={config.accent_color || "#7e3af2"}
                  onChange={(e) => set("accent_color", e.target.value)}
                  style={{ width: 40, height: 38, border: "1px solid var(--gray-300)", borderRadius: 6, cursor: "pointer" }}
                />
                <input
                  className="form-input"
                  value={config.accent_color || "#7e3af2"}
                  onChange={(e) => set("accent_color", e.target.value)}
                  placeholder="#7e3af2"
                  style={{ maxWidth: 120 }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Software-Update */}
      <div className="card mb-4">
        <div className="card-header">
          <h3>Software-Update</h3>
          {version && (
            <span className="badge badge-blue" style={{ fontFamily: "monospace", fontSize: 11 }}>
              {version.commit} · {version.branch} · {version.date}
            </span>
          )}
        </div>
        <div className="card-body">
          {version && (
            <div style={{ marginBottom: 12, fontSize: 13, color: "var(--gray-600)" }}>
              <strong>Aktueller Stand:</strong> {version.message}
            </div>
          )}

          <div className="flex gap-3 items-center flex-wrap">
            <button
              className="btn btn-primary"
              onClick={handleUpdate}
              disabled={updating || restarting}
            >
              {updating ? "Aktualisierung läuft..." : "Update durchführen (git pull)"}
            </button>

            {updateResult?.restart_required && (
              <button
                className="btn btn-secondary"
                onClick={handleRestart}
                disabled={restarting}
              >
                {restarting ? "Backend startet neu..." : "Backend neu starten"}
              </button>
            )}
          </div>

          <p className="form-hint mt-3">
            Lädt den neuesten Code von GitHub (<code>git pull origin main</code>) und aktualisiert Python-Abhängigkeiten.
            Nach dem Update muss der Backend-Prozess neu gestartet werden.
          </p>

          {/* Update Log */}
          {updating && (
            <div style={{
              marginTop: 12, padding: "10px 14px",
              background: "var(--gray-100)", borderRadius: 6,
              fontSize: 12, fontFamily: "monospace", color: "var(--gray-600)",
            }}>
              Verbinde mit GitHub...
            </div>
          )}

          {updateResult && (
            <div style={{
              marginTop: 12, padding: "10px 14px",
              background: updateResult.success ? "#f0fdf4" : "#fef2f2",
              border: `1px solid ${updateResult.success ? "#bbf7d0" : "#fecaca"}`,
              borderRadius: 6,
            }}>
              <div style={{
                fontWeight: 600, marginBottom: 8, fontSize: 13,
                color: updateResult.success ? "var(--green)" : "var(--red)",
              }}>
                {updateResult.success ? "Update erfolgreich" : "Update fehlgeschlagen"}
              </div>
              <pre style={{
                fontFamily: "monospace", fontSize: 11,
                color: "var(--gray-700)", whiteSpace: "pre-wrap",
                maxHeight: 200, overflowY: "auto", margin: 0,
              }}>
                {updateResult.log}
              </pre>
              {updateResult.restart_required && (
                <div style={{ marginTop: 10, fontSize: 12, color: "var(--orange)", fontWeight: 600 }}>
                  Backend-Neustart erforderlich, damit alle Änderungen aktiv werden.
                </div>
              )}
            </div>
          )}

          {restarting && (
            <div className="alert alert-success mt-3">
              Backend wird neu gestartet – bitte 5–10 Sekunden warten...
            </div>
          )}
        </div>
      </div>

      {/* Setup Guide */}
      <div className="card mb-4">
        <div className="card-header"><h3>Setup-Anleitung</h3></div>
        <div className="card-body">
          <ol style={{ paddingLeft: 20, color: "var(--gray-600)", lineHeight: 2.2, fontSize: 14 }}>
            <li>
              <strong>Google Cloud Console:</strong>{" "}
              <code>console.cloud.google.com</code> → APIs &amp; Services → Bibliothek →
              „Google Analytics Data API" und „PageSpeed Insights API" aktivieren
            </li>
            <li>
              <strong>Service Account:</strong>{" "}
              IAM &amp; Verwaltung → Dienstkonten → Neu erstellen → JSON-Key herunterladen
            </li>
            <li>
              <strong>GA4 Zugriff erteilen:</strong>{" "}
              GA4 Admin → Property → Nutzerverwaltung → Service Account E-Mail als Betrachter hinzufügen
            </li>
            <li>
              <strong>Ollama installieren:</strong>{" "}
              <code>brew install ollama</code> (Mac) oder <a href="https://ollama.ai" target="_blank" rel="noreferrer" style={{ color: "var(--primary)" }}>ollama.ai</a> → dann{" "}
              <code>ollama pull llama3.1:8b</code>
            </li>
          </ol>
        </div>
      </div>

      <div className="flex justify-end">
        <button className="btn btn-primary" onClick={save}>
          {saved ? "✓ Gespeichert" : "Einstellungen speichern"}
        </button>
      </div>
    </div>
  );
}
