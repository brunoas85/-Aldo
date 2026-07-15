# Claude.md - Proyecto: $Aldo (Tu saldo diario, amigable y sin vueltas)

Este documento define la arquitectura, el alcance del MVP y las reglas de desarrollo para el proyecto **$Aldo**, una aplicación de finanzas personales simplificada que ayuda a los usuarios a administrar su dinero mostrándoles únicamente un presupuesto diario disponible, libre de culpa.

---

## 📌 Visión del Producto (MVP)
Olvidémonos de las categorías complejas y gráficos de torta aburridos. Con **$Aldo**, el usuario no se estresa con planillas. La app personifica el dinero en "Aldo", un asistente amigable que te cuida el bolsillo. 

Al abrir la app, el usuario solo ve:
1. **El saldo disponible para HOY** (un número gigante con la pregunta: *¿Qué onda, Bruno? Hoy tenés para gastar...*).
2. Un input ultra-rápido para restar un gasto en el momento.
3. Un panel de configuración inicial muy básico (Ingresos mensuales estimables y Gastos fijos obligatorios).

---

## 🛠️ Stack Tecnológico
*   **Frontend:** React.js (con Tailwind CSS para diseño moderno, limpio, responsive y mobile-first).
*   **Backend:** FastAPI (Python) - Rápido, ligero, con tipado y documentación automática de endpoints (Swagger).
*   **Base de Datos:** SQLite (ideal para la etapa de MVP, fácil de migrar luego a PostgreSQL).

---

## 🤖 Definición de Agentes y Roles

### Agente 1: Frontend Developer (React & UI/UX)
**Misión:** Diseñar e implementar una interfaz de usuario minimalista, rápida, intuitiva y optimizada para celulares.

*   **Responsabilidades:**
    *   Mantener el estado de la UI de forma fluida.
    *   Diseñar una pantalla principal limpia: el "monto diario disponible" provisto por **$Aldo** debe ser el protagonista indiscutido (tipografía grande, colores que indiquen salud financiera: verde, amarillo, rojo).
    *   Implementar un modal de "Configuración inicial" donde el usuario ingresa:
        *   `Ingresos totales del mes`
        *   `Gastos fijos estimados` (alquiler, servicios, etc.)
    *   Crear una forma de registrar gastos ultra rápida (un campo numérico y un botón de restar).
    *   Consumir los endpoints del Backend mediante `fetch` o `axios`.

*   **Regla de Oro de UI:** Cero fricción. El usuario debe poder registrar un gasto en menos de 3 segundos desde que abre la app.

---

### Agente 2: Backend Developer (FastAPI & Lógica de Negocio)
**Misión:** Diseñar la API, el modelo de datos y la fórmula de cálculo del presupuesto diario, asegurando consistencia matemática.

*   **Fórmula Core de $Aldo:**
    $$Presupuesto\ Diario = \frac{Ingresos\ Restantes\ del\ Mes - Gastos\ Fijos\ Restantes}{Días\ Restantes\ del\ Mes}$$
    
    *Nota: Si un día el usuario gasta de más, el excedente se resta del total mensual y se recalcula el dividendo para los días restantes, ajustando dinámicamente el presupuesto diario sin penalizar con "bloqueos".*

*   **Responsabilidades:**
    *   Crear la estructura de la Base de Datos (Tablas: `Usuarios`, `ConfiguracionMensual`, `TransaccionesDiarias`).
    *   Implementar los endpoints clave:
        *   `POST /api/config`: Guardar/Actualizar ingresos y gastos fijos del mes.
        *   `GET /api/dashboard`: Devolver el presupuesto diario calculado, días restantes, y un historial rápido de hoy.
        *   `POST /api/gastos`: Registrar un gasto del día (actualiza el acumulado y recalcula el presupuesto futuro).
    *   Asegurar que las fechas se manejen correctamente según la zona horaria del usuario.

---

## 🔄 Protocolo de Comunicación e Integración
1. **Contratos de API Primero:** Antes de codificar, ambos agentes deben acordar los esquemas JSON de entrada y salida para los endpoints de FastAPI.
2. **Mocking:** El Frontend puede simular las respuestas del Backend para avanzar de forma independiente mientras el Backend diseña la persistencia de datos.
3. **CORS:** El Backend debe tener configurados los middlewares de CORS para permitir peticiones desde el entorno local del Frontend.
