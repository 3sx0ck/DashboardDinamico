import { useState, useEffect } from "react";
import { listUsers, createUser } from "../api/client";

export default function Users() {
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({ email: "", nombre: "", password: "", rol: "visitante" });
  const load = () => listUsers().then(setUsers);
  useEffect(() => { load(); }, []);
  async function submit(e) {
    e.preventDefault();
    await createUser(form);
    setForm({ email: "", nombre: "", password: "", rol: "visitante" });
    load();
  }
  return (
    <div className="min-h-screen bg-slate-900 p-8 text-white">
      <h1 className="text-2xl font-bold mb-6">Usuarios</h1>
      <form onSubmit={submit} className="flex flex-wrap gap-3 mb-8 bg-slate-800 p-4 rounded-xl">
        <input className="p-2 rounded bg-slate-700" placeholder="Email" value={form.email}
               onChange={(e)=>setForm({...form,email:e.target.value})} />
        <input className="p-2 rounded bg-slate-700" placeholder="Nombre" value={form.nombre}
               onChange={(e)=>setForm({...form,nombre:e.target.value})} />
        <input type="password" className="p-2 rounded bg-slate-700" placeholder="Contraseña" value={form.password}
               onChange={(e)=>setForm({...form,password:e.target.value})} />
        <select className="p-2 rounded bg-slate-700" value={form.rol}
                onChange={(e)=>setForm({...form,rol:e.target.value})}>
          <option value="visitante">visitante</option>
          <option value="admin">admin</option>
        </select>
        <button className="bg-indigo-600 px-4 rounded">Crear</button>
      </form>
      <table className="w-full text-left">
        <thead><tr className="text-slate-400"><th>Email</th><th>Nombre</th><th>Rol</th></tr></thead>
        <tbody>{users.map((u)=>(
          <tr key={u.id} className="border-t border-slate-700"><td>{u.email}</td><td>{u.nombre}</td><td>{u.rol}</td></tr>
        ))}</tbody>
      </table>
    </div>
  );
}
