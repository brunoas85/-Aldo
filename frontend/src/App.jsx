import { useEffect, useState } from 'react'
import { AlertCircle, Clock3, Moon, Settings, Sun, X } from 'lucide-react'
import Dashboard from './components/Dashboard'
import ExpenseInput from './components/ExpenseInput'
import ConfigWizard from './components/ConfigWizard'
import IngresoModal from './components/IngresoModal'
import HistorialModal from './components/HistorialModal'
import SugerenciasList from './components/SugerenciasList'
import GastosFijosList from './components/GastosFijosList'
import GastoPorDiaChart from './components/GastoPorDiaChart'
import GastosFijosChart from './components/GastosFijosChart'
import CotizacionesCard from './components/CotizacionesCard'
import ClaveModal from './components/ClaveModal'
import useTema from './useTema'
import {
  getDashboard,
  saveConfig,
  registrarGasto,
  editarGasto,
  borrarGasto,
  registrarIngreso,
  editarIngreso,
  borrarIngreso,
  guardarClave,
} from './api/client'

function sumarDias(iso, n) {
  const d = new Date(`${iso}T00:00:00`)
  d.setDate(d.getDate() + n)
  return d.toISOString().slice(0, 10)
}

function mensajeDeError(err) {
  if (!err.response) return 'No me pude conectar con el servidor. ¿Está prendido el backend?'
  if (err.response.status === 422) return 'Revisá los datos: los montos tienen que ser mayores a cero.'
  const detail = err.response.data?.detail
  return typeof detail === 'string' ? detail : 'Algo salió mal. Probá de nuevo.'
}

function App() {
  const [dashboard, setDashboard] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)
  const [showConfig, setShowConfig] = useState(false)
  const [showIngreso, setShowIngreso] = useState(false)
  const [showHistorial, setShowHistorial] = useState(false)
  const { tema, alternarTema } = useTema()
  // null: no hace falta clave · 'nueva': la pedimos · 'incorrecta': la que puso no anduvo
  const [pedirClave, setPedirClave] = useState(null)
  const [despertando, setDespertando] = useState(false)

  // Render (plan gratis) duerme el backend: el primer request puede tardar hasta un minuto.
  useEffect(() => {
    if (!cargando) return setDespertando(false)
    const t = setTimeout(() => setDespertando(true), 4000)
    return () => clearTimeout(t)
  }, [cargando])

  const manejarSinClave = (err) => {
    if (err.response?.status !== 401) return false
    setPedirClave((actual) => (actual === null && !err.config?.headers?.['X-Aldo-Clave'] ? 'nueva' : 'incorrecta'))
    return true
  }

  const cargarDashboard = () => {
    setCargando(true)
    setError(null)
    getDashboard()
      .then(setDashboard)
      .catch((err) => {
        // Solo un 404 significa "todavía no configuraste nada"; cualquier otro error
        // (backend caído, 500) no tiene que mandarte a cargar todo de nuevo.
        if (err.response?.status === 404) setShowConfig(true)
        else if (!manejarSinClave(err)) setError(mensajeDeError(err))
      })
      .finally(() => setCargando(false))
  }

  useEffect(cargarDashboard, [])

  // Ejecuta una llamada que devuelve el dashboard. Devuelve true si salió bien, así
  // los componentes solo limpian sus inputs cuando el dato quedó guardado.
  const conDashboard = async (llamada) => {
    try {
      setDashboard(await llamada())
      setError(null)
      return true
    } catch (err) {
      if (!manejarSinClave(err)) setError(mensajeDeError(err))
      return false
    }
  }

  const handleSaveClave = (clave) => {
    guardarClave(clave)
    setPedirClave(null)
    cargarDashboard()
  }

  const handleSaveConfig = async (config) => {
    const ok = await conDashboard(() => saveConfig(config))
    if (ok) setShowConfig(false)
    return ok
  }

  const handleAddGasto = (monto) => conDashboard(() => registrarGasto({ monto }))

  const handleEditGasto = (id, payload) => conDashboard(() => editarGasto(id, payload))

  const handleDeleteGasto = (id) => conDashboard(() => borrarGasto(id))

  const handleAddIngreso = async (payload) => {
    const ok = await conDashboard(() => registrarIngreso(payload))
    if (ok) setShowIngreso(false)
    return ok
  }

  const handleEditIngreso = (id, payload) => conDashboard(() => editarIngreso(id, payload))

  const handleDeleteIngreso = (id) => conDashboard(() => borrarIngreso(id))

  const hoy = dashboard
    ? sumarDias(dashboard.inicio_ciclo, dashboard.dias_totales_ciclo - dashboard.dias_restantes)
    : null

  const ingresoTotal = dashboard ? dashboard.ingresos_mensuales + dashboard.ingresos_variables_ciclo : 0

  const poolInicial = dashboard
    ? ingresoTotal - dashboard.gastos_fijos.reduce((acc, g) => acc + g.monto, 0) - dashboard.meta_ahorro
    : 0

  return (
    <main className="flex min-h-svh flex-col items-center gap-6 px-4 pb-32 pt-10">
      {error && (
        <div
          role="alert"
          className="fixed inset-x-4 top-4 z-[60] mx-auto flex max-w-sm items-start gap-2 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700 shadow-md ring-1 ring-red-100 dark:bg-red-950 dark:text-red-200 dark:ring-red-900"
        >
          <AlertCircle size={18} className="mt-0.5 shrink-0" />
          <p className="flex-1">{error}</p>
          {!dashboard && !cargando ? (
            <button type="button" onClick={cargarDashboard} className="font-semibold underline">
              Reintentar
            </button>
          ) : (
            <button type="button" onClick={() => setError(null)} aria-label="Cerrar" className="text-red-400">
              <X size={16} />
            </button>
          )}
        </div>
      )}

      {cargando && !dashboard && (
        <div className="mt-20 text-center text-sm text-gray-400">
          <p>Cargando...</p>
          {despertando && <p className="mt-1">Aldo se está despertando, puede tardar hasta un minuto.</p>}
        </div>
      )}

      {dashboard && (
        <>
          <Dashboard
            nombre={dashboard.nombre}
            presupuestoDiario={dashboard.presupuesto_diario}
            diasRestantes={dashboard.dias_restantes}
            estado={dashboard.estado}
            gastadoHoy={dashboard.gastado_hoy}
            metaAhorro={dashboard.meta_ahorro}
            saldoCiclo={dashboard.saldo_disponible_ciclo}
            ingresoTotal={ingresoTotal}
            ingresoNeto={poolInicial}
            accion={
              <button
                type="button"
                onClick={alternarTema}
                aria-label={tema === 'oscuro' ? 'Pasar a modo claro' : 'Pasar a modo oscuro'}
                className="rounded-full p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
              >
                {tema === 'oscuro' ? <Sun size={18} /> : <Moon size={18} />}
              </button>
            }
          />
          <SugerenciasList sugerencias={dashboard.sugerencias} />
          <GastosFijosList gastosFijos={dashboard.gastos_fijos} ingresosMensuales={dashboard.ingresos_mensuales} />
          <GastoPorDiaChart
            inicioCiclo={dashboard.inicio_ciclo}
            finCiclo={dashboard.fin_ciclo}
            hoy={hoy}
            poolInicial={poolInicial}
            gastosCiclo={dashboard.gastos_ciclo}
          />
          <GastosFijosChart gastosFijos={dashboard.gastos_fijos} />
          <CotizacionesCard presupuestoDiario={dashboard.presupuesto_diario} />

          <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-2">
            <button
              type="button"
              onClick={() => setShowHistorial(true)}
              className="flex items-center gap-1.5 text-sm font-medium text-gray-500 hover:text-gray-700"
            >
              <Clock3 size={15} />
              Ver movimientos del ciclo
            </button>
            <button
              type="button"
              onClick={() => setShowConfig(true)}
              className="flex items-center gap-1.5 text-sm font-medium text-gray-500 hover:text-gray-700"
            >
              <Settings size={15} />
              Editar ingresos y gastos fijos
            </button>
          </div>

          <ExpenseInput onAdd={handleAddGasto} onOpenIngreso={() => setShowIngreso(true)} />
        </>
      )}

      <ConfigWizard
        open={showConfig}
        onSave={handleSaveConfig}
        onClose={dashboard ? () => setShowConfig(false) : undefined}
        initialData={dashboard}
      />
      <ClaveModal open={pedirClave !== null} incorrecta={pedirClave === 'incorrecta'} onSave={handleSaveClave} />
      <IngresoModal open={showIngreso} onSave={handleAddIngreso} onClose={() => setShowIngreso(false)} />
      {dashboard && (
        <HistorialModal
          open={showHistorial}
          gastos={dashboard.gastos_ciclo}
          ingresos={dashboard.ingresos_variables}
          onClose={() => setShowHistorial(false)}
          onEditGasto={handleEditGasto}
          onDeleteGasto={handleDeleteGasto}
          onEditIngreso={handleEditIngreso}
          onDeleteIngreso={handleDeleteIngreso}
        />
      )}
    </main>
  )
}

export default App
