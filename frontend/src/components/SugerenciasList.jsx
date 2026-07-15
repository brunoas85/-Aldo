import { Lightbulb } from 'lucide-react'

export default function SugerenciasList({ sugerencias }) {
  if (!sugerencias?.length) return null

  return (
    <div className="flex w-full max-w-sm flex-col gap-2">
      <span className="px-1 text-xs font-medium uppercase tracking-wide text-gray-400">
        $Aldo te cuenta
      </span>
      {sugerencias.map((texto, i) => (
        <div
          key={i}
          className="flex items-start gap-2 rounded-2xl bg-violet-50 p-3 text-sm text-violet-900 ring-1 ring-violet-100"
        >
          <Lightbulb size={16} className="mt-0.5 shrink-0 text-violet-500" />
          <span>{texto}</span>
        </div>
      ))}
    </div>
  )
}
