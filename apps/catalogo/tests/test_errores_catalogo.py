import pytest
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.views import APIView

from apps.catalogo.domain.excepciones import (
    CatalogoError,
    OperacionNoPermitidaError,
    RecursoNoEncontradoError,
    ValidacionError,
)
from apps.catalogo.presentation.errors import ManejoErroresCatalogoMixin


class VistaErrorCatalogo(ManejoErroresCatalogoMixin, APIView):
    excepcion = CatalogoError

    def get(self, request):
        raise self.excepcion("Error de prueba")


@pytest.mark.parametrize(
    ("excepcion", "estado_http"),
    [
        (ValidacionError, 400),
        (RecursoNoEncontradoError, 404),
        (OperacionNoPermitidaError, 405),
    ],
)
def test_presentacion_traduce_categoria_de_error_a_http(
    excepcion,
    estado_http,
) -> None:
    request = APIRequestFactory().get("/errores/")
    vista = VistaErrorCatalogo.as_view(excepcion=excepcion)

    respuesta = vista(request)

    assert respuesta.status_code == estado_http
    assert "error" in respuesta.data


def test_excepciones_de_negocio_comparten_una_base() -> None:
    for excepcion in (
        ValidacionError,
        RecursoNoEncontradoError,
        OperacionNoPermitidaError,
    ):
        assert issubclass(excepcion, CatalogoError)


@pytest.mark.django_db
def test_error_inesperado_conserva_respuesta_http_500(monkeypatch) -> None:
    class ServicioConFallo:
        def buscar_prendas(self, **kwargs):
            raise RuntimeError("Fallo inesperado")

    monkeypatch.setattr(
        "apps.catalogo.presentation.views._servicio",
        lambda: ServicioConFallo(),
    )
    cliente = APIClient()
    cliente.raise_request_exception = False

    respuesta = cliente.get("/api/prendas/")

    assert respuesta.status_code == 500
