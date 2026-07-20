import { useState, useEffect, useCallback } from "react";
import { getDashboard } from "../api/client";

export function useDashboard() {
  const [filters, setFilters] = useState({});
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const reload = useCallback(() => {
    setLoading(true);
    getDashboard(filters).then(setData).finally(() => setLoading(false));
  }, [filters]);
  useEffect(() => { reload(); }, [reload]);
  return { data, loading, filters, setFilters, reload };
}
