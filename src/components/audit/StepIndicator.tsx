interface Props {
  current: number;
  maxReached: number;
  onNavigate: (step: number) => void;
}

const STEPS = [
  { label: "Kickoff" },
  { label: "Website" },
  { label: "Tech Scan" },
  { label: "Crawl" },
  { label: "SemRush" },
  { label: "Lighthouse" },
  { label: "Report" },
];

export default function StepIndicator({ current, maxReached, onNavigate }: Props) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 0, marginBottom: 32, overflowX: "auto" }}>
      {STEPS.map((step, i) => {
        const done = i < current;
        const active = i === current;
        const reachable = i <= maxReached;
        return (
          <div key={i} style={{ display: "flex", alignItems: "center", flexShrink: 0 }}>
            <div onClick={() => reachable && onNavigate(i)}
              style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 5, cursor: reachable ? "pointer" : "default", opacity: reachable ? 1 : 0.4 }}>
              <div style={{
                width: 32, height: 32, borderRadius: "50%",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontWeight: 700, fontSize: 12,
                background: done ? "#16a34a" : active ? "#2563eb" : "#e5e7eb",
                color: done || active ? "white" : "#6b7280",
                boxShadow: active ? "0 0 0 3px rgba(37,99,235,0.25)" : "none",
                transition: "all 0.2s",
              }}>
                {done ? "✓" : i + 1}
              </div>
              <span style={{
                fontSize: 10, fontWeight: active ? 700 : 500, whiteSpace: "nowrap",
                color: active ? "#2563eb" : done ? "#16a34a" : "#6b7280",
              }}>
                {step.label}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <div style={{ width: 28, height: 2, background: i < current ? "#16a34a" : "#e5e7eb", margin: "0 2px", marginBottom: 18, transition: "background 0.3s", flexShrink: 0 }} />
            )}
          </div>
        );
      })}
    </div>
  );
}
