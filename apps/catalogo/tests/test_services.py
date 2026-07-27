from apps.catalogo.application.services import ServicioCatalogo
from apps.catalogo.domain.prenda import Categoria, Prenda, TipoProducto
from apps.catalogo.domain.repositorios import RepositorioCatalogo, RepositorioPrenda
from apps.compartido.domain.enums import EstadoPrenda


class RepositorioPrendaEnMemoria(RepositorioPrenda):
    def __init__(self) -> None:
        self.prendas: dict[str, Prenda] = {}

    def guardar(self, prenda: Prenda) -> None:
        self.prendas[prenda.id] = prenda

    def buscar_por_id(self, prenda_id: str) -> Prenda | None:
        return self.prendas.get(prenda_id)

    def listar(self) -> list[Prenda]:
        return list(self.prendas.values())


class RepositorioCatalogoEnMemoria(RepositorioCatalogo):
    def __init__(self) -> None:
        self.categorias: dict[str, Categoria] = {}
        self.tipos: dict[str, TipoProducto] = {}

    def guardar_categoria(self, categoria: Categoria) -> None:
        self.categorias[categoria.id] = categoria

    def guardar_tipo_producto(self, tipo_producto: TipoProducto) -> None:
        self.tipos[tipo_producto.id] = tipo_producto

    def listar_categorias(self) -> list[Categoria]:
        return list(self.categorias.values())

    def listar_tipos(self) -> list[TipoProducto]:
        return list(self.tipos.values())

    def buscar_categoria(self, categoria_id: str) -> Categoria | None:
        return self.categorias.get(categoria_id)


def crear_servicio() -> tuple[
    ServicioCatalogo,
    RepositorioPrendaEnMemoria,
    RepositorioCatalogoEnMemoria,
]:
    repo_prenda = RepositorioPrendaEnMemoria()
    repo_catalogo = RepositorioCatalogoEnMemoria()
    return ServicioCatalogo(repo_prenda, repo_catalogo), repo_prenda, repo_catalogo


def test_servicio_gestiona_prendas_con_repositorios_en_memoria() -> None:
    servicio, repo_prenda, repo_catalogo = crear_servicio()
    repo_catalogo.guardar_categoria(Categoria(id="categoria-1", nombre="Polos"))

    prenda = servicio.crear_prenda(
        nombre="Polo basico",
        descripcion="Algodon",
        precio_monto="39.90",
        precio_moneda="PEN",
        categoria_id="categoria-1",
        registrado_por="usuario-1",
    )

    assert servicio.buscar_prenda(prenda.id) == prenda
    assert servicio.listar_prendas() == [prenda]
    assert repo_prenda.prendas[prenda.id] == prenda

    servicio.desactivar_prenda(prenda.id)

    assert prenda.estado == EstadoPrenda.INACTIVA


def test_servicio_gestiona_catalogo_con_repositorios_en_memoria() -> None:
    servicio, _, _ = crear_servicio()

    categoria = servicio.crear_categoria("Pantalones", "Prendas inferiores")
    tipo = servicio.crear_tipo_producto("Jean", {"material": "denim"})

    assert servicio.listar_categorias() == [categoria]
    assert servicio.listar_tipos() == [tipo]


def test_servicio_conserva_errores_para_recursos_inexistentes() -> None:
    servicio, _, _ = crear_servicio()

    try:
        servicio.crear_prenda(
            nombre="Polo",
            descripcion="",
            precio_monto="10",
            precio_moneda="PEN",
            categoria_id="inexistente",
            registrado_por="usuario-1",
        )
    except ValueError as exc:
        assert str(exc) == "La categoria no existe"
    else:
        raise AssertionError("Se esperaba el error de categoria inexistente")

    try:
        servicio.desactivar_prenda("inexistente")
    except ValueError as exc:
        assert str(exc) == "Prenda no encontrada"
    else:
        raise AssertionError("Se esperaba el error de prenda inexistente")
