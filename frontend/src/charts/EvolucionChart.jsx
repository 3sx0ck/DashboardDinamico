import "./setup";
import { Line } from "react-chartjs-2";
export default function EvolucionChart({ evolucion }) {
  const labels = evolucion.map((e) => e.mes);
  const mk = (k, c) => ({ label: k, data: evolucion.map((e) => e[k]), borderColor: c, tension: 0.3 });
  return <Line data={{ labels, datasets: [mk("ofertas","#6366f1"), mk("promesas","#3b82f6"), mk("escrituras","#10b981")] }}
               options={{ responsive: true, maintainAspectRatio: false }} />;
}
