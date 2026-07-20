import "./setup";
import { Bar } from "react-chartjs-2";

export default function FunnelChart({ funnel }) {
  if (!funnel) return null;
  const data = {
    labels: ["Ofertas", "Desistidos", "En curso", "Promesas", "Escrituras"],
    datasets: [{ label: "Funnel", data: [funnel.ofertas, funnel.desistidos, funnel.enCurso, funnel.promesas, funnel.escrituras],
      backgroundColor: ["#6366f1","#ef4444","#f59e0b","#3b82f6","#10b981"] }],
  };
  return <Bar data={data} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }} />;
}
