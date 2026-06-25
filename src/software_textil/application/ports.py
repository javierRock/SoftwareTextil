"""Puertos tecnicos usados por la capa de aplicacion."""

from typing import Protocol

from software_textil.domain.facturacion.comprobante import ComprobanteElectronico


class PasswordHasher(Protocol):
    nombre: str

    def hash(self, password: str) -> str:
        raise NotImplementedError

    def verify(self, password: str, password_hash: str, salt: str = "") -> bool:
        raise NotImplementedError


class SunatPort(Protocol):
    def enviar(self, comprobante: ComprobanteElectronico) -> dict[str, str]:
        raise NotImplementedError
