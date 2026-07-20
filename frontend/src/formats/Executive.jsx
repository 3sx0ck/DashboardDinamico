import { useAuth } from "../auth/AuthContext";
import { useDashboard } from "../hooks/useDashboard";
import KpiCard from "../components/KpiCard";
import Uploader from "../components/Uploader";
import FilterBar from "../components/FilterBar";
import FunnelChart from "../charts/FunnelChart";
import StockTorreChart from "../charts/StockTorreChart";
import EvolucionChart from "../charts/EvolucionChart";
import MediosChart from "../charts/MediosChart";
import CanalChart from "../charts/CanalChart";

export default function Executive() {
  const { auth } = useAuth();
  const { data, loading, filters, setFilters, reload } = useDashboard();
  if (loading || !data) return <div className="p-8 text-slate-400">Cargando...</div>;
  if (data.empty) return <div className="p-8 text-slate-400">Sin datos. Suba un archivo.</div>;
  const torres = [...new Set((data.ventas || []).map((v) => v.torre))];
  const fmt = (n) => new Intl.NumberFormat("es-CL").format(Math.round(n || 0));
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 p-6 space-y-6">
      <header className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Parque Mackenna · {data.periodo}</h1>
        <div className="flex gap-3">
          <FilterBar filters={filters} setFilters={setFilters} torres={torres} />
          {auth.rol === "admin" && <Uploader onDone={reload} />}
        </div>
      </header>
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard label="Venta total" value={fmt(data.kpis.ventaTotalUF)} suffix=" UF" />
        <KpiCard label="Por recibir" value={fmt(data.kpis.xRecibirUF)} suffix=" UF" />
        <KpiCard label="Escriturados" value={fmt(data.kpis.escriturados)} />
        <KpiCard label="Promesas" value={fmt(data.funnel?.promesas)} />
      </section>
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Funnel comercial"><FunnelChart funnel={data.funnel} /></Card>
        <Card title="Stock por torre"><StockTorreChart stock={data.stock} /></Card>
        <Card title="Evolución mensual"><EvolucionChart evolucion={data.evolucionMensual} /></Card>
        <Card title="Capital vs Brokers"><CanalChart canal={data.canal} /></Card>
        <Card title="Medios de llegada"><MediosChart medios={data.marketing.medios} /></Card>
      </section>
    </div>
  );
}
function Card({ title, children }) {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-md p-5">
      <h3 className="text-slate-700 dark:text-slate-200 font-semibold mb-3">{title}</h3>
      {children}
    </div>
  );
}
