const selectClass = {
  light:
    "p-2 rounded-lg border border-slate-200 bg-white text-slate-900 shadow-sm",
  dark:
    "p-2 rounded-lg border border-slate-600 bg-slate-800 text-white shadow-sm",
};

export default function PeriodSelector({ periodos = [], sel, setSel, variant = "light" }) {
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

  const selectCls = selectClass[variant] ?? selectClass.light;

  return (
    <div className="flex gap-3 flex-wrap">
      <select
        className={selectCls}
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
        className={selectCls}
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
