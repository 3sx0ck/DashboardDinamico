import { useState } from "react";
import { uploadFile } from "../api/client";

export default function Uploader({ onDone }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  async function onChange(e) {
    const f = e.target.files[0];
    if (!f) return;
    setBusy(true);
    setError(null);
    try {
      const resp = await uploadFile(f);
      onDone?.(resp);
    } catch (err) {
      setError(err?.response?.data?.detail || "Error al procesar el archivo.");
    } finally {
      setBusy(false);
      e.target.value = "";
    }
  }

  return (
    <>
      <label className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-xl cursor-pointer">
        Subir archivo (.xlsx)
        <input type="file" accept=".xlsx,.xls,.csv" className="hidden" onChange={onChange} disabled={busy} />
      </label>

      {busy && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-8 flex flex-col items-center gap-4">
            <div className="h-10 w-10 rounded-full border-4 border-indigo-500 border-t-transparent animate-spin" />
            <p className="text-slate-700 dark:text-slate-200 font-medium">Generando dashboard...</p>
          </div>
        </div>
      )}

      {error && !busy && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={() => setError(null)}>
          <div
            className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6 max-w-sm text-center space-y-3"
            onClick={(e) => e.stopPropagation()}
          >
            <p className="text-red-500 font-medium">{error}</p>
            <button
              className="px-4 py-1.5 rounded-lg bg-slate-200 dark:bg-slate-700 dark:text-white text-sm"
              onClick={() => setError(null)}
            >
              Cerrar
            </button>
          </div>
        </div>
      )}
    </>
  );
}
