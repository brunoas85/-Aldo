import { useState } from 'react'
import { Plus } from 'lucide-react'

export default function ExpenseInput({ onAdd, onOpenIngreso }) {
  const [monto, setMonto] = useState('')
  const [enviando, setEnviando] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    const valor = Number(monto)
    if (!(valor > 0) || enviando) return
    setEnviando(true)
    try {
      if (await onAdd(valor)) setMonto('')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="fixed inset-x-0 bottom-0 z-40 border-t border-gray-100 bg-white/95 p-4 backdrop-blur">
      <form onSubmit={handleSubmit} className="mx-auto flex w-full max-w-sm gap-2">
        <input
          type="number"
          inputMode="decimal"
          min="0"
          value={monto}
          onChange={(e) => setMonto(e.target.value)}
          placeholder="¿Cuánto gastaste?"
          className="flex-1 rounded-xl border border-gray-300 px-4 py-4 text-lg focus:border-emerald-500 focus:outline-none [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
        />
        <button
          type="submit"
          disabled={enviando}
          className="rounded-xl bg-gray-900 px-6 py-4 text-lg font-semibold text-white active:bg-gray-700 disabled:opacity-50"
        >
          Restar
        </button>
        <button
          type="button"
          onClick={onOpenIngreso}
          aria-label="Sumar ingreso"
          className="rounded-xl border border-gray-300 px-4 py-4 text-gray-500 active:bg-gray-100"
        >
          <Plus size={20} />
        </button>
      </form>
    </div>
  )
}
