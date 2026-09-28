from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.migraciones import aplicar_migraciones
from app.routers import config, dashboard, gastos, ingresos


@asynccontextmanager
async def lifespan(_app: FastAPI):
    aplicar_migraciones()
    yield


app = FastAPI(title="$Aldo API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(config.router)
app.include_router(dashboard.router)
app.include_router(gastos.router)
app.include_router(ingresos.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
