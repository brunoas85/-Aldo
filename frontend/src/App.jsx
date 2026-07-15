import { useEffect, useState } from 'react'
import { Clock3, Settings } from 'lucide-react'
import Dashboard from './components/Dashboard'
import ExpenseInput from './components/ExpenseInput'
import ConfigWizard from './components/ConfigWizard'
import IngresoModal from './components/IngresoModal'
import HistorialModal from './components/HistorialModal'
import SugerenciasList from './components/SugerenciasList'
import GastosFijosList from './components/GastosFijosList'
import GastoPorDiaChart from './components/GastoPorDiaChart'
import GastosFijosChart from './components/GastosFijosChart'
import {
  getDashboard,
  saveConfig,
  registrarGasto,
  editarGasto,
  borrarGasto,
  registrarIngreso,
  editarIngreso,
  borrarIngreso,
} from './api/client'

function sumarDias(iso, n) {
  const d = new Date(`${iso}T00:00:00`)
  d.setDate(d.getDate() + n)
  return d.toISOString().slice(0, 10)
}

function App() {
  const [dashboard, setDashboard] = useState(null)
  const [showConfig, setShowConfig] = useState(false)
  const [showIngreso, setShowIngreso] = useState(false)
  const [showHistorial, setShowHistorial] = useState(false)

  useEffect(() => {
    getDashboard()
      .then(setDashboard)
      .catch(() => setShowConfig(true))
  }, [])

  const handleSaveConfig = async (config) => {
    const data = await saveConfig(config)
    setDashboard(data)
    setShowConfig(false)
  }

  const handleAddGasto = async (monto) => {
    const data = await registrarGasto({ monto })
    setDashboard(data)
  }

  const handleEditGasto = async (id, payload) => {
    const data = await editarGasto(id, payload)
    setDashboard(data)
  }

  const handleDeleteGasto = async (id) => {
    const data = await borrarGasto(id)
    setDashboard(data)
  }

  const handleAddIngreso = async (payload) => {
    const data = await registrarIngreso(payload)
    setDashboard(data)
    setShowIngreso(false)
  }

  const handleEditIngreso = async (id, payload) => {
    const data = await editarIngreso(id, payload)
    setDashboard(data)
  }

  const handleDeleteIngreso = async (id) => {
    const data = await borrarIngreso(id)
    setDashboard(data)
  }

  const hoy = dashboard
    ? sumarDias(dashboard.inicio_ciclo, dashboard.dias_totales_ciclo - dashboard.dias_restantes)
    : null

  const ingresoTotal = dashboard ? dashboard.ingresos_mensuales + dashboard.ingresos_variables_ciclo : 0

  const poolInicial = dashboard
    ? ingresoTotal - dashboard.gastos_fijos.reduce((acc, g) => acc + g.monto, 0) - dashboard.meta_ahorro
    : 0

  return (
    <main className="flex min-h-svh flex-col items-center gap-6 px-4 pb-32 pt-10">
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
