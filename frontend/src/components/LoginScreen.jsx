import { useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'
import MangoAvatar from './MangoAvatar'

const INPUT = 'mt-1 w-full rounded-xl border border-gray-300 bg-mango-card px-4 py-3 focus:border-emerald-500 focus:outline-none'

export default function LoginScreen({ entrando, error, onEntrar, onRegistrarse }) {
  const [modo, setModo] = useState('login')
  const [nombre, setNombre] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [verPassword, setVerPassword] = useState(false)
  const registro = modo === 'registro'

  const handleSubmit = (e) => {
    e.preventDefault()
    if (registro) onRegistrarse({ nombre, email, password })
    else onEntrar({ email, password })
  }

  return (
    <div className="flex w-full max-w-sm flex-1 flex-col items-center justify-center gap-6 text-center">
      <MangoAvatar />
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Mango</h1>
        <p className="mt-2 text-gray-500">Cuánto podés gastar hoy, sin culpa y sin planillas.</p>
      </div>

      <form onSubmit={handleSubmit} className="w-full text-left">
        {registro && (
          <label className="mb-3 block text-sm font-medium text-gray-700">
            ¿Cómo te llamo?
            <input
              type="text"
              required
              maxLength={50}
              autoComplete="given-name"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              className={INPUT}
            />
          </label>
        )}
        <label className="mb-3 block text-sm font-medium text-gray-700">
          Email
          <input
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className={INPUT}
          />
        </label>
        <label className="mb-5 block text-sm font-medium text-gray-700">
          Contraseña
          <div className="relative">
            <input
              type={verPassword ? 'text' : 'password'}
              required
              minLength={registro ? 8 : undefined}
              autoComplete={registro ? 'new-password' : 'current-password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={`${INPUT} pr-12`}
            />
            <button
              type="button"
              onClick={() => setVerPassword((v) => !v)}
              aria-label={verPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              className="absolute inset-y-0 right-0 mt-1 px-4 text-gray-400 hover:text-gray-600"
            >
              {verPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
          {registro && <span className="mt-1 block text-xs font-normal text-gray-400">Al menos 8 caracteres.</span>}
        </label>

        <button
          type="submit"
          disabled={entrando}
          className="w-full rounded-xl bg-emerald-500 py-3 font-semibold text-white active:bg-emerald-600 disabled:opacity-40"
        >
          {registro ? 'Crear cuenta' : 'Entrar'}
        </button>
      </form>

      <div className="flex flex-col items-center gap-2">
        {entrando && <p className="text-sm text-gray-400">Entrando... si Mango estaba dormido, puede tardar un minuto.</p>}
        {error && <p className="text-sm text-red-500">{error}</p>}
        <p className="text-sm text-gray-500">
          {registro ? '¿Ya tenés cuenta?' : '¿No tenés cuenta?'}{' '}
          <button
            type="button"
            onClick={() => setModo(registro ? 'login' : 'registro')}
            className="font-semibold text-emerald-600 underline dark:text-emerald-400"
          >
            {registro ? 'Entrá' : 'Registrate'}
          </button>
        </p>
      </div>

      <p className="text-xs text-gray-400">Tus datos quedan guardados en tu cuenta y solo los ves vos.</p>
    </div>
  )
}
