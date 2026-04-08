/**
 * GeoBoost – API Client
 * Kommuniziert mit dem Python FastAPI Backend auf localhost:8765
 */

const BASE = "http://127.0.0.1:8765/api";

async function req<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const opts: RequestInit = { method, headers: { "Content-Type": "application/json" } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${BASE}${path}`, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

const get = <T>(path: string) => req<T>("GET", path);
const post = <T>(path: string, body: unknown) => req<T>("POST", path, body);
const put = <T>(path: string, body: unknown) => req<T>("PUT", path, body);
const del = <T>(path: string) => req<T>("DELETE", path);

// ── Health ───────────────────────────────────────────────────────────────────
export const checkHealth = () => get<{ status: string; version: string }>("/health");

// ── Config ───────────────────────────────────────────────────────────────────
export interface AppConfig {
  storage_path?: string;
  google_credentials_path?: string;
  pagespeed_api_key?: string;
  ollama_model?: string;
  crawler_max_depth?: number;
  crawler_max_urls?: number;
  primary_color?: string;
  accent_color?: string;
  company_name?: string;
  company_contact?: string;
}
export const getConfig = () => get<AppConfig>("/config");
export const updateConfig = (c: Partial<AppConfig>) => put<{ ok: boolean }>("/config", c);

export const uploadCredentials = async (file: File): Promise<{ ok: boolean; path: string }> => {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/config/upload-credentials`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`);
  return res.json();
};

// ── Projects ─────────────────────────────────────────────────────────────────
export interface Project {
  id: number;
  name: string;
  website_url: string;
  ga4_property_id?: string;
  created_at: string;
  updated_at: string;
  analysis_count: number;
  last_analysis?: string;
  kickoff_data?: KickoffData;
  analyses?: AnalysisSummary[];
}

export interface AnalysisSummary {
  id: number;
  status: string;
  progress: number;
  status_message: string;
  created_at: string;
  completed_at?: string;
}

export const listProjects = () => get<Project[]>("/projects");
export const getProject = (id: number) => get<Project>(`/projects/${id}`);
export const deleteProject = (id: number) => del<{ ok: boolean }>(`/projects/${id}`);

// ── Analysis ─────────────────────────────────────────────────────────────────
export interface KickoffData {
  website_url: string;
  ga4_property_id: string;
  project_name: string;
  analysis_period: string;
  primary_goal: string;
  main_action: string;
  lead_value?: number;
  target_audience: string;
  audience_type: string;
  seasonality: boolean;
  seasonality_notes: string;
  active_campaigns: string[];
  expected_channels: string[];
  known_issues: string;
  tech_feedback: string;
  recent_changes: boolean;
  recent_changes_notes: string;
  responsible_person: string;
  ga4_setup_by: string;
  third_party_tools: string[];
  competitors: string;
  main_question: string;
  use_search_console: boolean;
  search_console_url?: string;
}

export interface CheckConfig {
  crawling: boolean;
  pagespeed: boolean;
  speedtest: boolean;
  ga4_traffic: boolean;
  ga4_channels: boolean;
  ga4_landingpages: boolean;
  ga4_devices: boolean;
  search_console: boolean;
  ai_analysis: boolean;
  pdf_report: boolean;
}

export interface AnalysisStatus {
  step: string;
  progress: number;
  message: string;
  error?: string;
  done: boolean;
}

export interface AnalysisResults {
  id: number;
  project_id: number;
  status: string;
  results?: {
    crawler?: unknown;
    pagespeed?: unknown;
    speedtest?: unknown;
    ga4_traffic?: unknown;
    ga4_channels?: unknown;
    ga4_devices?: unknown;
    ai_analysis?: { text: string; model: string };
    pdf_path?: string;
  };
  created_at: string;
  completed_at?: string;
}

// ── Update ───────────────────────────────────────────────────────────────────
export interface VersionInfo {
  commit: string;
  branch: string;
  date: string;
  message: string;
  error: string | null;
}
export interface UpdateResult {
  success: boolean;
  log: string;
  commit: string;
  date: string;
  restart_required: boolean;
}
export const getVersion = () => get<VersionInfo>("/version");
export const runUpdate = () => post<UpdateResult>("/update", {});

export const startAnalysis = (kickoff: KickoffData, checks: CheckConfig) =>
  post<{ analysis_id: number; project_id: number }>("/analyze/start", { kickoff, checks });

export const getAnalysisStatus = (id: number) =>
  get<AnalysisStatus>(`/analyze/status/${id}`);

export const getAnalysisResults = (id: number) =>
  get<AnalysisResults>(`/analyze/results/${id}`);

export const getPdfUrl = (analysisId: number) =>
  `${BASE}/reports/${analysisId}/pdf`;

export const downloadPdf = (analysisId: number) => {
  const url = getPdfUrl(analysisId);
  const a = document.createElement("a");
  a.href = url;
  a.download = `geoboost_report_${analysisId}.pdf`;
  a.click();
};

// ── Audits ────────────────────────────────────────────────────────────────────

export interface AuditSummary {
  id: number;
  title: string;
  client_name: string;
  website_url: string;
  status: "draft" | "in_progress" | "complete";
  current_step: number;
  pdf_path?: string;
  created_at: string;
  updated_at: string;
}

export interface Step0Kickoff {
  client_name: string;
  website_url: string;
  analysis_period: string;
  analysis_date: string;
  analyst_name: string;
  responsible_person: string;
  main_goals: string;
  notes: string;
}

export interface ChannelRow { channel: string; sessions: number; pct: number }
export interface TopPage { page: string; sessions: number }

export interface Step1Website {
  sessions_total?: number;
  sessions_organic?: number;
  sessions_paid?: number;
  sessions_direct?: number;
  sessions_social?: number;
  new_users_total?: number;
  bounce_rate?: number;
  avg_session_duration?: string;
  conversions_total?: number;
  conversion_rate?: number;
  channel_breakdown?: ChannelRow[];
  device_breakdown?: { desktop?: number; mobile?: number; tablet?: number };
  top_pages?: TopPage[];
  notes?: string;
}

export interface CrawlIssue {
  url: string;
  status_code: number;
  title: string;
  title_length: number;
  title_issue: string;
  meta: string;
  meta_length: number;
  meta_issue: string;
  h1: string;
  h1_issue: string;
  response_time_ms: number;
  flags: string[];
}

export interface CrawlSummary {
  total_urls: number;
  ok_200: number;
  redirects_3xx: number;
  errors_4xx: number;
  errors_5xx: number;
  missing_title: number;
  title_too_long: number;
  missing_meta: number;
  meta_too_long: number;
  missing_h1: number;
  slow_pages: number;
}

export interface Step2Crawl {
  summary?: CrawlSummary;
  issues?: CrawlIssue[];
  notes?: string;
}

export interface SemrushIssue {
  issue: string;
  count: number;
  severity: "error" | "warning" | "notice";
  category: string;
}

export interface SemrushSummary {
  total_issues: number;
  errors: number;
  warnings: number;
  notices: number;
}

export interface Step3Semrush {
  summary?: SemrushSummary;
  issues?: SemrushIssue[];
  notes?: string;
}

export interface Step4Lighthouse {
  mobile_performance?: number;
  mobile_accessibility?: number;
  mobile_best_practices?: number;
  mobile_seo?: number;
  desktop_performance?: number;
  desktop_accessibility?: number;
  desktop_best_practices?: number;
  desktop_seo?: number;
  cwv_lcp?: string;
  cwv_fid?: string;
  cwv_cls?: string;
  notes?: string;
}

export interface Step5Notes {
  findings: string;
  recommendations: string;
  general_notes: string;
}

export interface AuditFull extends AuditSummary {
  step0_kickoff?: Step0Kickoff;
  step1_website?: Step1Website;
  step2_crawl?: Step2Crawl;
  step3_semrush?: Step3Semrush;
  step4_lighthouse?: Step4Lighthouse;
  step5_notes?: Step5Notes;
  project_id?: number;
}

export const listAudits = () => get<AuditSummary[]>("/audits");
export const createAudit = (title: string, client_name = "", website_url = "") =>
  post<{ id: number }>("/audits", { title, client_name, website_url });
export const getAudit = (id: number) => get<AuditFull>(`/audits/${id}`);
export const deleteAudit = (id: number) => del<{ ok: boolean }>(`/audits/${id}`);
export const updateAuditStep = (id: number, step: number, data: object) =>
  put<{ ok: boolean }>(`/audits/${id}/step`, { step, data });

export const uploadScreamingFrogCsv = async (auditId: number, file: File): Promise<Step2Crawl> => {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/audits/${auditId}/upload/screaming-frog`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`);
  return res.json();
};

export const uploadSemrushCsv = async (auditId: number, file: File): Promise<Step3Semrush> => {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/audits/${auditId}/upload/semrush`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`);
  return res.json();
};

export const fetchLighthouseForAudit = (auditId: number, websiteUrl: string) =>
  post<Step4Lighthouse>(`/audits/${auditId}/lighthouse/fetch`, { website_url: websiteUrl });

export const generateAuditPdf = (auditId: number) =>
  post<{ pdf_path: string }>(`/audits/${auditId}/report/generate`, {});

export const getAuditPdfUrl = (auditId: number) => `${BASE}/audits/${auditId}/report/pdf`;
