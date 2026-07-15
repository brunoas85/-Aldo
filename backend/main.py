from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import config, dashboard, gastos, ingresos

Base.metadata.create_all(bind=engine)

app = FastAPI(title="$Aldo API")

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
