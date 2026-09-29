import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.deps import verificar_clave
from app.migraciones import aplicar_migraciones
from app.routers import config, dashboard, gastos, ingresos


@asynccontextmanager
async def lifespan(_app: FastAPI):
    aplicar_migraciones()
    yield


app = FastAPI(title="$Aldo API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    # En producción: la URL del frontend (ej. https://aldo.vercel.app), separadas por coma.
    allow_origins=[
        o.strip() for o in os.environ.get("ALDO_CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# /api/health queda afuera a propósito: Render lo usa para saber si el server está vivo.
for router in (config.router, dashboard.router, gastos.router, ingresos.router):
    app.include_router(router, dependencies=[Depends(verificar_clave)])


@app.get("/api/health")
def health():
    return {"status": "ok"}
