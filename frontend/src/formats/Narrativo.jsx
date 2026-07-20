import { Link } from "react-router-dom";
import { useDashboard } from "../hooks/useDashboard";
import HeatmapTorre from "../charts/HeatmapTorre";
import EvolucionChart from "../charts/EvolucionChart";
import PeriodSelector from "../components/PeriodSelector";

const fmt = (n) => new Intl.NumberFormat("es-CL").format(Math.round(n || 0));

export default function Narrativo() {
  const { data, loading, periodos, sel, setSel } = useDashboard();
  if (loading || !data) return <div className="min-h-screen bg-slate-900 p-8 text-slate-400">Cargando...</div>;
  if (data.empty) return <div className="min-h-screen bg-slate-900 p-8 text-slate-400">Sin datos. Suba un archivo.</div>;

  return (
    <div className="bg-slate-900 text-white">
      <Link
        to="/"
        className="fixed top-6 left-6 z-10 text-sm text-slate-400 hover:text-white transition"
      >
        &larr; Volver
      </Link>

      <div className="fixed top-6 right-6 z-10">
        <PeriodSelector periodos={periodos} sel={sel} setSel={setSel} />
      </div>

      <section className="min-h-[70vh] flex flex-col justify-center items-center text-center px-6">
        <p className="text-slate-400 uppercase tracking-[0.3em] text-sm">
          Parque Mackenna · {data.periodo} · Semana {data.semana}
        </p>
        <h1 className="text-6xl sm:text-7xl lg:text-8xl font-black mt-6 bg-gradient-to-br from-white to-slate-400 bg-clip-text text-transparent">
          {fmt(data.kpis.ventaTotalUF)} UF
        </h1>
        <p className="text-slate-400 mt-3 text-lg">Venta total</p>
        <div className="flex gap-10 mt-14 text-center">
          <div>
            <p className="text-3xl font-bold">{fmt(data.kpis.xRecibirUF)} UF</p>
            <p className="text-slate-500 text-sm mt-1">Por recibir</p>
          </div>
          <div>
            <p className="text-3xl font-bold">{fmt(data.kpis.escriturados)}</p>
            <p className="text-slate-500 text-sm mt-1">Escriturados</p>
          </div>
          <div>
            <p className="text-3xl font-bold">{fmt(data.funnel?.promesas)}</p>
            <p className="text-slate-500 text-sm mt-1">Promesas</p>
          </div>
        </div>
      </section>

      <section className="min-h-screen p-10 lg:p-16 flex flex-col justify-center">
        <h2 className="text-3xl font-bold mb-2">Estado de unidades</h2>
        <p className="text-slate-400 mb-8 max-w-2xl">
          Cada celda representa una unidad. El color indica su estado comercial dentro de la torre.
        </p>
        <HeatmapTorre grilla={data.grillaUnidades} />
      </section>

      <section className="min-h-screen p-10 lg:p-16 flex flex-col justify-center">
        <h2 className="text-3xl font-bold mb-8">Evolución comercial</h2>
        <div className="max-w-3xl w-full h-80 relative">
          <EvolucionChart evolucion={data.evolucionMensual} />
        </div>
      </section>
    </div>
  );
}
