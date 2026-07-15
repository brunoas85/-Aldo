import { Calendar, Landmark, PiggyBank, Receipt, Scale, Wallet } from 'lucide-react'
import AldoAvatar from './AldoAvatar'
import StatCard from './StatCard'

const GRADIENTES = {
  bien: 'from-emerald-400 to-teal-500',
  alerta: 'from-amber-400 to-orange-500',
  critico: 'from-red-400 to-rose-500',
}

const formatMonto = (valor) =>
  new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
    maximumFractionDigits: 0,
  }).format(valor)

export default function Dashboard({
  nombre,
  presupuestoDiario,
  diasRestantes,
  estado,
  gastadoHoy,
  metaAhorro,
  saldoCiclo,
  ingresoTotal,
  ingresoNeto,
}) {
  return (
    <div className="flex w-full max-w-sm flex-col items-center gap-4">
      <div className="flex w-full items-center gap-3">
        <AldoAvatar estado={estado} />
        <div className="text-left">
          <p className="text-sm text-gray-400">¿Qué onda, {nombre}?</p>
          <p className="text-sm font-medium text-gray-600">Hoy tenés para gastar</p>
        </div>
      </div>

      <div
        className={`w-full rounded-3xl bg-gradient-to-br ${GRADIENTES[estado] ?? GRADIENTES.bien} px-6 py-8 text-center text-white shadow-lg`}
      >
        <p className="text-5xl font-bold tabular-nums">{formatMonto(presupuestoDiario)}</p>
        <p className="mt-2 text-sm text-white/80">Quedan {diasRestantes} días en el ciclo</p>
      </div>

      <div className="grid w-full grid-cols-2 gap-3">
        <StatCard icon={Landmark} label="Ingreso total" value={formatMonto(ingresoTotal)} />
        <StatCard icon={Scale} label="Neto (post fijos y ahorro)" value={formatMonto(ingresoNeto)} />
        <StatCard icon={Calendar} label="Días restantes" value={diasRestantes} />
        <StatCard icon={Receipt} label="Gastado hoy" value={formatMonto(gastadoHoy)} />
        <StatCard icon={PiggyBank} label="Meta ahorro" value={formatMonto(metaAhorro)} accent="text-emerald-600" />
        <StatCard
          icon={Wallet}
          label="Te queda en el ciclo"
          value={formatMonto(saldoCiclo)}
          accent={saldoCiclo < 0 ? 'text-red-600' : 'text-gray-900'}
        />
      </div>
    </div>
  )
}
