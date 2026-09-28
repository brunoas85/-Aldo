from sqlalchemy import Column, Date, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, default="vos")
    dia_cobro = Column(Integer, nullable=False, default=1)

    configuraciones = relationship("ConfiguracionMensual", back_populates="usuario")
    transacciones = relationship("TransaccionDiaria", back_populates="usuario")


class ConfiguracionMensual(Base):
    __tablename__ = "configuraciones_mensuales"
    # Una sola config por ciclo: (anio, mes) es el mes en que arranca el ciclo.
    __table_args__ = (Index("uq_config_usuario_ciclo", "usuario_id", "anio", "mes", unique=True),)

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    anio = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    ingresos_mensuales = Column(Float, nullable=False)
    meta_ahorro = Column(Float, nullable=False, default=0)

    usuario = relationship("Usuario", back_populates="configuraciones")
    gastos_fijos_detalle = relationship(
        "GastoFijo", back_populates="configuracion", cascade="all, delete-orphan"
    )
    ingresos_variables = relationship(
        "IngresoVariable", back_populates="configuracion", cascade="all, delete-orphan"
    )


class GastoFijo(Base):
    __tablename__ = "gastos_fijos"

    id = Column(Integer, primary_key=True, index=True)
    configuracion_id = Column(Integer, ForeignKey("configuraciones_mensuales.id"), nullable=False)
    nombre = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    categoria = Column(String, nullable=True)

    configuracion = relationship("ConfiguracionMensual", back_populates="gastos_fijos_detalle")


class IngresoVariable(Base):
    __tablename__ = "ingresos_variables"

    id = Column(Integer, primary_key=True, index=True)
    configuracion_id = Column(Integer, ForeignKey("configuraciones_mensuales.id"), nullable=False)
    fecha = Column(Date, nullable=False, index=True)
    monto = Column(Float, nullable=False)
    descripcion = Column(String, nullable=True)

    configuracion = relationship("ConfiguracionMensual", back_populates="ingresos_variables")


class TransaccionDiaria(Base):
    __tablename__ = "transacciones_diarias"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha = Column(Date, nullable=False, index=True)
    monto = Column(Float, nullable=False)
    descripcion = Column(String, nullable=True)

    usuario = relationship("Usuario", back_populates="transacciones")
