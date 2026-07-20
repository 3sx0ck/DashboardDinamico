import { useState } from "react";
import { useAuth } from "../auth/AuthContext";
import { useDashboard } from "../hooks/useDashboard";
import Uploader from "../components/Uploader";
import FunnelChart from "../charts/FunnelChart";
import StockTorreChart from "../charts/StockTorreChart";
import EvolucionChart from "../charts/EvolucionChart";
import MediosChart from "../charts/MediosChart";
import CanalChart from "../charts/CanalChart";

const TABS = [
  { id: "Ventas", label: "Ventas" },
  { id: "Stock", label: "Stock" },
  { id: "Comercial", label: "Comercial" },
  { id: "Marketing", label: "Marketing" },
];

const fmt = (n) => new Intl.NumberFormat("es-CL").format(Math.round(n || 0));

export default function Analitico() {
  const { auth } = useAuth();
  const { data, loading, reload } = useDashboard();
  const [tab, setTab] = useState("Ventas");

  if (loading || !data) return <div className="p-8 text-slate-400">Cargando...</div>;
  if (data.empty) return <div className="p-8 text-slate-400">Sin datos. Suba un archivo.</div>;

  return (
    <div className="min-h-screen flex bg-slate-50 dark:bg-slate-900">
      <aside className="w-60 shrink-0 bg-slate-900 text-white p-5 flex flex-col">
        <div className="mb-8">
          <p className="text-xs uppercase tracking-widest text-indigo-400">Parque Mackenna</p>
          <h1 className="text-lg font-bold mt-1">Analítico</h1>
          <p className="text-xs text-slate-500 mt-1">Periodo {data.periodo}</p>
        </div>
        <nav className="space-y-1 flex-1">
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`block w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition ${
                tab === t.id
                  ? "bg-indigo-600 text-white shadow-lg shadow-indigo-900/40"
                  : "text-slate-300 hover:bg-slate-800"
              }`}
            >
              {t.label}
            </button>
          ))}
        </nav>
        {auth.rol === "admin" && (
          <div className="pt-4 border-t border-slate-800">
            <Uploader onDone={reload} />
          </div>
        )}
      </aside>

      <main className="flex-1 p-6 lg:p-8 space-y-6 overflow-y-auto">
        <header className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">{tab}</h2>
          <div className="flex gap-4 text-sm text-slate-500 dark:text-slate-400">
            <span>Venta total: <strong className="text-slate-900 dark:text-white">{fmt(data.kpis.ventaTotalUF)} UF</strong></span>
            <span>Por recibir: <strong className="text-slate-900 dark:text-white">{fmt(data.kpis.xRecibirUF)} UF</strong></span>
          </div>
        </header>

        {tab === "Ventas" && (
          <>
            <Panel title="Evolución mensual">
              <EvolucionChart evolucion={data.evolucionMensual} />
            </Panel>
            <Section title="Venta por torre">
              <Table
                columns={["Torre", "Venta UF", "Por recibir UF"]}
                rows={data.ventas.map((v) => [`Torre ${v.torre}`, fmt(v.ventaUF), fmt(v.xRecibirUF)])}
              />
            </Section>
          </>
        )}

        {tab === "Stock" && (
          <>
            <Panel title="Stock por torre">
              <StockTorreChart stock={data.stock} />
            </Panel>
            <Section title="Detalle por tipología">
              <Table
                columns={["Torre", "Tipología", "Disponible", "Reservado", "Promesado", "Escriturado"]}
                rows={data.stock.map((s) => [
                  `Torre ${s.torre}`,
                  s.tipologia,
                  s.disponible,
                  s.reservado,
                  s.promesado,
                  s.escriturado,
                ])}
              />
            </Section>
          </>
        )}

        {tab === "Comercial" && (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Panel title="Funnel">
                <FunnelChart funnel={data.funnel} />
              </Panel>
              <Panel title="Capital vs Brokers">
                <CanalChart canal={data.canal} />
              </Panel>
            </div>
            <Section title="Detalle por canal">
              <Table
                columns={["Canal", "Reservas", "Promesas", "Escrituras", "Desistidos"]}
                rows={data.canal.map((c) => [c.canal, c.reservas, c.promesas, c.escrituras, c.desistidos])}
              />
            </Section>
          </>
        )}

        {tab === "Marketing" && (
          <>
            <Panel title="Medios de llegada">
              <MediosChart medios={data.marketing.medios} />
            </Panel>
            <Section title="Detalle por medio">
              <Table
                columns={["Medio", "Cantidad"]}
                rows={data.marketing.medios.map((m) => [m.medio, m.cant])}
              />
            </Section>
          </>
        )}
      </main>
    </div>
  );
}

function Panel({ title, children }) {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-md p-5">
      <h3 className="text-slate-700 dark:text-slate-200 font-semibold mb-3">{title}</h3>
      <div className="h-72 relative">{children}</div>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-md p-5">
      <h3 className="text-slate-700 dark:text-slate-200 font-semibold mb-3">{title}</h3>
      {children}
    </div>
  );
}

function Table({ columns, rows }) {
  return (
    <div className="overflow-x-auto -mx-1">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="text-left text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-700">
            {columns.map((c) => (
              <th key={c} className="px-3 py-2 font-medium">{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-b border-slate-100 dark:border-slate-700/50">
              {r.map((cell, j) => (
                <td key={j} className="px-3 py-2 text-slate-700 dark:text-slate-300">{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
