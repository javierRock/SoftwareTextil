"""Reexportacion explicita de los modelos ORM de despachos."""

from apps.ventas.models import DespachoModel, GuiaRemisionModel

__all__ = ["DespachoModel", "GuiaRemisionModel"]
