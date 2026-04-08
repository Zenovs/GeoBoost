import { useState, useEffect, useRef } from "react";
import type { AuditFull, Step0Kickoff, Step1Website, Step2Crawl, Step3Semrush, Step4Lighthouse, Step5Notes } from "../../api";
import { getAudit, updateAuditStep } from "../../api";
import StepIndicator from "./StepIndicator";
import Step0KickoffForm from "./steps/Step0Kickoff";
import Step1WebsiteForm from "./steps/Step1Website";
import Step2CrawlForm from "./steps/Step2Crawl";
import Step3SemrushForm from "./steps/Step3Semrush";
import Step4LighthouseForm from "./steps/Step4Lighthouse";
import Step5ReportForm from "./steps/Step5Report";

interface Props {
  auditId: number;
  onBack: () => void;
}

export default function AuditWorkflow({ auditId, onBack }: Props) {
  const [audit, setAudit] = useState<AuditFull | null>(null);
  const [step, setStep] = useState(0);
  const [saving, setSaving] = useState(false);
  const [saveErr, setSaveErr] = useState("");

  // Pending step data collected from child form onChange
  const pendingRef = useRef<Record<string, unknown>>({});

  const load = async () => {
    const a = await getAudit(auditId);
    setAudit(a);
    setStep(a.current_step || 0);
  };

  useEffect(() => { load(); }, [auditId]);

  if (!audit) {
    return (
      <div style={{ textAlign: "center", padding: 48, color: "var(--gray-400,#9ca3af)" }}>
        Analyse wird geladen...
      </div>
    );
  }

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
    if (pendingRef.current[step] !== undefined) {
      await saveStep(step, pendingRef.current[step]);
    }
    setStep((s) => Math.min(s + 1, 5));
  };

  const goPrev = () => setStep((s) => Math.max(s - 1, 0));

  const handleNavigate = (s: number) => setStep(s);

  const setStepData = (stepNum: number) => (data: unknown) => {
    pendingRef.current[stepNum] = data;
  };

  const websiteUrl = (audit.step0_kickoff as Step0Kickoff | undefined)?.website_url || audit.website_url;

  return (
    <div>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 28 }}>
        <button
          onClick={onBack}
          style={{ background: "none", border: "1px solid var(--gray-200,#e5e7eb)", borderRadius: 8, padding: "7px 14px", fontSize: 13, cursor: "pointer", color: "var(--gray-600,#4b5563)" }}
        >
          ← Zurück
        </button>
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 800, margin: 0, color: "var(--gray-900,#111827)" }}>{audit.title}</h2>
          {(audit.client_name || audit.website_url) && (
            <div style={{ fontSize: 12, color: "var(--gray-400,#9ca3af)", marginTop: 2 }}>
              {audit.client_name && <span style={{ marginRight: 10 }}>{audit.client_name}</span>}
              {audit.website_url && <span>{audit.website_url}</span>}
            </div>
          )}
        </div>
        <div style={{ marginLeft: "auto", display: "flex", gap: 8, alignItems: "center" }}>
          {saving && <span style={{ fontSize: 12, color: "var(--gray-400,#9ca3af)" }}>Speichert...</span>}
          {saveErr && <span style={{ fontSize: 12, color: "#dc2626" }}>{saveErr}</span>}
        </div>
      </div>

      <StepIndicator current={step} maxReached={audit.current_step} onNavigate={handleNavigate} />

      {/* Step content */}
      <div style={{
        background: "white",
        border: "1px solid var(--gray-200,#e5e7eb)",
        borderRadius: 14,
        padding: "28px 32px",
        minHeight: 400,
      }}>
        {step === 0 && (
          <Step0KickoffForm
            initial={audit.step0_kickoff as Step0Kickoff | undefined}
            onChange={setStepData(0)}
          />
        )}
        {step === 1 && (
          <Step1WebsiteForm
            initial={audit.step1_website as Step1Website | undefined}
            onChange={setStepData(1)}
          />
        )}
        {step === 2 && (
          <Step2CrawlForm
            auditId={auditId}
            initial={audit.step2_crawl as Step2Crawl | undefined}
            onUpdate={(data) => {
              pendingRef.current[2] = data;
              setAudit((a) => a ? { ...a, step2_crawl: data } : a);
            }}
          />
        )}
        {step === 3 && (
          <Step3SemrushForm
            auditId={auditId}
            initial={audit.step3_semrush as Step3Semrush | undefined}
            onUpdate={(data) => {
              pendingRef.current[3] = data;
              setAudit((a) => a ? { ...a, step3_semrush: data } : a);
            }}
          />
        )}
        {step === 4 && (
          <Step4LighthouseForm
            auditId={auditId}
            websiteUrl={websiteUrl}
            initial={audit.step4_lighthouse as Step4Lighthouse | undefined}
            onChange={setStepData(4)}
          />
        )}
        {step === 5 && (
          <Step5ReportForm
            auditId={auditId}
            pdfPath={audit.pdf_path}
            initial={audit.step5_notes as Step5Notes | undefined}
            onChange={setStepData(5)}
            onPdfGenerated={(path) => {
              setAudit((a) => a ? { ...a, pdf_path: path, status: "complete" } : a);
            }}
          />
        )}
      </div>

      {/* Navigation buttons */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 20 }}>
        <button
          onClick={goPrev}
          disabled={step === 0}
          style={{
            background: "var(--gray-100,#f3f4f6)",
            color: "var(--gray-700,#374151)",
            border: "none",
            borderRadius: 8,
            padding: "10px 22px",
            fontSize: 14,
            fontWeight: 600,
            cursor: step === 0 ? "default" : "pointer",
            opacity: step === 0 ? 0.4 : 1,
          }}
        >
          ← Zurück
        </button>

        <div style={{ display: "flex", gap: 10 }}>
          <button
            onClick={() => saveStep(step, pendingRef.current[step] || {})}
            disabled={saving}
            style={{
              background: "var(--gray-100,#f3f4f6)",
              color: "var(--gray-700,#374151)",
              border: "none",
              borderRadius: 8,
              padding: "10px 22px",
              fontSize: 14,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            💾 Speichern
          </button>

          {step < 5 && (
            <button
              onClick={goNext}
              disabled={saving}
              style={{
                background: "var(--blue-600,#2563eb)",
                color: "white",
                border: "none",
                borderRadius: 8,
                padding: "10px 24px",
                fontSize: 14,
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              Weiter →
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
