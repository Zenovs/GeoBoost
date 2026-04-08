import { useRef, useState } from "react";

interface Props {
  label: string;
  hint?: string;
  onFile: (file: File) => Promise<void>;
  loading?: boolean;
  done?: boolean;
}

export default function CsvUploadZone({ label, hint, onFile, loading, done }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [err, setErr] = useState("");

  const handle = async (file: File) => {
    setErr("");
    if (!file.name.endsWith(".csv")) {
      setErr("Bitte eine .csv Datei hochladen.");
      return;
    }
    try {
      await onFile(file);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "Fehler beim Verarbeiten der Datei.");
    }
  };

  return (
    <div>
      <div
        onClick={() => !loading && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          const f = e.dataTransfer.files[0];
          if (f) handle(f);
        }}
        style={{
          border: `2px dashed ${dragging ? "var(--blue-400,#60a5fa)" : done ? "#16a34a" : "var(--gray-300,#d1d5db)"}`,
          borderRadius: 10,
          padding: "28px 20px",
          textAlign: "center",
          cursor: loading ? "wait" : "pointer",
          background: dragging ? "rgba(37,99,235,0.04)" : done ? "rgba(22,163,74,0.04)" : "var(--gray-50,#f9fafb)",
          transition: "all 0.2s",
        }}
      >
        <div style={{ fontSize: 28, marginBottom: 8 }}>
          {loading ? "⏳" : done ? "✅" : "📂"}
        </div>
        <div style={{ fontWeight: 600, fontSize: 14, color: "var(--gray-700,#374151)", marginBottom: 4 }}>
          {loading ? "Wird verarbeitet..." : done ? "Datei erfolgreich verarbeitet" : label}
        </div>
        {hint && !done && (
          <div style={{ fontSize: 12, color: "var(--gray-400,#9ca3af)" }}>{hint}</div>
        )}
        {!loading && (
          <button
            type="button"
            style={{
              marginTop: 12,
              background: done ? "#16a34a" : "var(--blue-600,#2563eb)",
              color: "white",
              border: "none",
              borderRadius: 6,
              padding: "7px 18px",
              fontSize: 13,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            {done ? "Neue Datei hochladen" : "CSV auswählen"}
          </button>
        )}
      </div>
      {err && (
        <div style={{ color: "#dc2626", fontSize: 12, marginTop: 6 }}>{err}</div>
      )}
      <input
        ref={inputRef}
        type="file"
        accept=".csv"
        style={{ display: "none" }}
        onChange={(e) => { const f = e.target.files?.[0]; if (f) handle(f); e.target.value = ""; }}
      />
    </div>
  );
}
