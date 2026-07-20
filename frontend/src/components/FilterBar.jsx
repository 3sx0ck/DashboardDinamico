export default function FilterBar({ filters, setFilters, torres = [] }) {
  return (
    <div className="flex gap-3 flex-wrap">
      <select className="p-2 rounded-lg bg-slate-100 dark:bg-slate-700 dark:text-white"
              value={filters.torre || ""} onChange={(e) => setFilters({ ...filters, torre: e.target.value || undefined })}>
        <option value="">Todas las torres</option>
        {torres.map((t) => <option key={t} value={t}>Torre {t}</option>)}
      </select>
    </div>
  );
}
