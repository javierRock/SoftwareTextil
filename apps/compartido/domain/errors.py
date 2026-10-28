"""Error base de todo el dominio.

Tener una raiz comun permite que un caso de uso que orquesta varios agregados
(por ejemplo, generar un pedido a partir de un carrito) capture cualquier
violacion de regla de negocio con una sola clausula, sin enumerar modulos.

Hereda de `ValueError` para mantener compatibilidad con el codigo que ya
trataba estos errores como errores de valor.
"""


class DominioError(ValueError):
    """Se violo una regla de negocio."""
