import React, { useEffect, useState, useRef } from "react";
import {
  getAnalysisStatus,
  getAnalysisResults,
  downloadPdf,
  type AnalysisStatus,
  type AnalysisResults,
} from "../api";

interface Props {
  analysisId: number;
  projectId?: number;
  onDone: () => void;
  onNewAnalysis: () => void;
}

const STEP_LABELS: Record<string, string> = {
  start:     "Analyse wird gestartet",
  crawling:  "Website wird gecrawlt",
  pagespeed: "PageSpeed wird analysiert",
  speedtest: "Speed-Test läuft",
  ga4:       "GA4 Daten werden abgerufen",
  ai:        "KI-Analyse läuft",
  pdf:       "PDF wird erstellt",
  done:      "Analyse abgeschlossen",
  error:     "Fehler",
};

function MetricCard({ label, value, sub, color }: { label: string; value: string | number; sub?: string; color?: string }) {
  return (
    <div className="kpi-card">
      <div className="kpi-value" style={color ? { color } : undefined}>{value}</div>
      <div className="kpi-label">{label}</div>
      {sub && <div className="text-xs text-muted mt-2">{sub}</div>}
    </div>
  );
}

export default function AnalysisProgress({ analysisId, onDone, onNewAnalysis }: Props) {
  const [status, setStatus] = useState<AnalysisStatus | null>(null);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [log, setLog] = useState<string[]>([]);
  const [error, setError] = useState("");
  const logRef = useRef<HTMLDivElement>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!analysisId) return;

    const poll = async () => {
      try {
        const s = await getAnalysisStatus(analysisId);
        setStatus(s);
        if (s.message) {
          setLog((l) => {
            const last = l[l.length - 1];
            if (last === s.message) return l;
            return [...l, `[${new Date().toLocaleTimeString("de-CH")}] ${s.message}`];
          });
        }
        if (s.done) {
          if (intervalRef.current) clearInterval(intervalRef.current);
          const r = await getAnalysisResults(analysisId);
          setResults(r);
        }
        if (s.error) {
          setError(s.error);
          if (intervalRef.current) clearInterval(intervalRef.current);
        }
      } catch {
        // Silently retry
      }
    };

    poll();
    intervalRef.current = setInterval(poll, 1500);
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, [analysisId]);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [log]);

  const done = status?.done;
  const progress = status?.progress ?? 0;

  const getScoreColor = (score: number | undefined) => {
    if (!score) return "var(--gray-400)";
    if (score >= 90) return "var(--green)";
    if (score >= 50) return "var(--orange)";
    return "var(--red)";
  };

  const fmtNum = (n?: number) =>
    n != null ? n.toLocaleString("de-CH") : "–";

  return (
    <div>
      <div className="section-header">
        <div>
          <h1>{done ? "Analyse abgeschlossen" : "Analyse läuft..."}</h1>
          <p className="text-muted mt-2">Analyse #{analysisId}</p>
        </div>
        {done && (
          <div className="flex gap-2">
            {results?.results?.pdf_path && (
              <button className="btn btn-primary" onClick={() => downloadPdf(analysisId)}>
                📄 PDF herunterladen
              </button>
            )}
            <button className="btn btn-secondary" onClick={onNewAnalysis}>
              + Neue Analyse
            </button>
            <button className="btn btn-ghost" onClick={onDone}>
              Dashboard
            </button>
          </div>
        )}
      </div>

      {/* Progress Card */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="flex justify-between items-center mb-2">
            <div className="flex items-center gap-2">
              {!done && !error && <div className="status-dot orange" />}
              {done && !error && <div className="status-dot green" />}
              {error && <div className="status-dot red" />}
              <span className="font-semibold">
                {status ? (STEP_LABELS[status.step] || status.step) : "Starte..."}
              </span>
            </div>
            <span className="text-sm text-muted">{progress}%</span>
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }} />
          </div>
          {status?.message && (
            <p className="text-sm text-muted mt-2">{status.message}</p>
          )}
          {error && (
            <div className="alert alert-error mt-3">{error}</div>
          )}
        </div>
      </div>

      {/* Log */}
      {log.length > 0 && (
        <div className="card mb-4">
          <div className="card-header"><h3>Analyse-Log</h3></div>
          <div className="card-body" style={{ padding: 0 }}>
            <div className="analysis-log" ref={logRef}>
              {log.map((l, i) => <div key={i}>{l}</div>)}
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {done && results?.results && (
        <>
          {/* KPI Overview */}
          <div className="kpi-grid mb-4">
            {(() => {
              const ga4 = results.results.ga4_traffic as Record<string, number> | undefined;
              const ps = results.results.pagespeed as Record<string, Record<string, number>> | undefined;
              const crawler = results.results.crawler as Record<string, Record<string, number>> | undefined;
              const mobScore = ps?.mobile?.performance_score;
              const seoScore = crawler?.summary?.seo_score;
              return (
                <>
                  <MetricCard label="Sessions" value={fmtNum(ga4?.sessions)} />
                  <MetricCard label="Conversions" value={fmtNum(ga4?.conversions)} />
                  <MetricCard label="PageSpeed Mobile" value={mobScore ?? "–"}
                    color={getScoreColor(mobScore)} sub="/100" />
                  <MetricCard label="SEO Score" value={seoScore ?? "–"}
                    color={getScoreColor(seoScore)} sub="/100" />
                </>
              );
            })()}
          </div>

          {/* PageSpeed */}
          {(() => {
            const ps = results.results.pagespeed as Record<string, Record<string, unknown>> | undefined;
            const mob = ps?.mobile;
            const desk = ps?.desktop;
            if (!mob && !desk) return null;
            return (
              <div className="card mb-4">
                <div className="card-header"><h3>PageSpeed Insights</h3></div>
                <div className="card-body table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Metrik</th>
                        <th>Mobile</th>
                        <th>Desktop</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        ["Performance Score", "performance_score"],
                        ["SEO Score", "seo_score"],
                        ["LCP", "lcp"],
                        ["CLS", "cls"],
                        ["TBT", "tbt"],
                        ["FCP", "fcp"],
                      ].map(([label, key]) => (
                        <tr key={key}>
                          <td>{label}</td>
                          <td>{String(mob?.[key] ?? "–")}</td>
                          <td>{String(desk?.[key] ?? "–")}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            );
          })()}

          {/* PageSpeed Failed Audits */}
          {(() => {
            const ps = results.results.pagespeed as Record<string, Record<string, unknown>> | undefined;
            const mob = ps?.mobile as Record<string, unknown> | undefined;
            const failedAudits = mob?.failed_audits as Array<{
              id: string; title: string; description: string; explanation_de: string;
              display_value: string; score: number; savings_ms: number | null; rating: string; category: string;
            }> | undefined;
            if (!failedAudits?.length) return null;
            return (
              <div className="card mb-4">
                <div className="card-header">
                  <h3>PageSpeed – Gefundene Probleme</h3>
                  <span className="badge badge-blue">{failedAudits.length} Audits</span>
                </div>
                <div className="card-body">
                  {failedAudits.map((audit) => (
                    <div key={audit.id} style={{
                      background: "var(--gray-50, #f9fafb)",
                      border: "1px solid var(--gray-200)",
                      borderLeft: `4px solid ${audit.rating === "fail" ? "var(--red)" : "var(--orange)"}`,
                      borderRadius: "0 6px 6px 0",
                      padding: "10px 14px",
                      marginBottom: 8,
                    }}>
                      <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 4 }}>
                        <span className={`badge ${audit.rating === "fail" ? "badge-p1" : "badge-p2"}`} style={{ textTransform: "uppercase", fontSize: 10 }}>{audit.rating}</span>
                        <span className="badge badge-blue" style={{ fontSize: 10 }}>{audit.category}</span>
                        <strong style={{ fontSize: 13 }}>{audit.title}</strong>
                        {audit.savings_ms != null && (
                          <span style={{ marginLeft: "auto", fontSize: 11, color: "var(--orange)", fontWeight: 600 }}>
                            -{audit.savings_ms} ms
                          </span>
                        )}
                        {audit.display_value && (
                          <span style={{ fontSize: 11, color: "var(--gray-500)" }}>{audit.display_value}</span>
                        )}
                      </div>
                      {audit.explanation_de && (
                        <div style={{ fontSize: 12, color: "var(--gray-600)", marginBottom: 3 }}>{audit.explanation_de}</div>
                      )}
                      {!audit.explanation_de && audit.description && (
                        <div style={{ fontSize: 12, color: "var(--gray-500)" }}>{audit.description}</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            );
          })()}

          {/* Speed Test */}
          {(() => {
            const st = results.results.speedtest as {
              summary?: Record<string, unknown>;
              pages?: Array<Record<string, unknown>>;
              issues?: Array<{ id: string; priority: string; title: string; explanation: string; fix: string; benchmark: string }>;
            } | undefined;
            if (!st?.summary) return null;
            const sum = st.summary;
            const ratingColor = (r: unknown) =>
              r === "good" ? "var(--green)" : r === "needs_work" ? "var(--orange)" : "var(--red)";
            return (
              <div className="card mb-4">
                <div className="card-header"><h3>HTTP Speed-Test</h3></div>
                <div className="card-body">
                  <div className="kpi-grid mb-4" style={{ gridTemplateColumns: "repeat(4, 1fr)" }}>
                    <div className="kpi-card">
                      <div className="kpi-value" style={{ color: ratingColor(sum.avg_ttfb_rating) }}>{sum.avg_ttfb_ms != null ? `${sum.avg_ttfb_ms} ms` : "–"}</div>
                      <div className="kpi-label">Ø TTFB</div>
                    </div>
                    <div className="kpi-card">
                      <div className="kpi-value" style={{ color: ratingColor(sum.avg_total_rating) }}>{sum.avg_total_ms != null ? `${Number(sum.avg_total_ms).toFixed(0)} ms` : "–"}</div>
                      <div className="kpi-label">Ø Ladezeit</div>
                    </div>
                    <div className="kpi-card">
                      <div className="kpi-value">{String(sum.pages_tested ?? "–")}</div>
                      <div className="kpi-label">Seiten getestet</div>
                    </div>
                    <div className="kpi-card">
                      <div className="kpi-value">{sum.slowest_ms != null ? `${Number(sum.slowest_ms).toFixed(0)} ms` : "–"}</div>
                      <div className="kpi-label">Langsamste Seite</div>
                    </div>
                  </div>

                  {st.pages && st.pages.length > 0 && (
                    <div className="table-container">
                      <table>
                        <thead>
                          <tr>
                            <th>URL</th>
                            <th>DNS</th>
                            <th>TCP</th>
                            <th>TLS</th>
                            <th>TTFB</th>
                            <th>Transfer</th>
                            <th>Total</th>
                            <th>Komprimierung</th>
                            <th>HTTP</th>
                          </tr>
                        </thead>
                        <tbody>
                          {st.pages.map((p, i) => (
                            <tr key={i}>
                              <td style={{ maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                                <span title={String(p.url)}>{String(p.url).replace(/^https?:\/\//, "").slice(0, 40)}</span>
                              </td>
                              <td>{p.dns_ms != null ? `${p.dns_ms} ms` : "–"}</td>
                              <td>{p.connect_ms != null ? `${p.connect_ms} ms` : "–"}</td>
                              <td>{p.tls_ms != null ? `${p.tls_ms} ms` : "–"}</td>
                              <td style={{ color: ratingColor(p.ttfb_rating), fontWeight: 600 }}>{p.ttfb_ms != null ? `${p.ttfb_ms} ms` : "–"}</td>
                              <td>{p.transfer_ms != null ? `${p.transfer_ms} ms` : "–"}</td>
                              <td style={{ color: ratingColor(p.total_rating), fontWeight: 600 }}>{p.total_ms != null ? `${p.total_ms} ms` : "–"}</td>
                              <td>{p.content_encoding ? String(p.content_encoding) : <span style={{ color: "var(--red)" }}>Nein</span>}</td>
                              <td>{p.http2 ? <span style={{ color: "var(--green)", fontWeight: 600 }}>H2</span> : <span style={{ color: "var(--gray-400)" }}>H1.1</span>}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  {st.issues && st.issues.length > 0 && (
                    <div style={{ marginTop: 12 }}>
                      <h4 style={{ marginBottom: 8, fontSize: 13, fontWeight: 600 }}>Gefundene Probleme</h4>
                      {st.issues.map((iss) => (
                        <div key={iss.id} style={{
                          background: "var(--gray-50, #f9fafb)",
                          border: "1px solid var(--gray-200)",
                          borderLeft: `4px solid ${iss.priority === "P1" ? "var(--red)" : iss.priority === "P2" ? "var(--orange)" : "var(--green)"}`,
                          borderRadius: "0 6px 6px 0",
                          padding: "10px 14px",
                          marginBottom: 8,
                        }}>
                          <div style={{ display: "flex", gap: 8, marginBottom: 4 }}>
                            <span className={`badge badge-${iss.priority === "P1" ? "p1" : iss.priority === "P2" ? "p2" : "p3"}`}>{iss.priority}</span>
                            <strong style={{ fontSize: 13 }}>{iss.title}</strong>
                          </div>
                          <div style={{ fontSize: 12, color: "var(--gray-600)", marginBottom: 3 }}>{iss.explanation}</div>
                          <div style={{ fontSize: 12, color: "var(--gray-500)" }}><strong>Fix:</strong> {iss.fix}</div>
                          <div style={{ fontSize: 11, color: "var(--gray-400)", marginTop: 3 }}>{iss.benchmark}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })()}

          {/* GA4 Channels */}
          {(() => {
            const channels = results.results.ga4_channels as Array<Record<string, unknown>> | undefined;
            if (!channels?.length) return null;
            return (
              <div className="card mb-4">
                <div className="card-header"><h3>GA4 Kanal-Analyse</h3></div>
                <div className="card-body table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Kanal</th>
                        <th>Sessions</th>
                        <th>Conversions</th>
                        <th>Conv.-Rate</th>
                      </tr>
                    </thead>
                    <tbody>
                      {channels.map((ch, i) => (
                        <tr key={i}>
                          <td><strong>{String(ch.channel)}</strong></td>
                          <td>{String(ch.sessions)}</td>
                          <td>{String(ch.conversions)}</td>
                          <td>{String(ch.conversion_rate)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            );
          })()}

          {/* Crawler Summary */}
          {(() => {
            const crawlerData = results.results.crawler as Record<string, unknown> | undefined;
            const summary = crawlerData?.summary as Record<string, number> | undefined;
            const issues = crawlerData?.issues as Record<string, unknown[]> | undefined;
            if (!summary) return null;

            const IssueList = ({ items, label, renderItem }: {
              items: unknown[]; label: string; renderItem: (item: unknown, i: number) => React.ReactNode;
            }) => items.length === 0 ? null : (
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: "var(--gray-600)", marginBottom: 4 }}>{label} ({items.length})</div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                  {items.slice(0, 10).map((item, i) => renderItem(item, i))}
                  {items.length > 10 && <span style={{ fontSize: 11, color: "var(--gray-400)" }}>+{items.length - 10} weitere</span>}
                </div>
              </div>
            );

            return (
              <div className="card mb-4">
                <div className="card-header"><h3>Crawl-Ergebnisse</h3></div>
                <div className="card-body">
                  <div className="table-container mb-4">
                    <table>
                      <thead><tr><th>Check</th><th>Wert</th></tr></thead>
                      <tbody>
                        <tr><td>Seiten gecrawlt</td><td>{summary.total_pages}</td></tr>
                        <tr><td>Fehlerseiten (4xx/5xx)</td><td><span className={summary.pages_error > 0 ? "text-red font-semibold" : ""}>{summary.pages_error}</span></td></tr>
                        <tr><td>Fehlende Titles</td><td><span className={summary.missing_titles > 0 ? "text-orange font-semibold" : ""}>{summary.missing_titles}</span></td></tr>
                        <tr><td>Fehlende Meta-Descriptions</td><td><span className={summary.missing_meta > 0 ? "text-orange" : ""}>{summary.missing_meta}</span></td></tr>
                        <tr><td>Bilder ohne Alt-Text</td><td><span className={summary.images_without_alt > 0 ? "text-orange" : ""}>{summary.images_without_alt}</span></td></tr>
                        <tr><td>Doppelte Titles</td><td><span className={summary.duplicate_titles > 0 ? "text-orange" : ""}>{summary.duplicate_titles ?? 0}</span></td></tr>
                        <tr><td>Seiten mit strukturierten Daten</td><td>{summary.pages_with_structured_data ?? 0}</td></tr>
                        <tr><td>Langsame Seiten (&gt;1s)</td><td><span className={summary.slow_pages_count > 0 ? "text-orange" : ""}>{summary.slow_pages_count ?? 0}</span></td></tr>
                        <tr><td>Ø Ladezeit (Crawler)</td><td>{summary.avg_response_ms != null ? `${summary.avg_response_ms} ms` : "–"}</td></tr>
                      </tbody>
                    </table>
                  </div>

                  {issues && (
                    <div>
                      <IssueList
                        items={issues.missing_title ?? []}
                        label="Seiten ohne Title-Tag"
                        renderItem={(url, i) => (
                          <span key={i} style={{ fontSize: 11, background: "var(--red-light, #fee2e2)", color: "var(--red)", padding: "2px 6px", borderRadius: 4 }}>
                            {String(url).replace(/^https?:\/\/[^/]+/, "").slice(0, 40) || "/"}
                          </span>
                        )}
                      />
                      <IssueList
                        items={issues.missing_meta_description ?? []}
                        label="Seiten ohne Meta-Description"
                        renderItem={(url, i) => (
                          <span key={i} style={{ fontSize: 11, background: "#fff7ed", color: "var(--orange)", padding: "2px 6px", borderRadius: 4 }}>
                            {String(url).replace(/^https?:\/\/[^/]+/, "").slice(0, 40) || "/"}
                          </span>
                        )}
                      />
                      <IssueList
                        items={(issues.title_too_long ?? []) as Array<{url: string; length: number; title: string}>}
                        label="Title zu lang (&gt;60 Zeichen)"
                        renderItem={(item: unknown, i) => {
                          const it = item as {url: string; length: number; title: string};
                          return (
                            <span key={i} title={it.title} style={{ fontSize: 11, background: "#fff7ed", color: "var(--orange)", padding: "2px 6px", borderRadius: 4 }}>
                              {String(it.url).replace(/^https?:\/\/[^/]+/, "").slice(0, 35) || "/"} ({it.length}Z)
                            </span>
                          );
                        }}
                      />
                      <IssueList
                        items={issues.error_pages ?? []}
                        label="Fehlerseiten (4xx/5xx)"
                        renderItem={(url, i) => (
                          <span key={i} style={{ fontSize: 11, background: "#fee2e2", color: "var(--red)", padding: "2px 6px", borderRadius: 4 }}>
                            {String(url).replace(/^https?:\/\/[^/]+/, "").slice(0, 40) || "/"}
                          </span>
                        )}
                      />
                    </div>
                  )}
                </div>
              </div>
            );
          })()}

          {/* AI Analysis Preview */}
          {(() => {
            const ai = results.results.ai_analysis as { text?: string; model?: string } | undefined;
            if (!ai?.text) return null;
            return (
              <div className="card mb-4">
                <div className="card-header">
                  <h3>KI-Analyse</h3>
                  <span className="badge badge-blue">{ai.model}</span>
                </div>
                <div className="card-body">
                  <pre style={{
                    fontFamily: "inherit",
                    fontSize: 13,
                    color: "var(--gray-700)",
                    whiteSpace: "pre-wrap",
                    lineHeight: 1.7,
                    maxHeight: 400,
                    overflowY: "auto",
                  }}>
                    {ai.text}
                  </pre>
                </div>
              </div>
            );
          })()}

          {/* PDF Download */}
          {results.results.pdf_path && (
            <div className="alert alert-success">
              <span>✓</span>
              <div>
                <strong>PDF erfolgreich erstellt.</strong>{" "}
                <button className="btn btn-secondary btn-sm" style={{ marginLeft: 8 }}
                  onClick={() => downloadPdf(analysisId)}>
                  PDF herunterladen
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
