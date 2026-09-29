import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { COLOR_CATEGORIA } from '../categorias'

const formatMonto = (valor) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }).format(valor)

function agruparPorCategoria(gastosFijos) {
  const totales = {}
  for (const g of gastosFijos) {
    const cat = g.categoria || 'Otros'
    totales[cat] = (totales[cat] || 0) + g.monto
  }
  return Object.entries(totales)
    .map(([categoria, monto]) => ({ categoria, monto }))
    .sort((a, b) => b.monto - a.monto)
}

function TooltipPersonalizado({ active, payload }) {
  if (!active || !payload?.length) return null
  const { categoria, monto } = payload[0].payload
  return (
    <div className="rounded-lg bg-aldo-card px-3 py-2 text-xs shadow-md ring-1 ring-gray-100">
      <p className="font-medium text-gray-700">{categoria}</p>
      <p className="text-gray-500">{formatMonto(monto)}</p>
    </div>
  )
}

export default function GastosFijosChart({ gastosFijos }) {
  if (!gastosFijos?.length) return null

  const datos = agruparPorCategoria(gastosFijos)
  const total = datos.reduce((acc, d) => acc + d.monto, 0)

  return (
    <div className="w-full max-w-sm rounded-2xl bg-aldo-card p-4 shadow-sm ring-1 ring-gray-100">
      <span className="text-sm font-medium text-gray-700">Gastos fijos por categoría</span>

      <div className="flex items-center gap-4">
        <div className="h-36 w-36 shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={datos}
                dataKey="monto"
                nameKey="categoria"
                innerRadius={38}
                outerRadius={64}
                strokeWidth={2}
                stroke="var(--color-aldo-card)"
                isAnimationActive={false}
              >
                {datos.map((d) => (
                  <Cell key={d.categoria} fill={COLOR_CATEGORIA[d.categoria] ?? '#898781'} />
                ))}
              </Pie>
              <Tooltip content={<TooltipPersonalizado />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <ul className="flex min-w-0 flex-1 flex-col gap-1.5">
          {datos.map((d) => (
            <li key={d.categoria} className="flex items-center justify-between gap-2 text-xs">
              <span className="flex min-w-0 items-center gap-1.5 text-gray-600">
                <span
                  className="h-2 w-2 shrink-0 rounded-full"
                  style={{ backgroundColor: COLOR_CATEGORIA[d.categoria] ?? '#898781' }}
                />
                <span className="truncate">{d.categoria}</span>
              </span>
              <span className="shrink-0 font-medium text-gray-900">
                {total > 0 ? Math.round((d.monto / total) * 100) : 0}%
              </span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
