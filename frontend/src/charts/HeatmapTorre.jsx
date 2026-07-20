const COLOR = {
  ESC: "#10b981",
  PROM: "#3b82f6",
  RES: "#f59e0b",
  DISP: "#64748b",
  INVM: "#8b5cf6",
  BLOQ: "#ef4444",
};
const FALLBACK_COLOR = "#334155";

const LABELS = {
  ESC: "Escriturado",
  PROM: "Promesado",
  RES: "Reservado",
  DISP: "Disponible",
  INVM: "Invendible/Móvil",
  BLOQ: "Bloqueado",
};

export default function HeatmapTorre({ grilla }) {
  if (!grilla || grilla.length === 0) {
    return <p className="text-slate-400">Sin unidades para mostrar.</p>;
  }
  const torres = [...new Set(grilla.map((u) => u.torre))].sort((a, b) => a - b);
  const estadosPresentes = [...new Set(grilla.map((u) => u.estado))];

  return (
    <div className="space-y-10">
      {torres.map((torre) => {
        const unidades = grilla.filter((u) => u.torre === torre);
        const pisos = [...new Set(unidades.map((u) => u.piso))].sort((a, b) => b - a);
        return (
          <div key={torre}>
            <h4 className="text-slate-300 font-medium mb-2">Torre {torre}</h4>
            <div className="space-y-1">
              {pisos.map((p) => (
                <div key={p} className="flex gap-1 items-center flex-wrap">
                  <span className="w-8 text-xs text-slate-400 shrink-0">{p}</span>
                  {unidades
                    .filter((u) => u.piso === p)
                    .map((u, i) => (
                      <span
                        key={`${torre}-${p}-${i}-${u.depto}`}
                        title={`${u.depto} · ${LABELS[u.estado] || u.estado}`}
                        className="w-6 h-6 rounded"
                        style={{ background: COLOR[u.estado] || FALLBACK_COLOR }}
                      />
                    ))}
                </div>
              ))}
            </div>
          </div>
        );
      })}

      <div className="flex flex-wrap gap-4 pt-2 border-t border-slate-700/60">
        {estadosPresentes.map((estado) => (
          <span key={estado} className="flex items-center gap-2 text-xs text-slate-400">
            <span
              className="w-3 h-3 rounded-sm inline-block"
              style={{ background: COLOR[estado] || FALLBACK_COLOR }}
            />
            {LABELS[estado] || estado}
          </span>
        ))}
      </div>
    </div>
  );
}
