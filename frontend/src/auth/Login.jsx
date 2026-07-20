import { useState } from "react";
import { useAuth } from "./AuthContext";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState(""); const [pw, setPw] = useState(""); const [err, setErr] = useState("");
  async function submit(e) {
    e.preventDefault();
    try { await login(email, pw); nav("/"); }
    catch { setErr("Credenciales inválidas"); }
  }
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">
      <form onSubmit={submit} className="bg-slate-800 p-8 rounded-2xl shadow-xl w-80 space-y-4">
        <h1 className="text-white text-xl font-semibold">Dashboard PMK</h1>
        <input className="w-full p-2 rounded bg-slate-700 text-white" placeholder="Email"
               value={email} onChange={(e) => setEmail(e.target.value)} />
        <input type="password" className="w-full p-2 rounded bg-slate-700 text-white" placeholder="Contraseña"
               value={pw} onChange={(e) => setPw(e.target.value)} />
        {err && <p className="text-red-400 text-sm">{err}</p>}
        <button className="w-full bg-indigo-600 hover:bg-indigo-500 text-white p-2 rounded">Ingresar</button>
      </form>
    </div>
  );
}
