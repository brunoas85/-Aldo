import { useEffect, useRef, useState } from 'react'
import MangoAvatar from './MangoAvatar'

const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID
const SCRIPT_GOOGLE = 'https://accounts.google.com/gsi/client'

// Carga una sola vez el script de "Sign in with Google".
let cargaScript = null
function cargarGoogle() {
  cargaScript ??= new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = SCRIPT_GOOGLE
    script.async = true
    script.onload = () => resolve(window.google)
    script.onerror = () => {
      cargaScript = null
      reject(new Error('No se pudo cargar Google'))
    }
    document.head.appendChild(script)
  })
  return cargaScript
}

export default function LoginScreen({ tema, entrando, error, onCredential }) {
  const boton = useRef(null)
  const [sinGoogle, setSinGoogle] = useState(false)

  useEffect(() => {
    if (!CLIENT_ID) return
    let cancelado = false
    cargarGoogle()
      .then((google) => {
        if (cancelado || !boton.current) return
        google.accounts.id.initialize({
          client_id: CLIENT_ID,
          callback: ({ credential }) => onCredential(credential),
        })
        boton.current.replaceChildren()
        google.accounts.id.renderButton(boton.current, {
          theme: tema === 'oscuro' ? 'filled_black' : 'outline',
          size: 'large',
          shape: 'pill',
          text: 'continue_with',
          locale: 'es',
          width: 280,
        })
      })
      .catch(() => !cancelado && setSinGoogle(true))
    return () => {
      cancelado = true
    }
  }, [tema, onCredential])

  return (
    <div className="flex w-full max-w-sm flex-1 flex-col items-center justify-center gap-6 text-center">
      <MangoAvatar />
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Mango</h1>
        <p className="mt-2 text-gray-500">Cuánto podés gastar hoy, sin culpa y sin planillas.</p>
      </div>

      <div className="flex min-h-11 flex-col items-center gap-2">
        {!CLIENT_ID ? (
          <p className="text-sm text-red-500">Falta configurar VITE_GOOGLE_CLIENT_ID.</p>
        ) : sinGoogle ? (
          <p className="text-sm text-red-500">No pude cargar el botón de Google. Revisá tu conexión y recargá.</p>
        ) : (
          <div ref={boton} className={entrando ? 'pointer-events-none opacity-50' : ''} />
        )}
        {entrando && <p className="text-sm text-gray-400">Entrando... si Mango estaba dormido, puede tardar un minuto.</p>}
        {error && <p className="text-sm text-red-500">{error}</p>}
      </div>

      <p className="text-xs text-gray-400">Tus datos quedan guardados en tu cuenta y solo los ves vos.</p>
    </div>
  )
}
