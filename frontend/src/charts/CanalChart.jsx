import "./setup";
import { Bar } from "react-chartjs-2";
export default function CanalChart({ canal }) {
  const labels = canal.map((c)=>c.canal);
  const mk = (k,c)=>({ label:k, backgroundColor:c, data: canal.map((x)=>x[k]) });
  return <Bar data={{ labels, datasets:[mk("reservas","#3b82f6"),mk("promesas","#f59e0b"),mk("escrituras","#10b981")] }}
              options={{ responsive:true }} />;
}
