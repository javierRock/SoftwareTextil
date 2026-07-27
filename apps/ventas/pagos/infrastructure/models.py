"""Reexportacion explicita del modelo ORM de pagos."""

from apps.ventas.models import PagoModel

__all__ = ["PagoModel"]
