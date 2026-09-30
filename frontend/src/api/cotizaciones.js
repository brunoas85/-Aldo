import axios from 'axios'

// Cotizaciones desde dolarapi.com (gratis, sin API key, CORS abierto).
// Va directo desde el navegador: no pasa por nuestro backend.
const DOLARES_URL = 'https://dolarapi.com/v1/dolares'
const OTRAS_URL = 'https://dolarapi.com/v1/cotizaciones'

const CLAVE_CACHE = 'mango-cotizaciones'
const VIGENCIA_MS = 30 * 60 * 1000

// Las casas que muestra la tarjeta, en este orden.
const CASAS = ['oficial', 'blue', 'bolsa', 'tarjeta']

function leerCache() {
  try {
    return JSON.parse(localStorage.getItem(CLAVE_CACHE))
  } catch {
    return null
  }
}

// Devuelve { dolares: [{casa, nombre, compra, venta}], clp: {compra, venta}, actualizado, desactualizado }.
// Si la API falla, devuelve lo último que se guardó marcado como desactualizado; si no hay nada, tira.
export async function getCotizaciones() {
  const cache = leerCache()
  if (cache && Date.now() - cache.guardado < VIGENCIA_MS) return cache.datos

  try {
    const [dolares, otras] = await Promise.all([
      axios.get(DOLARES_URL, { timeout: 8000 }).then((r) => r.data),
      axios.get(OTRAS_URL, { timeout: 8000 }).then((r) => r.data),
    ])
    const clp = otras.find((c) => c.moneda === 'CLP')
    const datos = {
      dolares: CASAS.map((casa) => dolares.find((d) => d.casa === casa)).filter(Boolean),
      clp: clp ? { compra: clp.compra, venta: clp.venta } : null,
      actualizado: dolares.map((d) => d.fechaActualizacion).sort().at(-1),
      desactualizado: false,
    }
    try {
      localStorage.setItem(CLAVE_CACHE, JSON.stringify({ guardado: Date.now(), datos }))
    } catch {
      // sin cache, no pasa nada
    }
    return datos
  } catch (err) {
    if (cache) return { ...cache.datos, desactualizado: true }
    throw err
  }
}
