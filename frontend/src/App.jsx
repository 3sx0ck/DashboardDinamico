import { Routes, Route } from "react-router-dom";
import Login from "./auth/Login";
import { RequireAuth, RequireAdmin } from "./auth/guards";
import Landing from "./pages/Landing";
import Executive from "./formats/Executive";
import Analitico from "./formats/Analitico";
import Narrativo from "./formats/Narrativo";
import Users from "./admin/Users";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<RequireAuth><Landing /></RequireAuth>} />
      <Route path="/executive" element={<RequireAuth><Executive /></RequireAuth>} />
      <Route path="/analitico" element={<RequireAuth><Analitico /></RequireAuth>} />
      <Route path="/narrativo" element={<RequireAuth><Narrativo /></RequireAuth>} />
      <Route path="/admin/users" element={<RequireAdmin><Users /></RequireAdmin>} />
    </Routes>
  );
}
