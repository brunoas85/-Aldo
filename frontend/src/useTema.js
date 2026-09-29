import { useEffect, useState } from 'react'

const CLAVE = 'aldo-tema'

// Arranca con lo que eligió el usuario; si nunca eligió, sigue al sistema.
// index.html aplica la misma lógica antes de pintar para evitar el parpadeo.
function temaInicial() {
  try {
    const guardado = localStorage.getItem(CLAVE)
    if (guardado === 'claro' || guardado === 'oscuro') return guardado
  } catch {
    // localStorage bloqueado: seguimos con el sistema
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'oscuro' : 'claro'
}

export default function useTema() {
  const [tema, setTema] = useState(temaInicial)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', tema === 'oscuro')
  }, [tema])

  const alternarTema = () => {
    const nuevo = tema === 'oscuro' ? 'claro' : 'oscuro'
    setTema(nuevo)
    try {
      localStorage.setItem(CLAVE, nuevo)
    } catch {
      // sin persistencia, pero el cambio aplica igual
    }
  }

  return { tema, alternarTema }
}
