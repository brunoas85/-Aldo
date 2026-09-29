import axios from 'axios'

// En desarrollo VITE_API_URL no está y se usa el proxy de Vite (/api -> :8000).
// En producción es la URL del backend en Render, sin /api al final.
const api = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL ?? ''}/api`,
})

// Clave de la API (ALDO_API_KEY del server). Se pide una vez y queda en este dispositivo.
const CLAVE_STORAGE = 'aldo-clave'

export function guardarClave(clave) {
  try {
    localStorage.setItem(CLAVE_STORAGE, clave)
  } catch {
    // sin localStorage: habrá que cargarla de nuevo la próxima vez
  }
}

api.interceptors.request.use((config) => {
  try {
    const clave = localStorage.getItem(CLAVE_STORAGE)
    if (clave) config.headers['X-Aldo-Clave'] = clave
  } catch {
    // sin localStorage el server responde 401 y se pide la clave
  }
  return config
})

export const getDashboard = () => api.get('/dashboard').then((res) => res.data)

export const saveConfig = (data) => api.post('/config', data).then((res) => res.data)

export const registrarGasto = (data) => api.post('/gastos', data).then((res) => res.data)

export const editarGasto = (id, data) => api.put(`/gastos/${id}`, data).then((res) => res.data)

export const borrarGasto = (id) => api.delete(`/gastos/${id}`).then((res) => res.data)

export const registrarIngreso = (data) => api.post('/ingresos', data).then((res) => res.data)

export const editarIngreso = (id, data) => api.put(`/ingresos/${id}`, data).then((res) => res.data)

export const borrarIngreso = (id) => api.delete(`/ingresos/${id}`).then((res) => res.data)

export default api
