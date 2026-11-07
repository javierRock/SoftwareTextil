"""Suite de servicio: ServicioCatalogo con dobles de prueba (Lab 05).

`RepositorioPrenda` y `RepositorioCatalogo` se reemplazan por mocks con la
firma del contrato. Se verifica que el servicio valide referencias antes de
persistir y que nunca guarde un agregado invalido.
"""

from decimal import Decimal
from unittest.mock import create_autospec

import pytest

from apps.catalogo.application.services import ServicioCatalogo
from apps.catalogo.domain.excepciones import RecursoNoEncontradoError, ValidacionError
from apps.catalogo.domain.prenda import Categoria, PrendaFabrica
from apps.catalogo.domain.repositorios import RepositorioCatalogo, RepositorioPrenda
from apps.compartido.domain.dinero import Dinero
from apps.compartido.domain.enums import EstadoPrenda


class TestServicioCatalogoConMocks:
    def setup_method(self) -> None:
        self.repo_prenda = create_autospec(RepositorioPrenda, instance=True)
        self.repo_catalogo = create_autospec(RepositorioCatalogo, instance=True)
        self.servicio = ServicioCatalogo(self.repo_prenda, self.repo_catalogo)
        self.repo_catalogo.buscar_categoria.return_value = Categoria("c-1", "Polos")

    def _crear(self, **cambios):
        datos = {
            "nombre": "Polo",
            "descripcion": "Algodon",
            "precio_monto": "39.90",
            "precio_moneda": "PEN",
            "categoria_id": "c-1",
            "registrado_por": None,
            "tallas": ["S", "M"],
        } | cambios
        return self.servicio.crear_prenda(**datos)

    def test_crear_prenda_valida_categoria_y_guarda(self) -> None:
        prenda = self._crear()

        self.repo_catalogo.buscar_categoria.assert_called_once_with("c-1")
        self.repo_prenda.guardar.assert_called_once_with(prenda)
        assert prenda.precio == Dinero(Decimal("39.90"))

    def test_categoria_inexistente_no_guarda(self) -> None:
        self.repo_catalogo.buscar_categoria.return_value = None

        with pytest.raises(RecursoNoEncontradoError):
            self._crear()

        self.repo_prenda.guardar.assert_not_called()

    def test_tipo_de_producto_inexistente_no_guarda(self) -> None:
        self.repo_catalogo.buscar_tipo.return_value = None

        with pytest.raises(RecursoNoEncontradoError):
            self._crear(tipo_producto_id="t-x")

        self.repo_catalogo.buscar_tipo.assert_called_once_with("t-x")
        self.repo_prenda.guardar.assert_not_called()

    @pytest.mark.parametrize("monto", ["abc", "-5", "0"])
    def test_precio_invalido_no_guarda(self, monto: str) -> None:
        with pytest.raises(ValidacionError):
            self._crear(precio_monto=monto)
        self.repo_prenda.guardar.assert_not_called()

    def test_desactivar_prenda_existente(self) -> None:
        prenda = PrendaFabrica.crear(
            "Polo", "", Dinero(Decimal("10.00")), "c-1", None, tallas=["M"]
        )
        self.repo_prenda.buscar_por_id.return_value = prenda

        resultado = self.servicio.desactivar_prenda(prenda.id)

        assert resultado.estado == EstadoPrenda.INACTIVA
        self.repo_prenda.guardar.assert_called_once_with(prenda)

    def test_buscar_prenda_inexistente(self) -> None:
        self.repo_prenda.buscar_por_id.return_value = None

        with pytest.raises(RecursoNoEncontradoError):
            self.servicio.buscar_prenda("p-x")
