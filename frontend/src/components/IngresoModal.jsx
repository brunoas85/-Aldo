import { useState } from 'react'
import { X } from 'lucide-react'

export default function IngresoModal({ open, onSave, onClose }) {
  const [monto, setMonto] = useState('')
  const [descripcion, setDescripcion] = useState('')
  const [enviando, setEnviando] = useState(false)

  if (!open) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    const valor = Number(monto)
    if (!(valor > 0) || enviando) return
    setEnviando(true)
    try {
      if (await onSave({ monto: valor, descripcion: descripcion.trim() || null })) {
        setMonto('')
        setDescripcion('')
      }
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 p-4 sm:items-center">
      <form onSubmit={handleSubmit} className="w-full max-w-sm rounded-3xl bg-white p-6 shadow-xl">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Sumaste un ingreso</h2>
          <button type="button" onClick={onClose} className="rounded-full p-1 text-gray-400 hover:bg-gray-100">
            <X size={18} />
          </button>
        </div>

        <label className="mb-3 block text-sm font-medium text-gray-700">
          Monto
          <input
            type="number"
            inputMode="decimal"
            autoFocus
            required
            min="0"
            value={monto}
            onChange={(e) => setMonto(e.target.value)}
            placeholder="$ 0"
            className="mt-1 w-full rounded-xl border border-gray-300 px-4 py-3 text-lg focus:border-emerald-500 focus:outline-none [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
          />
        </label>

        <label className="mb-5 block text-sm font-medium text-gray-700">
          Descripción (opcional)
          <input
            type="text"
            value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)}
            placeholder="Changa, venta, etc."
            className="mt-1 w-full rounded-xl border border-gray-300 px-4 py-3 text-sm focus:border-emerald-500 focus:outline-none"
          />
        </label>

        <button
          type="submit"
          disabled={enviando}
          className="w-full rounded-xl bg-emerald-500 py-3 font-semibold text-white active:bg-emerald-600 disabled:opacity-40"
        >
          {enviando ? 'Guardando...' : 'Sumar ingreso'}
        </button>
      </form>
    </div>
  )
}
