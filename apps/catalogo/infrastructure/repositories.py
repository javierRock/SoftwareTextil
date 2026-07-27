"""Repositorios concretos con Django ORM para catalogo."""

from django.db.models import Q

from apps.catalogo.domain.prenda import (
    Categoria,
    Prenda,
    TipoProducto,
    VariantePrenda,
)
from apps.catalogo.domain.repositorios import (
    RepositorioCatalogo,
    RepositorioPrenda,
    RepositorioVariante,
)
from apps.catalogo.infrastructure.models import (
    CategoriaModel,
    PrendaModel,
    TipoProductoModel,
    VariantePrendaModel,
)
from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPrenda
from apps.compartido.infrastructure.mapeo import (
    a_dinero,
    a_texto,
    de_dinero,
    uuid_valido,
)


def _categoria_from_model(model: CategoriaModel) -> Categoria:
    return Categoria(
        id=str(model.id),
        nombre=model.nombre,
        descripcion=model.descripcion,
    )


def _tipo_from_model(model: TipoProductoModel) -> TipoProducto:
    return TipoProducto(
        id=str(model.id),
        nombre=model.nombre,
        atributos_base=model.atributos_base or {},
        activo=model.activo,
    )


def _variante_from_model(model: VariantePrendaModel) -> VariantePrenda:
    precio = None
    if model.precio_monto is not None and model.precio_moneda:
        precio = a_dinero(model.precio_monto, model.precio_moneda)
    return VariantePrenda(
        id=str(model.id),
        prenda_id=str(model.prenda_id),
        talla=model.talla,
        color=model.color,
        sku=model.sku,
        precio=precio,
        activa=model.activa,
    )


def _prenda_from_model(model: PrendaModel) -> Prenda:
    return Prenda(
        id=str(model.id),
        nombre=model.nombre,
        descripcion=model.descripcion,
        precio=a_dinero(model.precio_monto, model.precio_moneda),
        categoria_id=str(model.categoria_id),
        tipo_producto_id=a_texto(model.tipo_producto_id),
        variantes=[
            _variante_from_model(variante) for variante in model.variantes.all()
        ],
        estado=EstadoPrenda(model.estado),
        registrado_por=a_texto(model.registrado_por_id),
        fecha_registro=model.fecha_registro,
    )


class DjangoRepositorioPrenda(RepositorioPrenda):
    def guardar(self, prenda: Prenda) -> None:
        model = PrendaModel.objects.filter(id=prenda.id).first()
        if model is None:
            model = PrendaModel(id=prenda.id)
        model.nombre = prenda.nombre
        model.descripcion = prenda.descripcion
        model.precio_monto, model.precio_moneda = de_dinero(prenda.precio)
        model.categoria_id = prenda.categoria_id
        model.tipo_producto_id = prenda.tipo_producto_id
        model.estado = prenda.estado.value
        model.registrado_por_id = prenda.registrado_por
        model.save()
        self._sincronizar_variantes(model, prenda.variantes)

    def buscar_por_id(self, prenda_id: str) -> Prenda | None:
        if uuid_valido(prenda_id) is None:
            return None
        model = self._consulta().filter(id=prenda_id).first()
        return _prenda_from_model(model) if model else None

    def listar(self) -> list[Prenda]:
        return [_prenda_from_model(model) for model in self._consulta()]

    def listar_visibles(self) -> list[Prenda]:
        modelos = self._consulta().filter(estado=EstadoPrenda.ACTIVA.value)
        return [_prenda_from_model(modelo) for modelo in modelos]

    def buscar(
        self,
        texto: str | None,
        categoria_id: str | None,
        tipo_producto_id: str | None,
        estado: EstadoPrenda,
    ) -> list[Prenda]:
        modelos = self._consulta().filter(estado=estado.value)
        if texto:
            modelos = modelos.filter(
                Q(nombre__icontains=texto) | Q(descripcion__icontains=texto)
            )
        if categoria_id:
            modelos = modelos.filter(categoria_id=categoria_id)
        if tipo_producto_id:
            modelos = modelos.filter(tipo_producto_id=tipo_producto_id)
        return [_prenda_from_model(modelo) for modelo in modelos]

    @staticmethod
    def _consulta():
        """Trae en dos consultas la prenda y todas sus variantes."""
        return PrendaModel.objects.prefetch_related("variantes")

    @staticmethod
    def _sincronizar_variantes(
        model: PrendaModel,
        variantes: list[VariantePrenda],
    ) -> None:
        """Refleja en la tabla las variantes que hoy tiene el agregado."""
        identificadores = [variante.id for variante in variantes]
        VariantePrendaModel.objects.filter(prenda=model).exclude(
            id__in=identificadores
        ).delete()
        for variante in variantes:
            precio_monto, precio_moneda = (
                de_dinero(variante.precio) if variante.precio else (None, None)
            )
            VariantePrendaModel.objects.update_or_create(
                id=variante.id,
                defaults={
                    "prenda": model,
                    "sku": variante.sku,
                    "talla": variante.talla,
                    "color": variante.color,
                    "precio_monto": precio_monto,
                    "precio_moneda": precio_moneda,
                    "activa": variante.activa,
                },
            )


class DjangoRepositorioVariante(RepositorioVariante):
    def buscar_por_id(self, variante_id: str) -> VariantePrenda | None:
        if uuid_valido(variante_id) is None:
            return None
        model = VariantePrendaModel.objects.filter(id=variante_id).first()
        return _variante_from_model(model) if model else None

    def buscar_por_sku(self, sku: str) -> VariantePrenda | None:
        model = VariantePrendaModel.objects.filter(sku__iexact=sku).first()
        return _variante_from_model(model) if model else None

    def listar_por_prenda(self, prenda_id: str) -> list[VariantePrenda]:
        if uuid_valido(prenda_id) is None:
            return []
        modelos = VariantePrendaModel.objects.filter(prenda_id=prenda_id).order_by(
            "talla",
            "color",
        )
        return [_variante_from_model(modelo) for modelo in modelos]

    def precio_efectivo(self, variante_id: str) -> Dinero | None:
        """Precio de venta de la variante, con el de la prenda como respaldo."""
        if uuid_valido(variante_id) is None:
            return None
        model = (
            VariantePrendaModel.objects.select_related("prenda")
            .filter(id=variante_id)
            .first()
        )
        if model is None:
            return None
        if model.precio_monto is not None and model.precio_moneda:
            return a_dinero(model.precio_monto, model.precio_moneda)
        return a_dinero(model.prenda.precio_monto, model.prenda.precio_moneda)


class DjangoRepositorioCatalogo(RepositorioCatalogo):
    def guardar_categoria(self, categoria: Categoria) -> None:
        CategoriaModel.objects.update_or_create(
            id=categoria.id,
            defaults={
                "nombre": categoria.nombre,
                "descripcion": categoria.descripcion,
            },
        )

    def guardar_tipo_producto(self, tipo_producto: TipoProducto) -> None:
        TipoProductoModel.objects.update_or_create(
            id=tipo_producto.id,
            defaults={
                "nombre": tipo_producto.nombre,
                "atributos_base": tipo_producto.atributos_base,
                "activo": tipo_producto.activo,
            },
        )

    def listar_categorias(self) -> list[Categoria]:
        return [_categoria_from_model(m) for m in CategoriaModel.objects.all()]

    def listar_tipos(self) -> list[TipoProducto]:
        return [_tipo_from_model(m) for m in TipoProductoModel.objects.all()]

    def buscar_tipo(self, tipo_producto_id: str) -> TipoProducto | None:
        if uuid_valido(tipo_producto_id) is None:
            return None
        model = TipoProductoModel.objects.filter(id=tipo_producto_id).first()
        return _tipo_from_model(model) if model else None

    def buscar_categoria(self, categoria_id: str) -> Categoria | None:
        if uuid_valido(categoria_id) is None:
            return None
        model = CategoriaModel.objects.filter(id=categoria_id).first()
        return _categoria_from_model(model) if model else None
