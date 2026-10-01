import { useRef, useState } from 'react'
import { Plus } from 'lucide-react'
import { CATEGORIAS_GASTO, ICONO_CATEGORIA_GASTO } from '../categorias'

export default function ExpenseInput({ onAdd, onOpenIngreso }) {
  const [monto, setMonto] = useState('')
  const [enviando, setEnviando] = useState(false)
  const input = useRef(null)
  const montoValido = Number(monto) > 0

  // Con categoría (tocando un chip) o sin ella (botón Restar / Enter): un solo paso.
  const guardar = async (categoria = null) => {
    const valor = Number(monto)
    if (!(valor > 0)) return input.current?.focus()
    if (enviando) return
    setEnviando(true)
    try {
      if (await onAdd(valor, categoria)) setMonto('')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="fixed inset-x-0 bottom-0 z-40 border-t border-gray-100 bg-mango-card/95 p-4 backdrop-blur">
      <div className="mx-auto flex w-full max-w-sm flex-col gap-2">
        <div className="-mx-4 flex gap-1.5 overflow-x-auto px-4 [scrollbar-width:none]">
          {CATEGORIAS_GASTO.map((categoria) => {
            const Icono = ICONO_CATEGORIA_GASTO[categoria]
            return (
              <button
                key={categoria}
                type="button"
                disabled={enviando}
                onClick={() => guardar(categoria)}
                className={`flex shrink-0 items-center gap-1 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors disabled:opacity-50 ${
                  montoValido
                    ? 'border-emerald-300 text-emerald-700 active:bg-emerald-50 dark:border-emerald-800 dark:text-emerald-300 dark:active:bg-emerald-950'
                    : 'border-gray-200 text-gray-500'
                }`}
              >
                <Icono size={14} />
                {categoria}
              </button>
            )
          })}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            guardar()
          }}
          className="flex gap-2"
        >
          <input
            ref={input}
            type="number"
            inputMode="decimal"
            min="0"
            value={monto}
            onChange={(e) => setMonto(e.target.value)}
            placeholder="¿Cuánto gastaste?"
            className="min-w-0 flex-1 rounded-xl border border-gray-300 px-4 py-4 text-lg focus:border-emerald-500 focus:outline-none [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
          />
          <button
            type="submit"
            disabled={enviando}
            className="rounded-xl bg-gray-900 px-6 py-4 text-lg font-semibold text-white active:bg-gray-700 disabled:opacity-50 dark:bg-emerald-600 dark:active:bg-emerald-700"
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
    </div>
  )
}
