# Ciclo TDD y refactorización — Quality & Automation

## Caso seleccionado

El caso de uso seleccionado es `ServicioPagos.registrar_pago`, que coordina el pedido, valida al cliente y persiste el pago mediante contratos de repositorio.

## Red — prueba que expresa el comportamiento

Las pruebas de `tests/pagos/test_servicio_pagos_doubles.py` expresan el comportamiento esperado:

- Un pedido válido genera un pago pendiente.
- Los repositorios reciben exactamente los identificadores y el pago creado.
- Un monto diferente al total produce `MontoNoCoincideConPedido`.
- Cuando la validación falla, no se llama a `crear`.

## Green — implementación mínima

`apps/ventas/pagos/application/services.py` implementa el caso de uso con las dependencias recibidas por constructor. Los puertos se sustituyen por dobles durante la prueba, de modo que el resultado se valida sin conectarse a la persistencia.

## Refactor — mejora conservando el comportamiento

La implementación mantiene responsabilidades separadas:

- `ServicioPagos` coordina el caso de uso.
- `RepositorioPago` y `RepositorioPedidoPago` son contratos.
- `Pago` y `PagoFactory` contienen las reglas del dominio.
- La unidad de trabajo se inyecta y puede reemplazarse por `nullcontext` o un `MagicMock`.

La suite final valida el comportamiento después de la refactorización.

## Comprobación

```bash
uv run pytest tests/pagos/test_servicio_pagos_doubles.py -q
```

Resultado registrado: **3 pruebas aprobadas**.
