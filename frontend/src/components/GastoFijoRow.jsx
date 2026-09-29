import { Trash2 } from 'lucide-react'
import { CATEGORIAS } from '../categorias'

export default function GastoFijoRow({ gasto, onChange, onRemove }) {
  return (
    <div className="flex items-center gap-2">
      <input
        type="text"
        required
        value={gasto.nombre}
        onChange={(e) => onChange({ ...gasto, nombre: e.target.value })}
        placeholder="Nombre (ej: Alquiler)"
        className="min-w-0 flex-[2] rounded-xl border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
      />
      <input
        type="number"
        inputMode="decimal"
        required
        value={gasto.monto}
        onChange={(e) => onChange({ ...gasto, monto: e.target.value })}
        placeholder="$"
        className="w-24 min-w-0 flex-1 rounded-xl border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
      />
      <select
        value={gasto.categoria}
        onChange={(e) => onChange({ ...gasto, categoria: e.target.value })}
        className="flex-1 rounded-xl border border-gray-300 px-2 py-2 text-sm focus:border-emerald-500 focus:outline-none"
      >
        {CATEGORIAS.map((cat) => (
          <option key={cat} value={cat}>
            {cat}
          </option>
        ))}
      </select>
      <button
        type="button"
        onClick={onRemove}
        className="shrink-0 rounded-lg p-2 text-gray-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-950/50"
        aria-label="Quitar gasto"
      >
        <Trash2 size={16} />
      </button>
    </div>
  )
}
