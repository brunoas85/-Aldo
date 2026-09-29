import { useEffect, useState } from 'react'
import { ChevronLeft, X } from 'lucide-react'
import AldoAvatar from './AldoAvatar'
import GastoFijoRow from './GastoFijoRow'
import { CATEGORIAS } from '../categorias'

const PASO_VACIO_GASTO = () => ({ nombre: '', monto: '', categoria: CATEGORIAS[0] })

const TITULOS = [
  'Contame de tu plata',
  'Tus gastos fijos',
  'Meta de ahorro',
  'Todo listo',
]

const formatMonto = (valor) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }).format(valor || 0)

export default function ConfigWizard({ open, onSave, onClose, initialData }) {
  const [paso, setPaso] = useState(0)
  const [ingresos, setIngresos] = useState('')
  const [diaCobro, setDiaCobro] = useState('1')
  const [gastosFijos, setGastosFijos] = useState([PASO_VACIO_GASTO()])
  const [metaAhorro, setMetaAhorro] = useState('')
  const [enviando, setEnviando] = useState(false)

  useEffect(() => {
    if (!open) return
    setPaso(0)
    if (initialData) {
      setIngresos(String(initialData.ingresos_mensuales ?? ''))
      setDiaCobro(String(initialData.dia_cobro ?? '1'))
      setMetaAhorro(String(initialData.meta_ahorro || ''))
      setGastosFijos(
        initialData.gastos_fijos?.length
          ? initialData.gastos_fijos.map((g) => ({ nombre: g.nombre, monto: String(g.monto), categoria: g.categoria || CATEGORIAS[0] }))
          : [PASO_VACIO_GASTO()],
      )
    } else {
      setIngresos('')
      setDiaCobro('1')
      setMetaAhorro('')
      setGastosFijos([PASO_VACIO_GASTO()])
    }
  }, [open, initialData])

  if (!open) return null

  const totalGastosFijos = gastosFijos.reduce((acc, g) => acc + (Number(g.monto) || 0), 0)

  const pasoValido = () => {
    if (paso === 0) return Number(ingresos) > 0 && Number(diaCobro) >= 1 && Number(diaCobro) <= 31
    if (paso === 1) return gastosFijos.every((g) => g.nombre.trim() && Number(g.monto) > 0)
    return true
  }

  const siguiente = () => setPaso((p) => Math.min(p + 1, TITULOS.length - 1))
  const atras = () => setPaso((p) => Math.max(p - 1, 0))

  const confirmar = async () => {
    setEnviando(true)
    try {
      await onSave({
        ingresos_mensuales: Number(ingresos),
        dia_cobro: Number(diaCobro),
        meta_ahorro: Number(metaAhorro) || 0,
        gastos_fijos: gastosFijos
          .filter((g) => g.nombre.trim() && Number(g.monto) > 0)
          .map((g) => ({ nombre: g.nombre.trim(), monto: Number(g.monto), categoria: g.categoria })),
      })
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 p-4 sm:items-center">
      <div className="flex w-full max-w-sm flex-col rounded-3xl bg-aldo-card p-6 shadow-xl">
        <div className="mb-4 flex items-center gap-3">
          {paso > 0 && (
            <button type="button" onClick={atras} className="rounded-full p-1 text-gray-400 hover:bg-gray-100">
              <ChevronLeft size={20} />
            </button>
          )}
          <AldoAvatar size="sm" />
          <div className="flex-1">
            <h2 className="text-lg font-semibold text-gray-900">{TITULOS[paso]}</h2>
            <p className="text-xs text-gray-400">
              Paso {paso + 1} de {TITULOS.length}
            </p>
          </div>
          {onClose && (
            <button type="button" onClick={onClose} className="rounded-full p-1 text-gray-400 hover:bg-gray-100">
              <X size={18} />
            </button>
          )}
        </div>

        <div className="mb-2 flex gap-1">
          {TITULOS.map((_, i) => (
            <div key={i} className={`h-1 flex-1 rounded-full ${i <= paso ? 'bg-emerald-500' : 'bg-gray-100'}`} />
          ))}
        </div>

        <div className="flex min-h-[240px] flex-col gap-4 py-4">
          {paso === 0 && (
            <>
              <p className="text-sm text-gray-500">Con esto $Aldo calcula cuánto podés gastar por día.</p>
              <label className="block text-sm font-medium text-gray-700">
                Ingresos totales del mes
                <input
                  type="number"
                  inputMode="decimal"
                  autoFocus
                  value={ingresos}
                  onChange={(e) => setIngresos(e.target.value)}
                  placeholder="$ 0"
                  className="mt-1 w-full rounded-xl border border-gray-300 px-4 py-3 text-lg focus:border-emerald-500 focus:outline-none [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
                />
              </label>
              <label className="block text-sm font-medium text-gray-700">
                Día de cobro
                <input
                  type="number"
                  min={1}
                  max={31}
                  value={diaCobro}
                  onChange={(e) => setDiaCobro(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-gray-300 px-4 py-3 text-lg focus:border-emerald-500 focus:outline-none [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
                />
                <span className="mt-1 block text-xs text-gray-400">
                  El día del mes en que te pagan. $Aldo arma tu ciclo a partir de ahí.
                </span>
              </label>
            </>
          )}

          {paso === 1 && (
            <>
              <p className="text-sm text-gray-500">Cargá cada gasto fijo por separado, así $Aldo sabe en qué se te va la plata.</p>
              <div className="flex flex-col gap-2">
                {gastosFijos.map((g, i) => (
                  <GastoFijoRow
                    key={i}
                    gasto={g}
                    onChange={(nuevo) =>
                      setGastosFijos((prev) => prev.map((item, idx) => (idx === i ? nuevo : item)))
                    }
                    onRemove={() => setGastosFijos((prev) => prev.filter((_, idx) => idx !== i))}
                  />
                ))}
              </div>
              <button
                type="button"
                onClick={() => setGastosFijos((prev) => [...prev, PASO_VACIO_GASTO()])}
                className="self-start text-sm font-medium text-emerald-600"
              >
                + Agregar gasto fijo
              </button>
              <div className="mt-auto flex justify-between border-t border-gray-100 pt-3 text-sm">
                <span className="text-gray-500">Total gastos fijos</span>
                <span className="font-semibold text-gray-900">{formatMonto(totalGastosFijos)}</span>
              </div>
            </>
          )}

          {paso === 2 && (
            <>
              <p className="text-sm text-gray-500">
                Opcional. $Aldo la descuenta de tu presupuesto diario como si fuera otro gasto fijo, para que
                ahorrar no dependa de tu fuerza de voluntad.
              </p>
              <label className="block text-sm font-medium text-gray-700">
                Meta de ahorro mensual
                <input
                  type="number"
                  inputMode="decimal"
                  autoFocus
                  value={metaAhorro}
                  onChange={(e) => setMetaAhorro(e.target.value)}
                  placeholder="$ 0"
                  className="mt-1 w-full rounded-xl border border-gray-300 px-4 py-3 text-lg focus:border-emerald-500 focus:outline-none [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
                />
              </label>
            </>
          )}

          {paso === 3 && (
            <div className="flex flex-col gap-3 text-sm">
              <div className="flex justify-between rounded-xl bg-gray-50 px-4 py-3">
                <span className="text-gray-500">Ingresos del mes</span>
                <span className="font-semibold text-gray-900">{formatMonto(Number(ingresos))}</span>
              </div>
              <div className="flex justify-between rounded-xl bg-gray-50 px-4 py-3">
                <span className="text-gray-500">Día de cobro</span>
                <span className="font-semibold text-gray-900">{diaCobro}</span>
              </div>
              <div className="flex justify-between rounded-xl bg-gray-50 px-4 py-3">
                <span className="text-gray-500">Gastos fijos ({gastosFijos.length})</span>
                <span className="font-semibold text-gray-900">{formatMonto(totalGastosFijos)}</span>
              </div>
              <div className="flex justify-between rounded-xl bg-gray-50 px-4 py-3">
                <span className="text-gray-500">Meta de ahorro</span>
                <span className="font-semibold text-gray-900">{formatMonto(Number(metaAhorro) || 0)}</span>
              </div>
            </div>
          )}
        </div>

        {paso < TITULOS.length - 1 ? (
          <button
            type="button"
            disabled={!pasoValido()}
            onClick={siguiente}
            className="rounded-xl bg-emerald-500 py-3 font-semibold text-white disabled:opacity-40 active:bg-emerald-600"
          >
            Siguiente
          </button>
        ) : (
          <button
            type="button"
            disabled={enviando}
            onClick={confirmar}
            className="rounded-xl bg-emerald-500 py-3 font-semibold text-white disabled:opacity-40 active:bg-emerald-600"
          >
            {enviando ? 'Guardando...' : 'Confirmar'}
          </button>
        )}
      </div>
    </div>
  )
}
