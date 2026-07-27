"""Crea el primer administrador de SoftwareTextil."""

from getpass import getpass

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from apps.usuarios.application.services import ServicioGestionUsuarios
from apps.usuarios.domain.exceptions import UsuariosError
from apps.usuarios.infrastructure.repositories import (
    DjangoRepositorioRol,
    DjangoRepositorioUsuario,
)


class Command(BaseCommand):
    help = "Crea un usuario con rol Administrador"

    def add_arguments(self, parser):
        parser.add_argument("--nombre", required=True)
        parser.add_argument("--email", required=True)
        parser.add_argument("--username", required=True)
        parser.add_argument(
            "--password",
            help="Omitir para ingresar la contrasena de forma interactiva",
        )

    def handle(self, *_args, **options):
        password = options["password"] or getpass("Contrasena: ")
        confirmacion = (
            password if options["password"] else getpass("Confirma la contrasena: ")
        )
        if password != confirmacion:
            raise CommandError("Las contrasenas no coinciden")

        repo_rol = DjangoRepositorioRol()
        rol = repo_rol.buscar_por_nombre("Administrador")
        if rol is None:
            raise CommandError(
                "Ejecuta las migraciones antes de crear el administrador"
            )

        servicio = ServicioGestionUsuarios(DjangoRepositorioUsuario(), repo_rol)
        try:
            usuario = servicio.crear_usuario(
                nombre=options["nombre"],
                email=options["email"],
                username=options["username"],
                password=password,
                rol_id=rol.id,
            )
        except (ValidationError, UsuariosError) as exc:
            detalle = exc.messages if isinstance(exc, ValidationError) else str(exc)
            raise CommandError(detalle) from exc

        self.stdout.write(
            self.style.SUCCESS(f"Administrador '{usuario.username}' creado")
        )
