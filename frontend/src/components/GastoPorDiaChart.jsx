import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis } from 'recharts'

const ACCENT = '#2a78d6'
const MUTED = '#898781'
const GRID = 'var(--color-aldo-grid)'

const formatMonto = (valor) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }).format(valor)

const formatFechaCorta = (iso) => {
  const [, mes, dia] = iso.split('-')
  return `${dia}/${mes}`
}

function sumarDias(iso, n) {
  const d = new Date(`${iso}T00:00:00`)
  d.setDate(d.getDate() + n)
  return d.toISOString().slice(0, 10)
}

function construirSerie({ inicioCiclo, finCiclo, hoy, poolInicial, gastosCiclo }) {
  const gastoPorFecha = {}
  for (const g of gastosCiclo) {
    gastoPorFecha[g.fecha] = (gastoPorFecha[g.fecha] || 0) + g.monto
  }

  const dias = []
  let d = inicioCiclo
  while (d <= finCiclo) {
    dias.push(d)
    d = sumarDias(d, 1)
  }
  const diasTotales = dias.length

  let acumuladoReal = 0
  return dias.map((fecha, i) => {
    if (fecha <= hoy) acumuladoReal += gastoPorFecha[fecha] || 0
    return {
      fecha,
      etiqueta: formatFechaCorta(fecha),
      ideal: Math.round(((i + 1) / diasTotales) * poolInicial),
      real: fecha <= hoy ? Math.round(acumuladoReal) : null,
    }
  })
}

function TooltipPersonalizado({ active, payload, label }) {
  if (!active || !payload?.length) return null
  const real = payload.find((p) => p.dataKey === 'real')
  const ideal = payload.find((p) => p.dataKey === 'ideal')
  return (
    <div className="rounded-lg bg-aldo-card px-3 py-2 text-xs shadow-md ring-1 ring-gray-100">
      <p className="mb-1 font-medium text-gray-700">{label}</p>
      {real?.value != null && <p style={{ color: ACCENT }}>Gasto real: {formatMonto(real.value)}</p>}
      {ideal && <p style={{ color: MUTED }}>Ritmo ideal: {formatMonto(ideal.value)}</p>}
    </div>
  )
}

export default function GastoPorDiaChart({ inicioCiclo, finCiclo, hoy, poolInicial, gastosCiclo }) {
  const datos = construirSerie({ inicioCiclo, finCiclo, hoy, poolInicial, gastosCiclo })

  return (
    <div className="w-full max-w-sm rounded-2xl bg-aldo-card p-4 shadow-sm ring-1 ring-gray-100">
      <div className="mb-3 flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">Ritmo de gasto del ciclo</span>
        <div className="flex items-center gap-3 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: ACCENT }} />
            Real
          </span>
          <span className="flex items-center gap-1">
            <span className="h-0.5 w-2.5" style={{ backgroundColor: MUTED }} />
            Ideal
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={datos} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
          <CartesianGrid stroke={GRID} vertical={false} strokeWidth={1} />
          <XAxis
            dataKey="etiqueta"
            interval="preserveStartEnd"
            tick={{ fill: MUTED, fontSize: 11 }}
            axisLine={{ stroke: GRID }}
            tickLine={false}
            minTickGap={24}
          />
          <Tooltip content={<TooltipPersonalizado />} />
          <Area
            type="monotone"
            dataKey="ideal"
            stroke={MUTED}
            strokeWidth={2}
            fill="none"
            dot={false}
            isAnimationActive={false}
          />
          <Area
            type="monotone"
            dataKey="real"
            stroke={ACCENT}
            strokeWidth={2}
            fill={ACCENT}
            fillOpacity={0.1}
            dot={false}
            connectNulls={false}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
