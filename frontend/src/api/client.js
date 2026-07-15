import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
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
