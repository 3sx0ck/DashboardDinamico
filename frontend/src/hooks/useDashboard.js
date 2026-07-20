import { useState, useEffect, useCallback, useRef } from "react";
import { getDashboard, getPeriodos } from "../api/client";

export function useDashboard() {
  const [filters, setFilters] = useState({});
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [periodos, setPeriodos] = useState([]);
  const [periodosLoaded, setPeriodosLoaded] = useState(false);
  const [sel, setSelState] = useState({ periodo: undefined, uploadId: undefined });
  const selInitialized = useRef(false);

  const loadPeriodos = useCallback(async () => {
    let p = [];
    try {
      p = (await getPeriodos()) || [];
    } catch {
      p = [];
    }
    setPeriodos(p);
    setPeriodosLoaded(true);
    return p;
  }, []);

  useEffect(() => {
    loadPeriodos();
  }, [loadPeriodos]);

  // Default selection: first week of first periodo (latest snapshot), set once.
  useEffect(() => {
    if (selInitialized.current || !periodosLoaded) return;
    const first = periodos[0];
    const firstWeek = first?.weeks?.[0];
    selInitialized.current = true;
    if (firstWeek) setSelState({ periodo: first.periodo, uploadId: firstWeek.uploadId });
  }, [periodos, periodosLoaded]);

  const setSel = useCallback((periodo, uploadId) => {
    selInitialized.current = true;
    setSelState({ periodo, uploadId });
  }, []);

  const reload = useCallback(() => {
    setLoading(true);
    const params = sel.uploadId
      ? { upload_id: sel.uploadId, torre: filters.torre }
      : { torre: filters.torre };
    return getDashboard(params).then(setData).finally(() => setLoading(false));
  }, [sel, filters]);

  useEffect(() => {
    // Wait until periodos have been fetched at least once (so we know whether
    // there's an uploadId to select) before hitting /api/dashboard, unless
    // there are no periodos at all (empty DB) — then fetch with no params.
    if (!periodosLoaded) return;
    reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sel, filters, periodosLoaded]);

  const refreshAfterUpload = useCallback(
    async (newUploadId) => {
      const fresh = await loadPeriodos();
      let periodo;
      for (const p of fresh) {
        if ((p.weeks || []).some((w) => w.uploadId === newUploadId)) {
          periodo = p.periodo;
          break;
        }
      }
      setSel(periodo, newUploadId);
    },
    [loadPeriodos, setSel]
  );

  return { data, loading, periodos, sel, setSel, filters, setFilters, reload, refreshAfterUpload };
}
