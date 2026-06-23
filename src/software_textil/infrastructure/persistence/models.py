"""Modelos ORM que reflejan la estructura principal del dominio."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from software_textil.infrastructure.persistence.database import db


class CategoriaModel(db.Model):
    __tablename__ = "categorias"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, default="")


class TipoProductoModel(db.Model):
    __tablename__ = "tipos_producto"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    atributos_base: Mapped[str] = mapped_column(Text, default="{}")


class PrendaModel(db.Model):
    __tablename__ = "prendas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, default="")
    precio_monto: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    precio_moneda: Mapped[str] = mapped_column(String(3), default="PEN")
    categoria_id: Mapped[str] = mapped_column(String(36), ForeignKey("categorias.id"), nullable=False)
    tipo_producto_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("tipos_producto.id"))
    estado: Mapped[str] = mapped_column(String(30), nullable=False)
    registrado_por: Mapped[str | None] = mapped_column(String(36))
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    categoria = relationship("CategoriaModel")
    tipo_producto = relationship("TipoProductoModel")


class StockPrendaModel(db.Model):
    __tablename__ = "stocks_prenda"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    prenda_id: Mapped[str] = mapped_column(String(36), ForeignKey("prendas.id"), nullable=False, unique=True)
    cantidad_actual: Mapped[int] = mapped_column(nullable=False)
    nivel_minimo: Mapped[int] = mapped_column(nullable=False)
    ubicacion: Mapped[str] = mapped_column(String(120), default="almacen")
    unidad: Mapped[str] = mapped_column(String(30), default="unidad")
    ultima_actualizacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MovimientoInventarioModel(db.Model):
    __tablename__ = "movimientos_inventario"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    stock_id: Mapped[str] = mapped_column(String(36), ForeignKey("stocks_prenda.id"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    cantidad: Mapped[int] = mapped_column(nullable=False)
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    registrado_por: Mapped[str] = mapped_column(String(36), nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UsuarioModel(db.Model):
    __tablename__ = "usuarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    rol_id: Mapped[str] = mapped_column(String(36), ForeignKey("roles.id"), nullable=False)
    estado: Mapped[str] = mapped_column(String(30), nullable=False)
    creado_por: Mapped[str | None] = mapped_column(String(36))
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    rol = relationship("RolModel")


class RolModel(db.Model):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, default="")


class ReporteModel(db.Model):
    __tablename__ = "reportes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tipo: Mapped[str] = mapped_column(String(60), nullable=False)
    generado_por: Mapped[str] = mapped_column(String(36), nullable=False)
    formato: Mapped[str] = mapped_column(String(20), nullable=False)
    fecha_generacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RegistroAuditoriaModel(db.Model):
    __tablename__ = "registros_auditoria"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    entidad_id: Mapped[str] = mapped_column(String(36), nullable=False)
    entidad: Mapped[str] = mapped_column(String(80), nullable=False)
    accion: Mapped[str] = mapped_column(String(80), nullable=False)
    realizado_por: Mapped[str] = mapped_column(String(36), nullable=False)
    detalles: Mapped[str] = mapped_column(Text, default="")
    ip: Mapped[str] = mapped_column(String(60), default="")
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
