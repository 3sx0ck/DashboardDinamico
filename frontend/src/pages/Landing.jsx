import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const formatos = [
  { to: "/executive", titulo: "Executive Overview", desc: "Una pantalla, KPIs + 6 gráficos" },
  { to: "/analitico", titulo: "Analítico Multi-tab", desc: "Secciones detalladas con tablas" },
  { to: "/narrativo", titulo: "Reporte Narrativo", desc: "Storytelling para reunión" },
];

export default function Landing() {
  const { auth, logout } = useAuth();
  return (
    <div className="min-h-screen bg-slate-900 p-10">
      <div className="flex justify-between items-center mb-10">
        <h1 className="text-3xl font-bold text-white">Dashboard PMK</h1>
        <div className="flex gap-3 items-center">
          {auth.rol === "admin" && <Link to="/admin/users" className="text-indigo-300">Usuarios</Link>}
          <span className="text-slate-400">{auth.nombre} ({auth.rol})</span>
          <button onClick={logout} className="text-slate-300">Salir</button>
        </div>
      </div>
      <div className="grid md:grid-cols-3 gap-6">
        {formatos.map((f) => (
          <Link key={f.to} to={f.to}
                className="bg-slate-800 hover:bg-slate-700 rounded-2xl p-8 shadow-xl transition">
            <h2 className="text-xl font-semibold text-white">{f.titulo}</h2>
            <p className="text-slate-400 mt-2">{f.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
