import { createContext, useContext, useState } from "react";
import { login as apiLogin } from "../api/client";

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(() => {
    const t = localStorage.getItem("token");
    return t ? { token: t, rol: localStorage.getItem("rol"), nombre: localStorage.getItem("nombre") } : null;
  });
  async function login(email, password) {
    const d = await apiLogin(email, password);
    localStorage.setItem("token", d.access_token);
    localStorage.setItem("rol", d.rol);
    localStorage.setItem("nombre", d.nombre);
    setAuth({ token: d.access_token, rol: d.rol, nombre: d.nombre });
  }
  function logout() { localStorage.clear(); setAuth(null); }
  return <AuthCtx.Provider value={{ auth, login, logout }}>{children}</AuthCtx.Provider>;
}
export const useAuth = () => useContext(AuthCtx);
