import axios from 'axios'

// En desarrollo VITE_API_URL no está y se usa el proxy de Vite (/api -> :8000).
// En producción es la URL del backend en Render, sin /api al final.
const api = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL ?? ''}/api`,
})

// Token de sesión que devuelven /api/auth/login y /api/auth/registro. Queda en este dispositivo hasta que
// cerrás sesión o vence (60 días); ahí el server responde 401 y se vuelve al login.
const SESION_STORAGE = 'mango-sesion'

function leerToken() {
  try {
    return localStorage.getItem(SESION_STORAGE)
  } catch {
    return null
  }
}

export const haySesion = () => Boolean(leerToken())

export function cerrarSesion() {
  try {
    localStorage.removeItem(SESION_STORAGE)
  } catch {
    // sin localStorage no había nada guardado
  }
}

api.interceptors.request.use((config) => {
  const token = leerToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

const guardarSesion = ({ data }) => {
  try {
    localStorage.setItem(SESION_STORAGE, data.token)
  } catch {
    // sin localStorage la sesión dura hasta que se recargue la página
    api.defaults.headers.common.Authorization = `Bearer ${data.token}`
  }
  return data
}

export const entrar = (datos) => api.post('/auth/login', datos).then(guardarSesion)

export const registrarse = (datos) => api.post('/auth/registro', datos).then(guardarSesion)

export const getDashboard = () => api.get('/dashboard').then((res) => res.data)

export const saveConfig = (data) => api.post('/config', data).then((res) => res.data)

export const registrarGasto = (data) => api.post('/gastos', data).then((res) => res.data)

export const editarGasto = (id, data) => api.put(`/gastos/${id}`, data).then((res) => res.data)

export const borrarGasto = (id) => api.delete(`/gastos/${id}`).then((res) => res.data)

export const registrarIngreso = (data) => api.post('/ingresos', data).then((res) => res.data)

export const editarIngreso = (id, data) => api.put(`/ingresos/${id}`, data).then((res) => res.data)

export const borrarIngreso = (id) => api.delete(`/ingresos/${id}`).then((res) => res.data)

export default api
