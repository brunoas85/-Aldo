import { useState } from 'react'
import { KeyRound } from 'lucide-react'
import AldoAvatar from './AldoAvatar'

export default function ClaveModal({ open, incorrecta, onSave }) {
  const [clave, setClave] = useState('')

  if (!open) return null

  const handleSubmit = (e) => {
    e.preventDefault()
    if (clave.trim()) onSave(clave.trim())
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 p-4 sm:items-center">
      <form onSubmit={handleSubmit} className="w-full max-w-sm rounded-3xl bg-aldo-card p-6 shadow-xl">
        <div className="mb-4 flex items-center gap-3">
          <AldoAvatar size="sm" />
          <div>
            <h2 className="text-lg font-semibold text-gray-900">¿Sos vos?</h2>
            <p className="text-sm text-gray-500">Poné tu clave de $Aldo. Te la pido una sola vez en este dispositivo.</p>
          </div>
        </div>

        <label className="mb-5 block text-sm font-medium text-gray-700">
          <span className="flex items-center gap-1.5">
            <KeyRound size={14} className="text-gray-400" />
            Clave
          </span>
          <input
            type="password"
            autoFocus
            required
            autoComplete="current-password"
            value={clave}
            onChange={(e) => setClave(e.target.value)}
            className="mt-1 w-full rounded-xl border border-gray-300 px-4 py-3 text-sm focus:border-emerald-500 focus:outline-none"
          />
          {incorrecta && <span className="mt-1 block text-xs text-red-500">Esa clave no es. Probá de nuevo.</span>}
        </label>

        <button
          type="submit"
          className="w-full rounded-xl bg-emerald-500 py-3 font-semibold text-white active:bg-emerald-600"
        >
          Entrar
        </button>
      </form>
    </div>
  )
}
