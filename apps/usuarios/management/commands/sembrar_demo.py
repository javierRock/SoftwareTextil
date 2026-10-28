"""Carga un conjunto idempotente de datos para probar la aplicacion completa."""

from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.catalogo.models import (
    CategoriaModel,
    PrendaModel,
    TipoProductoModel,
    VariantePrendaModel,
)
from apps.inventario.models import StockVarianteModel
from apps.usuarios.models import RolModel, UsuarioModel

ROLES_REQUERIDOS = 3


class Command(BaseCommand):
    help = "Crea usuarios y catalogo de demostracion sin duplicar registros"

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            default="Zuren2026!",
            help="Contrasena de los usuarios demo (solo desarrollo)",
        )

    @transaction.atomic
    def handle(self, *_args, **options):
        roles = {
            rol.nombre: rol
            for rol in RolModel.objects.filter(
                nombre__in=[
                    "Administrador",
                    "Cliente",
                    "Encargado de inventario",
                ]
            )
        }
        if len(roles) != ROLES_REQUERIDOS:
            raise CommandError("Ejecuta las migraciones antes de sembrar datos")

        password_hash = make_password(options["password"])
        usuarios = [
            ("admin", "Administradora Zuren", "admin@zuren.pe", "Administrador"),
            (
                "inventario",
                "Encargado de Almacen",
                "inventario@zuren.pe",
                "Encargado de inventario",
            ),
            ("cliente", "Cliente Zuren", "cliente@zuren.pe", "Cliente"),
        ]
        for username, nombre, email, rol in usuarios:
            usuario, creado = UsuarioModel.objects.get_or_create(
                username=username,
                defaults={
                    "nombre": nombre,
                    "email": email,
                    "rol": roles[rol],
                    "password_hash": password_hash,
                },
            )
            if creado:
                continue
            usuario.nombre = nombre
            usuario.email = email
            usuario.rol = roles[rol]
            usuario.estado = "activo"
            usuario.password_hash = password_hash
            usuario.save(
                update_fields=["nombre", "email", "rol", "estado", "password_hash"]
            )

        categoria, _ = CategoriaModel.objects.update_or_create(
            nombre="Esenciales",
            defaults={
                "descripcion": "Prendas versatiles de uso diario",
                "activa": True,
            },
        )
        abrigos, _ = CategoriaModel.objects.update_or_create(
            nombre="Abrigos",
            defaults={
                "descripcion": "Capas exteriores y tejido abrigador",
                "activa": True,
            },
        )
        tipo, _ = TipoProductoModel.objects.update_or_create(
            nombre="Prenda superior",
            defaults={"atributos_base": {"material": "algodon"}, "activo": True},
        )
        administrador = UsuarioModel.objects.get(username="admin")

        productos = [
            (
                categoria,
                "Camisa Lino Norte",
                "Lino lavado de corte relajado.",
                "149.90",
            ),
            (
                categoria,
                "Polo Algodon Pima",
                "Jersey suave para todos los dias.",
                "89.90",
            ),
            (
                abrigos,
                "Sobrecamisa Andina",
                "Tejido estructurado para media estacion.",
                "239.90",
            ),
        ]
        stocks = [
            ("S", "Crudo", 18, 5),
            ("M", "Bosque", 8, 5),
            ("L", "Arcilla", 3, 5),
        ]
        for indice, datos_producto in enumerate(productos):
            categoria_producto, nombre, descripcion, precio = datos_producto
            prenda, _ = PrendaModel.objects.update_or_create(
                nombre=nombre,
                defaults={
                    "descripcion": descripcion,
                    "precio_monto": Decimal(precio),
                    "precio_moneda": "PEN",
                    "categoria": categoria_producto,
                    "tipo_producto": tipo,
                    "estado": "activa",
                    "registrado_por": administrador,
                },
            )
            for talla, color, cantidad, minimo in stocks:
                sku = f"ZR-{indice + 1:02d}-{talla}"
                variante, _ = VariantePrendaModel.objects.update_or_create(
                    sku=sku,
                    defaults={
                        "prenda": prenda,
                        "talla": talla,
                        "color": color,
                        "activa": True,
                        "precio_monto": None,
                        "precio_moneda": None,
                    },
                )
                StockVarianteModel.objects.update_or_create(
                    variante=variante,
                    defaults={
                        "cantidad_actual": cantidad,
                        "cantidad_reservada": 0,
                        "nivel_minimo": minimo,
                        "ubicacion": f"A-{indice + 1}",
                        "unidad": "unidad",
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Datos demo listos: admin, inventario y cliente comparten "
                "la contrasena indicada"
            )
        )
