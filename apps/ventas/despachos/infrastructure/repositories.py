"""Adaptador de persistencia de despachos basado en Django ORM."""

from django.db import transaction

from apps.compartido.domain.enums import EstadoDespacho
from apps.compartido.infrastructure.mapeo import a_texto, uuid_valido
from apps.ventas.despachos.domain.despacho import Despacho, GuiaRemision
from apps.ventas.despachos.domain.repositorios import RepositorioDespacho
from apps.ventas.despachos.infrastructure.models import (
    DespachoModel,
    GuiaRemisionModel,
)


def _guia_from_model(model: DespachoModel) -> GuiaRemision | None:
    guia = getattr(model, "guia", None)
    if guia is None:
        return None
    return GuiaRemision(
        serie=guia.serie,
        numero=guia.numero,
        transportista=guia.transportista,
        fecha_emision=guia.fecha_emision,
    )


def _despacho_from_model(model: DespachoModel) -> Despacho:
    return Despacho(
        id=str(model.id),
        pedido_id=str(model.pedido_id),
        direccion_entrega=model.direccion_entrega,
        estado=EstadoDespacho(model.estado),
        responsable_id=a_texto(model.responsable_id),
        guia=_guia_from_model(model),
        fecha_preparacion=model.fecha_preparacion,
        fecha_confirmacion=model.fecha_confirmacion,
    )


class DjangoRepositorioDespacho(RepositorioDespacho):
    @transaction.atomic
    def guardar(self, despacho: Despacho) -> None:
        model = DespachoModel.objects.filter(id=despacho.id).first()
        if model is None:
            model = DespachoModel(id=despacho.id)
        model.pedido_id = despacho.pedido_id
        model.direccion_entrega = despacho.direccion_entrega
        model.estado = despacho.estado.value
        model.responsable_id = despacho.responsable_id
        model.fecha_preparacion = despacho.fecha_preparacion
        model.fecha_confirmacion = despacho.fecha_confirmacion
        model.save()
        self._sincronizar_guia(model, despacho.guia)

    def buscar_por_id(self, despacho_id: str) -> Despacho | None:
        if uuid_valido(despacho_id) is None:
            return None
        model = self._consulta().filter(id=despacho_id).first()
        return _despacho_from_model(model) if model else None

    def buscar_por_id_para_actualizar(
        self, despacho_id: str
    ) -> Despacho | None:
        if uuid_valido(despacho_id) is None:
            return None
        model = (
            DespachoModel.objects.select_for_update()
            .filter(id=despacho_id)
            .first()
        )
        return _despacho_from_model(model) if model else None

    def buscar_por_pedido(self, pedido_id: str) -> Despacho | None:
        if uuid_valido(pedido_id) is None:
            return None
        model = self._consulta().filter(pedido_id=pedido_id).first()
        return _despacho_from_model(model) if model else None

    def listar(self) -> list[Despacho]:
        return [_despacho_from_model(model) for model in self._consulta()]

    @staticmethod
    def _consulta():
        return DespachoModel.objects.select_related("guia")

    @staticmethod
    def _sincronizar_guia(model: DespachoModel, guia: GuiaRemision | None) -> None:
        """La guia es un objeto de valor: se reemplaza entera, no se edita."""
        if guia is None:
            GuiaRemisionModel.objects.filter(despacho=model).delete()
            return
        GuiaRemisionModel.objects.update_or_create(
            despacho=model,
            defaults={
                "serie": guia.serie,
                "numero": guia.numero,
                "transportista": guia.transportista,
            },
        )
