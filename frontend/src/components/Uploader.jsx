import { useState } from "react";
import { uploadFile } from "../api/client";

export default function Uploader({ onDone }) {
  const [busy, setBusy] = useState(false);
  async function onChange(e) {
    const f = e.target.files[0];
    if (!f) return;
    setBusy(true);
    try { await uploadFile(f); onDone?.(); } finally { setBusy(false); e.target.value = ""; }
  }
  return (
    <label className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-xl cursor-pointer">
      {busy ? "Procesando..." : "Subir archivo (.xlsx)"}
      <input type="file" accept=".xlsx,.xls,.csv" className="hidden" onChange={onChange} disabled={busy} />
    </label>
  );
}
