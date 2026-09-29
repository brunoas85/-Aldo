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
*   **Frontend:** React 19 + Vite + Tailwind CSS 4, mobile-first (`frontend/`). Modo oscuro con la clase `.dark` en `<html>` (`useTema.js`): en `index.css` se invierte la escala de grises y `bg-aldo-card` reemplaza a `bg-white`, así que en los componentes nuevos usá grises y `bg-aldo-card`, y agregá `dark:` solo para los colores con tinte.
*   **Backend:** FastAPI + SQLAlchemy + Pydantic v2 (`backend/`).
*   **Base de Datos:** SQLite en local (`backend/aldo.db`) y PostgreSQL (Neon) en producción, elegida con `ALDO_DATABASE_URL`. Migraciones Alembic (`backend/migrations/`) que tienen que funcionar en los dos motores.

### Cómo levantarlo
```bash
# Backend (desde backend/)
venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn main:app --reload          # http://localhost:8000  ·  Swagger en /docs
                                   # al arrancar aplica las migraciones pendientes
pytest                             # tests (usan una base temporal, nunca aldo.db)
alembic revision -m "descripcion"  # nueva migración (escribirla a mano en migrations/versions/)

# Frontend (desde frontend/)
npm run dev                        # http://localhost:5173 (proxy /api -> :8000)
npm run lint && npm run build      # verificación
```

### Producción (Render + Neon + Vercel)
*   **Backend en Render** con `render.yaml` (Blueprint). Variables: `ALDO_DATABASE_URL` (connection string de Neon, `postgresql://...`), `ALDO_API_KEY` (la genera Render) y `ALDO_CORS_ORIGINS` (URL del frontend, separadas por coma si hay varias).
*   **Frontend en Vercel** con Root Directory `frontend/` y `VITE_API_URL` = URL del backend en Render (sin `/api` al final).
*   **Pasar los datos locales a Neon:** `python -m scripts.migrar_a_neon` (desde `backend/`). Pide la URL sin mostrarla, crea las tablas, copia todo en una transacción y no hace nada si el destino ya tiene datos.
*   Si `ALDO_API_KEY` no está definida, la API queda abierta. Eso solo tiene sentido en desarrollo local.

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

**Clave:** si el server tiene `ALDO_API_KEY`, todas las rutas salvo `/api/health` exigen el header `X-Aldo-Clave` con ese valor, y sin él responden `401`. El frontend pide la clave la primera vez y la guarda en `localStorage`.

| Método | Ruta | Body | Notas |
|---|---|---|---|
| `GET` | `/api/dashboard` | — | 404 si nunca se configuró |
| `POST` | `/api/config` | `{ingresos_mensuales>0, dia_cobro 1-31, meta_ahorro>=0, gastos_fijos:[{nombre, monto>0, categoria?}]}` | Crea o actualiza la config del ciclo actual |
| `POST` | `/api/gastos` | `{monto>0, descripcion?}` | Fecha = hoy |
| `PUT` / `DELETE` | `/api/gastos/{id}` | `{monto>0, descripcion?}` | |
| `POST` | `/api/ingresos` | `{monto>0, descripcion?}` | Ingreso extra del ciclo |
| `PUT` / `DELETE` | `/api/ingresos/{id}` | `{monto>0, descripcion?}` | |
| `GET` | `/api/health` | — | No pide clave |

**API externa:** las cotizaciones (dólar oficial/blue/MEP/tarjeta y peso chileno) se piden directo desde el navegador a `dolarapi.com` (`frontend/src/api/cotizaciones.js`), con caché de 30 min en `localStorage`. No pasan por el backend.

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
*   No hay tests de frontend.
*   Cambiar `dia_cobro` puede mover el ciclo y dejar ingresos extra en la configuración anterior.
