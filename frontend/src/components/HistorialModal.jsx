import { useState } from 'react'
import { Check, Pencil, Trash2, X } from 'lucide-react'

const formatMonto = (valor) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }).format(valor)

const formatFecha = (fecha) =>
  new Date(`${fecha}T00:00:00`).toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit' })

function MovimientoRow({ movimiento, onEdit, onDelete }) {
  const [editando, setEditando] = useState(false)
  const [monto, setMonto] = useState(movimiento.monto)
  const [descripcion, setDescripcion] = useState(movimiento.descripcion || '')
  const esGasto = movimiento.tipo === 'gasto'

  const guardar = async () => {
    const valor = Number(monto)
    if (!valor) return
    await onEdit(movimiento.id, { monto: valor, descripcion: descripcion.trim() || null })
    setEditando(false)
  }

  if (editando) {
    return (
      <div className="flex items-center gap-2 py-2">
        <input
          type="number"
          inputMode="decimal"
          autoFocus
          value={monto}
          onChange={(e) => setMonto(e.target.value)}
          className="w-24 rounded-lg border border-gray-300 px-2 py-1.5 text-sm [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
        />
        <input
          type="text"
          value={descripcion}
          onChange={(e) => setDescripcion(e.target.value)}
          placeholder="Descripción"
          className="min-w-0 flex-1 rounded-lg border border-gray-300 px-2 py-1.5 text-sm"
        />
        <button
          type="button"
          onClick={guardar}
          aria-label="Guardar"
          className="rounded-lg p-1.5 text-emerald-600 hover:bg-emerald-50"
        >
          <Check size={16} />
        </button>
      </div>
    )
  }

  return (
    <div className="flex items-center justify-between gap-2 py-2">
      <div className="min-w-0">
        <p className="truncate text-sm text-gray-700">{movimiento.descripcion || (esGasto ? 'Gasto' : 'Ingreso')}</p>
        <p className="text-xs text-gray-400">{formatFecha(movimiento.fecha)}</p>
      </div>
      <div className="flex shrink-0 items-center gap-1">
        <span className={`text-sm font-semibold tabular-nums ${esGasto ? 'text-red-500' : 'text-emerald-600'}`}>
          {esGasto ? '-' : '+'}
          {formatMonto(movimiento.monto)}
        </span>
        <button
          type="button"
          onClick={() => setEditando(true)}
          aria-label="Editar"
          className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100"
        >
          <Pencil size={14} />
        </button>
        <button
          type="button"
          onClick={() => onDelete(movimiento.id)}
          aria-label="Borrar"
          className="rounded-lg p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-500"
        >
          <Trash2 size={14} />
        </button>
      </div>
    </div>
  )
}

export default function HistorialModal({
  open,
  gastos,
  ingresos,
  onClose,
  onEditGasto,
  onDeleteGasto,
  onEditIngreso,
  onDeleteIngreso,
}) {
  if (!open) return null

  const movimientos = [
    ...gastos.map((g) => ({ ...g, tipo: 'gasto' })),
    ...ingresos.map((i) => ({ ...i, tipo: 'ingreso' })),
  ].sort((a, b) => (a.fecha === b.fecha ? b.id - a.id : a.fecha < b.fecha ? 1 : -1))

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 p-4 sm:items-center">
      <div className="flex max-h-[80vh] w-full max-w-sm flex-col rounded-3xl bg-white p-6 shadow-xl">
        <div className="mb-2 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Tus movimientos</h2>
          <button type="button" onClick={onClose} className="rounded-full p-1 text-gray-400 hover:bg-gray-100">
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 divide-y divide-gray-100 overflow-y-auto">
          {movimientos.length === 0 && (
            <p className="py-6 text-center text-sm text-gray-400">Todavía no cargaste nada este ciclo.</p>
          )}
          {movimientos.map((m) => (
            <MovimientoRow
              key={`${m.tipo}-${m.id}`}
              movimiento={m}
              onEdit={m.tipo === 'gasto' ? onEditGasto : onEditIngreso}
              onDelete={m.tipo === 'gasto' ? onDeleteGasto : onDeleteIngreso}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
