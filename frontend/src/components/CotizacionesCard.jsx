import { useEffect, useState } from 'react'
import { DollarSign } from 'lucide-react'
import { getCotizaciones } from '../api/cotizaciones'

const NOMBRE_CASA = { oficial: 'Oficial', blue: 'Blue', bolsa: 'MEP', tarjeta: 'Tarjeta' }
const CLAVE_MONEDA = 'aldo-moneda-cotizacion'

const formatPesos = (valor, decimales = 0) =>
  new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
    minimumFractionDigits: decimales,
    maximumFractionDigits: decimales,
  }).format(valor)

const formatEntero = (valor) => new Intl.NumberFormat('es-AR', { maximumFractionDigits: 0 }).format(valor)

const formatHora = (iso) =>
  new Date(iso).toLocaleString('es-AR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })

function monedaInicial() {
  try {
    return localStorage.getItem(CLAVE_MONEDA) === 'CLP' ? 'CLP' : 'USD'
  } catch {
    return 'USD'
  }
}

function Pestana({ activa, onClick, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-lg px-3 py-1 text-xs font-medium transition-colors ${
        activa ? 'bg-aldo-card text-gray-900 shadow-sm' : 'text-gray-500'
      }`}
    >
      {children}
    </button>
  )
}

export default function CotizacionesCard({ presupuestoDiario }) {
  const [datos, setDatos] = useState(null)
  const [fallo, setFallo] = useState(false)
  const [moneda, setMoneda] = useState(monedaInicial)

  useEffect(() => {
    getCotizaciones()
      .then(setDatos)
      .catch(() => setFallo(true))
  }, [])

  const elegir = (m) => {
    setMoneda(m)
    try {
      localStorage.setItem(CLAVE_MONEDA, m)
    } catch {
      // sin persistencia
    }
  }

  // Si no hay datos ni cache, la tarjeta no aparece: es info de apoyo, no vale un error.
  if (fallo) return null

  const blue = datos?.dolares.find((d) => d.casa === 'blue')
  const saldoPositivo = presupuestoDiario > 0

  return (
    <div className="w-full max-w-sm rounded-2xl bg-aldo-card p-4 shadow-sm ring-1 ring-gray-100">
      <div className="mb-3 flex items-center justify-between">
        <span className="flex items-center gap-1.5 text-sm font-medium text-gray-700">
          <DollarSign size={15} className="text-gray-400" />
          Cotizaciones
        </span>
        <div className="flex rounded-xl bg-gray-100 p-0.5">
          <Pestana activa={moneda === 'USD'} onClick={() => elegir('USD')}>
            Dólar
          </Pestana>
          <Pestana activa={moneda === 'CLP'} onClick={() => elegir('CLP')}>
            Peso chileno
          </Pestana>
        </div>
      </div>

      {!datos && <p className="py-4 text-center text-xs text-gray-400">Buscando cotizaciones...</p>}

      {datos && moneda === 'USD' && (
        <>
          <div className="grid grid-cols-[1fr_auto_auto] gap-x-4 gap-y-1.5 text-sm">
            <span />
            <span className="text-right text-xs text-gray-400">Compra</span>
            <span className="text-right text-xs text-gray-400">Venta</span>
            {datos.dolares.map((d) => (
              <div key={d.casa} className="contents">
                <span className="text-gray-600">{NOMBRE_CASA[d.casa] ?? d.nombre}</span>
                <span className="text-right tabular-nums text-gray-500">{d.compra ? formatPesos(d.compra) : '—'}</span>
                <span className="text-right font-medium tabular-nums text-gray-900">{formatPesos(d.venta)}</span>
              </div>
            ))}
          </div>
          {blue && saldoPositivo && (
            <p className="mt-3 text-xs text-gray-500">
              Tu saldo de hoy son unos <span className="font-medium text-gray-700">US$ {formatEntero(presupuestoDiario / blue.venta)}</span> al blue.
            </p>
          )}
        </>
      )}

      {datos && moneda === 'CLP' &&
        (datos.clp ? (
          <>
            <div className="flex flex-col gap-1.5 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">1 peso chileno</span>
                <span className="font-medium tabular-nums text-gray-900">{formatPesos(datos.clp.venta, 2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">{formatPesos(1000)} te dan</span>
                <span className="font-medium tabular-nums text-gray-900">CLP {formatEntero(1000 / datos.clp.venta)}</span>
              </div>
            </div>
            {saldoPositivo && (
              <p className="mt-3 text-xs text-gray-500">
                Tu saldo de hoy son unos <span className="font-medium text-gray-700">CLP {formatEntero(presupuestoDiario / datos.clp.venta)}</span>.
              </p>
            )}
          </>
        ) : (
          <p className="py-4 text-center text-xs text-gray-400">No encontré la cotización del peso chileno.</p>
        ))}

      {datos && (
        <p className="mt-3 text-[11px] text-gray-400">
          {datos.desactualizado ? 'Sin conexión · último dato del ' : 'Actualizado '}
          {formatHora(datos.actualizado)} · dolarapi.com
        </p>
      )}
    </div>
  )
}
