from datetime import date

from pydantic import BaseModel


class GastoFijoIn(BaseModel):
    nombre: str
    monto: float
    categoria: str | None = None


class GastoFijoOut(GastoFijoIn):
    id: int

    class Config:
        from_attributes = True


class ConfigIn(BaseModel):
    ingresos_mensuales: float
    dia_cobro: int = 1
    meta_ahorro: float = 0
    gastos_fijos: list[GastoFijoIn] = []


class GastoIn(BaseModel):
    monto: float
    descripcion: str | None = None


class GastoOut(BaseModel):
    id: int
    fecha: date
    monto: float
    descripcion: str | None

    class Config:
        from_attributes = True


class IngresoIn(BaseModel):
    monto: float
    descripcion: str | None = None


class IngresoOut(BaseModel):
    id: int
    fecha: date
    monto: float
    descripcion: str | None

    class Config:
        from_attributes = True


class DashboardOut(BaseModel):
    nombre: str
    presupuesto_diario: float
    dias_restantes: int
    dias_totales_ciclo: int
    inicio_ciclo: date
    fin_ciclo: date
    estado: str
    gastado_hoy: float
    dia_cobro: int
    ingresos_mensuales: float
    meta_ahorro: float
    gastos_fijos: list[GastoFijoOut]
    ingresos_variables_ciclo: float
    ingresos_variables: list[IngresoOut]
    gastos_ciclo: list[GastoOut]
    saldo_disponible_ciclo: float
    sugerencias: list[str]
