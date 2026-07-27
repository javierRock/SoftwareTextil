"""Repositorios concretos con Django ORM para inventario."""

from collections.abc import Iterable

from apps.compartido.domain.enums import EstadoAlerta, TipoMovimiento
from apps.compartido.infrastructure.mapeo import uuid_valido
from apps.inventario.domain.consultas import (
    CategoriaStockAgrupada,
    PrendaStockAgrupada,
    VarianteStockAgrupada,
)
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


def _agrupar_por_categoria(
    modelos: Iterable[StockVarianteModel],
) -> list[CategoriaStockAgrupada]:
    """Pliega las filas de stock en categoria -> prendas -> variantes.

    Recibe el resultado de una consulta ya resuelta con `select_related`, de
    modo que recorrerlo no dispara consultas adicionales.
    """
    categorias: dict[str, dict] = {}
    prendas: dict[tuple[str, str], dict] = {}

    for stock in modelos:
        variante = stock.variante
        prenda = variante.prenda
        categoria = prenda.categoria
        clave_categoria = str(categoria.id)
        clave_prenda = (clave_categoria, str(prenda.id))

        grupo = categorias.setdefault(
            clave_categoria,
            {"nombre": categoria.nombre, "cantidad_total": 0, "prendas": []},
        )
        grupo["cantidad_total"] += stock.cantidad_actual

        ficha = prendas.get(clave_prenda)
        if ficha is None:
            ficha = {"nombre": prenda.nombre, "cantidad": 0, "variantes": []}
            prendas[clave_prenda] = ficha
            grupo["prendas"].append((str(prenda.id), ficha))
        ficha["cantidad"] += stock.cantidad_actual
        ficha["variantes"].append(
            VarianteStockAgrupada(
                variante_id=str(variante.id),
                sku=variante.sku,
                talla=variante.talla,
                color=variante.color,
                cantidad=stock.cantidad_actual,
                cantidad_reservada=stock.cantidad_reservada,
            )
        )

    return [
        CategoriaStockAgrupada(
            categoria_id=categoria_id,
            categoria=datos["nombre"],
            cantidad_total=datos["cantidad_total"],
            prendas=[
                PrendaStockAgrupada(
                    prenda_id=prenda_id,
                    nombre=ficha["nombre"],
                    cantidad=ficha["cantidad"],
                    variantes=ficha["variantes"],
                )
                for prenda_id, ficha in datos["prendas"]
            ],
        )
        for categoria_id, datos in categorias.items()
    ]


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

    def buscar_por_variante_bloqueada(self, variante_id: str) -> StockVariante | None:
        """`select_for_update` serializa los movimientos sobre una variante.

        Sin el bloqueo, dos salidas simultaneas leen el mismo saldo y la
        segunda pisa a la primera: el stock termina mas alto de lo real.
        """
        if uuid_valido(variante_id) is None:
            return None
        model = (
            StockVarianteModel.objects.select_for_update()
            .filter(variante_id=variante_id)
            .first()
        )
        return _stock_from_model(model) if model else None

    def buscar_por_id(self, stock_id: str) -> StockVariante | None:
        if uuid_valido(stock_id) is None:
            return None
        model = StockVarianteModel.objects.filter(id=stock_id).first()
        return _stock_from_model(model) if model else None

    def listar(self) -> list[StockVariante]:
        return [_stock_from_model(m) for m in StockVarianteModel.objects.all()]

    def listar_por_categoria(
        self,
        categoria_id: str | None = None,
    ) -> list[CategoriaStockAgrupada]:
        """Resumen en tres niveles resuelto con una sola consulta.

        Las claves foraneas permiten recorrer stock -> variante -> prenda ->
        categoria con `select_related`, en vez de encadenar consultas por
        cada nivel.
        """
        if categoria_id is not None and uuid_valido(categoria_id) is None:
            return []
        modelos = StockVarianteModel.objects.select_related(
            "variante__prenda__categoria"
        ).order_by("variante__prenda__nombre", "variante__talla", "variante__color")
        if categoria_id:
            modelos = modelos.filter(variante__prenda__categoria_id=categoria_id)
        return _agrupar_por_categoria(modelos)


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
