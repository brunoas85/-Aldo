export default function StatCard({ icon: Icon, label, value, accent = 'text-gray-900' }) {
  return (
    <div className="flex flex-1 flex-col items-start gap-1 rounded-2xl bg-white p-4 shadow-sm ring-1 ring-gray-100">
      <Icon size={18} className="text-gray-400" />
      <span className={`text-lg font-semibold tabular-nums ${accent}`}>{value}</span>
      <span className="text-xs text-gray-400">{label}</span>
    </div>
  )
}
