"""Repositorios concretos con Django ORM para inventario."""

from django.db.models import F

from apps.catalogo.infrastructure.models import PrendaModel
from apps.compartido.domain.enums import EstadoAlerta, TipoMovimiento
from apps.inventario.domain.consultas import CategoriaStockAgrupada, PrendaStockAgrupada, PrendaStockBajoMinimo
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

    def listar_por_categoria(self, categoria_id: str | None = None) -> list[CategoriaStockAgrupada]:
        stocks_qs = StockPrendaModel.objects.all()
        if categoria_id:
            stocks_qs = stocks_qs.filter(
                prenda_id__in=PrendaModel.objects.filter(categoria_id=categoria_id).values_list("id", flat=True)
            )

        stocks = list(stocks_qs)
        if not stocks:
            return []

        prendas = PrendaModel.objects.select_related("categoria").filter(id__in=[stock.prenda_id for stock in stocks])
        if categoria_id:
            prendas = prendas.filter(categoria_id=categoria_id)

        prendas_por_id = {str(prenda.id): prenda for prenda in prendas}
        agrupados: dict[str, dict[str, object]] = {}

        for stock in stocks:
            prenda = prendas_por_id.get(stock.prenda_id)
            if prenda is None:
                continue

            categoria = prenda.categoria
            categoria_key = str(categoria.id)
            grupo = agrupados.setdefault(
                categoria_key,
                {
                    "categoria_id": categoria_key,
                    "categoria": categoria.nombre,
                    "cantidad_total": 0,
                    "prendas": [],
                },
            )
            grupo["cantidad_total"] = int(grupo["cantidad_total"]) + stock.cantidad_actual
            prendas_lista = grupo["prendas"]
            if not isinstance(prendas_lista, list):
                continue
            prendas_lista.append(
                PrendaStockAgrupada(
                    prenda_id=str(prenda.id),
                    nombre=prenda.nombre,
                    cantidad=stock.cantidad_actual,
                )
            )

        return [
            CategoriaStockAgrupada(
                categoria_id=str(datos["categoria_id"]),
                categoria=str(datos["categoria"]),
                cantidad_total=int(datos["cantidad_total"]),
                prendas=sorted(
                    datos["prendas"],
                    key=lambda item: item.nombre,
                ),
            )
            for datos in sorted(agrupados.values(), key=lambda item: str(item["categoria"]))
            if datos["prendas"]
        ]

    def listar_bajo_minimo(self) -> list[PrendaStockBajoMinimo]:
        stocks = list(StockPrendaModel.objects.filter(cantidad_actual__lt=F("nivel_minimo")))
        if not stocks:
            return []

        prendas = PrendaModel.objects.select_related("categoria").filter(id__in=[stock.prenda_id for stock in stocks])
        prendas_por_id = {str(prenda.id): prenda for prenda in prendas}

        alertas: list[PrendaStockBajoMinimo] = []
        for stock in stocks:
            prenda = prendas_por_id.get(stock.prenda_id)
            if prenda is None:
                continue

            categoria = prenda.categoria
            alertas.append(
                PrendaStockBajoMinimo(
                    categoria_id=str(categoria.id),
                    categoria=categoria.nombre,
                    prenda_id=str(prenda.id),
                    prenda=prenda.nombre,
                    cantidad_actual=stock.cantidad_actual,
                    nivel_minimo=stock.nivel_minimo,
                )
            )

        return sorted(alertas, key=lambda item: (item.categoria, item.prenda))


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
        qs = MovimientoInventarioModel.objects.select_related("stock").filter(stock_id=stock_id)
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
