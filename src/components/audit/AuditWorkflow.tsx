import { useState, useEffect, useRef } from "react";
import { getAudit, updateAuditStep } from "../../api";
import type { AuditFull } from "../../api";
import { ArrowLeft, Save, ChevronRight, ChevronLeft, User, Globe } from "lucide-react";
import StepIndicator from "./StepIndicator";
import Step0KickoffForm from "./steps/Step0Kickoff";
import Step1WebsiteForm from "./steps/Step1Website";
import Step2TechnicalScanForm from "./steps/Step2TechnicalScan";
import Step3CrawlForm from "./steps/Step3Crawl";
import Step4SemrushForm from "./steps/Step4Semrush";
import Step5LighthouseForm from "./steps/Step5Lighthouse";
import Step6ReportForm from "./steps/Step6Report";
import type { KickoffData } from "./steps/Step0Kickoff";

interface Props {
  auditId: number;
  onBack: () => void;
}

const STEP_LABELS = ["Kickoff", "Website & Kunden", "Tech. Scan", "Background-Crawl", "SemRush Check", "Lighthouse", "Report / PDF"];

export default function AuditWorkflow({ auditId, onBack }: Props) {
  const [audit, setAudit] = useState<AuditFull | null>(null);
  const [step, setStep] = useState(0);
  const [saving, setSaving] = useState(false);
  const [saveErr, setSaveErr] = useState("");
  const pendingRef = useRef<Record<number, unknown>>({});

  const load = async () => {
    const a = await getAudit(auditId);
    setAudit(a);
    setStep(a.current_step || 0);
  };

  useEffect(() => { load(); }, [auditId]);

  if (!audit) return (
    <div style={{ display: "flex", justifyContent: "center", padding: 64 }}>
      <div className="spinner" />
    </div>
  );

  const saveStep = async (stepNum: number, data: unknown) => {
    setSaving(true);
    setSaveErr("");
    try {
      await updateAuditStep(auditId, stepNum, data as object);
      setAudit((a) => a ? { ...a, current_step: Math.max(a.current_step, stepNum) } : a);
    } catch (e: unknown) {
      setSaveErr(e instanceof Error ? e.message : "Fehler beim Speichern.");
    } finally {
      setSaving(false);
    }
  };

  const goNext = async () => {
    if (pendingRef.current[step] !== undefined) await saveStep(step, pendingRef.current[step]);
    setStep((s) => Math.min(s + 1, 6));
  };
  const goPrev = () => setStep((s) => Math.max(s - 1, 0));
  const setStepData = (n: number) => (data: unknown) => { pendingRef.current[n] = data; };

  const kickoff = audit.step0_kickoff as KickoffData | undefined;
  const websiteUrl = kickoff?.website_url || audit.website_url;

  const stepData = [
    audit.step0_kickoff,
    audit.step1_website,
    audit.step2_crawl,
    audit.step3_semrush,
    audit.step4_lighthouse,
    audit.step5_notes,
    (audit as any).step6_report,
  ];

  return (
    <div>
      {/* Header */}
      <div className="workflow-header">
        <button className="btn btn-secondary btn-sm" onClick={onBack} style={{ gap: 6 }}>
          <ArrowLeft size={14} strokeWidth={2} />
          Zurück
        </button>
        <div style={{ flex: 1, minWidth: 0 }}>
          <h2 style={{ fontSize: 17, fontWeight: 700, margin: 0, color: "var(--gray-900)" }}>{audit.title}</h2>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 3 }}>
            {audit.client_name && (
              <span className="workflow-meta-item">
                <User size={11} strokeWidth={2} />
                {audit.client_name}
              </span>
            )}
            {audit.website_url && (
              <span className="workflow-meta-item">
                <Globe size={11} strokeWidth={2} />
                {audit.website_url}
              </span>
            )}
          </div>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          {saving && <span style={{ fontSize: 12, color: "var(--gray-400)" }}>Speichert...</span>}
          {saveErr && <span style={{ fontSize: 12, color: "var(--red)" }}>{saveErr}</span>}
          <span className="workflow-step-badge">{STEP_LABELS[step]}</span>
        </div>
      </div>

      <StepIndicator current={step} maxReached={audit.current_step} onNavigate={setStep} />

      {/* Step content */}
      <div className="workflow-content">
        {step === 0 && <Step0KickoffForm initial={stepData[0] as any} onChange={setStepData(0)} />}
        {step === 1 && <Step1WebsiteForm initial={stepData[1] as any} onChange={setStepData(1)} />}
        {step === 2 && <Step2TechnicalScanForm initial={stepData[2] as any} onChange={setStepData(2)} />}
        {step === 3 && (
          <Step3CrawlForm auditId={auditId} initial={stepData[3] as any}
            onUpdate={(data) => { pendingRef.current[3] = data; setAudit((a) => a ? { ...a, step3_semrush: data as any } : a); }} />
        )}
        {step === 4 && (
          <Step4SemrushForm auditId={auditId} initial={stepData[4] as any}
            onUpdate={(data) => { pendingRef.current[4] = data; setAudit((a) => a ? { ...a, step4_lighthouse: data as any } : a); }} />
        )}
        {step === 5 && (
          <Step5LighthouseForm auditId={auditId} websiteUrl={websiteUrl} initial={stepData[5] as any} onChange={setStepData(5)} />
        )}
        {step === 6 && (
          <Step6ReportForm auditId={auditId} pdfPath={audit.pdf_path} initial={stepData[6] as any}
            onChange={setStepData(6)}
            onPdfGenerated={(path) => setAudit((a) => a ? { ...a, pdf_path: path, status: "complete" } : a)} />
        )}
      </div>

      {/* Navigation */}
      <div className="workflow-nav">
        <button onClick={goPrev} disabled={step === 0} className="btn btn-secondary" style={{ gap: 6, opacity: step === 0 ? 0.4 : 1 }}>
          <ChevronLeft size={15} strokeWidth={2} />
          Zurück
        </button>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={() => saveStep(step, pendingRef.current[step] || {})} disabled={saving} className="btn btn-secondary" style={{ gap: 6 }}>
            <Save size={14} strokeWidth={1.75} />
            Speichern
          </button>
          {step < 6 && (
            <button onClick={goNext} disabled={saving} className="btn btn-primary" style={{ gap: 6 }}>
              Weiter
              <ChevronRight size={15} strokeWidth={2} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
