"""Repositorios concretos con Django ORM para inventario."""

from apps.compartido.domain.enums import EstadoAlerta, TipoMovimiento
from apps.inventario.domain.repositorios import (
    RepositorioAlertaStock,
    RepositorioInventario,
    RepositorioMovimientoInventario,
)
from apps.inventario.domain.stock_prenda import AlertaStock, MovimientoInventario, StockPrenda
from apps.inventario.infrastructure.models import (
    AlertaStockModel,
    MovimientoInventarioModel,
    StockPrendaModel,
)


def _stock_from_model(model: StockPrendaModel) -> StockPrenda:
    stock = StockPrenda(
        id=str(model.id),
        prenda_id=model.prenda_id,
        cantidad_actual=model.cantidad_actual,
        nivel_minimo=model.nivel_minimo,
        ubicacion=model.ubicacion,
        unidad=model.unidad,
    )
    stock.ultima_actualizacion = model.ultima_actualizacion
    return stock


def _movimiento_from_model(model: MovimientoInventarioModel) -> MovimientoInventario:
    return MovimientoInventario(
        id=str(model.id),
        stock_id=str(model.stock_id),
        tipo=TipoMovimiento(model.tipo),
        cantidad=model.cantidad,
        motivo=model.motivo,
        registrado_por=model.registrado_por,
        fecha=model.fecha,
    )


def _alerta_from_model(model: AlertaStockModel) -> AlertaStock:
    alerta = AlertaStock(
        id=str(model.id),
        stock_id=str(model.stock_id),
        nivel_actual=model.nivel_actual,
        nivel_minimo=model.nivel_minimo,
    )
    alerta.estado = EstadoAlerta(model.estado)
    alerta.fecha = model.fecha
    return alerta


class DjangoRepositorioInventario(RepositorioInventario):
    def guardar(self, stock: StockPrenda) -> None:
        model = StockPrendaModel.objects.filter(id=stock.id).first()
        if model is None:
            model = StockPrendaModel(id=stock.id)
        model.prenda_id = stock.prenda_id
        model.cantidad_actual = stock.cantidad_actual
        model.nivel_minimo = stock.nivel_minimo
        model.ubicacion = stock.ubicacion
        model.unidad = stock.unidad
        model.save()

    def buscar_por_prenda(self, prenda_id: str) -> StockPrenda | None:
        model = StockPrendaModel.objects.filter(prenda_id=prenda_id).first()
        return _stock_from_model(model) if model else None

    def buscar_por_prenda_bloqueado(self, prenda_id: str) -> StockPrenda | None:
        model = StockPrendaModel.objects.select_for_update().filter(prenda_id=prenda_id).first()
        return _stock_from_model(model) if model else None

    def buscar_por_id(self, stock_id: str) -> StockPrenda | None:
        model = StockPrendaModel.objects.filter(id=stock_id).first()
        return _stock_from_model(model) if model else None

    def listar(self) -> list[StockPrenda]:
        return [_stock_from_model(m) for m in StockPrendaModel.objects.all()]


class DjangoRepositorioMovimiento(RepositorioMovimientoInventario):
    def guardar(self, movimiento: MovimientoInventario) -> None:
        MovimientoInventarioModel.objects.update_or_create(
            id=movimiento.id,
            defaults={
                "stock_id": movimiento.stock_id,
                "tipo": movimiento.tipo.value,
                "cantidad": movimiento.cantidad,
                "motivo": movimiento.motivo,
                "registrado_por": movimiento.registrado_por,
                "fecha": movimiento.fecha,
            },
        )

    def listar_por_stock(self, stock_id: str) -> list[MovimientoInventario]:
        qs = MovimientoInventarioModel.objects.filter(stock_id=stock_id)
        return [_movimiento_from_model(m) for m in qs]


class DjangoRepositorioAlertaStock(RepositorioAlertaStock):
    def guardar(self, alerta: AlertaStock) -> None:
        AlertaStockModel.objects.update_or_create(
            id=alerta.id,
            defaults={
                "stock_id": alerta.stock_id,
                "nivel_actual": alerta.nivel_actual,
                "nivel_minimo": alerta.nivel_minimo,
                "estado": alerta.estado.value,
                "fecha": alerta.fecha,
            },
        )

    def buscar_pendiente_por_stock(self, stock_id: str) -> AlertaStock | None:
        model = AlertaStockModel.objects.filter(stock_id=stock_id, estado="pendiente").first()
        return _alerta_from_model(model) if model else None
