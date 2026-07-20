import "./setup";
import { Doughnut } from "react-chartjs-2";
export default function MediosChart({ medios }) {
  return <Doughnut data={{ labels: medios.map((m)=>m.medio),
    datasets: [{ data: medios.map((m)=>m.cant),
      backgroundColor:["#6366f1","#3b82f6","#10b981","#f59e0b","#ef4444","#8b5cf6"] }] }} />;
}
