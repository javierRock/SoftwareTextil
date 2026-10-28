"""Pruebas de API para reportes de inventario."""

from io import BytesIO
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import pytest

from apps.inventario.infrastructure.models import StockVarianteModel


def _leer_filas_xlsx(contenido: bytes, hoja: str) -> list[list[str]]:
    ruta = "xl/worksheets/sheet1.xml" if hoja == "Resumen" else "xl/worksheets/sheet2.xml"
    namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

    with ZipFile(BytesIO(contenido)) as archivo:
        xml = archivo.read(ruta)

    raiz = ET.fromstring(xml)
    filas: list[list[str]] = []
    for fila in raiz.findall("main:sheetData/main:row", namespace):
        celdas: list[str] = []
        for celda in fila.findall("main:c", namespace):
            tipo = celda.attrib.get("t")
            if tipo == "inlineStr":
                valor = celda.findtext("main:is/main:t", default="", namespaces=namespace)
            else:
                valor = celda.findtext("main:v", default="", namespaces=namespace)
            celdas.append(valor)
        filas.append(celdas)
    return filas


@pytest.mark.django_db
def test_reporte_xlsx_es_legible_y_no_toca_la_base_de_datos(client, stock, prenda) -> None:
    stock_count_before = StockVarianteModel.objects.count()

    respuesta = client.get("/api/stock/reporte/?formato=xlsx")

    assert respuesta.status_code == 200
    assert respuesta["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert respuesta["Content-Disposition"].startswith("attachment; filename=\"reporte-inventario")
    assert StockVarianteModel.objects.count() == stock_count_before

    resumen = _leer_filas_xlsx(respuesta.content, "Resumen")
    assert resumen[0] == ["Categoría", "Prenda", "Cantidad", "Precio unitario", "Moneda", "Valorización"]
    assert resumen[1][0] == "Camisetas"
    assert resumen[1][1].startswith("Prenda ")


@pytest.mark.django_db
def test_reporte_pdf_es_legible_y_respeta_el_filtro(
    client,
    stock,
    crear_categoria,
    crear_prenda,
    crear_variante,
) -> None:
    otra_categoria = crear_categoria(nombre="Jeans")
    jean = crear_prenda()
    jean.categoria = otra_categoria
    jean.nombre = "Jean de prueba"
    jean.save()
    StockVarianteModel.objects.create(
        variante=crear_variante(prenda=jean, talla="32"),
        cantidad_actual=5,
        nivel_minimo=3,
    )

    respuesta = client.get(
        f"/api/stock/reporte/?formato=pdf&categoria_id={otra_categoria.id}"
    )

    assert respuesta.status_code == 200
    assert respuesta["Content-Type"] == "application/pdf"
    assert respuesta.content.startswith(b"%PDF-1.4")
    assert b"Jeans" in respuesta.content
    assert b"Camisetas" not in respuesta.content


@pytest.mark.django_db
def test_reporte_vacio_genera_archivos_validos(client) -> None:
    respuesta = client.get("/api/stock/reporte/?formato=xlsx")

    assert respuesta.status_code == 200
    resumen = _leer_filas_xlsx(respuesta.content, "Resumen")
    assert resumen == [["Categoría", "Prenda", "Cantidad", "Precio unitario", "Moneda", "Valorización"]]


@pytest.mark.django_db
def test_reporte_rechaza_solicitudes_sin_autenticacion() -> None:
    from rest_framework.test import APIClient

    respuesta = APIClient().get("/api/stock/reporte/?formato=xlsx")

    assert respuesta.status_code in {401, 403}
