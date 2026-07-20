export default function PeriodSelector({ periodos = [], sel, setSel }) {
  if (!periodos.length) return null;

  const mesActual = periodos.find((p) => p.periodo === sel?.periodo) || periodos[0];
  const weeks = mesActual?.weeks || [];

  function onMesChange(e) {
    const periodo = e.target.value;
    const p = periodos.find((x) => x.periodo === periodo);
    const firstWeek = p?.weeks?.[0];
    setSel(periodo, firstWeek?.uploadId);
  }

  function onSemanaChange(e) {
    const uploadId = Number(e.target.value);
    setSel(mesActual.periodo, uploadId);
  }

  return (
    <div className="flex gap-3 flex-wrap">
      <select
        className="p-2 rounded-lg bg-slate-100 dark:bg-slate-700 dark:text-white"
        value={mesActual?.periodo || ""}
        onChange={onMesChange}
      >
        {periodos.map((p) => (
          <option key={p.periodo} value={p.periodo}>
            {p.periodo}
          </option>
        ))}
      </select>
      <select
        className="p-2 rounded-lg bg-slate-100 dark:bg-slate-700 dark:text-white"
        value={sel?.uploadId || ""}
        onChange={onSemanaChange}
      >
        {weeks.map((w) => (
          <option key={w.uploadId} value={w.uploadId}>
            {w.semana}
          </option>
        ))}
      </select>
    </div>
  );
}
