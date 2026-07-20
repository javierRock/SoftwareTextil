"""Politicas extensibles para validar metodos y referencias de pago."""

from abc import ABC, abstractmethod
from collections.abc import Iterable

from apps.compartido.domain.enums import MetodoPago
from apps.ventas.pagos.domain.excepciones import (
    MetodoPagoNoSoportado,
    ReferenciaPagoInvalida,
)


class PoliticaReferenciaPago(ABC):
    """Contrato de una estrategia de validacion de referencias."""

    @property
    @abstractmethod
    def metodos(self) -> frozenset[MetodoPago]:
        """Metodos a los que se aplica la politica."""
        raise NotImplementedError

    @abstractmethod
    def validar(self, metodo: MetodoPago, referencia: str) -> str:
        """Valida y normaliza una referencia."""
        raise NotImplementedError


class ReferenciaOpcional(PoliticaReferenciaPago):
    """Permite omitir la referencia para pagos en efectivo."""

    @property
    def metodos(self) -> frozenset[MetodoPago]:
        return frozenset({MetodoPago.EFECTIVO})

    def validar(self, metodo: MetodoPago, referencia: str) -> str:
        return referencia.strip()


class ReferenciaObligatoria(PoliticaReferenciaPago):
    """Exige una referencia para medios de pago trazables."""

    @property
    def metodos(self) -> frozenset[MetodoPago]:
        return frozenset(
            {
                MetodoPago.TARJETA,
                MetodoPago.TRANSFERENCIA,
                MetodoPago.YAPE,
            }
        )

    def validar(self, metodo: MetodoPago, referencia: str) -> str:
        referencia_normalizada = referencia.strip()
        if not referencia_normalizada:
            raise ReferenciaPagoInvalida(metodo)
        return referencia_normalizada


class ValidadorMetodoPago:
    """Selecciona la politica correspondiente a cada metodo de pago."""

    def __init__(
        self,
        politicas: Iterable[PoliticaReferenciaPago] | None = None,
    ) -> None:
        politicas_disponibles = (
            politicas
            if politicas is not None
            else (ReferenciaOpcional(), ReferenciaObligatoria())
        )
        self._politicas = {
            metodo: politica
            for politica in politicas_disponibles
            for metodo in politica.metodos
        }

    def validar(self, metodo: MetodoPago, referencia: str) -> str:
        if not isinstance(metodo, MetodoPago):
            raise MetodoPagoNoSoportado(metodo)
        politica = self._politicas.get(metodo)
        if politica is None:
            raise MetodoPagoNoSoportado(metodo)
        return politica.validar(metodo, referencia)
