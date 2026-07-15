import { useState } from 'react'
import { ChevronDown, Banknote } from 'lucide-react'
import { ICONO_CATEGORIA } from '../categorias'

const formatMonto = (valor) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }).format(valor)

export default function GastosFijosList({ gastosFijos, ingresosMensuales }) {
  const [abierto, setAbierto] = useState(false)
  if (!gastosFijos?.length) return null

  const total = gastosFijos.reduce((acc, g) => acc + g.monto, 0)

  return (
    <div className="w-full max-w-sm rounded-2xl bg-white p-4 shadow-sm ring-1 ring-gray-100">
      <button
        type="button"
        onClick={() => setAbierto((v) => !v)}
        className="flex w-full items-center justify-between"
      >
        <span className="text-sm font-medium text-gray-700">
          Gastos fijos · {formatMonto(total)}
        </span>
        <ChevronDown size={18} className={`text-gray-400 transition-transform ${abierto ? 'rotate-180' : ''}`} />
      </button>

      {abierto && (
        <ul className="mt-3 flex flex-col gap-2">
          {gastosFijos.map((g) => {
            const Icono = ICONO_CATEGORIA[g.categoria] ?? Banknote
            const pct = ingresosMensuales > 0 ? (g.monto / ingresosMensuales) * 100 : 0
            return (
              <li key={g.id} className="flex items-center justify-between gap-2 text-sm">
                <span className="flex items-center gap-2 text-gray-600">
                  <Icono size={15} className="text-gray-400" />
                  {g.nombre}
                </span>
                <span className="text-right">
                  <span className="block font-medium text-gray-900">{formatMonto(g.monto)}</span>
                  <span className="block text-xs text-gray-400">{pct.toFixed(0)}% de tus ingresos</span>
                </span>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}
