"""Traduccion entre los objetos de valor del dominio y sus columnas.

Concentra aqui la conversion que antes repetia cada repositorio, para que el
par de columnas `<concepto>_monto` / `<concepto>_moneda` tenga una sola lectura
y una sola escritura en todo el proyecto.
"""

from decimal import Decimal
from uuid import UUID

from apps.compartido.domain.dinero import Dinero


def a_dinero(monto: Decimal, moneda: str) -> Dinero:
    """Reconstruye el objeto de valor a partir de sus dos columnas."""
    return Dinero(Decimal(monto), moneda)


def de_dinero(dinero: Dinero) -> tuple[Decimal, str]:
    """Descompone el objeto de valor en el par de columnas persistidas."""
    return dinero.monto, dinero.moneda


def a_texto(identificador: UUID | str | None) -> str | None:
    """Normaliza a `str` los identificadores que el dominio maneja como texto."""
    return None if identificador is None else str(identificador)


def uuid_valido(identificador: object) -> UUID | None:
    """Devuelve el UUID del identificador, o `None` si no tiene esa forma.

    Las claves primarias son `uuid`, asi que consultar por un texto arbitrario
    haria fallar la conversion del ORM. Un identificador con forma invalida
    describe un recurso que no existe, y esa es la respuesta que corresponde:
    `None`, para que la vista devuelva 404 en lugar de un error 500.
    """
    try:
        return UUID(str(identificador))
    except (AttributeError, TypeError, ValueError):
        return None
