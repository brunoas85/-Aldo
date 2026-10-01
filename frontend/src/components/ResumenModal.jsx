import { useEffect, useState } from 'react'
import { Lightbulb, Sparkles, X } from 'lucide-react'
import { ICONO_CATEGORIA_GASTO } from '../categorias'
import MangoAvatar from './MangoAvatar'

const formatMonto = (valor) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }).format(valor)

const formatFecha = (fecha) =>
  new Date(`${fecha}T00:00:00`).toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit' })

const compras = (n) => `${n} ${n === 1 ? 'compra' : 'compras'}`

function CategoriaBarra({ categoria, maximo }) {
  const Icono = ICONO_CATEGORIA_GASTO[categoria.categoria]
  const ancho = maximo > 0 ? Math.max((categoria.total / maximo) * 100, categoria.total > 0 ? 2 : 0) : 0

  return (
    <li className="flex flex-col gap-1">
      <div className="flex items-baseline justify-between gap-2 text-sm">
        <span className="flex min-w-0 items-center gap-1.5 text-gray-700">
          {Icono && <Icono size={14} className="shrink-0 text-gray-400" />}
          <span className="truncate">{categoria.categoria}</span>
        </span>
        <span className="shrink-0 font-semibold tabular-nums text-gray-900">{formatMonto(categoria.total)}</span>
      </div>
      <div className="h-2 w-full rounded bg-gray-100">
        <div className="h-2 rounded bg-emerald-500" style={{ width: `${ancho}%` }} />
      </div>
      <p className="text-xs text-gray-400">
        {categoria.cantidad > 0 ? compras(categoria.cantidad) : 'Nada este ciclo'}
        {' · '}ciclo anterior {formatMonto(categoria.total_ciclo_anterior)}
      </p>
    </li>
  )
}

export default function ResumenModal({ open, onClose, cargar }) {
  const [resumen, setResumen] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!open) return
    let cancelado = false
    setResumen(null)
    setError(null)
    cargar()
      .then((datos) => !cancelado && setResumen(datos))
      .catch((mensaje) => !cancelado && setError(mensaje))
    return () => {
      cancelado = true
    }
  }, [open, cargar])

  if (!open) return null

  const maximo = resumen ? Math.max(...resumen.categorias.map((c) => c.total), 0) : 0

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 p-4 sm:items-center">
      <div className="flex max-h-[85vh] w-full max-w-sm flex-col rounded-3xl bg-mango-card p-6 shadow-xl">
        <div className="mb-3 flex items-start justify-between gap-2">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Resumen del ciclo</h2>
            {resumen && (
              <p className="text-xs text-gray-400">
                Del {formatFecha(resumen.inicio_ciclo)} al {formatFecha(resumen.fin_ciclo)} · día{' '}
                {resumen.dias_transcurridos} de {resumen.dias_totales_ciclo}
              </p>
            )}
          </div>
          <button type="button" onClick={onClose} aria-label="Cerrar" className="rounded-full p-1 text-gray-400 hover:bg-gray-100">
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {error && <p className="py-6 text-center text-sm text-red-500">{error}</p>}

          {!resumen && !error && (
            <div className="flex flex-col items-center gap-3 py-10 text-center text-sm text-gray-400">
              <MangoAvatar />
              <p>Mango está mirando tus gastos...</p>
            </div>
          )}

          {resumen && (
            <div className="flex flex-col gap-5">
              <div>
                <p className="text-sm text-gray-500">En el día a día gastaste</p>
                <p className="text-3xl font-bold tabular-nums text-gray-900">{formatMonto(resumen.total_gastado)}</p>
                <p className="text-xs text-gray-400">
                  El ciclo anterior, en total: {formatMonto(resumen.total_ciclo_anterior)}
                </p>
              </div>

              {resumen.analisis && (
                <div className="flex flex-col gap-2">
                  <span className="flex items-center gap-1 px-1 text-xs font-medium uppercase tracking-wide text-gray-400">
                    <Sparkles size={12} /> Mango te cuenta
                  </span>
                  <p className="text-sm text-gray-700">{resumen.analisis.resumen}</p>
                  {resumen.analisis.consejos.map((consejo, i) => (
                    <div
                      key={i}
                      className="flex items-start gap-2 rounded-2xl bg-violet-50 p-3 text-sm text-violet-900 ring-1 ring-violet-100 dark:bg-violet-950/50 dark:text-violet-100 dark:ring-violet-900"
                    >
                      <Lightbulb size={16} className="mt-0.5 shrink-0 text-violet-500" />
                      <span>{consejo}</span>
                    </div>
                  ))}
                </div>
              )}
              {resumen.aviso && <p className="rounded-xl bg-gray-50 p-3 text-sm text-gray-500">{resumen.aviso}</p>}

              <div className="flex flex-col gap-3">
                <span className="px-1 text-xs font-medium uppercase tracking-wide text-gray-400">Por categoría</span>
                {resumen.categorias.length === 0 ? (
                  <p className="text-sm text-gray-400">Todavía no cargaste gastos este ciclo.</p>
                ) : (
                  <ul className="flex flex-col gap-3">
                    {resumen.categorias.map((c) => (
                      <CategoriaBarra key={c.categoria} categoria={c} maximo={maximo} />
                    ))}
                  </ul>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
