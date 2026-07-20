import axios from "axios";

const api = axios.create({ baseURL: "http://localhost:8000" });

api.interceptors.request.use((cfg) => {
  const t = localStorage.getItem("token");
  if (t) cfg.headers.Authorization = `Bearer ${t}`;
  return cfg;
});

export async function login(email, password) {
  const body = new URLSearchParams({ username: email, password });
  const { data } = await api.post("/api/auth/login", body);
  return data; // {access_token, rol, nombre}
}
export const getDashboard = (params) => api.get("/api/dashboard", { params }).then((r) => r.data);
export const getPeriodos = () => api.get("/api/periodos").then((r) => r.data);
export const uploadFile = (file) => {
  const fd = new FormData(); fd.append("file", file);
  return api.post("/api/uploads", fd).then((r) => r.data);
};
export const listUsers = () => api.get("/api/users").then((r) => r.data);
export const createUser = (u) => api.post("/api/users", u).then((r) => r.data);
export default api;
