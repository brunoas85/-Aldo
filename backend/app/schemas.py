from datetime import date

from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_validator

# Validación mínima a propósito: algo@algo.algo. Se guarda en minúsculas.
Email = Annotated[
    str,
    Field(max_length=254, pattern=r"^\s*[^@\s]+@[^@\s]+\.[^@\s]+\s*$"),
    AfterValidator(lambda v: v.strip().lower()),
]


class LoginIn(BaseModel):
    email: Email
    password: str = Field(min_length=1, max_length=200)


class RegistroIn(BaseModel):
    nombre: str = Field(max_length=50, pattern=r"\S")
    email: Email
    password: str = Field(min_length=8, max_length=200)

    @field_validator("nombre")
    @classmethod
    def _sin_espacios_de_mas(cls, v: str) -> str:
        return v.strip()


class SesionOut(BaseModel):
    token: str
    nombre: str
    email: str


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


CATEGORIAS_GASTO = ("Súper", "Panadería", "Comida afuera", "Transporte", "Salidas", "Otros")
CategoriaGasto = Literal[CATEGORIAS_GASTO]


class GastoIn(BaseModel):
    monto: float = Field(gt=0)
    descripcion: str | None = None
    # En un PUT, si no viene, se deja la que tenía.
    categoria: CategoriaGasto | None = None


class GastoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha: date
    monto: float
    descripcion: str | None
    categoria: str | None


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


class CategoriaResumenOut(BaseModel):
    categoria: str
    total: float
    cantidad: int
    total_ciclo_anterior: float


class AnalisisOut(BaseModel):
    resumen: str
    consejos: list[str]


class ResumenOut(BaseModel):
    inicio_ciclo: date
    fin_ciclo: date
    dias_transcurridos: int
    dias_totales_ciclo: int
    total_gastado: float
    total_ciclo_anterior: float
    categorias: list[CategoriaResumenOut]
    # None si todavía no hay suficientes gastos; ahí se explica en `aviso`.
    analisis: AnalisisOut | None
    aviso: str | None
