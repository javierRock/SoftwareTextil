"""Repositorio SQLAlchemy para inventario."""

from software_textil.domain.compartido.enums import TipoMovimiento
from software_textil.domain.inventario.repositorios import RepositorioInventario, RepositorioMovimientoInventario
from software_textil.domain.inventario.stock_prenda import MovimientoInventario, StockPrenda
from software_textil.infrastructure.persistence.database import db
from software_textil.infrastructure.persistence.models import MovimientoInventarioModel, StockPrendaModel


class SQLAlchemyInventarioRepository(RepositorioInventario):
    def guardar(self, stock: StockPrenda) -> None:
        model = db.session.get(StockPrendaModel, stock.id) or StockPrendaModel(id=stock.id)
        model.prenda_id = stock.prenda_id
        model.cantidad_actual = stock.cantidad_actual
        model.nivel_minimo = stock.nivel_minimo
        model.ubicacion = stock.ubicacion
        model.unidad = stock.unidad
        model.ultima_actualizacion = stock.ultima_actualizacion
        db.session.add(model)
        db.session.commit()

    def buscar_por_prenda(self, prenda_id: str) -> StockPrenda | None:
        model = StockPrendaModel.query.filter_by(prenda_id=prenda_id).first()
        return _stock_from_model(model) if model else None

    def buscar_por_id(self, stock_id: str) -> StockPrenda | None:
        model = db.session.get(StockPrendaModel, stock_id)
        return _stock_from_model(model) if model else None


class SQLAlchemyMovimientoInventarioRepository(RepositorioMovimientoInventario):
    def guardar(self, movimiento: MovimientoInventario) -> None:
        db.session.merge(
            MovimientoInventarioModel(
                id=movimiento.id,
                stock_id=movimiento.stock_id,
                tipo=movimiento.tipo.value,
                cantidad=movimiento.cantidad,
                motivo=movimiento.motivo,
                registrado_por=movimiento.registrado_por,
                fecha=movimiento.fecha,
            )
        )
        db.session.commit()

    def listar_por_stock(self, stock_id: str) -> list[MovimientoInventario]:
        models = MovimientoInventarioModel.query.filter_by(stock_id=stock_id).all()
        return [
            MovimientoInventario(
                id=model.id,
                stock_id=model.stock_id,
                tipo=TipoMovimiento(model.tipo),
                cantidad=model.cantidad,
                motivo=model.motivo,
                registrado_por=model.registrado_por,
                fecha=model.fecha,
            )
            for model in models
        ]


def _stock_from_model(model: StockPrendaModel) -> StockPrenda:
    return StockPrenda(
        id=model.id,
        prenda_id=model.prenda_id,
        cantidad_actual=model.cantidad_actual,
        nivel_minimo=model.nivel_minimo,
        ubicacion=model.ubicacion,
        unidad=model.unidad,
        ultima_actualizacion=model.ultima_actualizacion,
    )
