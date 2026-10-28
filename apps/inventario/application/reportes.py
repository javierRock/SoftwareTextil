"""Servicio de reportes del inventario actual."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from io import BytesIO
from xml.sax.saxutils import escape as xml_escape
from zipfile import ZIP_DEFLATED, ZipFile

from django.utils import timezone

from apps.catalogo.domain.repositorios import RepositorioPrenda
from apps.inventario.application.services import ServicioInventario
from apps.inventario.domain.consultas import (
    ReporteInventario,
    ReporteInventarioCategoria,
    ReporteInventarioPrenda,
)


@dataclass(frozen=True)
class ArchivoReporte:
    contenido: bytes
    nombre_archivo: str
    content_type: str


class ServicioReporteInventario:
    def __init__(self, servicio_inventario: ServicioInventario, repo_prenda: RepositorioPrenda) -> None:
        self.servicio_inventario = servicio_inventario
        self.repo_prenda = repo_prenda

    def construir_reporte(self, categoria_id: str | None = None) -> ReporteInventario:
        resumen = self.servicio_inventario.listar_stock_por_categoria(categoria_id)
        prendas_catalogo = {str(prenda.id): prenda for prenda in self.repo_prenda.listar()}

        categorias: list[ReporteInventarioCategoria] = []
        for grupo in resumen:
            prendas: list[ReporteInventarioPrenda] = []
            for item in grupo.prendas:
                prenda = prendas_catalogo.get(item.prenda_id)
                if prenda is None:
                    continue

                precio = Decimal(prenda.precio.monto).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                prendas.append(
                    ReporteInventarioPrenda(
                        categoria_id=grupo.categoria_id,
                        categoria=grupo.categoria,
                        prenda_id=item.prenda_id,
                        prenda=item.nombre,
                        cantidad_actual=item.cantidad,
                        precio_unitario=precio,
                        moneda=prenda.precio.moneda,
                    )
                )

            categorias.append(
                ReporteInventarioCategoria(
                    categoria_id=grupo.categoria_id,
                    categoria=grupo.categoria,
                    prendas=prendas,
                )
            )

        return ReporteInventario(categorias=categorias)

    def generar_archivo(self, formato: str, categoria_id: str | None = None) -> ArchivoReporte:
        reporte = self.construir_reporte(categoria_id)
        formato_normalizado = formato.lower()
        if formato_normalizado == "pdf":
            return ArchivoReporte(
                contenido=self._generar_pdf(reporte),
                nombre_archivo=self._nombre_archivo("pdf", categoria_id),
                content_type="application/pdf",
            )
        if formato_normalizado == "xlsx":
            return ArchivoReporte(
                contenido=self._generar_xlsx(reporte),
                nombre_archivo=self._nombre_archivo("xlsx", categoria_id),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        raise ValueError("El formato de reporte debe ser pdf o xlsx")

    def _nombre_archivo(self, extension: str, categoria_id: str | None) -> str:
        ahora = timezone.localtime(timezone.now()).strftime("%Y%m%d-%H%M")
        sufijo = f"-{categoria_id}" if categoria_id else ""
        return f"reporte-inventario{sufijo}-{ahora}.{extension}"

    def _generar_xlsx(self, reporte: ReporteInventario) -> bytes:
        buffer = BytesIO()
        with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
            archive.writestr("[Content_Types].xml", self._xlsx_content_types())
            archive.writestr("_rels/.rels", self._xlsx_root_rels())
            archive.writestr("xl/workbook.xml", self._xlsx_workbook_xml())
            archive.writestr("xl/_rels/workbook.xml.rels", self._xlsx_workbook_rels())
            archive.writestr("xl/styles.xml", self._xlsx_styles_xml())
            archive.writestr("xl/worksheets/sheet1.xml", self._xlsx_sheet_xml(
                ["Categoría", "Prenda", "Cantidad", "Precio unitario", "Moneda", "Valorización"],
                [
                    [
                        categoria.categoria,
                        prenda.prenda,
                        prenda.cantidad_actual,
                        prenda.precio_unitario.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                        prenda.moneda,
                        prenda.valorizacion.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                    ]
                    for categoria in reporte.categorias
                    for prenda in categoria.prendas
                ],
            ))
            archive.writestr("xl/worksheets/sheet2.xml", self._xlsx_sheet_xml(
                ["Categoría", "Cantidad total", "Valorización total"],
                [
                    [categoria.categoria, categoria.cantidad_total, categoria.valorizacion_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)]
                    for categoria in reporte.categorias
                ] + [["TOTAL", reporte.cantidad_total, reporte.valorizacion_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)]],
            ))
        return buffer.getvalue()

    def _generar_pdf(self, reporte: ReporteInventario) -> bytes:
        lineas = self._lineas_pdf(reporte)
        paginas = [lineas[indice : indice + 42] for indice in range(0, len(lineas), 42)] or [["Inventario sin registros"]]

        font_object_number = 3 + len(paginas) * 2
        pages_refs = [3 + indice * 2 for indice in range(len(paginas))]
        objects: list[bytes] = [
            self._pdf_object(1, "/Type /Catalog /Pages 2 0 R"),
            self._pdf_object(2, f"/Type /Pages /Kids [{' '.join(f'{ref} 0 R' for ref in pages_refs)}] /Count {len(paginas)}"),
        ]

        for page_index, pagina in enumerate(paginas, start=1):
            page_number = 3 + (page_index - 1) * 2
            content_number = page_number + 1
            objects.append(
                self._pdf_object(
                    page_number,
                    f"/Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 {font_object_number} 0 R >> >> /Contents {content_number} 0 R",
                )
            )
            content = self._build_pdf_page_content(pagina, page_index, len(paginas))
            objects.append(self._pdf_stream_object(content_number, content))

        objects.append(self._pdf_object(font_object_number, "/Type /Font /Subtype /Type1 /BaseFont /Helvetica"))
        return self._ensamblar_pdf(objects)

    @staticmethod
    def _pdf_object(object_number: int, contenido: str) -> bytes:
        return f"{object_number} 0 obj << {contenido} >> endobj\n".encode("latin-1")

    @staticmethod
    def _pdf_stream_object(object_number: int, contenido: bytes) -> bytes:
        encabezado = f"{object_number} 0 obj << /Length {len(contenido)} >> stream\n".encode("latin-1")
        return encabezado + contenido + b"\nendstream\nendobj\n"

    @staticmethod
    def _ensamblar_pdf(objects: list[bytes]) -> bytes:
        partes = [b"%PDF-1.4\n"]
        offsets = [0]
        posicion_actual = len(partes[0])

        for objeto in objects:
            offsets.append(posicion_actual)
            partes.append(objeto)
            posicion_actual += len(objeto)

        cuerpo = b"".join(partes)
        xref_offset = len(cuerpo)
        total_objetos = len(objects)
        xref = [b"xref\n", f"0 {total_objetos + 1}\n".encode("latin-1"), b"0000000000 65535 f \n"]
        for offset in offsets[1:]:
            xref.append(f"{offset:010d} 00000 n \n".encode("latin-1"))

        trailer = f"trailer << /Size {total_objetos + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("latin-1")
        return cuerpo + b"".join(xref) + trailer

    def _build_pdf_page_content(self, lineas: Iterable[str], pagina: int, total_paginas: int) -> bytes:
        contenido = ["BT", "/F1 10 Tf", "50 800 Td"]
        for indice, linea in enumerate(lineas):
            texto = self._escapar_pdf(linea)
            if indice == 0:
                contenido.append(f"({texto}) Tj")
            else:
                contenido.append("T*")
                contenido.append(f"({texto}) Tj")
        contenido.extend([
            "T*",
            f"(Página {pagina} de {total_paginas}) Tj",
            "ET",
        ])
        return "\n".join(contenido).encode("latin-1", errors="replace")

    def _lineas_pdf(self, reporte: ReporteInventario) -> list[str]:
        lineas = [
            "Reporte del inventario actual",
            f"Generado: {timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M')}",
            f"Cantidad total: {reporte.cantidad_total}",
            f"Valorización total: {reporte.valorizacion_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}",
            "",
        ]
        for categoria in reporte.categorias:
            lineas.append(f"Categoría: {categoria.categoria} | Total: {categoria.cantidad_total} | Valor: {categoria.valorizacion_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}")
            for prenda in categoria.prendas:
                lineas.append(
                    f"- {prenda.prenda} ({prenda.prenda_id}) | Stock: {prenda.cantidad_actual} | Precio: {prenda.precio_unitario.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)} {prenda.moneda} | Valor: {prenda.valorizacion.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}"
                )
            lineas.append("")
        if not reporte.categorias:
            lineas.append("Sin registros de inventario para el filtro actual.")
        return lineas

    @staticmethod
    def _escapar_pdf(texto: str) -> str:
        return texto.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    @staticmethod
    def _xlsx_content_types() -> str:
        return (
            "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
            "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">"
            "<Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>"
            "<Default Extension=\"xml\" ContentType=\"application/xml\"/>"
            "<Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/>"
            "<Override PartName=\"/xl/worksheets/sheet1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/>"
            "<Override PartName=\"/xl/worksheets/sheet2.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/>"
            "<Override PartName=\"/xl/styles.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml\"/>"
            "</Types>"
        )

    @staticmethod
    def _xlsx_root_rels() -> str:
        return (
            "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
            "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
            "<Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/>"
            "</Relationships>"
        )

    @staticmethod
    def _xlsx_workbook_xml() -> str:
        return (
            "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
            "<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">"
            "<sheets>"
            "<sheet name=\"Resumen\" sheetId=\"1\" r:id=\"rId1\"/>"
            "<sheet name=\"Totales\" sheetId=\"2\" r:id=\"rId2\"/>"
            "</sheets>"
            "</workbook>"
        )

    @staticmethod
    def _xlsx_workbook_rels() -> str:
        return (
            "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
            "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
            "<Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet1.xml\"/>"
            "<Relationship Id=\"rId2\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet2.xml\"/>"
            "<Relationship Id=\"rId3\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\" Target=\"styles.xml\"/>"
            "</Relationships>"
        )

    @staticmethod
    def _xlsx_styles_xml() -> str:
        return (
            "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
            "<styleSheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">"
            "<fonts count=\"1\"><font><sz val=\"11\"/><color theme=\"1\"/><name val=\"Calibri\"/><family val=\"2\"/></font></fonts>"
            "<fills count=\"1\"><fill><patternFill patternType=\"none\"/></fill></fills>"
            "<borders count=\"1\"><border><left/><right/><top/><bottom/><diagonal/></border></borders>"
            "<cellStyleXfs count=\"1\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\"/></cellStyleXfs>"
            "<cellXfs count=\"1\"><xf numFmtId=\"0\" fontId=\"0\" fillId=\"0\" borderId=\"0\" xfId=\"0\"/></cellXfs>"
            "</styleSheet>"
        )

    @staticmethod
    def _xlsx_sheet_xml(encabezados: list[str], filas: list[list[object]]) -> str:
        filas_xml = []
        filas_xml.append(ServicioReporteInventario._xlsx_row_xml(1, encabezados))
        for indice, fila in enumerate(filas, start=2):
            filas_xml.append(ServicioReporteInventario._xlsx_row_xml(indice, fila))
        return (
            "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
            "<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">"
            f"<sheetData>{''.join(filas_xml)}</sheetData>"
            "</worksheet>"
        )

    @staticmethod
    def _xlsx_row_xml(row_number: int, values: list[object]) -> str:
        cells = []
        for column_index, value in enumerate(values, start=1):
            reference = ServicioReporteInventario._xlsx_cell_reference(column_index, row_number)
            cells.append(ServicioReporteInventario._xlsx_cell_xml(reference, value))
        return f"<row r=\"{row_number}\">{''.join(cells)}</row>"

    @staticmethod
    def _xlsx_cell_reference(column_index: int, row_number: int) -> str:
        letters = ""
        while column_index:
            column_index, remainder = divmod(column_index - 1, 26)
            letters = chr(65 + remainder) + letters
        return f"{letters}{row_number}"

    @staticmethod
    def _xlsx_cell_xml(reference: str, value: object) -> str:
        if isinstance(value, bool):
            return f"<c r=\"{reference}\" t=\"b\"><v>{int(value)}</v></c>"
        if isinstance(value, (int, Decimal)):
            return f"<c r=\"{reference}\"><v>{xml_escape(str(value))}</v></c>"
        return f"<c r=\"{reference}\" t=\"inlineStr\"><is><t>{xml_escape(str(value))}</t></is></c>"
