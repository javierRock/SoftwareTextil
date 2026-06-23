"""Contratos de auditoria."""

from abc import ABC, abstractmethod

from software_textil.domain.auditoria.registro_auditoria import RegistroAuditoria


class RepositorioAuditoria(ABC):
    @abstractmethod
    def guardar(self, registro: RegistroAuditoria) -> None:
        raise NotImplementedError
