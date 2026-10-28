import base64

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APIClient

from apps.catalogo.infrastructure.models import (
    CategoriaModel,
    PrendaModel,
    VariantePrendaModel,
)
from apps.inventario.models import StockVarianteModel
from apps.usuarios.presentation.authentication import UsuarioAutenticado

pytestmark = pytest.mark.django_db


def _datos_prenda(categoria):
    return {
        "nombre": "Camisa segura",
        "precio_monto": "49.90",
        "precio_moneda": "PEN",
        "categoria_id": str(categoria.id),
    }


def test_prendas_publicas_ocultan_inactivas_y_mutaciones_exigen_admin(
    crear_usuario,
    cliente_admin,
) -> None:
    categoria = CategoriaModel.objects.create(nombre="Camisas seguras")
    activa = PrendaModel.objects.create(
        nombre="Visible",
        precio_monto="49.90",
        categoria=categoria,
    )
    inactiva = PrendaModel.objects.create(
        nombre="Oculta",
        precio_monto="49.90",
        categoria=categoria,
        estado="inactiva",
    )

    publico = APIClient()
    assert [item["id"] for item in publico.get("/api/prendas/").data] == [
        str(activa.id)
    ]
    assert publico.get(f"/api/prendas/{inactiva.id}/").status_code == 404
    assert publico.post("/api/prendas/", _datos_prenda(categoria)).status_code == 401

    usuario = crear_usuario(rol="Cliente")
    cliente = APIClient()
    cliente.force_authenticate(
        user=UsuarioAutenticado(
            id=str(usuario.id),
            nombre=usuario.nombre,
            username=usuario.username,
            email=usuario.email,
            rol=usuario.rol.nombre,
        )
    )
    assert cliente.post("/api/prendas/", _datos_prenda(categoria)).status_code == 403

    admin, _ = cliente_admin
    assert {item["id"] for item in admin.get("/api/prendas/").data} == {
        str(activa.id),
        str(inactiva.id),
    }


def test_registrado_por_sale_de_la_sesion_y_no_del_body(cliente_admin) -> None:
    categoria = CategoriaModel.objects.create(nombre="Autor seguro")
    admin, usuario = cliente_admin
    datos = _datos_prenda(categoria)
    datos["registrado_por"] = "00000000-0000-0000-0000-000000000000"

    respuesta = admin.post("/api/prendas/", datos, format="json")

    assert respuesta.status_code == 201
    assert respuesta.data["registrado_por"] == str(usuario.id)
    assert PrendaModel.objects.get(id=respuesta.data["id"]).registrado_por == usuario


def test_variantes_exponen_precio_heredado_stock_y_filtros(cliente_admin) -> None:
    categoria = CategoriaModel.objects.create(nombre="Variantes")
    prenda = PrendaModel.objects.create(
        nombre="Polo",
        precio_monto="39.90",
        precio_moneda="PEN",
        categoria=categoria,
    )
    activa = VariantePrendaModel.objects.create(
        prenda=prenda,
        sku="POLO-M-AZUL",
        talla="M",
        color="AZUL",
    )
    inactiva = VariantePrendaModel.objects.create(
        prenda=prenda,
        sku="POLO-L-AZUL",
        talla="L",
        color="AZUL",
        activa=False,
    )
    StockVarianteModel.objects.create(
        variante=activa,
        cantidad_actual=9,
        cantidad_reservada=2,
    )

    respuesta = APIClient().get(
        "/api/variantes/",
        {"prenda_id": str(prenda.id), "activa": "true"},
    )

    assert respuesta.status_code == 200
    assert respuesta.data == [
        {
            "id": str(activa.id),
            "prenda_id": str(prenda.id),
            "sku": "POLO-M-AZUL",
            "talla": "M",
            "color": "AZUL",
            "activa": True,
            "precio_monto": None,
            "precio_moneda": None,
            "precio_efectivo": "39.90",
            "moneda": "PEN",
            "stock_disponible": 7,
        }
    ]
    assert APIClient().get(f"/api/variantes/{inactiva.id}/").status_code == 404
    assert APIClient().get("/api/variantes/inexistente/").status_code == 404
    assert APIClient().get(
        "/api/variantes/",
        {"activa": "valor-invalido"},
    ).status_code == 400
    assert APIClient().post(
        "/api/variantes/",
        {
            "prenda_id": str(prenda.id),
            "sku": "NO-AUTORIZADA",
            "talla": "XS",
        },
        format="json",
    ).status_code == 401

    admin, _ = cliente_admin
    creada = admin.post(
        "/api/variantes/",
        {
            "prenda_id": str(prenda.id),
            "sku": "POLO-S-ROJO",
            "talla": "S",
            "color": "ROJO",
            "precio_monto": "44.90",
            "precio_moneda": "PEN",
        },
        format="json",
    )
    assert creada.status_code == 201
    assert creada.data["precio_efectivo"] == "44.90"
    assert admin.patch(
        f"/api/variantes/{creada.data['id']}/",
        {"activa": False},
        format="json",
    ).status_code == 200
    assert admin.delete(f"/api/variantes/{creada.data['id']}/").status_code == 204


@override_settings(MEDIA_URL="/media/")
def test_prenda_acepta_imagen_multipart_y_expone_url(cliente_admin, tmp_path) -> None:
    categoria = CategoriaModel.objects.create(nombre="Imagenes")
    admin, _ = cliente_admin
    gif = base64.b64decode(
        "R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="
    )
    imagen = SimpleUploadedFile("camisa.gif", gif, content_type="image/gif")

    with override_settings(MEDIA_ROOT=tmp_path):
        respuesta = admin.post(
            "/api/prendas/",
            {**_datos_prenda(categoria), "imagen": imagen},
            format="multipart",
        )

    assert respuesta.status_code == 201
    assert respuesta.data["imagen"].endswith("/media/catalogo/camisa.gif")
    assert PrendaModel.objects.get(id=respuesta.data["id"]).imagen.name.startswith(
        "catalogo/"
    )
