# Claude.md - Proyecto: $Aldo (Tu saldo diario, amigable y sin vueltas)

**$Aldo** es una app de finanzas personales simplificada: le muestra al usuario únicamente cuánto puede gastar **hoy**, sin culpa y sin planillas. La app personifica el dinero en "Aldo", un asistente amigable que te cuida el bolsillo.

---

## 📌 Visión del Producto (MVP)
Al abrir la app, lo protagonista es:
1. **El saldo disponible para HOY**: un número gigante con la pregunta *¿Qué onda, Bruno? Hoy tenés para gastar...*, con color según la salud financiera.
2. **Un input ultra rápido** para restar un gasto en el momento.

Como apoyo secundario: una configuración en wizard (ingresos, día de cobro, gastos fijos, meta de ahorro), ingresos extra, historial editable, sugerencias de Aldo y gráficos del ciclo.

**Regla de Oro:** cero fricción. Registrar un gasto tiene que tomar menos de 3 segundos desde que abrís la app. Todo lo secundario no puede competir visualmente con el número del día.

---

## 🛠️ Stack Tecnológico
*   **Frontend:** React 19 + Vite + Tailwind CSS 4, mobile-first (`frontend/`).
*   **Backend:** FastAPI + SQLAlchemy + Pydantic v2 (`backend/`).
*   **Base de Datos:** SQLite (`backend/aldo.db`), a migrar a PostgreSQL más adelante.

### Cómo levantarlo
```bash
# Backend (desde backend/)
venv\Scripts\activate
uvicorn main:app --reload          # http://localhost:8000  ·  Swagger en /docs

# Frontend (desde frontend/)
npm run dev                        # http://localhost:5173 (proxy /api -> :8000)
npm run lint && npm run build      # verificación
```

---

## 🧮 Fórmula Core de $Aldo
El presupuesto se calcula por **ciclo de cobro**, no por mes calendario. El ciclo va desde el `dia_cobro` hasta el día anterior al próximo cobro (con ajuste para meses cortos).

$$Pool = Ingresos\ del\ mes + Ingresos\ extra\ del\ ciclo - Gastos\ fijos - Meta\ de\ ahorro - Gastado\ en\ el\ ciclo$$

$$Presupuesto\ de\ hoy = \frac{Pool + Gastado\ hoy}{Días\ restantes\ (incluye\ hoy)} - Gastado\ hoy$$

*   Si un día gastás de más, el número de hoy puede quedar negativo. El excedente se reparte entre los días restantes a partir de mañana, sin bloqueos.
*   **Estado:** `critico` si el presupuesto de hoy es menor a 0; `alerta` si es menor al 50% del promedio diario base del ciclo; en otro caso, `bien`.
*   **Ciclo nuevo:** si arranca un ciclo y no hay configuración, se hereda automáticamente la del último ciclo (`asegurar_config_actual`).

---

## 🔌 Contrato de API
Todas las mutaciones devuelven el **`DashboardOut` completo**, así el frontend reemplaza su estado sin recalcular nada. Si el usuario nunca configuró nada, las rutas responden `404`. Si los datos no son válidos, responden `422`.

| Método | Ruta | Body | Notas |
|---|---|---|---|
| `GET` | `/api/dashboard` | — | 404 si nunca se configuró |
| `POST` | `/api/config` | `{ingresos_mensuales>0, dia_cobro 1-31, meta_ahorro>=0, gastos_fijos:[{nombre, monto>0, categoria?}]}` | Crea o actualiza la config del ciclo actual |
| `POST` | `/api/gastos` | `{monto>0, descripcion?}` | Fecha = hoy |
| `PUT` / `DELETE` | `/api/gastos/{id}` | `{monto>0, descripcion?}` | |
| `POST` | `/api/ingresos` | `{monto>0, descripcion?}` | Ingreso extra del ciclo |
| `PUT` / `DELETE` | `/api/ingresos/{id}` | `{monto>0, descripcion?}` | |
| `GET` | `/api/health` | — | |

`DashboardOut` incluye: `nombre`, `presupuesto_diario`, `estado`, `dias_restantes`, `dias_totales_ciclo`, `inicio_ciclo`, `fin_ciclo`, `gastado_hoy`, `dia_cobro`, `ingresos_mensuales`, `meta_ahorro`, `gastos_fijos[]`, `ingresos_variables_ciclo`, `ingresos_variables[]`, `gastos_ciclo[]`, `saldo_disponible_ciclo`, `sugerencias[]`. La definición exacta está en `backend/app/schemas.py`.

---

## 🤖 Agentes
Hay dos subagentes definidos en `.claude/agents/`, cada uno con sus reglas específicas:

*   **`frontend-dev`**: todo lo que está en `frontend/` (UI, UX, consumo de la API).
*   **`backend-dev`**: todo lo que está en `backend/` (modelos, endpoints, fórmula, fechas).

### Protocolo de integración
1. **Contratos primero:** un cambio en la API se acuerda y se refleja en la tabla de arriba antes de codificarlo.
2. **Mocking:** el frontend puede simular respuestas respetando el contrato mientras el backend implementa.
3. **CORS:** el backend permite `http://localhost:5173`. En desarrollo, el proxy de Vite evita CORS de todas formas.

---

## 🗺️ Pendientes conocidos
*   Zona horaria: hoy se usa `date.today()` del servidor. Falta respetar la zona del usuario.
*   La plata se guarda como `Float`. Conviene migrar a centavos (`Integer`) o `Numeric`.
*   No hay migraciones (Alembic) ni tests automatizados.
*   Cambiar `dia_cobro` puede mover el ciclo y dejar ingresos extra en la configuración anterior.
