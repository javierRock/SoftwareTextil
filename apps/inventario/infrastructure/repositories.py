"""Repositorios concretos con Django ORM para inventario."""

from apps.compartido.domain.enums import EstadoAlerta, TipoMovimiento
from apps.compartido.infrastructure.mapeo import uuid_valido
from apps.inventario.domain.repositorios import (
    RepositorioAlertaStock,
    RepositorioInventario,
    RepositorioMovimientoInventario,
)
from apps.inventario.domain.stock_prenda import (
    AlertaStock,
    MovimientoInventario,
    StockVariante,
)
from apps.inventario.infrastructure.models import (
    AlertaStockModel,
    MovimientoInventarioModel,
    StockVarianteModel,
)


def _stock_from_model(model: StockVarianteModel) -> StockVariante:
    return StockVariante(
        id=str(model.id),
        variante_id=str(model.variante_id),
        cantidad_actual=model.cantidad_actual,
        cantidad_reservada=model.cantidad_reservada,
        nivel_minimo=model.nivel_minimo,
        ubicacion=model.ubicacion,
        unidad=model.unidad,
        ultima_actualizacion=model.ultima_actualizacion,
    )


def _movimiento_from_model(model: MovimientoInventarioModel) -> MovimientoInventario:
    return MovimientoInventario(
        id=str(model.id),
        stock_id=str(model.stock_id),
        tipo=TipoMovimiento(model.tipo),
        cantidad=model.cantidad,
        motivo=model.motivo,
        registrado_por=str(model.registrado_por_id),
        fecha=model.fecha,
    )


def _alerta_from_model(model: AlertaStockModel) -> AlertaStock:
    return AlertaStock(
        id=str(model.id),
        stock_id=str(model.stock_id),
        nivel_actual=model.nivel_actual,
        nivel_minimo=model.nivel_minimo,
        estado=EstadoAlerta(model.estado),
        fecha=model.fecha,
    )


class DjangoRepositorioInventario(RepositorioInventario):
    def guardar(self, stock: StockVariante) -> None:
        model = StockVarianteModel.objects.filter(id=stock.id).first()
        if model is None:
            model = StockVarianteModel(id=stock.id)
        model.variante_id = stock.variante_id
        model.cantidad_actual = stock.cantidad_actual
        model.cantidad_reservada = stock.cantidad_reservada
        model.nivel_minimo = stock.nivel_minimo
        model.ubicacion = stock.ubicacion
        model.unidad = stock.unidad
        model.save()

    def buscar_por_variante(self, variante_id: str) -> StockVariante | None:
        if uuid_valido(variante_id) is None:
            return None
        model = StockVarianteModel.objects.filter(variante_id=variante_id).first()
        return _stock_from_model(model) if model else None

    def buscar_por_id(self, stock_id: str) -> StockVariante | None:
        if uuid_valido(stock_id) is None:
            return None
        model = StockVarianteModel.objects.filter(id=stock_id).first()
        return _stock_from_model(model) if model else None

    def listar(self) -> list[StockVariante]:
        return [_stock_from_model(m) for m in StockVarianteModel.objects.all()]


class DjangoRepositorioMovimiento(RepositorioMovimientoInventario):
    def guardar(self, movimiento: MovimientoInventario) -> None:
        # `create` y no `update_or_create`: el historico es de solo insercion,
        # tal como exige el invariante "un movimiento registrado no se modifica".
        MovimientoInventarioModel.objects.create(
            id=movimiento.id,
            stock_id=movimiento.stock_id,
            tipo=movimiento.tipo.value,
            cantidad=movimiento.cantidad,
            motivo=movimiento.motivo,
            registrado_por_id=movimiento.registrado_por,
        )

    def listar_por_stock(self, stock_id: str) -> list[MovimientoInventario]:
        if uuid_valido(stock_id) is None:
            return []
        qs = MovimientoInventarioModel.objects.filter(stock_id=stock_id).order_by(
            "-fecha"
        )
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
            },
        )

    def buscar_pendiente_por_stock(self, stock_id: str) -> AlertaStock | None:
        if uuid_valido(stock_id) is None:
            return None
        model = AlertaStockModel.objects.filter(
            stock_id=stock_id,
            estado=EstadoAlerta.PENDIENTE.value,
        ).first()
        return _alerta_from_model(model) if model else None
