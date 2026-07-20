import { Link } from "react-router-dom";

export default function ProximamentePlaceholder({ titulo }) {
  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-10">
      <div className="bg-slate-800 rounded-2xl shadow-xl p-10 text-center max-w-md">
        <h1 className="text-2xl font-bold text-white mb-2">{titulo}</h1>
        <p className="text-slate-400 mb-6">Próximamente. Este formato se encuentra en desarrollo.</p>
        <Link to="/" className="inline-block bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-xl transition">
          Volver al inicio
        </Link>
      </div>
    </div>
  );
}
