import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.migraciones import aplicar_migraciones
from app.routers import auth, config, dashboard, gastos, ingresos, resumen


@asynccontextmanager
async def lifespan(_app: FastAPI):
    aplicar_migraciones()
    yield


app = FastAPI(title="Mango API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    # En producción: la URL del frontend (ej. https://mango.vercel.app), separadas por coma.
    allow_origins=[
        o.strip() for o in os.environ.get("MANGO_CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Las rutas de datos piden sesión a través de get_usuario_actual; /api/auth y /api/health no.
for router in (auth.router, config.router, dashboard.router, gastos.router, ingresos.router, resumen.router):
    app.include_router(router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
