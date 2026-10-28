"""Configuracion de la app compartido."""

from django.apps import AppConfig


class CompartidoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.compartido"
