"""Fabricas de campos y restricciones derivadas de los enums del dominio.

Los `StrEnum` de `compartido/domain/enums` son la unica fuente de verdad de los
valores validos. Estas funciones construyen a partir de ellos tanto las
`choices` del ORM como los `CheckConstraint` de la base de datos, de modo que
agregar un valor al enum basta para que la validacion de aplicacion y la de
base de datos queden alineadas.
"""

from decimal import Decimal
from enum import StrEnum

from django.db import models

from apps.compartido.domain.enums import Moneda

DIGITOS_MONTO = 12
DECIMALES_MONTO = 2
LONGITUD_ESTADO = 30
LONGITUD_MONEDA = 3


def valores(enumeracion: type[StrEnum]) -> list[str]:
    """Devuelve los valores del enum, para `__in` y `CheckConstraint`."""
    return [miembro.value for miembro in enumeracion]


def opciones(enumeracion: type[StrEnum]) -> list[tuple[str, str]]:
    """Devuelve las `choices` del ORM a partir del enum."""
    return [(miembro.value, miembro.value) for miembro in enumeracion]


def campo_estado(
    enumeracion: type[StrEnum],
    *,
    default: StrEnum,
) -> models.CharField:
    """Columna de estado validada contra un enum del dominio."""
    return models.CharField(
        max_length=LONGITUD_ESTADO,
        choices=opciones(enumeracion),
        default=default.value,
    )


def campo_monto(**extra: object) -> models.DecimalField:
    """Componente `monto` del objeto de valor `Dinero`."""
    return models.DecimalField(
        max_digits=DIGITOS_MONTO,
        decimal_places=DECIMALES_MONTO,
        **extra,
    )


def campo_moneda(**extra: object) -> models.CharField:
    """Componente `moneda` del objeto de valor `Dinero`."""
    return models.CharField(
        max_length=LONGITUD_MONEDA,
        choices=opciones(Moneda),
        default=Moneda.PEN.value,
        **extra,
    )


def check_enum(
    campo: str,
    enumeracion: type[StrEnum],
    nombre: str,
) -> models.CheckConstraint:
    """Restringe una columna a los valores del enum indicado."""
    return models.CheckConstraint(
        condition=models.Q(**{f"{campo}__in": valores(enumeracion)}),
        name=nombre,
    )


def check_positivo(campo: str, nombre: str) -> models.CheckConstraint:
    """Exige que una cantidad o importe sea estrictamente mayor a cero."""
    return models.CheckConstraint(
        condition=models.Q(**{f"{campo}__gt": 0}),
        name=nombre,
    )


def check_no_negativo(campo: str, nombre: str) -> models.CheckConstraint:
    """Exige que una cantidad no baje de cero."""
    return models.CheckConstraint(
        condition=models.Q(**{f"{campo}__gte": 0}),
        name=nombre,
    )


def check_monto_positivo(prefijo: str, nombre: str) -> models.CheckConstraint:
    """Exige un importe mayor a cero sobre el par de columnas de `Dinero`."""
    return models.CheckConstraint(
        condition=models.Q(**{f"{prefijo}_monto__gt": Decimal("0")}),
        name=nombre,
    )
