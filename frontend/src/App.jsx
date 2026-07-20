import { Routes, Route } from "react-router-dom";
import Login from "./auth/Login";
import { RequireAuth, RequireAdmin } from "./auth/guards";
import Landing from "./pages/Landing";
import Executive from "./formats/Executive";
import Users from "./admin/Users";
import ProximamentePlaceholder from "./pages/ProximamentePlaceholder";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<RequireAuth><Landing /></RequireAuth>} />
      <Route path="/executive" element={<RequireAuth><Executive /></RequireAuth>} />
      <Route path="/analitico" element={<RequireAuth><ProximamentePlaceholder titulo="Analítico Multi-tab" /></RequireAuth>} />
      <Route path="/narrativo" element={<RequireAuth><ProximamentePlaceholder titulo="Reporte Narrativo" /></RequireAuth>} />
      <Route path="/admin/users" element={<RequireAdmin><Users /></RequireAdmin>} />
    </Routes>
  );
}
