from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class GastoFijoIn(BaseModel):
    nombre: str = Field(min_length=1)
    monto: float = Field(gt=0)
    categoria: str | None = None


class GastoFijoOut(GastoFijoIn):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ConfigIn(BaseModel):
    ingresos_mensuales: float = Field(gt=0)
    dia_cobro: int = Field(default=1, ge=1, le=31)
    meta_ahorro: float = Field(default=0, ge=0)
    gastos_fijos: list[GastoFijoIn] = []


class GastoIn(BaseModel):
    monto: float = Field(gt=0)
    descripcion: str | None = None


class GastoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha: date
    monto: float
    descripcion: str | None


class IngresoIn(BaseModel):
    monto: float = Field(gt=0)
    descripcion: str | None = None


class IngresoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha: date
    monto: float
    descripcion: str | None


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
