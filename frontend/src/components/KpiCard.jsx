export default function KpiCard({ label, value, suffix = "" }) {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-md p-5">
      <p className="text-slate-500 dark:text-slate-400 text-sm">{label}</p>
      <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">
        {value}{suffix}
      </p>
    </div>
  );
}
