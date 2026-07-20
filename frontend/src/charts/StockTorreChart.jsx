import "./setup";
import { Bar } from "react-chartjs-2";
export default function StockTorreChart({ stock }) {
  const torres = [...new Set(stock.map((s) => s.torre))];
  const estados = ["disponible","reservado","promesado","escriturado"];
  const colores = { disponible:"#10b981", reservado:"#f59e0b", promesado:"#3b82f6", escriturado:"#6366f1" };
  const datasets = estados.map((es) => ({
    label: es, backgroundColor: colores[es],
    data: torres.map((t) => stock.filter((s) => s.torre === t).reduce((a, s) => a + (s[es] || 0), 0)),
  }));
  return <Bar data={{ labels: torres.map((t)=>`Torre ${t}`), datasets }}
              options={{ responsive:true, scales:{ x:{ stacked:true }, y:{ stacked:true } } }} />;
}
